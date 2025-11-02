from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps

def user_type_required(user_types):
    """
    装饰器：检查用户是否具有指定的用户类型权限
    user_types: 允许访问的用户类型列表
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth import views as auth_views
                return auth_views.redirect_to_login(request.get_full_path())
            
            if request.user.user_type in user_types:
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied("您没有权限访问此页面")
        return wrapper
    return decorator

def is_regular_employee(user):
    """检查是否为普通员工"""
    return user.is_authenticated and user.user_type == 1

def is_branch_manager(user):
    """检查是否为分公司负责人"""
    return user.is_authenticated and user.user_type == 2

def is_headquarters_manager(user):
    """检查是否为总部负责人"""
    return user.is_authenticated and user.user_type == 3

def is_super_admin(user):
    """检查是否为超级管理员"""
    return user.is_authenticated and user.user_type == 4

def is_manager_or_above(user):
    """检查是否为管理员级别（分公司负责人及以上）"""
    return user.is_authenticated and user.user_type >= 2

def is_headquarters_or_above(user):
    """检查是否为总部级别（总部负责人及以上）"""
    return user.is_authenticated and user.user_type >= 3

def is_admin_or_above(user):
    """检查是否为管理员级别（超级管理员）"""
    return user.is_authenticated and user.user_type >= 4

# 权限级别常量
USER_TYPES = {
    'EMPLOYEE': 1,      # 普通员工
    'BRANCH': 2,        # 分公司负责人
    'HEADQUARTERS': 3,  # 总部负责人
    'ADMIN': 4,         # 超级管理员
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
        }
    
    permissions = {
        'can_view_dashboard': True,
        'can_apply_leave': True,
        'can_approve_leave': False,
        'can_view_reports': False,
        'can_manage_employees': False,
        'can_view_location': False,
        'can_send_alerts': False,
    }
    
    # 分公司负责人权限
    if user.user_type >= 2:
        permissions.update({
            'can_approve_leave': True,
            'can_view_reports': True,
            'can_view_location': True,
        })
    
    # 总部负责人权限
    if user.user_type >= 3:
        permissions.update({
            'can_manage_employees': True,
            'can_send_alerts': True,
        })
    
    # 超级管理员权限
    if user.user_type >= 4:
        permissions.update({
            'can_manage_system': True,
            'can_manage_all_data': True,
        })
    
    return permissions