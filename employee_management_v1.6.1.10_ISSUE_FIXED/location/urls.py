"""
位置管理URL配置
"""
from django.urls import path
from . import views

app_name = 'location'

urlpatterns = [
    path('update/', views.update_location, name='update_location'),
    path('map/', views.employee_map, name='employee_map'),
    path('ajax-update/', views.ajax_update_location, name='ajax_update_location'),
]
