from django.http import JsonResponse
import re

# 管理员认证中间件
class AdminAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # 定义管理员API路径模式
        self.admin_api_pattern = re.compile(r'^/userapi/admin/')
        # 管理员凭据
        self.admin_credentials = {
            'username': 'admin',
            'password': 'admin123'
        }

    def __call__(self, request):
        # 检查是否访问管理员API
        if self.admin_api_pattern.match(request.path):
            # 获取认证头
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            # 简单的基本认证
            if not auth_header.startswith('Basic '):
                return JsonResponse({'status': 'error', 'msg': '需要管理员权限'}, status=401)
            
            try:
                import base64
                
                # 解码Basic认证信息
                auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                username, password = auth_decoded.split(':')
                
                # 验证管理员凭据
                if username != self.admin_credentials['username'] or password != self.admin_credentials['password']:
                    return JsonResponse({'status': 'error', 'msg': '管理员认证失败'}, status=401)
                    
            except Exception:
                return JsonResponse({'status': 'error', 'msg': '无效的认证头'}, status=401)
        
        response = self.get_response(request)
        return response 