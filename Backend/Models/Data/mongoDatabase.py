from pymongo import MongoClient, ASCENDING
import time

class mgOperator:
    def __init__(self):
        self.admin = "admin"
        self.password = "password"
        self.client = MongoClient(
            host="localhost",
            port=27017,
            username=self.admin,
            password=self.password,
            authSource="admin",
        )
        self.db = self.client["mcdb"]
        self.users = self.db["users"]
        self.sessions = self.db["sessions"]
        self.memories = self.db["memories"]
        self.preparing()

    def preparing(self):
        self.users.create_index([("userid", ASCENDING)], unique=True)

    def insertUser(self, userid, userpw):
        record = {"userid": userid, "userpw": userpw, "self_info": {},"health_info": []}
        memory = {"userid": userid, "memory": []}
        try:
            self.memories.insert_one(memory)
            return self.users.insert_one(record)
        except Exception as e:
            print(f"新建用户失败: {e}")
            return None

    def deleteUser(self, userid):
        return self.users.delete_one({"userid": userid})
        
    def verifyUser(self, userid, userpw):
        """
        验证用户登录信息
        :param userid: 用户ID
        :param userpw: 用户密码
        :return: 如果验证成功返回用户文档，否则返回None
        """
        try:
            user = self.users.find_one({"userid": userid})
            if user and user.get("userpw") == userpw:
                return True
            return False
        except Exception as e:
            print(f"验证用户失败: {e}")
            return False
        

    def insertSession(self, sessionid, userid, messages, title):
        record = {"sessionid": sessionid, "userid": userid, "timestamp": int(time.time() * 1000), "messages": messages,"knowledge":{},"title":title}
        try:
            return self.sessions.insert_one(record)
        except Exception as e:
            print(f"新建会话失败: {e}")
            return None
        
    def updateSession(self, sessionid, userid, messages):
        current_session = self.sessions.find_one({"sessionid": sessionid, "userid": userid})
        if current_session and "messages" in current_session and len(current_session["messages"]) > 0:
            first_message = current_session["messages"][0]
            updated_messages = [first_message] + messages
            return self.sessions.update_one(
                {"sessionid": sessionid, "userid": userid},
                {"$set": {"messages": updated_messages}}
            )
        else:
            return self.sessions.update_one(
                {"sessionid": sessionid, "userid": userid},
                {"$set": {"messages": messages}}
            )
    
    def insertAssitantMessage(self, sessionid, userid, message):
        return self.sessions.update_one({"sessionid": sessionid, "userid": userid}, {"$push": {"messages": message}})
    
    def prependSystemMessage(self, sessionid, userid, message):
        return self.sessions.update_one(
            {"sessionid": sessionid, "userid": userid},
            {"$push": {"messages": {"$each": [message], "$position": 0}}}
        )
    def insertUserMessage(self, sessionid, userid, message):
        return self.sessions.update_one({"sessionid": sessionid, "userid": userid}, {"$push": {"messages": message}})
    def getMessages(self, sessionid, userid):
        session = self.sessions.find_one({"sessionid": sessionid, "userid": userid}, {"messages": 1, "_id": 0})
        if session and "messages" in session:
            messages_without_timestamp = []
            for msg in session["messages"]:
                filtered_msg = {k: v for k, v in msg.items() if k != "timestamp"}
                messages_without_timestamp.append(filtered_msg)
            return messages_without_timestamp
        return []
    def getMessagesExceptSystem(self, sessionid, userid):
        session = self.sessions.find_one(
            {"sessionid": sessionid, "userid": userid},
            {"messages": 1, "_id": 0}
        )
        return session.get("messages", [])[1:] if session else []
    
    def getSessionData(self, sessionid, userid):
        result = self.sessions.find_one({"sessionid": sessionid, "userid": userid})
        print(result)
        return result
    
    def updateSessionKnowledge(self, sessionid, userid, knowledge):
        return self.sessions.update_one({"sessionid": sessionid, "userid": userid}, {"$set": {"knowledge": knowledge}})

    def deleteSession(self, sessionid, userid):
        return self.sessions.delete_one({"sessionid": sessionid, "userid": userid})
    
    def findSession(self, sessionid, userid):
        try:
            return self.sessions.find_one({"sessionid": sessionid, "userid": userid})
        except Exception as e:
            print(f"查找会话失败: {e}")
            return None
    
    def getMemory(self, userid):
        memory = self.memories.find_one({"userid": userid})
        if memory:
            return memory.get("memory")
        self.memories.insert_one({"userid": userid, "memory": []})
        return []
    
    def updateMemory(self, userid, update_data):
        return self.memories.update_one({"userid": userid}, {"$set": {"memory": update_data}})

        
    def updateMemories(self, userid, memories):
        return self.memories.update_one({"userid": userid}, {"$set": {"memory": memories}})
    
    def findMemory(self, userid):
        try:
            return self.memories.find_one({"userid": userid})
        except Exception as e:
            print(f"查找记忆失败: {e}")
            return None
    
    def getSelfInfo(self, userid):
        user_document = self.users.find_one({"userid": userid})
        if user_document:
            return user_document.get("self_info")
        return None
    
    def getHealthInfo(self, userid):
        user_document = self.users.find_one({"userid": userid})
        if user_document:
            return user_document.get("health_info")
        return None
    
    def updateHealthInfo(self, userid, update_data):
        return self.users.update_one({"userid": userid}, {"$set": {"health_info": update_data}})
    

    def updateSelfInfo(self, userid, update_data):
        return self.users.update_one({"userid": userid}, {"$set": {"self_info": update_data}})


    def getAllInfo(self, userid):
        self_info = self.getSelfInfo(userid)
        health_info = self.getHealthInfo(userid)
        memories = self.getMemory(userid)
        print(memories)
        return {"self_info": self_info, "health_info": health_info, "memories": memories}

if __name__ == "__main__":
    mgOperator = mgOperator()
    print(mgOperator.insertUser("test", "test"))
    print(mgOperator.deleteUser("test"))
