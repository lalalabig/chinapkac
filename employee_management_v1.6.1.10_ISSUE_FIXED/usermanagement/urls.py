"""
用户管理URL配置
"""
from django.urls import path
from . import views

app_name = 'usermanagement'

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('create/', views.user_create, name='user_create'),
    path('<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('<int:user_id>/detail/', views.user_detail, name='user_detail'),
]
