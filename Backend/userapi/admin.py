from django.contrib import admin
from django.http import JsonResponse
from Models import mongo_operator
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.db import models

# 创建一个代理模型来表示MongoDB中的用户
class MongoUser:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        return self.data.get(name, '')

# 创建MongoDB用户管理界面
class MongoUserAdmin(admin.ModelAdmin):
    list_display = ('userid', 'view_password', 'actions_column')
    search_fields = ('userid',)
    
    def get_queryset(self, request):
        # 从MongoDB获取所有用户
        self.users_list = list(mongo_operator.users.find())
        # 创建一个User对象的空查询集
        return User.objects.none()
    
    def userid(self, obj):
        return obj.get('userid', '-')
    
    def view_password(self, obj):
        return obj.get('userpw', '-')
    
    def actions_column(self, obj):
        # 为每个用户添加编辑和删除按钮
        userid = obj.get('userid')
        return format_html(
            '<button class="button" onclick="deleteUser(\'{}\')">删除</button>', 
            userid
        )
    
    actions_column.short_description = '操作'
    view_password.short_description = '密码'
    
    class Media:
        js = ('js/mongo_user_admin.js',)

# 创建自定义管理站点
class MongoUserAdminSite(admin.AdminSite):
    site_header = "MongoDB用户管理"
    site_title = "MongoDB用户管理"

# 创建自定义管理站点实例
mongo_admin_site = MongoUserAdminSite(name='mongoadmin')

# 在自定义管理站点注册MongoDB用户管理
# 注意：不要使用 admin.site.register，这会与 Django 默认的 User 模型冲突
# 创建一个代理模型用于管理界面
class MongoUserModel(models.Model):
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户管理'
        # 这是一个代理模型，不会创建数据库表
        managed = False
        app_label = 'userapi'

# 注册到默认管理站点，但使用不同的模型
admin.site.register(MongoUserModel, MongoUserAdmin)
