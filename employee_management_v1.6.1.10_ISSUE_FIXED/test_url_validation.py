#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URL验证脚本 - 检查所有模板中的URL是否能正确解析
验证不同层级账号是否存在同样的URL问题
"""
import os
import sys
import django

# 设置Django环境
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.template import engines
from django.template.loader import get_template
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from accounts.models import User as CustomUser

def test_template_urls():
    """测试所有模板中的URL是否能正确解析"""
    
    # 获取所有HTML模板文件
    template_files = []
    for root, dirs, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                template_files.append(os.path.join(root, file))
    
    print(f"找到 {len(template_files)} 个模板文件")
    
    # 创建请求工厂
    factory = RequestFactory()
    
    # 测试不同角色的用户
    test_users = [
        ('匿名用户', AnonymousUser()),
    ]
    
    try:
        # 尝试获取现有用户
        existing_users = CustomUser.objects.all()
        for user in existing_users[:5]:  # 限制测试数量
            test_users.append((f'{user.username}({user.role})', user))
    except Exception as e:
        print(f"获取用户失败: {e}")
    
    # 测试URL解析
    url_errors = []
    
    for user_role, user in test_users:
        print(f"\n=== 测试 {user_role} ===")
        
        # 创建请求对象
        request = factory.get('/')
        request.user = user
        
        for template_file in template_files:
            try:
                # 相对路径转换为模板路径
                template_path = template_file.replace('templates/', '')
                
                # 尝试加载模板
                template = get_template(template_path)
                
                # 尝试渲染模板（忽略模板语法错误）
                try:
                    context = {
                        'user': user,
                        'request': request,
                        # 添加常见的上下文变量
                        'leave_statistics': {
                            'total_applications': 0,
                            'pending_applications': 0,
                            'approved_applications': 0,
                            'rejected_applications': 0
                        },
                        'name_filter': '',
                    }
                    template.render(context)
                except Exception as template_error:
                    # 只记录URL相关的错误
                    if 'Reverse for' in str(template_error) or 'NoReverseMatch' in str(template_error):
                        url_errors.append({
                            'user': user_role,
                            'template': template_file,
                            'error': str(template_error)
                        })
                        print(f"  ❌ URL错误: {template_file} - {template_error}")
                    else:
                        # 其他模板错误不是我们关心的
                        pass
                        
            except Exception as e:
                if 'Reverse for' in str(e) or 'NoReverseMatch' in str(e):
                    url_errors.append({
                        'user': user_role,
                        'template': template_file,
                        'error': str(e)
                    })
                    print(f"  ❌ URL错误: {template_file} - {e}")
                else:
                    # 忽略其他类型的错误
                    pass
    
    return url_errors

def check_url_patterns():
    """检查所有定义的URL模式"""
    from django.urls import get_resolver
    
    resolver = get_resolver()
    all_urls = []
    
    def collect_urls(patterns, namespace=''):
        for pattern in patterns:
            if hasattr(pattern, 'pattern'):
                if hasattr(pattern, 'url_patterns'):
                    new_namespace = f"{namespace}:{pattern.app_name}" if pattern.app_name else namespace
                    collect_urls(pattern.url_patterns, new_namespace)
                elif hasattr(pattern, 'name') and pattern.name:
                    url_name = f"{namespace}:{pattern.name}" if namespace else pattern.name
                    all_urls.append(url_name)
    
    collect_urls(resolver.url_patterns)
    
    print("\n=== 定义的URL模式 ===")
    for url in sorted(all_urls):
        print(f"  {url}")
    
    return all_urls

if __name__ == '__main__':
    print("开始验证URL配置...")
    
    # 检查URL模式
    defined_urls = check_url_patterns()
    
    # 测试模板URL
    url_errors = test_template_urls()
    
    print("\n" + "="*50)
    if url_errors:
        print("❌ 发现URL错误:")
        for error in url_errors:
            print(f"  用户: {error['user']}")
            print(f"  模板: {error['template']}")
            print(f"  错误: {error['error']}")
            print()
    else:
        print("✅ 所有URL都能正确解析")
    
    print("验证完成!")