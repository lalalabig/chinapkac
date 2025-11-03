#!/usr/bin/env python
"""
极简用户创建脚本 - Render部署专用
避免Render shell的所有问题
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from accounts.models import User

# 简单创建用户
print("Creating default users...")

users = [
    ('admin', 'admin@chinacompany.com', True, True),
    ('manager', 'manager@chinacompany.com', True, False),
    ('employee', 'employee@chinacompany.com', False, False),
    ('head_manager', 'head@chinacompany.com', True, True)
]

for username, email, is_staff, is_superuser in users:
    user, created = User.objects.get_or_create(
        username=username,
        defaults={'email': email, 'is_staff': is_staff, 'is_superuser': is_superuser}
    )
    user.set_password('password123')
    user.save()
    print(f"User {username} ready")

print("All users created successfully! Password: password123")