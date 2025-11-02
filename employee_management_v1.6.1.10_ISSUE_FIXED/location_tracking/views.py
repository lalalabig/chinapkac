from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import json


@login_required
def map_view(request):
    """显示所有用户位置（管理员用）"""
    # 检查权限 - 只有分公司负责人及以上可以查看
    if request.user.role not in ['branch_manager', 'head_manager', 'superuser']:
        messages.error(request, '您没有权限查看此页面')
        return redirect('dashboard:home')
    
    # 根据权限获取用户
    if request.user.role == 'branch_manager':  # 分公司负责人
        # 分公司负责人只能看到自己公司的员工
        if request.user.assigned_company:
            users = request.user.__class__.objects.filter(
                role='employee',
                assigned_company=request.user.assigned_company,
                latitude__isnull=False, 
                longitude__isnull=False
            )
        else:
            # 如果没有设置公司，则显示所有员工
            users = request.user.__class__.objects.filter(
                role='employee',
                latitude__isnull=False, 
                longitude__isnull=False
            )
    else:  # 总部负责人和超级管理员
        users = request.user.__class__.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        ).exclude(id=request.user.id)
    
    users_data = []
    for user in users:
        users_data.append({
            'username': user.username,
            'name': f"{user.first_name} {user.last_name}",
            'role': user.get_role_display(),
            'latitude': float(user.latitude),
            'longitude': float(user.longitude),
            'address': user.location_address or '未设置地址',
            'updated_at': user.location_updated_at.strftime('%Y-%m-%d %H:%M') if user.location_updated_at else '未更新'
        })
    
    context = {
        'users_data': json.dumps(users_data),
        'total_users': len(users_data)
    }
    
    return render(request, 'location_tracking/map_view.html', context)


@login_required
def update_location(request):
    """更新用户位置"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            address = data.get('address', '')
            
            if latitude and longitude:
                request.user.latitude = latitude
                request.user.longitude = longitude
                request.user.location_address = address
                request.user.location_updated_at = timezone.now()
                request.user.save()
                
                return JsonResponse({
                    'success': True,
                    'message': '位置更新成功'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': '位置数据不完整'
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'更新失败: {str(e)}'
            })
    
    # GET请求显示位置更新页面
    context = {
        'current_latitude': request.user.latitude,
        'current_longitude': request.user.longitude,
        'current_address': request.user.location_address,
        'last_updated': request.user.location_updated_at
    }
    
    return render(request, 'location_tracking/update_location.html', context)
