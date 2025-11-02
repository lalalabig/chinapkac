"""
用户管理后台配置
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, TaskArea


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    自定义用户管理后台
    """
    list_display = ('username', 'email', 'role', 'department_rank', 'task_area', 'is_active', 'date_joined')
    list_filter = ('role', 'task_area', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'passport_number', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('个人信息'), {
            'fields': ('first_name', 'last_name', 'email', 'passport_number', 'phone_number')
        }),
        (_('工作信息'), {
            'fields': ('role', 'department_rank', 'task_area', 'position', 'employment_start_date')
        }),
        (_('权限'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        (_('重要日期'), {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )


@admin.register(TaskArea)
class TaskAreaAdmin(admin.ModelAdmin):
    """
    任务区管理后台
    """
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)
