import torch
from torch import nn
import os
import pickle
import numpy as np
from transformers import BertModel, BertTokenizer

from Models.AnalysisModels.dataset import get_ner_result, RuleMatcher, TFIDIalign


class Bert_Model(nn.Module):
    def __init__(self, model_name, hidden_size, tag_num, bi):
        super().__init__()
        self.bert = BertModel.from_pretrained(model_name, local_files_only=True)
        self.gru = nn.RNN(
            input_size=768,
            hidden_size=hidden_size,
            num_layers=2,
            batch_first=True,
            bidirectional=bi,
        )
        if bi:
            self.classifier = nn.Linear(hidden_size * 2, tag_num)
        else:
            self.classifier = nn.Linear(hidden_size, tag_num)
        self.loss_fn = nn.CrossEntropyLoss(ignore_index=0)

    def getBertFeats(self, x):
        bert_0, _ = self.bert(x, attention_mask=(x > 0), return_dict=False)
        return bert_0

    def forward(self, x, label=None):
        bert_0, _ = self.bert(x, attention_mask=(x > 0), return_dict=False)
        gru_0, _ = self.gru(bert_0)
        pre = self.classifier(gru_0)
        if label is not None:
            loss = self.loss_fn(pre.reshape(-1, pre.shape[-1]), label.reshape(-1))
            return loss
        else:
            return torch.argmax(pre, dim=-1).squeeze(0)


class Bert_ZH_Model:
    def __init__(
        self,
        model="./cache/model/chinese-roberta-wwm-ext",
        hidden_size=128,
        tag_num=0,
        bi=True,
        is_train=False,
    ):
        super().__init__()
        script_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(script_dir, "cache", "tag2idx.npy"), "rb") as f:
            self.tag2idx = pickle.load(f)
        self.idx2tag = list(self.tag2idx)

        self.tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
        self.device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )

        if not is_train:
            self.hidden_size = 128
            self.bi = True
            self.model = Bert_Model(
                model_name=os.path.join(
                    script_dir, "cache", "model", "chinese-roberta-wwm-ext"
                ),
                hidden_size=self.hidden_size,
                tag_num=len(self.tag2idx),
                bi=self.bi,
            )
            self.model.load_state_dict(
                torch.load(
                    os.path.join(
                        script_dir,
                        "cache",
                        "model",
                        "best_roberta_rnn_model_ent_aug.pt",
                    )
                )
            )
            self.model.to(self.device)
            self.model.eval()
        else:
            self.model = Bert_Model(model, hidden_size, tag_num, bi)

        self.rule = RuleMatcher()
        self.tfidf_r = TFIDIalign()

    def getBertFeatsNumpy(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        inputs = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        ).to(self.device)

        with torch.no_grad():
            bert_feats = self.model.getBertFeats(inputs["input_ids"])

        # 转换为numpy数组
        if self.device != "cpu":
            return bert_feats.detach().cpu().numpy()
        return bert_feats.detach().numpy()

    def getNerResult(self, text):
        result = get_ner_result(
            self.model,
            self.tokenizer,
            text,
            self.rule,
            self.tfidf_r,
            self.device,
            self.idx2tag,
        )
        return result


if __name__ == "__main__":
    BertClassifier = Bert_ZH_Model()
    while True:
        sen = input("请输入:")
        print(BertClassifier.getNerResult(sen))
