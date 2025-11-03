#!/usr/bin/env python
"""
完整数据库迁移和启动脚本
解决Render部署中的所有数据库问题
"""
import os
import sys
import django
import subprocess

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.core.management import call_command

def run_migration(app_name=None):
    """执行数据库迁移"""
    try:
        if app_name:
            print(f"🔄 正在迁移 {app_name} 应用...")
            call_command('migrate', app_name, '--noinput')
            print(f"✅ {app_name} 应用迁移完成")
        else:
            print("🔄 正在执行完整数据库迁移...")
            call_command('migrate', '--noinput')
            print("✅ 完整数据库迁移完成")
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        raise

def main():
    """主部署流程"""
    print("🚀 开始Render完整部署流程...")
    
    try:
        # 1. 迁移核心Django应用
        print("\n📊 步骤1: 迁移核心Django应用")
        run_migration('contenttypes')
        run_migration('auth')
        run_migration('admin')
        run_migration('sessions')  # 关键：会话表
        run_migration('accounts')
        
        # 2. 完整迁移
        print("\n📊 步骤2: 执行完整数据库迁移")
        run_migration()
        
        # 3. 收集静态文件
        print("\n📊 步骤3: 收集静态文件")
        call_command('collectstatic', '--noinput')
        print("✅ 静态文件收集完成")
        
        # 4. 创建用户
        print("\n📊 步骤4: 创建默认用户")
        from accounts.models import User
        
        users = [
            ('superuser01', 'admin@company.com', True, True),
            ('head_manager01', 'head@company.com', True, False),
            ('manager01', 'manager@company.com', True, False),
            ('employee01', 'employee@company.com', False, False),
        ]
        
        for username, email, is_staff, is_superuser in users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email, 'is_staff': is_staff, 'is_superuser': is_superuser}
            )
            if created or not user.has_usable_password():
                user.set_password('123456')
                user.save()
                print(f"✅ 用户 {username} {'创建' if created else '更新'} 成功")
        
        print("\n🎉 Render部署流程全部完成!")
        print("\n📋 登录信息:")
        print("   超级管理员: superuser01 / 123456")
        print("   总经理: head_manager01 / 123456")
        print("   管理员: manager01 / 123456")
        print("   普通员工: employee01 / 123456")
        
    except Exception as e:
        print(f"❌ 部署过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()