"""
位置管理视图
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from accounts.models import User
import json


@login_required
def update_location(request):
    """更新用户位置"""
    # 总部负责人和超级管理员不需要更新位置
    if request.user.role in ['head_manager', 'superuser']:
        messages.warning(request, '您没有权限更新位置。')
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        address = request.POST.get('address', '')
        
        if latitude and longitude:
            request.user.latitude = float(latitude)
            request.user.longitude = float(longitude)
            request.user.location_address = address
            request.user.location_updated_at = timezone.now()
            request.user.save()
            
            messages.success(request, '位置更新成功！')
            return redirect('location:update_location')
        else:
            messages.error(request, '位置信息不完整，请重试。')
    
    return render(request, 'location/update_location.html')


@login_required
def employee_map(request):
    """员工位置地图（管理员查看）"""
    # 超级管理员、总部负责人、任务区负责人都可以查看地图
    if not (request.user.is_superuser_role or request.user.is_head_manager or request.user.is_task_area_manager):
        messages.error(request, '您没有权限查看此页面。')
        return redirect('dashboard:dashboard')
    
    # 获取下属员工列表
    if request.user.is_superuser_role:
        # 超级管理员看到所有员工
        employees = User.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        ).exclude(id=request.user.id)
    elif request.user.is_head_manager:
        # 总部负责人看到任务区负责人和员工
        employees = User.objects.filter(
            role__in=[User.Role.TASK_AREA_MANAGER, User.Role.EMPLOYEE],
            latitude__isnull=False,
            longitude__isnull=False
        )
    else:  # 任务区负责人
        # 任务区负责人看到同任务区的员工
        if request.user.task_area_fk:
            employees = User.objects.filter(
                role=User.Role.EMPLOYEE,
                task_area_fk=request.user.task_area_fk,
                latitude__isnull=False,
                longitude__isnull=False
            )
        else:
            # 如果任务区负责人没有设置task_area_fk，则显示所有员工
            employees = User.objects.filter(
                role=User.Role.EMPLOYEE,
                latitude__isnull=False,
                longitude__isnull=False
            )
    
    # 准备地图数据
    employee_locations = []
    for emp in employees:
        employee_locations.append({
            'id': emp.id,
            'username': emp.username,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'latitude': emp.latitude,
            'longitude': emp.longitude,
            'address': emp.location_address or '',
            'updated_at': emp.location_updated_at.strftime('%Y-%m-%d %H:%M') if emp.location_updated_at else '',
            'role': emp.get_role_display(),
            'task_area': emp.task_area_fk.name if emp.task_area_fk else '-'
        })
    
    context = {
        'employee_locations': json.dumps(employee_locations, ensure_ascii=False),
        'employee_count': len(employee_locations)
    }
    
    return render(request, 'location/employee_map.html', context)


@csrf_exempt
@login_required
def ajax_update_location(request):
    """AJAX更新位置"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            address = data.get('address', '')
            
            if latitude and longitude:
                request.user.latitude = float(latitude)
                request.user.longitude = float(longitude)
                request.user.location_address = address
                request.user.location_updated_at = timezone.now()
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '位置更新成功！'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '位置信息不完整。'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新失败：{str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': '无效的请求方法。'})
