"""
上下文处理器 - 用于在所有模板中提供用户权限信息
"""
from .permissions import get_user_permissions, get_role_display_name

def user_permissions(request):
    """
    为所有模板提供用户权限信息
    """
    if request.user.is_authenticated:
        return {
            'user_permissions': get_user_permissions(request.user),
            'user_role_display': get_role_display_name(request.user.role),
        }
    return {
        'user_permissions': {},
        'user_role_display': '',
    }
