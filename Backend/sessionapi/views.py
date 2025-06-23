from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseNotAllowed, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
import uuid
from datetime import datetime
import time
# 导入 MongoDB 操作对象
from Models.Data.db_init import mongo_operator
from bson import ObjectId # ObjectId 用于处理 MongoDB 的 _id (如果需要)
from pymongo.errors import PyMongoError

sessions_db = {} 
user_sessions_db = {}

def get_timestamp_ms():
    return int(time.time() * 1000)




@csrf_exempt 
def create_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            title = data.get('title', '新会话') 

            if not userid:
                return HttpResponseBadRequest(json.dumps({'error': 'userid is required'}), content_type='application/json')

            session_id = str(uuid.uuid4()) # 生成唯一的 session ID
            timestamp = get_timestamp_ms() 

            new_session_doc = {
                'sessionid': session_id,
                'userid': userid,
                'title': title,
                'timestamp': timestamp,
                'messages': [] # 初始历史为空
            }

            result = mongo_operator.sessions.insert_one(new_session_doc)
            if not result.inserted_id:
                 raise PyMongoError("Failed to insert session into MongoDB")

            print(f"Session created: {session_id} for user: {userid}")
            return JsonResponse({'sessionid': session_id})

        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON'}), content_type='application/json')
        except PyMongoError as pe:
            print(f"MongoDB Error creating session: {pe}")
            return JsonResponse({'error': 'Database error during session creation'}, status=500)
        except Exception as e:
            print(f"Error creating session: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from bson import json_util  # 用于处理MongoDB的特殊数据类型

def get_all_sessions(request):
    if request.method == 'GET':
        userid = request.GET.get('userid')
        if not userid:
            return HttpResponseBadRequest(
                json.dumps({'error': 'userid query parameter is required'}),
                content_type='application/json'
            )
        
        try:
            # 获取用户会话游标
            user_sessions_cursor = mongo_operator.sessions.find({'userid': userid})
            
            # 转换并处理数据
            all_sessions_data = []
            for doc in user_sessions_cursor:  # 直接遍历游标，无需转换为list
                print(doc)
                session_data = {
                    "session_id": str(doc.get("sessionid", "")), 
                    "title": doc.get("title", ""),
                    "timestamp": doc.get("timestamp", ""),
                    "messages": doc.get("messages", [])[1:] if doc.get("messages") else [],
                    "knowledge": {
                        "knowledge_from_chroma": doc.get("knowledge", {}).get("knowledge_from_chroma", []),
                        "knowledge_from_graph": doc.get("knowledge", {}).get("knowledge_from_graph", [])
                    }
                }
                all_sessions_data.append(session_data)
            
            # 使用json_util处理可能存在的MongoDB特殊数据类型
            return JsonResponse(all_sessions_data, safe=False, json_dumps_params={'default': json_util.default})
            
        except Exception as e:
            return JsonResponse(
                {'error': f'An error occurred: {str(e)}'},
                status=500
            )

    return HttpResponseNotAllowed(['GET'])

def get_session_details(request, session_id):
    """
    处理 GET /agentapi/session/<session_id> 请求
    获取单个会话的详细信息 (使用 MongoDB)
    """
    if request.method == 'GET':
        try:
            # --- 数据库操作 (MongoDB) ---
            session_doc = mongo_operator.sessions.find_one({'sessionid': session_id})
            # --- 数据库操作 (结束) ---

            if session_doc:
                return JsonResponse(mongo_doc_to_dict(session_doc))
            else:
                return HttpResponseNotFound(json.dumps({'error': 'Session not found'}), content_type='application/json')
        except PyMongoError as pe:
             print(f"MongoDB Error getting session details for {session_id}: {pe}")
             return JsonResponse({'error': 'Database error retrieving session details'}, status=500)
        except Exception as e:
            print(f"Error getting session details {session_id}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return HttpResponseNotAllowed(['GET'])

@csrf_exempt
def delete_session(request):
    if request.method == 'POST':
        try:
            try:
                data = json.loads(request.body)
                userid = data.get('userid')
                session_id = data.get('sessionid')
                if not userid:
                    return HttpResponseBadRequest(json.dumps({'error': 'userid is required in request body'}), content_type='application/json')
            except json.JSONDecodeError:
                 return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON in request body'}), content_type='application/json')

            session_to_delete = mongo_operator.sessions.find_one({'sessionid': session_id})

            if not session_to_delete:
                return HttpResponseNotFound(json.dumps({'error': 'Session not found'}), content_type='application/json')

            if session_to_delete.get('userid') != userid:
                return HttpResponseForbidden(json.dumps({'error': 'User not authorized to delete this session'}), content_type='application/json')

            delete_result = mongo_operator.sessions.delete_one({'sessionid': session_id, 'userid': userid})
            # --- 数据库操作 (结束) ---

            if delete_result.deleted_count > 0:
                print(f"Session deleted: {session_id} by user {userid}")
                return JsonResponse({'message': 'Session deleted successfully'})
            else:
                # 理论上，如果 find_one 成功且 userid 匹配，这里应该能删除
                # 但以防万一，添加此错误处理
                print(f"Session {session_id} found but delete operation failed (count=0) for user {userid}.")
                return HttpResponseNotFound(json.dumps({'error': 'Session found but could not be deleted'}), content_type='application/json')

        except PyMongoError as pe:
            print(f"MongoDB Error deleting session {session_id}: {pe}")
            return JsonResponse({'error': 'Database error during session deletion'}, status=500)
        except Exception as e:
            print(f"Error deleting session {session_id}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def add_message_to_session(request, session_id):
    """
    处理 POST /agentapi/session/<session_id>/message 请求
    向指定会话添加一条消息 (使用 MongoDB)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid') # 用于权限验证
            message_data = data.get('message')

            if not userid or not message_data or 'role' not in message_data or 'content' not in message_data:
                return HttpResponseBadRequest(json.dumps({'error': 'userid and message (with role and content) are required'}), content_type='application/json')

            # 准备要添加的消息
            new_message = {
                'role': message_data['role'],
                'content': message_data['content'],
                'timestamp': message_data.get('timestamp', get_timestamp_ms())
            }

            # --- 数据库操作 (MongoDB) ---
            # 使用 $push 将消息添加到 history 数组
            # 同时验证 sessionid 和 userid 匹配，确保用户只能修改自己的会话
            update_result = mongo_operator.sessions.update_one(
                {'sessionid': session_id, 'userid': userid},
                {'$push': {'history': new_message}}
            )
            # --- 数据库操作 (结束) ---

            if update_result.matched_count == 0:
                # 检查会话是否存在但用户不匹配
                session_exists = mongo_operator.sessions.count_documents({'sessionid': session_id}) > 0
                if session_exists:
                     return HttpResponseForbidden(json.dumps({'error': 'User not authorized for this session'}), content_type='application/json')
                else:
                     return HttpResponseNotFound(json.dumps({'error': 'Session not found'}), content_type='application/json')
            elif update_result.modified_count == 0:
                # 匹配但未修改，可能出现问题，但理论上 $push 应该总能修改
                print(f"Warning: Message add matched session {session_id} but did not modify document.")
                # 仍然返回成功，因为数据可能已被添加

            print(f"Message added to session {session_id} by user {userid}")
            return JsonResponse({'message': 'Message added successfully'})

        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON'}), content_type='application/json')
        except PyMongoError as pe:
            print(f"MongoDB Error adding message to session {session_id}: {pe}")
            return JsonResponse({'error': 'Database error adding message'}, status=500)
        except Exception as e:
            print(f"Error adding message to session {session_id}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def update_session_title(request, session_id):
    """
    处理 PUT /agentapi/session/<session_id>/title 请求
    更新会话标题 (使用 MongoDB)
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            userid = data.get('userid') # 用于权限验证
            new_title = data.get('title')

            # Title 可以是空字符串，但不能是 None
            if not userid or new_title is None:
                return HttpResponseBadRequest(json.dumps({'error': 'userid and title are required'}), content_type='application/json')

            # --- 数据库操作 (MongoDB) ---
            # 使用 $set 更新 session_title
            # 同时验证 sessionid 和 userid 匹配
            update_result = mongo_operator.sessions.update_one(
                {'sessionid': session_id, 'userid': userid},
                {'$set': {'session_title': new_title}}
            )
            # --- 数据库操作 (结束) ---

            if update_result.matched_count == 0:
                 # 检查会话是否存在但用户不匹配
                session_exists = mongo_operator.sessions.count_documents({'sessionid': session_id}) > 0
                if session_exists:
                     return HttpResponseForbidden(json.dumps({'error': 'User not authorized for this session'}), content_type='application/json')
                else:
                     return HttpResponseNotFound(json.dumps({'error': 'Session not found'}), content_type='application/json')
            # modified_count 可能为 0 （如果新旧标题相同），这是正常情况

            print(f"Session title updated for {session_id} by user {userid}")
            return JsonResponse({'message': 'Title updated successfully'})

        except json.JSONDecodeError:
            return HttpResponseBadRequest(json.dumps({'error': 'Invalid JSON'}), content_type='application/json')
        except PyMongoError as pe:
            print(f"MongoDB Error updating title for session {session_id}: {pe}")
            return JsonResponse({'error': 'Database error updating title'}, status=500)
        except Exception as e:
            print(f"Error updating title for session {session_id}: {e}")
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return HttpResponseNotAllowed(['PUT'])

