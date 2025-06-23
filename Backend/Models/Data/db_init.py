from .mongoDatabase import mgOperator
from .chromaDatabase import ChromaOperator
from .neo4j import neo4jOperator

# 创建全局MongoDB操作对象，以便在Django应用中使用
mongo_operator = mgOperator() 
chroma_operator = ChromaOperator()
neo4j_operator = neo4jOperator()