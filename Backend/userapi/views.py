from django.shortcuts import render
from django.http import JsonResponse
import json
from Models import mongo_operator
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register(request):
    """
    用户注册接口
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            password = data.get('password')
            
            if not userid or not password:
                return JsonResponse({'status': 'error', 'msg': '用户名和密码不能为空'})
            
            # 注册用户
            result = mongo_operator.insertUser(userid, password)
            if result:
                return JsonResponse({'status': 'success', 'msg': '注册成功'})
            else:
                return JsonResponse({'status': 'error', 'msg': '注册失败，可能用户名已存在'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'注册失败: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'msg': '仅支持POST请求'})


@csrf_exempt
def login(request):
    """
    用户登录接口
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            password = data.get('password')
            
            if not userid or not password:
                return JsonResponse({'status': 'error', 'msg': '用户名和密码不能为空'})
            
            # 验证用户
            user = mongo_operator.verifyUser(userid, password)
            if user:
                # 登录成功
                return JsonResponse({'status': 'success', 'msg': '登录成功', 'userid': userid})
            else:
                # 登录失败
                return JsonResponse({'status': 'error', 'msg': '用户名或密码错误'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'登录失败: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'msg': '仅支持POST请求'})


@csrf_exempt
def getSelfInfo(request):
    """
    获取用户信息接口
    """
    if request.method == 'GET':
        try:
            userid = request.GET.get('userid')
            user_info = mongo_operator.getSelfInfo(userid)
            return JsonResponse({'status': 'success', 'info': user_info})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'获取用户信息失败: {str(e)}'})


@csrf_exempt
def updateSelfInfo(request):
    """
    更新用户信息接口
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            update_data = data.get('update_data')
            mongo_operator.updateSelfInfo(userid, update_data)
            return JsonResponse({'status': 'success', 'msg': '更新用户信息成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'更新用户信息失败: {str(e)}'})


# 以下是管理员API

@csrf_exempt
def get_all_users(request):
    """
    获取所有用户列表，仅供管理员使用
    """
    if request.method == 'GET':
        try:
            # 从MongoDB获取所有用户
            users = list(mongo_operator.users.find({}, {'_id': 0}))
            return JsonResponse({'status': 'success', 'users': users})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'获取用户列表失败: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'msg': '仅支持GET请求'})

@csrf_exempt
def delete_user(request, userid):
    """
    删除用户接口，仅供管理员使用
    """
    if request.method == 'DELETE':
        try:
            # 删除用户
            result = mongo_operator.deleteUser(userid)
            if result.deleted_count > 0:
                return JsonResponse({'status': 'success', 'msg': f'成功删除用户 {userid}'})
            else:
                return JsonResponse({'status': 'error', 'msg': f'用户 {userid} 不存在'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'删除用户失败: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'msg': '仅支持DELETE请求'})

@csrf_exempt
def update_user(request, userid):
    """
    更新用户信息接口，仅供管理员使用
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            password = data.get('password')
            
            if not password:
                return JsonResponse({'status': 'error', 'msg': '密码不能为空'})
            
            # 更新用户密码
            result = mongo_operator.users.update_one(
                {"userid": userid}, 
                {"$set": {"userpw": password}}
            )
            
            if result.modified_count > 0:
                return JsonResponse({'status': 'success', 'msg': f'成功更新用户 {userid} 的信息'})
            else:
                return JsonResponse({'status': 'error', 'msg': f'用户 {userid} 不存在或信息未变更'})
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'更新用户失败: {str(e)}'})
    
    return JsonResponse({'status': 'error', 'msg': '仅支持PUT请求'})

@csrf_exempt
def getHealthInfo(request):
    """
    获取用户健康信息接口
    """
    if request.method == 'GET':     
        try:
            userid = request.GET.get('userid')
            health_info = mongo_operator.getHealthInfo(userid)
            return JsonResponse({'status': 'success', 'info': health_info})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'获取用户健康信息失败: {str(e)}'})


@csrf_exempt
def updateHealthInfo(request):
    """
    更新用户健康信息接口
    """ 
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            update_data = data.get('update_data')
            mongo_operator.updateHealthInfo(userid, update_data)    
            return JsonResponse({'status': 'success', 'msg': '更新用户健康信息成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'更新用户健康信息失败: {str(e)}'})

    return JsonResponse({'status': 'error', 'msg': '仅支持POST请求'})


@csrf_exempt
def getMemory(request):
    """
    获取用户记忆接口
    """
    if request.method == 'GET':
        try:      
            userid = request.GET.get('userid')
            memory = mongo_operator.getMemory(userid)
            return JsonResponse({'status': 'success', 'memory': memory})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'获取用户记忆失败: {str(e)}'})

    return JsonResponse({'status': 'error', 'msg': '仅支持GET请求'})    


@csrf_exempt
def updateMemory(request):
    """
    更新用户记忆接口
    """
    if request.method == 'POST':            
        try:
            data = json.loads(request.body)
            userid = data.get('userid')
            update_data = data.get('update_data')
            mongo_operator.updateMemory(userid, update_data)
            return JsonResponse({'status': 'success', 'msg': '更新用户记忆成功'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': f'更新用户记忆失败: {str(e)}'})

    return JsonResponse({'status': 'error', 'msg': '仅支持POST请求'})







