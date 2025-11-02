"""
dashboard 应用 URL 配置
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # 主要页面
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    
    # 管理功能（需要相应权限）
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/edit/<int:user_id>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('team/', views.team_management, name='team_management'),  # 员工列表
    path('settings/', views.system_settings, name='system_settings'),
    
    # 错误页面
    path('access-denied/', views.access_denied, name='access_denied'),
]
