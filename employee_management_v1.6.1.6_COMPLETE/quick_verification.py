#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证脚本 - 检查修复后的关键功能
"""
import os
import sys

def check_template_files():
    """检查关键模板文件是否已修复"""
    print("🔍 检查模板文件修复状态...")
    
    # 检查 leave_management/dashboard.html
    dashboard_file = "templates/leave_management/dashboard.html"
    if os.path.exists(dashboard_file):
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "'leave_management:dashboard'" in content:
                print("  ✅ leave_management/dashboard.html: URL已修复")
            else:
                print("  ❌ leave_management/dashboard.html: URL未修复")
    else:
        print(f"  ❌ 文件不存在: {dashboard_file}")
    
    # 检查 delete_user_confirm.html
    confirm_file = "templates/dashboard/delete_user_confirm.html"
    if os.path.exists(confirm_file):
        with open(confirm_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if "{% if target_user and target_user.id %}" in content:
                print("  ✅ dashboard/delete_user_confirm.html: 防护代码已添加")
            else:
                print("  ❌ dashboard/delete_user_confirm.html: 防护代码未添加")
    else:
        print(f"  ❌ 文件不存在: {confirm_file}")

def check_django_setup():
    """检查Django环境"""
    print("\n🔍 检查Django环境...")
    try:
        import django
        print(f"  ✅ Django版本: {django.get_version()}")
    except ImportError:
        print("  ❌ Django未安装")
        return False
    return True

def main():
    print("=" * 60)
    print("🚀 员工管理系统 v1.6.1.8 修复验证")
    print("=" * 60)
    
    # 检查模板文件
    check_template_files()
    
    # 检查Django环境
    if check_django_setup():
        print("\n🎉 修复验证完成!")
        print("建议使用以下账号测试功能:")
        print("  - 超级用户: superuser01 / admin123456")
        print("  - 总部负责人: head_manager01 / admin123456") 
        print("  - 区域经理: task_area_manager01 / admin123456")
        print("  - 普通员工: test_employee / admin123456")
        print("\n重点测试:")
        print("  ✅ 审批管理仪表盘访问")
        print("  ✅ 用户删除确认功能")
    else:
        print("\n⚠️  请先安装Django依赖: pip install -r requirements.txt")

if __name__ == '__main__':
    main()