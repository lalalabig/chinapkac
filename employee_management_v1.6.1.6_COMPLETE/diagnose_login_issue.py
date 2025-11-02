#!/usr/bin/env python
"""
登录问题诊断脚本
"""
import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.contrib.auth import authenticate
from accounts.models import User

def diagnose_login():
    """诊断登录问题"""
    print("="*60)
    print("登录问题诊断")
    print("="*60)
    
    # 获取所有用户
    users = User.objects.all()
    print(f"\n数据库中共有 {users.count()} 个用户:")
    
    for user in users:
        print(f"\n用户: {user.username}")
        print(f"  - ID: {user.id}")
        print(f"  - Email: {user.email}")
        print(f"  - 角色: {user.get_role_display()}")
        print(f"  - is_active: {user.is_active}")
        print(f"  - is_staff: {user.is_staff}")
        print(f"  - is_superuser: {user.is_superuser}")
        print(f"  - 密码哈希: {user.password[:50]}...")
        
        # 测试密码123456
        auth_user = authenticate(username=user.username, password='123456')
        if auth_user:
            print(f"  ✓ 可以使用密码 '123456' 登录")
        else:
            print(f"  ✗ 无法使用密码 '123456' 登录")
            
            # 尝试检查密码是否有效
            if user.check_password('123456'):
                print(f"  ! 密码验证通过，但authenticate失败 - 可能是is_active问题")
            else:
                print(f"  ! 密码验证失败 - 密码可能未正确设置")
    
    print("\n" + "="*60)
    print("诊断完成")
    print("="*60)

if __name__ == '__main__':
    diagnose_login()
