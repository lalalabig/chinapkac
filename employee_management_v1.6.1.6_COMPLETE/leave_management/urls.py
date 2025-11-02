"""
leave_management 应用 URL 配置
"""
from django.urls import path
from . import views

app_name = 'leave_management'

urlpatterns = [
    # 个人申请相关
    path('apply/', views.apply_leave, name='apply_leave'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('my-applications/<int:application_id>/', views.application_detail, name='application_detail'),
    path('my-applications/<int:application_id>/cancel/', views.cancel_application, name='cancel_application'),
    
    # 审批相关
    path('pending-approvals/', views.pending_approvals, name='pending_approvals'),
    path('pending-approvals/<int:application_id>/', views.approve_application, name='approve_application'),
    
    # 仪表板和导出
    path('dashboard/', views.leave_management_dashboard, name='dashboard'),
    path('export/', views.export_leave_records, name='export'),
]
