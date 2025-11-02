from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 个人报告管理
    path('upload/', views.upload_report, name='upload'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('<int:report_id>/download/', views.download_report, name='download_report'),
    
    # 管理功能
    path('manage/', views.manage_reports, name='manage_reports'),
    path('bulk-download/', views.bulk_download, name='bulk_download'),
    path('bulk-download/<int:package_id>/', views.download_package, name='download_package'),
    
    # 维护功能
    path('cleanup/', views.cleanup_old_reports, name='cleanup_old_reports'),
]
