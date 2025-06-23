from typing import Optional, cast

from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.core.llms import ChatMessage  # 如果需要ChatMessage
from llama_index.legacy.vector_stores import ChromaVectorStore

from Models.Data.chromaDatabase import ChromaOperator
from Models.Data.db_init import chroma_operator
from utils import  chinese_to_pinyin

class QueryEngineManager:
    def __init__(self, chroma_operator: ChromaOperator):

        self.chroma_operator = chroma_operator
        self.current_collection_py_name: Optional[str] = None
        self._vector_store: Optional[ChromaVectorStore] = None
        self._storage_context: Optional[StorageContext] = None
        self._index: Optional[VectorStoreIndex] = None # 缓存索引
        self._query_engine = None # 缓存查询引擎

    def switch_collection(self, collection_name_zh: str):

        print(f"\n切换到科室: {collection_name_zh}")
        collection_name_py = chinese_to_pinyin(collection_name_zh)
        self.current_collection_py_name = collection_name_py
        chroma_collection_object = self.chroma_operator.get_collection(self.current_collection_py_name)
        self._vector_store = ChromaVectorStore(chroma_collection=chroma_collection_object)
        print(f"创建 LlamaIndex ChromaVectorStore 成功，连接到 collection: {self.current_collection_py_name}")
        self._storage_context = StorageContext.from_defaults(
            vector_store=cast(StorageContext.from_defaults.__annotations__['vector_store'], self._vector_store)
        )
        print("创建 LlamaIndex StorageContext 成功。")

        self._index = None
        self._query_engine = None


    def get_query_engine(self):

        if self._query_engine is not None:
            print(f"返回缓存的 QueryEngine (科室: {self.current_collection_py_name})")
            return self._query_engine

        if self._storage_context is None or self._vector_store is None:
            print("错误: StorageContext 或 VectorStore 未初始化。请先调用 switch_collection() 方法。")
            return None

        print(f"创建新的 LlamaIndex VectorStoreIndex (科室: {self.current_collection_py_name})")
        try:
            self._index = VectorStoreIndex.from_vector_store(
                vector_store=cast(VectorStoreIndex.from_vector_store.__annotations__['vector_store'],
                                  self._vector_store),
            )
            print(f"创建 VectorStoreIndex 成功 (科室: {self.current_collection_py_name})")

            # 创建 QueryEngine
            self._query_engine = self._index.as_query_engine()
            print(f"创建 QueryEngine 成功 (科室: {self.current_collection_py_name})")

            return self._query_engine

        except Exception as e:
            print(f"创建 VectorStoreIndex 或 QueryEngine 时发生错误: {e}")
            self._index = None
            self._query_engine = None
            return None


if __name__ == "__main__":


    print("\n初始化 QueryEngineManager...")
    try:
        qem = QueryEngineManager(chroma_operator)
        print("QueryEngineManager 初始化成功。")

        department_to_query_zh = "呼吸内科"
        qem.switch_collection(department_to_query_zh)


        qe = qem.get_query_engine()

        if qe:

            query_text = "我感觉我呼吸有点乏力是怎么回事"
            print(f"\n对 '{department_to_query_zh}' 进行查询: '{query_text}'")
            response = qe.query(query_text)


            print("\n--- 最终回答 ---")
            print(response)
            print("----------------\n")


            print("--- 检索到的源文档 (Source Nodes) ---")
            if response.source_nodes:
                for i, source_node in enumerate(response.source_nodes):
                    print(f"--- 源文档 {i+1} ---")
                    print(f"相似度得分 (Score): {source_node.score:.4f}")
                    print("元数据 (Metadata):")

                    print(source_node.metadata)
                    print("文档文本 (Text):")

                    print(source_node.get_content()[:500] + "...")

                    print("-" * 30) # 分隔符
            else:
                print("没有检索到源文档。")
            print("----------------------------------\n")



        else:
            print("无法获取 QueryEngine，请检查 switch_collection 是否成功。")

    except Exception as e:
        print(f"\nQueryEngineManager 使用过程中发生错误: {e}")

    print("\n脚本执行完毕。")