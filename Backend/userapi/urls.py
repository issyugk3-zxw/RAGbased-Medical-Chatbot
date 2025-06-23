from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('getSelfInfo/', views.getSelfInfo, name='getSelfInfo'),
    path('updateSelfInfo/', views.updateSelfInfo, name='updateSelfInfo'),
    path('getHealthInfo/', views.getHealthInfo, name='getHealthInfo'),
    path('updateHealthInfo/', views.updateHealthInfo, name='updateHealthInfo'),
    path('getMemory/', views.getMemory, name='getMemory'),
    path('updateMemory/', views.updateMemory, name='updateMemory'),
    # 管理员API
    path('admin/users/', views.get_all_users, name='get_all_users'),
    path('admin/users/<str:userid>/', views.delete_user, name='delete_user'),
    path('admin/users/<str:userid>/update/', views.update_user, name='update_user'),
] 