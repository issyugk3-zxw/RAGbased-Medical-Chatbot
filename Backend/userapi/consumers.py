import json
import time # For timestamping
from channels.generic.websocket import AsyncWebsocketConsumer
from Models.Data.db_init import mongo_operator
from Models import analyzer
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.userid = self.scope["url_route"]["kwargs"]["userid"]
        self.room_group_name = f"chat_{self.userid}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"User {self.userid} connected to WebSocket. Group: {self.room_group_name}")
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": f"已成功连接 WebSocket，用户ID: {self.userid}"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"User {self.userid} disconnected from WebSocket. Code: {close_code}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get("type")
            messages = text_data_json.get("messages")
            session_id = text_data_json.get("sessionid") 
            client_userid = text_data_json.get("userid")
            current_sense = text_data_json.get("current_sense")
            print("current sense",current_sense)
            session_title = text_data_json.get("title")
            print(f"Received message from {self.userid} (group: {self.room_group_name}): {text_data_json}")

            if message_type == "user_message":
                print(f"服务器已收到您的session id: '{session_id}'。正在处理...") 
                session = mongo_operator.findSession(sessionid=session_id,userid=client_userid)
                if session:
                    print(f"已存在session。正在处理...") 
                    mongo_operator.updateSession(sessionid=session_id,userid=client_userid,messages=messages)
                    memories = mongo_operator.getMemory(userid=client_userid)
                else:
                    print(f"不存在session。正在创建...") 
                    mongo_operator.insertSession(sessionid=session_id,userid=client_userid,messages=messages,title=session_title)
                    print(f"session创建成功。正在处理...") 
                    query = messages[-1]["content"]
                    all_information = mongo_operator.getAllInfo(client_userid)
                    print(f"获取所有信息成功。正在处理...") 
                    knowledge = analyzer.obtain_knowledge(query, all_information["self_info"])
                    print(f"获取知识成功。正在处理...") 
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat.message", 
                            "message": {
                                "type": "knowledge_update",
                                "knowledge":knowledge
                            }
                        }
                    )
                    mongo_operator.updateSessionKnowledge(sessionid=session_id,userid=client_userid,knowledge=knowledge)
                    print(f"更新session知识成功。正在处理...") 
                    system_prompt = analyzer.construct_system_prompt(query, knowledge, all_information)
                    print(f"构造系统提示成功。正在处理...") 
                    system_prompt_message = {"role":"system","content":system_prompt,"timestamp":int(time.time() * 1000)}
                    print(f"添加系统提示成功。正在处理...") 
                    mongo_operator.prependSystemMessage(sessionid=session_id,userid=client_userid,message=system_prompt_message)
                    print(f"添加系统提示成功。正在处理...") 
                    memories = mongo_operator.getMemory(userid=client_userid)
                chat_messages = mongo_operator.getMessages(sessionid=session_id,userid=client_userid)
                print(f"获取聊天记录成功。正在处理...") 
                chatbot_reply = analyzer.chat(chat_messages, current_sense, memories)
                print("reply:", chatbot_reply)
                print(f"生成回复成功。正在处理...") 
                voice_file_url = analyzer.get_voice_speak(chatbot_reply)
                chatbot_message = {"role":"assistant","content":chatbot_reply,"timestamp":int(time.time() * 1000)}
                print(f"插入回复成功。正在处理...") 
                mongo_operator.insertAssitantMessage(sessionid=session_id,userid=client_userid,message=chatbot_message)
                print(f"插入回复成功。正在处理...") 

                print(f"发送语音消息成功。正在处理...") 
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.voiceMessage", 
                        "message": {
                            "type": "voice",
                            "voice_file_url":voice_file_url
                        }
                    }
                )
                print(f"发送文本消息成功。正在处理...") 
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat.message", 
                        "message": {
                            "type": "text",
                            "sender": "assistant",
                            "session_id": session_id,
                            "text": chatbot_reply,
                            "timestamp": chatbot_message.get("timestamp")
                        }
                    }
                )
            else:
                print(f"Received unhandled message type: {message_type}")
                await self.send(text_data=json.dumps({
                    "type": "error",
                    "message": f"未知消息类型: {message_type}"
                }))

        except json.JSONDecodeError:
            print(f"Error decoding JSON from {self.userid}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "无效的JSON格式."
            }))
        except Exception as e:
            print(f"Error in receive method for {self.userid}: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": f"处理消息时发生错误: {str(e)}"
            }))

    async def chat_voiceMessage(self, event):
        message_data = event["message"] 
        await self.send(text_data=json.dumps(message_data))
        print(f"Sent voice message to {self.userid} (via group): {message_data}")

    async def chat_message(self, event):
        message_data = event["message"] 
        await self.send(text_data=json.dumps(message_data))
        print(f"Sent message to {self.userid} (via group): {message_data}")