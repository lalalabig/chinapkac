from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.db import models
from functools import wraps

def role_required(roles):
    """
    装饰器：检查用户是否具有指定的角色权限
    roles: 允许访问的角色列表
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth import views as auth_views
                return auth_views.redirect_to_login(request.get_full_path())
            
            if request.user.role in roles:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("您没有权限访问此页面")
        return wrapper
    return decorator

def is_employee(user):
    """检查是否为普通员工"""
    return user.is_authenticated and user.role == 'employee'

def is_task_area_manager(user):
    """检查是否为任务区负责人"""
    return user.is_authenticated and user.role == 'task_area_manager'

def is_head_manager(user):
    """检查是否为总部负责人"""
    return user.is_authenticated and user.role == 'head_manager'

def is_superuser_role(user):
    """检查是否为超级管理员"""
    return user.is_authenticated and user.role == 'superuser'

def is_manager_or_above(user):
    """检查是否为管理员级别（任务区负责人及以上）"""
    return user.is_authenticated and user.role in ['task_area_manager', 'head_manager', 'superuser']

def is_head_manager_or_above(user):
    """检查是否为总部级别（总部负责人及以上）"""
    return user.is_authenticated and user.role in ['head_manager', 'superuser']

def is_admin_only(user):
    """检查是否为超级管理员"""
    return user.is_authenticated and user.role == 'superuser'

# 角色常量
ROLES = {
    'EMPLOYEE': 'employee',         # 普通员工
    'TASK_AREA_MANAGER': 'task_area_manager',    # 任务区负责人
    'HEAD_MANAGER': 'head_manager',        # 总部负责人
    'SUPERUSER': 'superuser',             # 超级管理员
}

class PermissionMixin:
    """权限检查混入类，用于类视图"""
    required_user_types = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth import views as auth_views
            return auth_views.redirect_to_login(request.get_full_path())
        
        if self.required_user_types and request.user.user_type not in self.required_user_types:
            raise PermissionDenied("您没有权限访问此页面")
        
        return super().dispatch(request, *args, **kwargs)

def get_user_permissions(user):
    """获取用户的权限信息"""
    if not user.is_authenticated:
        return {
            'can_view_dashboard': False,
            'can_apply_leave': False,
            'can_approve_leave': False,
            'can_view_reports': False,
            'can_manage_employees': False,
            'can_view_location': False,
            'can_send_alerts': False,
            'can_manage_system': False,
        }
    
    # 基础权限（所有用户）
    permissions = {
        'can_view_dashboard': True,
        'can_apply_leave': user.needs_leave_approval,  # 使用模型中的方法
        'can_approve_leave': False,
        'can_view_reports': False,
        'can_manage_employees': False,
        'can_view_location': False,
        'can_update_location': user.role in ['employee', 'task_area_manager'],  # 只有员工和任务区负责人需要更新位置
        'can_send_alerts': False,
        'can_manage_system': False,
    }
    
    # 任务区负责人权限
    if user.role in ['task_area_manager', 'head_manager', 'superuser']:
        permissions.update({
            'can_approve_leave': True,
            'can_view_reports': True,
            'can_view_location': True,
        })
    
    # 总部负责人权限
    if user.role in ['head_manager', 'superuser']:
        permissions.update({
            'can_manage_employees': True,
            'can_send_alerts': True,
        })
    
    # 超级管理员权限
    if user.role == 'superuser':
        permissions.update({
            'can_manage_system': True,
            'can_manage_all_data': True,
        })
    
    return permissions

def get_role_display_name(role):
    """获取角色显示名称"""
    role_names = {
        'employee': '普通员工',
        'task_area_manager': '任务区负责人',
        'head_manager': '总部负责人',
        'superuser': '超级管理员',
    }
    return role_names.get(role, '未知角色')

def get_accessible_users(current_user):
    """获取当前用户可访问的用户列表"""
    from .models import User
    
    if current_user.role == 'superuser':
        # 超级管理员可以访问所有用户
        return User.objects.all()
    elif current_user.role == 'head_manager':
        # 总部负责人可以访问其管辖任务区内的所有用户
        managed_areas = current_user.managed_task_areas.all()
        if managed_areas.exists():
            return User.objects.filter(task_area_fk__in=managed_areas)
        return User.objects.none()
    elif current_user.role == 'task_area_manager':
        # 任务区负责人可以访问同任务区的普通员工
        if current_user.task_area_fk:
            return User.objects.filter(
                task_area_fk=current_user.task_area_fk,
                role__in=['employee']
            )
        return User.objects.none()
    else:
        # 普通员工只能看到自己
        return User.objects.filter(id=current_user.id)

def filter_users_by_task_area_permission(queryset, current_user):
    """根据任务区权限过滤用户查询集"""
    if current_user.role == 'superuser':
        return queryset
    elif current_user.role == 'head_manager':
        managed_areas = current_user.managed_task_areas.all()
        if managed_areas.exists():
            # 总部负责人可以看到：1) 管辖任务区内的用户，2) 自己
            return queryset.filter(
                models.Q(task_area_fk__in=managed_areas) | 
                models.Q(id=current_user.id)
            )
        else:
            # 如果没有管辖任务区，至少能看到自己
            return queryset.filter(id=current_user.id)
    elif current_user.role == 'task_area_manager':
        if current_user.task_area_fk:
            return queryset.filter(task_area_fk=current_user.task_area_fk)
        return queryset.none()
    else:
        return queryset.filter(id=current_user.id)