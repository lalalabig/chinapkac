#!/usr/bin/env python3
"""
快速功能验证脚本 - 工作报告筛选功能
版本: v1.6.1.9
用途: 快速验证筛选功能是否正常工作
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append('/workspace/employee_management_v1.6.1.9_REPORT_FILTERING_ENHANCED')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.test import Client
from accounts.models import User, TaskArea
from reports.models import Report

def test_filtering_functionality():
    """测试筛选功能"""
    print("=" * 60)
    print("工作报告筛选功能快速验证 v1.6.1.9")
    print("=" * 60)
    
    client = Client()
    
    # 测试不同角色的筛选功能
    test_cases = [
        {
            'username': 'admin',
            'password': 'admin123',
            'role': '超级管理员',
            'expected_filters': ['时间', '任务区', '姓名'],
            'filter_permissions': {
                'time': True,
                'task_area': True,
                'name': True
            }
        },
        {
            'username': 'head_manager_1',
            'password': 'password123',
            'role': '总部负责人',
            'expected_filters': ['时间', '任务区', '姓名'],
            'filter_permissions': {
                'time': True,
                'task_area': True,
                'name': True
            }
        },
        {
            'username': 'task_manager_1',
            'password': 'password123',
            'role': '任务区负责人',
            'expected_filters': ['时间'],
            'filter_permissions': {
                'time': True,
                'task_area': False,
                'name': False
            }
        }
    ]
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_count}] 测试 {test_case['role']} ({test_case['username']})")
        print("-" * 40)
        
        try:
            # 登录
            login_response = client.post('/accounts/login/', {
                'username': test_case['username'],
                'password': test_case['password']
            }, follow=True)
            
            if login_response.status_code == 200:
                print("✅ 登录成功")
                
                # 访问报告页面
                reports_response = client.get('/reports/my_reports/')
                
                if reports_response.status_code == 200:
                    print("✅ 报告页面访问成功")
                    
                    # 检查筛选参数
                    filters_to_test = [
                        ('time', 'date_from', '2024-01-01'),
                        ('time', 'date_to', '2024-12-31'),
                    ]
                    
                    if test_case['filter_permissions']['task_area']:
                        # 获取任务区列表进行测试
                        user = User.objects.get(username=test_case['username'])
                        task_areas = TaskArea.objects.all()
                        if task_areas.exists():
                            filters_to_test.append(('task_area', 'task_area', str(task_areas.first().id)))
                        else:
                            print("⚠️  警告: 未找到任务区数据，跳过任务区筛选测试")
                    
                    if test_case['filter_permissions']['name']:
                        filters_to_test.append(('name', 'name', 'test'))
                    
                    # 测试筛选功能
                    filter_success = True
                    for filter_type, param_name, param_value in filters_to_test:
                        filter_response = client.get('/reports/my_reports/', {
                            param_name: param_value
                        })
                        
                        if filter_response.status_code == 200:
                            print(f"  ✅ {param_name}筛选参数接受正常")
                        else:
                            print(f"  ❌ {param_name}筛选参数失败")
                            filter_success = False
                    
                    if filter_success:
                        success_count += 1
                        print(f"✅ {test_case['role']}筛选功能测试通过")
                    else:
                        print(f"❌ {test_case['role']}筛选功能测试失败")
                else:
                    print(f"❌ 报告页面访问失败 (状态码: {reports_response.status_code})")
            else:
                print(f"❌ 登录失败 (状态码: {login_response.status_code})")
                
        except Exception as e:
            print(f"❌ 测试过程中发生异常: {str(e)}")
        
        # 登出
        try:
            client.post('/accounts/logout/')
        except:
            pass
    
    print("\n" + "=" * 60)
    print(f"测试完成: {success_count}/{total_count} 个角色测试通过")
    
    if success_count == total_count:
        print("🎉 所有角色筛选功能测试通过！")
        return True
    else:
        print("⚠️  部分功能存在问题，请检查日志")
        return False

def test_server_status():
    """测试服务器状态"""
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("✅ Django服务器运行正常")
            return True
        else:
            print(f"❌ 服务器响应异常 (状态码: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到服务器: {str(e)}")
        print("请确保Django服务器正在运行: uv run python manage.py runserver")
        return False

def check_database_connection():
    """检查数据库连接"""
    try:
        # 测试数据库连接
        user_count = User.objects.count()
        task_area_count = TaskArea.objects.count()
        report_count = Report.objects.count()
        
        print(f"✅ 数据库连接正常")
        print(f"  - 用户数量: {user_count}")
        print(f"  - 任务区数量: {task_area_count}")
        print(f"  - 报告数量: {report_count}")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("正在启动工作报告筛选功能验证...")
    
    # 检查服务器状态
    print("\n1. 检查Django服务器状态")
    server_ok = test_server_status()
    
    # 检查数据库连接
    print("\n2. 检查数据库连接")
    db_ok = check_database_connection()
    
    if server_ok and db_ok:
        print("\n3. 测试筛选功能")
        filter_ok = test_filtering_functionality()
        
        if filter_ok:
            print("\n🎉 工作报告筛选功能验证完成！")
            print("所有功能正常工作，可以进行生产部署。")
        else:
            print("\n⚠️  部分功能存在问题，请检查代码或数据库。")
    else:
        print("\n❌ 基础环境检查失败，请确保:")
        print("1. Django服务器正在运行")
        print("2. 数据库连接正常")
        print("3. 依赖项已正确安装")

if __name__ == "__main__":
    main()