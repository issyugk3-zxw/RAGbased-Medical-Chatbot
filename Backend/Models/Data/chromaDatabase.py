from io import StringIO

import chromadb
import torch
from chromadb.config import Settings
from chromadb.utils.embedding_functions import EmbeddingFunction
import pandas as pd
from typing import List, Dict, Optional
from Models.AnalysisModels.Bert_ZH_Model import Bert_ZH_Model
from transformers import BertModel, BertTokenizer

from torch.nn.functional import normalize
from Models.AnalysisModels import Bert_zh_Model
import os
from utils import chinese_to_pinyin
class BertEmbedding(EmbeddingFunction):
    def __init__(self, bert_model):
        super().__init__()
        self.model = bert_model

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为嵌入向量"""
        print(f"BertEmbedding 输入文本数量: {len(texts)}")  # 打印输入数量
        embeddings = self.model.getBertFeatsNumpy(texts)
        semantic = embeddings[:, 0, :]
        output_embeddings = semantic.tolist()
        print(f"BertEmbedding 输出向量数量: {len(output_embeddings)}")  # 打印输出数量
        if len(output_embeddings) != len(texts):
            print("!!! 警告: EmbeddingFunction 输入输出数量不一致 !!!")  # 警告
        return output_embeddings


class HuggingFaceBertEmbedding(EmbeddingFunction):
    def __init__(self, device: str = None, normalize_embeddings: bool = True):
        """
        初始化 HuggingFace BERT 嵌入模型

        参数:
            model_name: 预训练模型名称或路径 (默认: 'bert-base-uncased')
            device: 指定设备 ('cuda' 或 'cpu')，如果为None则自动选择
            normalize_embeddings: 是否对输出嵌入进行L2归一化
        """
        super().__init__()
        self.tokenizer = BertTokenizer.from_pretrained("hfl/chinese-roberta-wwm-ext")
        self.model = BertModel.from_pretrained(
            "../AnalysisModels/cache/model/chinese-roberta-wwm-ext"
        )
        self.normalize = normalize_embeddings

        # 设置设备
        self.device = (
            device if device else "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.model.eval()  # 设置为评估模式

    def __call__(self, texts: List[str]) -> List[List[float]]:
        """将文本列表转换为嵌入向量"""
        print(f"HuggingFaceBertEmbedding 输入文本数量: {len(texts)}")

        # 分词并转换为模型输入
        inputs = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt", max_length=512
        ).to(self.device)

        # 获取嵌入
        with torch.no_grad():
            outputs = self.model(**inputs)

        # 使用[CLS] token的表示作为句子嵌入
        embeddings = outputs.last_hidden_state[:, 0, :]

        if self.normalize:
            embeddings = normalize(embeddings, p=2, dim=1)

        output_embeddings = embeddings.cpu().numpy().tolist()

        print(f"HuggingFaceBertEmbedding 输出向量数量: {len(output_embeddings)}")
        if len(output_embeddings) != len(texts):
            print("!!! 警告: EmbeddingFunction 输入输出数量不一致 !!!")

        return output_embeddings





class ChromaOperator:
    def __init__(self, bert_model=None, host="localhost", port=8000):
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
        )
        if bert_model is None:
            self.bert = Bert_zh_Model
            bert_model = BertEmbedding(self.bert)
        self.embedding = bert_model
        self.departments = []  

    def create_collection(self, py_name: str, zh_name :str):
        """创建集合（会自动持久化）"""
        return self.client.create_collection(
            name=py_name, embedding_function=self.embedding,metadata={"zh_name": f'{zh_name}'}
        )

    def get_collection(self, name: str):
        """获取已存在的集合"""
        return self.client.get_collection(name=name, embedding_function=self.embedding)

    def reset_database(self):
        """清空数据库（需要服务器配置ALLOW_RESET=True）"""
        self.client.reset()

    def add_documents(
        self, collection_name: str, documents: List[str], ids: List[str], metadatas=None
    ):
        """添加文档到指定集合"""
        collection = self.get_collection(collection_name)
        collection.add(documents=documents, ids=ids, metadatas=metadatas)

    def query(self, collection_name: str, query_texts: List[str], n_results: int = 5):
        """相似性查询"""
        collection = self.get_collection(collection_name)
        return collection.query(query_texts=query_texts, n_results=n_results)
    
    def create_department_collections_from_txt(self, txt_path: str):
        """
        从txt文件创建科室对应的collection
        每行一个科室名称
        """
        with open(txt_path, 'r', encoding='utf-8') as f:
            departments = [line.strip() for line in f if line.strip()]
        
        self.departments = departments
        
        for dept in departments:
            try:
                dept_py = chinese_to_pinyin(dept)
                self.create_collection(dept_py, dept)
                print(f"成功创建科室集合: {dept}, 为:{dept_py}")
            except Exception as e:
                print(f"创建科室集合 {dept} 时出错: {str(e)}")

    def process_csv_and_store(self, csv_path: str, id_prefix: str = "doc"):
        """
        处理CSV文件并将数据存储到对应的科室collection中，分批处理以避免一次性编码过多。

        参数:
            csv_path: CSV文件路径
            id_prefix: 文档ID的前缀，默认为"doc"
        """
        if not hasattr(self, 'departments') or not self.departments:
            # Added check for hasattr in case departments isn't an instance attribute
            raise ValueError("请先调用create_department_collections_from_txt加载科室列表")

        try:
            with open(csv_path, encoding='gb18030', errors='ignore') as f:
                content = f.read()
            df = pd.read_csv(StringIO(content))

            # 过滤出科室在指定列表中的行
            valid_df = df[df['department'].isin(self.departments)].reset_index(drop=True)  # Reset index after filtering

        except FileNotFoundError:
            print(f"错误: 文件未找到 - {csv_path}")
            return
        except Exception as e:
            print(f"读取或处理CSV文件时出错: {str(e)}")
            return

        if valid_df.empty:
            print("警告: 没有找到匹配科室的数据")
            return

        batch_size = 30
        print(f"开始按科室处理数据，每批次最多添加 {batch_size} 条记录...")

        # 按科室分组处理
        for dept, group in valid_df.groupby('department'):
            try:
                dept_py = chinese_to_pinyin(dept)
                collection = self.get_collection(dept_py)
                department_documents = group['ask'].tolist()
                department_titles = group['title'].tolist()
                department_answers = group['answer'].tolist()
                total_docs_in_dept = len(department_documents)

                print(f"开始处理科室: {dept} ({total_docs_in_dept} 条记录)")

                for i in range(0, total_docs_in_dept, batch_size):
                    # Calculate the slice for the current batch
                    start_index = i
                    end_index = min(i + batch_size, total_docs_in_dept)  # Ensure end_index doesn't exceed total
                    batch_num = (i // batch_size) + 1  # Calculate batch number

                    batch_documents = department_documents[start_index:end_index]
                    batch_ids = [f"{id_prefix}_{start_index + j}" for j in range(len(batch_documents))]

                    batch_metadatas = [
                        {"title": department_titles[start_index + j], "answer": department_answers[start_index + j]}
                        for j in range(len(batch_documents))
                    ]
                    collection.add(
                        documents=batch_documents,
                        ids=batch_ids,
                        metadatas=batch_metadatas
                    )
                    print(f"  成功添加 科室 {dept} 的第 {batch_num} 批次 ({len(batch_documents)} 条数据)")

                print(f"完成添加科室 {dept} 的所有数据")

            except Exception as e:
                print(f"处理科室 {dept} 时出错: {str(e)}")
                # Continue to the next department even if one fails
    
    def get_department_collections(self) -> List[str]:
        """获取所有科室collection名称"""
        return self.departments
    
    def delete_department_collection(self, department: str):
        """删除指定科室的collection"""
        try:
            self.client.delete_collection(department)
            if department in self.departments:
                self.departments.remove(department)
            print(f"成功删除科室集合: {department}")
        except Exception as e:
            print(f"删除科室集合 {department} 时出错: {str(e)}")


if __name__ == '__main__':
    chroma_operator = ChromaOperator()

    script_dir = os.path.dirname(os.path.abspath(__file__))


    txt_path = os.path.join(script_dir, '../AnalysisModels','data','ent_aug', '二级科室.txt')

    csv_path = os.path.join(script_dir, '../AnalysisModels','data','augment_data', 'nk_data.csv')
    chroma_operator.create_department_collections_from_txt(txt_path)
    chroma_operator.process_csv_and_store(csv_path)





