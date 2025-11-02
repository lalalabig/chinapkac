from django.urls import path
from . import views

app_name = 'emergency'

urlpatterns = [
    # 报警相关
    path('create/', views.create_alert, name='create_alert'),
    path('list/', views.alert_list, name='alert_list'),
    path('<uuid:alert_id>/', views.alert_detail, name='alert_detail'),
    path('<uuid:alert_id>/handle/', views.handle_alert, name='handle_alert'),
    path('dashboard/', views.emergency_dashboard, name='dashboard'),
    
    # API接口
    path('api/new-alerts/', views.get_new_alerts, name='get_new_alerts'),
]
