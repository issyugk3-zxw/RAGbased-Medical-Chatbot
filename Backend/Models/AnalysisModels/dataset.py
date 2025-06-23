import os
import random
import torch
from torch import nn
import pickle
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
from transformers import BertModel, BertTokenizer
from tqdm import tqdm
from seqeval.metrics import f1_score
import ahocorasick
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json


def get_data(path, max_len=None):
    all_text, all_tag = [], []
    with open(path, "r", encoding="utf8") as f:
        all_data = json.load(f)
    for data in all_data:
        sentences = data["sentences"]
        labels = data["labels"]

        if len(sentences) > 2:
            all_text.append(sentences)
            all_tag.append(labels)
    if max_len is not None:
        return all_text[:max_len], all_tag[:max_len]
    return all_text, all_tag


class RuleMatcher:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.idx2type = idx2type = [
            "疾病",
            "症状",
            "检查手段",
            "一级科室",
            "二级科室",
            "其他",
            "食物",
            "治疗方案",
            "药物",
            "食谱",
        ]
        self.type2idx = type2idx = {
            "疾病": 0,
            "症状": 1,
            "检查手段": 2,
            "一级科室": 3,
            "二级科室": 4,
            "其他": 5,
            "食物": 6,
            "治疗方案": 7,
            "药物": 8,
            "食谱": 9,
        }
        self.ahos = [ahocorasick.Automaton() for i in range(len(self.type2idx))]

        for type in idx2type:
            with open(
                os.path.join(script_dir, "data", "ent_aug", f"{type}.txt"),
                encoding="utf-8",
            ) as f:
                all_en = f.read().split("\n")
            for en in all_en:
                en = en.split(" ")[0]
                if len(en) >= 2:
                    self.ahos[type2idx[type]].add_word(en, en)
        for i in range(len(self.ahos)):
            self.ahos[i].make_automaton()

    def find(self, sen):
        rule_result = []
        mp = {}
        all_res = []
        all_ty = []
        for i in range(len(self.ahos)):
            now = list(self.ahos[i].iter(sen))
            all_res.extend(now)
            for j in range(len(now)):
                all_ty.append(self.idx2type[i])
        if len(all_res) != 0:
            all_res = sorted(all_res, key=lambda x: len(x[1]), reverse=True)
            for i, res in enumerate(all_res):
                be = res[0] - len(res[1]) + 1
                ed = res[0]
                if be in mp or ed in mp:
                    continue
                rule_result.append((be, ed, all_ty[i], res[1]))
                for t in range(be, ed + 1):
                    mp[t] = 1
        return rule_result


class TFIDIalign:
    def __init__(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        eneities_path = os.path.join(script_dir, "data", "ent_aug")
        files = os.listdir(eneities_path)
        files = [docu for docu in files if ".py" not in docu]

        self.tag_2_embs = {}
        self.tag_2_tfidf_model = {}
        self.tag_2_entity = {}
        for ty in files:
            with open(os.path.join(eneities_path, ty), "r", encoding="utf-8") as f:
                entities = f.read().split("\n")
                entities = [
                    ent
                    for ent in entities
                    if len(ent.split(" ")[0]) <= 15 and len(ent.split(" ")[0]) >= 1
                ]
                en_name = [ent.split(" ")[0] for ent in entities]
                ty = ty.strip(".txt")
                self.tag_2_entity[ty] = en_name
                tfidf_model = TfidfVectorizer(analyzer="char")
                embs = tfidf_model.fit_transform(en_name).toarray()
                self.tag_2_embs[ty] = embs
                self.tag_2_tfidf_model[ty] = tfidf_model

    def align(self, ent_list):
        new_result = {}
        for s, e, cls, ent in ent_list:
            ent_emb = self.tag_2_tfidf_model[cls].transform([ent])
            sim_score = cosine_similarity(ent_emb, self.tag_2_embs[cls])
            max_idx = sim_score[0].argmax()
            max_score = sim_score[0][max_idx]

            if max_score >= 0.5:
                matched_entity = self.tag_2_entity[cls][max_idx]
                if cls not in new_result:
                    new_result[cls] = []
                # 只有当这个实体不在列表中时才添加
                if matched_entity not in new_result[cls]:
                    new_result[cls].append(matched_entity)
        return new_result


class Nerdataset(Dataset):
    def __init__(self, all_text, all_label, tokenizer, max_len, tag2idx, is_test=False):
        self.all_text = all_text
        self.all_label = all_label
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.tag2idx = tag2idx
        self.is_test = is_test

    def __getitem__(self, x):
        text, label = self.all_text[x], self.all_label[x]
        if self.is_test:
            max_len = min(len(self.all_text[x]) + 2, 500)
        else:
            max_len = self.max_len
        text, label = text[: max_len - 2], label[: max_len - 2]

        x_len = len(text)
        assert len(text) == len(label)
        text_idx = self.tokenizer.encode(text, add_special_token=True)
        label_idx = (
            [self.tag2idx["<PAD>"]]
            + [self.tag2idx[i] for i in label]
            + [self.tag2idx["<PAD>"]]
        )

        text_idx += [0] * (max_len - len(text_idx))
        label_idx += [self.tag2idx["<PAD>"]] * (max_len - len(label_idx))
        return torch.tensor(text_idx), torch.tensor(label_idx), x_len

    def __len__(self):
        return len(self.all_text)


def build_tag2idx(all_tag):
    tag2idx = {"<PAD>": 0}
    for sen in all_tag:
        for tag in sen:
            tag2idx[tag] = tag2idx.get(tag, len(tag2idx))
    return tag2idx


def merge(model_result_word, rule_result):
    result = model_result_word + rule_result
    result = sorted(result, key=lambda x: len(x[-1]), reverse=True)
    check_result = []
    seen_entities = set()

    for res in result:
        entity_key = (res[0], res[1], res[2], res[3])
        if entity_key not in seen_entities:
            check_result.append(res)
            seen_entities.add(entity_key)

    return check_result


def find_entities(tag):
    result = []
    label_len = len(tag)
    i = 0
    while i < label_len:
        if tag[i][0] == "B":
            type = tag[i].strip("B-")
            j = i + 1
            while j < label_len and tag[j][0] == "I":
                j += 1
            result.append((i, j - 1, type))
            i = j
        else:
            i = i + 1
    return result


def get_ner_result(model, tokenizer, sen, rule, tfidf_r, device, idx2tag):
    sen_to = tokenizer.encode(sen, add_special_tokens=True, return_tensors="pt").to(
        device
    )

    pre = model(sen_to).tolist()

    pre_tag = [idx2tag[i] for i in pre[1:-1]]
    model_result = find_entities(pre_tag)
    model_result_word = []
    for res in model_result:
        word = sen[res[0] : res[1] + 1]
        model_result_word.append((res[0], res[1], res[2], word))
    rule_result = rule.find(sen)

    merge_result = merge(model_result_word, rule_result)
    # print('模型结果',model_result_word)
    # print('规则结果',rule_result)
    tfidf_result = tfidf_r.align(merge_result)
    # print('整合结果', merge_result)
    # print('tfidf对齐结果', tfidf_result)
    return tfidf_result
