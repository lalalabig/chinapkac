#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建管理员用户脚本
运行此脚本可以创建或重置管理员用户账号
"""

import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_or_update_admin():
    """创建或更新管理员用户"""
    
    admin_username = 'admin'
    admin_password = 'admin123456'  # 默认密码
    admin_email = 'admin@example.com'
    
    with transaction.atomic():
        # 检查是否已存在
        try:
            admin_user = User.objects.get(username=admin_username)
            print(f"找到现有用户: {admin_user.username}")
            
            # 更新密码和邮箱
            admin_user.set_password(admin_password)
            admin_user.email = admin_email
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.role = 'superuser'
            admin_user.save()
            
            print(f"已更新管理员用户: {admin_username}")
            print(f"密码: {admin_password}")
            
        except User.DoesNotExist:
            # 创建新用户
            admin_user = User.objects.create_user(
                username=admin_username,
                password=admin_password,
                email=admin_email,
                first_name='系统',
                last_name='管理员',
                role='superuser',
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            print(f"已创建管理员用户: {admin_username}")
            print(f"密码: {admin_password}")
        
        # 显示所有用户信息
        print("\n=== 系统中的用户列表 ===")
        for user in User.objects.all():
            print(f"用户名: {user.username:<15} | 角色: {user.role:<15} | 状态: {'激活' if user.is_active else '禁用'}")
        
        print(f"\n=== 登录信息 ===")
        print(f"管理员用户名: {admin_username}")
        print(f"管理员密码: {admin_password}")
        print(f"登录地址: http://127.0.0.1:8000/")
        
        print(f"\n=== 其他默认用户 ===")
        print(f"任务区负责人")
        print(f"  用户名: manager")
        print(f"  密码: manager123")
        print(f"  角色: task_area_manager")
        print(f"\n普通员工")
        print(f"  用户名: employee")
        print(f"  密码: employee123")
        print(f"  角色: employee")

if __name__ == '__main__':
    create_or_update_admin()