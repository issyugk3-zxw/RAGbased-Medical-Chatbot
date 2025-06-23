from typing import List, Optional, Any
from pydantic import Field

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.base.embeddings.base import BaseEmbedding, Embedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb
from Models.Data.db_init import chroma_operator
from utils import chinese_to_pinyin
from Models.CustomLLM.QWen import QWen

class CustomBertEmbedding(BaseEmbedding):
    chroma_bert: Any = Field(default=None, description="The Chroma BERT embedding model")
    def __init__(self, chroma_bert,**kwargs):
        super().__init__(**kwargs)
        self.chroma_bert = chroma_bert


    @classmethod
    def class_name(cls) -> str:
        return "Custom Bert Embedding"
    def _get_text_embedding(self, text: str) -> List[float]:
        return self.chroma_bert([text])[0]

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self.chroma_bert(texts)

    def _get_query_embedding(self, query: str) -> List[float]:
         return self._get_text_embedding(query)

    def _get_node_embedding(self, node) -> List[float]:
        return self._get_text_embedding(node.get_content())

    def _aget_query_embedding(self, query: str) -> Embedding:
        raise NotImplementedError



class QueryEnginManager:
    def __init__(self):
        self.chroma_operator = chroma_operator
        self.selected_collection = None
        self.vector_store = None
        self.llm = QWen()
        self.custom_embedding = CustomBertEmbedding(chroma_bert=chroma_operator.embedding)


    def switch_to_department(self, department):
        self.selected_collection = department
        department_py = chinese_to_pinyin(department)
        chroma_collection = self.chroma_operator.get_collection(department_py)
        self.vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store, embed_model=self.custom_embedding)


    def get_query_engin(self, department, k = 5):
        self.switch_to_department(department)

        return self.index.as_query_engine(llm=self.llm,similarity_top_k=k)
    
    def get_query_knowledge(self, query, department, k = 5):
        qe = self.get_query_engin(department, k)
        response = qe.query(query)
        return {
            "response": response.response,
            "source_nodes": [
                {
                    "id": i,
                    "score": node.score,
                    "title": node.metadata["title"],
                    "answer": node.metadata["answer"],
                }
                for i, node in enumerate(response.source_nodes)
            ],
        }

if __name__ == "__main__":
    qem = QueryEnginManager()
    qe = qem.get_query_engin("消化内科")
    response = qe.query("经常性的反酸、反胃是怎么回事")
    print(response)
    print("\n--- 检索到的文档信息 ---")
    for i, node in enumerate(response.source_nodes):
        print(f"文档 {i + 1}:")
        print(f"  得分 (Similarity): {node.score}")
        print(f"  Metadata: {node.metadata}")
        print("-" * 20)
