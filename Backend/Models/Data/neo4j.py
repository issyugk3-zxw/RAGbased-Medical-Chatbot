import os
import re
import py2neo
from tqdm import tqdm
import argparse

from Models.AnalysisModels.Bert_ZH_Model import Bert_ZH_Model
import json

class neo4jOperator:
    def __init__(self):
        self.website = "bolt://localhost:7687"
        self.user = "neo4j"
        self.password = "neo4j123456"
        self.dbname = "neo4j"
        self.client = py2neo.Graph(
            self.website, auth=(self.user, self.password), name=self.dbname
        )

    def find_diseases_by_symptoms(self, symptom_list):
        query = """
            MATCH (d:疾病)-[:疾病的症状]->(s:症状)
            WHERE s.名称 IN $symptoms
            WITH d, COUNT(s) AS 匹配症状数
            WHERE 匹配症状数 = $symptom_count
            RETURN d.名称 AS 疾病名称, 匹配症状数
            ORDER BY 匹配症状数 DESC
            """

        result = self.client.run(
            query, symptoms=symptom_list, symptom_count=len(symptom_list)
        )

        return [record["疾病名称"] for record in result]

    def execute_queries(self, queries):
        formatted_results = []

        for i, query in enumerate(queries):
            try:
                result = self.client.run(query).data()

                formatted_results.append({
                    "query_number": i + 1,
                    "cypher_statement": query,
                    "results": result
                })
            except Exception as e:
                formatted_results.append({
                    "query_number": i + 1,
                    "cypher_statement": query,
                    "error": str(e)
                })

        return json.dumps(formatted_results, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    neo4jop = neo4jOperator()
    BertClassifier = Bert_ZH_Model()
    while True:
        sen = input("请输入:")
        result = BertClassifier.getNerResult(sen)
        print(result)
