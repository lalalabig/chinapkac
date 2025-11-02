"""
紧急报警系统视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q, Count
from django.core.paginator import Paginator
import json
import logging

from .models import EmergencyAlert, NotificationLog
from accounts.models import User
from accounts.permissions import role_required

logger = logging.getLogger(__name__)


@login_required
def create_alert(request):
    """
    创建紧急报警
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # 验证必需字段
            required_fields = ['latitude', 'longitude', 'alert_message']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'message': f'缺少必需字段: {field}'
                    })
            
            # 获取地址信息
            location_address = data.get('location_address', '未知位置')
            alert_type = data.get('alert_type', 'emergency')
            
            # 创建报警
            alert = EmergencyAlert.objects.create(
                sender=request.user,
                alert_type=alert_type,
                latitude=data['latitude'],
                longitude=data['longitude'],
                location_address=location_address,
                alert_message=data['alert_message']
            )
            
            # 发送通知
            alert.send_notification()
            
            return JsonResponse({
                'success': True,
                'alert_id': str(alert.id),
                'message': '报警已成功发送！'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            })
        except Exception as e:
            logger.error(f"创建报警失败: {e}")
            return JsonResponse({
                'success': False,
                'message': '创建报警失败，请重试'
            })
    
    # GET请求显示报警页面
    return render(request, 'emergency/create_alert.html')


@login_required
def alert_list(request):
    """
    报警列表
    """
    # 根据角色获取可查看的报警
    if request.user.role == User.Role.SUPERUSER:
        alerts = EmergencyAlert.objects.all()
    elif request.user.role == User.Role.TASK_AREA_MANAGER:
        # 任务区负责人只能看本任务区员工的报警
        alerts = EmergencyAlert.objects.filter(
            sender__task_area=request.user.task_area
        )
    elif request.user.role == User.Role.HEAD_MANAGER:
        # 总部负责人可以看管辖任务区的报警
        managed_areas = request.user.managed_task_areas.all()
        alerts = EmergencyAlert.objects.filter(
            sender__task_area__in=managed_areas
        )
    else:
        # 普通员工只能看自己的报警
        alerts = EmergencyAlert.objects.filter(sender=request.user)
    
    # 搜索和筛选
    search = request.GET.get('search')
    status = request.GET.get('status')
    alert_type = request.GET.get('alert_type')
    
    if search:
        alerts = alerts.filter(
            Q(sender__first_name__icontains=search) |
            Q(sender__last_name__icontains=search) |
            Q(location_address__icontains=search) |
            Q(alert_message__icontains=search)
        )
    
    if status:
        alerts = alerts.filter(status=status)
    
    if alert_type:
        alerts = alerts.filter(alert_type=alert_type)
    
    alerts = alerts.order_by('-alert_time')
    
    # 分页
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计数据
    stats = {
        'active': alerts.filter(status=EmergencyAlert.AlertStatus.ACTIVE).count(),
        'handled': alerts.filter(status=EmergencyAlert.AlertStatus.HANDLED).count(),
        'resolved': alerts.filter(status=EmergencyAlert.AlertStatus.RESOLVED).count(),
        'total': alerts.count(),
    }
    
    context = {
        'alerts': page_obj,
        'stats': stats,
        'status_choices': EmergencyAlert.AlertStatus.choices,
        'alert_type_choices': EmergencyAlert.AlertType.choices,
    }
    return render(request, 'emergency/alert_list.html', context)


@login_required
def alert_detail(request, alert_id):
    """
    报警详情
    """
    alert = get_object_or_404(EmergencyAlert, id=alert_id)
    
    # 权限检查
    if not can_view_alert(request.user, alert):
        messages.error(request, '您没有权限查看此报警')
        return redirect('emergency:alert_list')
    
    # 获取通知日志
    notification_logs = alert.notification_logs.all().order_by('-created_at')
    
    context = {
        'alert': alert,
        'notification_logs': notification_logs,
        'can_handle': can_handle_alert(request.user, alert),
        'can_update': can_update_alert(request.user, alert),
    }
    return render(request, 'emergency/alert_detail.html', context)


@login_required
@role_required([User.Role.TASK_AREA_MANAGER, User.Role.HEAD_MANAGER, User.Role.SUPERUSER])
def handle_alert(request, alert_id):
    """
    处理报警
    """
    alert = get_object_or_404(EmergencyAlert, id=alert_id)
    
    # 权限检查
    if not can_handle_alert(request.user, alert):
        messages.error(request, '您没有权限处理此报警')
        return redirect('emergency:alert_list')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            action = data.get('action')  # 'handle' 或 'resolve'
            notes = data.get('handling_notes', '')
            
            if action == 'handle':
                alert.mark_as_handled(request.user, notes)
                message = '报警已标记为已处理'
            elif action == 'resolve':
                alert.mark_as_resolved(request.user, notes)
                message = '报警已标记为已解决'
            else:
                return JsonResponse({
                    'success': False,
                    'message': '无效的操作'
                })
            
            return JsonResponse({
                'success': True,
                'message': message
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': '无效的JSON数据'
            })
        except Exception as e:
            logger.error(f"处理报警失败: {e}")
            return JsonResponse({
                'success': False,
                'message': '处理失败，请重试'
            })
    
    context = {
        'alert': alert,
    }
    return render(request, 'emergency/handle_alert.html', context)


@login_required
def get_new_alerts(request):
    """
    获取新的报警（用于实时更新）
    """
    try:
        # 获取指定时间后的新报警
        last_check = request.GET.get('last_check')
        if last_check:
            last_check_time = timezone.datetime.fromisoformat(last_check)
        else:
            last_check_time = timezone.now() - timezone.timedelta(minutes=5)
        
        # 根据权限获取报警
        if request.user.role == User.Role.SUPERUSER:
            alerts = EmergencyAlert.objects.filter(alert_time__gt=last_check_time)
        elif request.user.role == User.Role.TASK_AREA_MANAGER:
            alerts = EmergencyAlert.objects.filter(
                sender__task_area=request.user.task_area,
                alert_time__gt=last_check_time
            )
        elif request.user.role == User.Role.HEAD_MANAGER:
            managed_areas = request.user.managed_task_areas.all()
            alerts = EmergencyAlert.objects.filter(
                sender__task_area__in=managed_areas,
                alert_time__gt=last_check_time
            )
        else:
            alerts = EmergencyAlert.objects.filter(
                sender=request.user,
                alert_time__gt=last_check_time
            )
        
        alerts_data = []
        for alert in alerts:
            alerts_data.append({
                'id': str(alert.id),
                'sender_name': alert.sender.get_full_name(),
                'alert_type': alert.get_alert_type_display(),
                'location_address': alert.location_address,
                'alert_message': alert.alert_message[:100] + '...' if len(alert.alert_message) > 100 else alert.alert_message,
                'alert_time': alert.alert_time.isoformat(),
                'latitude': float(alert.latitude) if alert.latitude else None,
                'longitude': float(alert.longitude) if alert.longitude else None,
            })
        
        return JsonResponse({
            'success': True,
            'alerts': alerts_data,
            'count': len(alerts_data)
        })
        
    except Exception as e:
        logger.error(f"获取新报警失败: {e}")
        return JsonResponse({
            'success': False,
            'message': '获取数据失败'
        })


@login_required
def emergency_dashboard(request):
    """
    紧急报警仪表板
    """
    # 获取统计数据
    if request.user.role == User.Role.SUPERUSER:
        base_query = EmergencyAlert.objects.all()
    elif request.user.role == User.Role.TASK_AREA_MANAGER:
        base_query = EmergencyAlert.objects.filter(
            sender__task_area=request.user.task_area
        )
    elif request.user.role == User.Role.HEAD_MANAGER:
        managed_areas = request.user.managed_task_areas.all()
        base_query = EmergencyAlert.objects.filter(
            sender__task_area__in=managed_areas
        )
    else:
        base_query = EmergencyAlert.objects.filter(sender=request.user)
    
    # 时间范围筛选
    time_range = request.GET.get('time_range', 'today')
    now = timezone.now()
    
    if time_range == 'today':
        start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif time_range == 'week':
        start_time = now - timezone.timedelta(days=7)
    elif time_range == 'month':
        start_time = now - timezone.timedelta(days=30)
    else:
        start_time = now - timezone.timedelta(days=7)  # 默认一周
    
    base_query = base_query.filter(alert_time__gte=start_time)
    
    # 统计数据
    stats = {
        'total': base_query.count(),
        'active': base_query.filter(status=EmergencyAlert.AlertStatus.ACTIVE).count(),
        'handled': base_query.filter(status=EmergencyAlert.AlertStatus.HANDLED).count(),
        'resolved': base_query.filter(status=EmergencyAlert.AlertStatus.RESOLVED).count(),
        'urgent': base_query.filter(
            alert_time__gte=now - timezone.timedelta(minutes=5)
        ).count(),
    }
    
    # 按类型统计
    type_stats = base_query.values('alert_type').annotate(
        count=Count('alert_type')
    ).order_by('-count')
    
    # 最近报警
    recent_alerts = base_query.order_by('-alert_time')[:10]
    
    context = {
        'stats': stats,
        'type_stats': list(type_stats),
        'recent_alerts': recent_alerts,
        'time_range': time_range,
        'current_time': now.isoformat(),
    }
    return render(request, 'emergency/dashboard.html', context)


# 辅助函数

def can_view_alert(user, alert):
    """检查用户是否可以查看报警"""
    if user == alert.sender:
        return True
    if user.role == User.Role.SUPERUSER:
        return True
    if user.role == User.Role.TASK_AREA_MANAGER:
        return alert.sender.task_area == user.task_area
    if user.role == User.Role.HEAD_MANAGER:
        return alert.sender.task_area in user.managed_task_areas.all()
    return False


def can_handle_alert(user, alert):
    """检查用户是否可以处理报警"""
    if user.role == User.Role.SUPERUSER:
        return True
    if user.role == User.Role.TASK_AREA_MANAGER:
        return alert.sender.task_area == user.task_area
    if user.role == User.Role.HEAD_MANAGER:
        return alert.sender.task_area in user.managed_task_areas.all()
    return False


def can_update_alert(user, alert):
    """检查用户是否可以更新报警"""
    return can_view_alert(user, alert)
