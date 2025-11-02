#!/usr/bin/env python
"""
数据库迁移脚本：从 SQLite 迁移到 PostgreSQL
适用于从现有 SQLite 数据库迁移数据到 Render PostgreSQL
"""

import os
import sys
import django
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings_postgresql')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connections

def create_admin_user():
    """创建管理员账户"""
    from accounts.models import User
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # 创建超级用户
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@company.com',
            'first_name': '管理员',
            'last_name': '系统',
            'is_staff': True,
            'is_superuser': True,
            'is_active': True,
        }
    )
    
    if created:
        admin_user.set_password('password123')
        admin_user.save()
        print("✅ 创建管理员账户：username=admin, password=password123")
    else:
        print("ℹ️ 管理员账户已存在：username=admin")
    
    # 创建部门经理账户
    manager_user, created = User.objects.get_or_create(
        username='manager',
        defaults={
            'email': 'manager@company.com',
            'first_name': '部门',
            'last_name': '经理',
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        manager_user.set_password('password123')
        manager_user.save()
        print("✅ 创建部门经理账户：username=manager, password=password123")
    else:
        print("ℹ️ 部门经理账户已存在：username=manager")
    
    # 创建任务区域经理账户
    taskmanager_user, created = User.objects.get_or_create(
        username='taskmanager',
        defaults={
            'email': 'taskmanager@company.com',
            'first_name': '任务区域',
            'last_name': '经理',
            'is_staff': True,
            'is_active': True,
        }
    )
    
    if created:
        taskmanager_user.set_password('password123')
        taskmanager_user.save()
        print("✅ 创建任务区域经理账户：username=taskmanager, password=password123")
    else:
        print("ℹ️ 任务区域经理账户已存在：username=taskmanager")
    
    # 创建普通员工账户
    employee_user, created = User.objects.get_or_create(
        username='employee',
        defaults={
            'email': 'employee@company.com',
            'first_name': '普通',
            'last_name': '员工',
            'is_active': True,
        }
    )
    
    if created:
        employee_user.set_password('password123')
        employee_user.save()
        print("✅ 创建普通员工账户：username=employee, password=password123")
    else:
        print("ℹ️ 普通员工账户已存在：username=employee")

def run_migrations():
    """运行数据库迁移"""
    print("🔄 开始数据库迁移...")
    try:
        # 初始化迁移
        execute_from_command_line(['manage.py', 'makemigrations'])
        print("✅ 生成迁移文件成功")
        
        # 执行迁移
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ 数据库迁移完成")
        
        # 收集静态文件
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ 静态文件收集完成")
        
        return True
    except Exception as e:
        print(f"❌ 迁移过程中出错：{str(e)}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"✅ 数据库连接成功：{version}")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败：{str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🚀 PostgreSQL 数据库迁移脚本")
    print("适用于 Render.com 部署")
    print("=" * 60)
    
    # 测试数据库连接
    if not test_database_connection():
        print("请检查数据库配置是否正确")
        return
    
    # 运行迁移
    if run_migrations():
        # 创建测试用户
        create_admin_user()
        
        print("\n" + "=" * 60)
        print("🎉 数据库迁移完成！")
        print("🌐 应用现已准备部署到 Render.com")
        print("\n📋 测试账户信息：")
        print("   管理员：admin / password123")
        print("   部门经理：manager / password123")
        print("   任务区域经理：taskmanager / password123")
        print("   普通员工：employee / password123")
        print("=" * 60)
    else:
        print("❌ 迁移失败，请检查错误信息")

if __name__ == '__main__':
    main()