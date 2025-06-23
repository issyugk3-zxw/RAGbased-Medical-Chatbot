import torch

from Models.AnalysisModels.dataset import *
from Models.AnalysisModels.Bert_ZH_Model import *
import json
from seqeval.metrics import f1_score, accuracy_score, precision_score


class Trainer:
    def __init__(self, language="zh"):
        self.max_len = 50
        self.epoch = 30
        self.batch_size = 60
        self.hidden_size = 128
        self.bi = True
        self.lr = 1e-5
        self.cache_model = "best_roberta_rnn_model_ent_aug"
        all_text, all_label = get_data(os.path.join("data", "ner_data_aug.json"))
        train_text, test_text, train_label, test_label = train_test_split(
            all_text, all_label, test_size=0.02, random_state=42
        )
        if os.path.exists("./cache/tag2idx.npy"):
            with open("./cache/tag2idx.npy", "rb") as f:
                tag2idx = pickle.load(f)
        else:
            tag2idx = build_tag2idx(all_label)
            with open("cache/tag2idx.npy", "wb") as f:
                pickle.dump(tag2idx, f)
        self.idx2tag = list(tag2idx)
        if language == "zh":
            self.bertmodel = Bert_ZH_Model(
                model="./cache/model/chinese-roberta-wwm-ext",
                hidden_size=self.hidden_size,
                tag_num=len(tag2idx),
                bi=self.bi,
            )
        self.opt = torch.optim.Adam(self.bertmodel.model.parameters(), lr=self.lr)
        train_dataset = Nerdataset(
            train_text, train_label, self.bertmodel.tokenizer, self.max_len, tag2idx
        )
        self.train_dataloader = DataLoader(
            train_dataset, batch_size=self.batch_size, shuffle=True
        )
        test_dataset = Nerdataset(
            test_text,
            test_label,
            self.bertmodel.tokenizer,
            self.max_len,
            tag2idx,
            is_test=True,
        )
        self.test_dataloader = DataLoader(test_dataset, batch_size=1, shuffle=False)
        self.device = (
            torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
        )

    def train_model(self):
        self.bertmodel.model.to(self.device)
        bestf1 = -1
        is_train = True
        if is_train:
            for e in range(self.epoch):
                self.bertmodel.model.train()
                loss_sum = 0
                ba = 0
                for x, y, batch_len in tqdm(self.train_dataloader):
                    x = x.to(self.device)
                    y = y.to(self.device)
                    self.opt.zero_grad()
                    loss = self.bertmodel.model(x, y)
                    loss.backward()

                    self.opt.step()
                    loss_sum += loss
                    ba += 1
                all_pre = []
                all_label = []
                self.bertmodel.model.eval()
                with torch.no_grad():
                    for x, y, batch_len in tqdm(self.test_dataloader):

                        assert len(x) == len(y)
                        x = x.to(self.device)
                        pre = self.bertmodel.model(x)
                        pre = [self.idx2tag[i] for i in pre[1 : batch_len + 1]]
                        all_pre.append(pre)

                        label = [self.idx2tag[i] for i in y[0][1 : batch_len + 1]]
                        all_label.append(label)
                f1 = f1_score(all_pre, all_label)
                accuracy = accuracy_score(all_label, all_pre)
                precision = precision_score(all_label, all_pre)
                if f1 > bestf1:
                    bestf1 = f1
                    print(
                        f"e={e},loss={loss_sum / ba:.5f} accuracy={accuracy:.5f} precision={precision:.5f} f1={f1:.5f} ---------------------->best"
                    )
                    torch.save(
                        self.bertmodel.model.state_dict(),
                        f"./cache/model/{self.cache_model}.pt",
                    )
                else:
                    print(
                        f"e={e},loss={loss_sum / ba:.5f} accuracy={accuracy:.5f} precision={precision:.5f} f1={f1:.5f}")

        rule = RuleMatcher()
        tfidf_r = TFIDIalign()

        while True:
            sen = input("请输入:")
            print(
                get_ner_result(
                    self.bertmodel.model,
                    self.bertmodel.tokenizer,
                    sen,
                    rule,
                    tfidf_r,
                    self.device,
                    self.idx2tag,
                )
            )


if __name__ == "__main__":
    trainer = Trainer()
    trainer.train_model()