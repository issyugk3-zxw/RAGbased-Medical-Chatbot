import json

from Models.AnalysisModels import Bert_zh_Model
from Models.CustomLLM.IntentionAgent import IntentionAgent
from Models.CustomLLM.QueryEnginManager import QueryEnginManager
from Models.Data.db_init import neo4j_operator
from Models.ReportGenerator import ReportGenerator
from Models.CustomLLM.Speaker import SpeakerAgent
import datetime
class Analyzer:
    def __init__(self):
        self.bert_model = Bert_zh_Model
        self.intentionAgent = IntentionAgent()
        self.qem = QueryEnginManager()
        self.report_generator = ReportGenerator()
        self.speaker = SpeakerAgent()


    def analyze_eneties(self, text):
        return self.bert_model.getNerResult(text)

    def analyze_intention(self, text):
        return self.intentionAgent.Intent_Recognition(text)


    def obtain_knowledge(self, query, self_info):
        analyzed_entities_json = self.analyze_eneties(query)
        print("NER Result:",analyzed_entities_json)
        analyzed_intention_json = self.analyze_intention(query)
        analyzed_intention = json.dumps(analyzed_intention_json, indent=2, sort_keys=True, ensure_ascii=False)
        analyzed_entities = json.dumps(analyzed_entities_json, indent=2, sort_keys=True, ensure_ascii=False)
        cypher_queries = self.intentionAgent.text2cypher(query,analyzed_entities, analyzed_intention)
        cypher_results = neo4j_operator.execute_queries(cypher_queries)
        knowledge_from_graph = self.intentionAgent.cypher2kgans(cypher_results,query,analyzed_entities,analyzed_intention,self_info)
        if json.loads(analyzed_intention)["问诊"] == "是":
             department = knowledge_from_graph['核心回应']["所属科室"].strip('[]')
        else:
             department =  knowledge_from_graph['核心回应']["相关科室"].strip('[]')
        knowledge_from_chroma = self.qem.get_query_knowledge(query, department)

        return {"knowledge_from_chroma": knowledge_from_chroma, "knowledge_from_graph": knowledge_from_graph}
    
    def chat(self, messages, current_sense, required_memories):
        if current_sense == {}:
            current_sense == "NETURAL"
        print("trans to intention agent to chat with memories")
        print(messages)
        return self.intentionAgent.chat_with_memories(messages, current_sense, required_memories)
    
    def construct_system_prompt(self, query, knowledge, all_information):
        return self.intentionAgent.construct_system_prompt(query, knowledge, all_information)

    def get_voice_speak(self, text):
        file_url = self.speaker.response(text)
        return file_url
    
    def get_report(self, userid, sessionid):
        report_data = self.intentionAgent.get_report_data(userid, sessionid)
        print("report data generated,", report_data)
        report_data["记录时间"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.report_generator.generate_report(report_data,f"health_report_{userid}_{sessionid}.pdf")
    


if __name__ == "__main__":
    az = Analyzer()
    print(az.analyze_all("我感觉有点胸痛，咳嗽带血丝"))




