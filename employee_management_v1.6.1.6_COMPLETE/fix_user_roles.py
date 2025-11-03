#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复用户角色问题脚本
确保不同用户账户具有正确的角色和权限
"""

import os
import sys
import django
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_django():
    """设置Django环境"""
    try:
        # 尝试多个可能的项目目录
        possible_dirs = [
            'employee_management_v1.6.1.6_COMPLETE',
            'employee_management',
            '.'
        ]
        
        for dir_name in possible_dirs:
            settings_file = Path(dir_name) / 'settings.py'
            if settings_file.exists():
                os.environ['DJANGO_SETTINGS_MODULE'] = f'{dir_name}.settings'
                logger.info(f"✅ 找到设置文件: {settings_file}")
                break
        else:
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
        
        # 初始化Django
        django.setup()
        logger.info("✅ Django环境设置成功")
        return True
    except Exception as e:
        logger.error(f"❌ Django环境设置失败: {e}")
        return False

def diagnose_user_roles():
    """诊断当前用户角色状态"""
    try:
        from django.contrib.auth.models import User
        
        logger.info("🔍 诊断当前用户角色...")
        
        # 获取所有用户
        users = User.objects.all()
        logger.info(f"📊 总共有 {users.count()} 个用户")
        
        # 详细分析每个用户
        for user in users:
            logger.info(f"👤 用户: {username} ({user.email})")
            logger.info(f"   - 是否管理员: {user.is_staff}")
            logger.info(f"   - 是否超级用户: {user.is_superuser}")
            logger.info(f"   - 是否活跃: {user.is_active}")
            
            # 检查是否有profile信息
            try:
                if hasattr(user, 'profile'):
                    logger.info(f"   - 职位: {getattr(user.profile, 'job_title', '未设置')}")
                    logger.info(f"   - 部门: {getattr(user.profile, 'department', '未设置')}")
            except:
                logger.info("   - 无profile信息")
                
            logger.info("")
        
        return True
    except Exception as e:
        logger.error(f"❌ 用户角色诊断失败: {e}")
        return False

def check_user_models():
    """检查用户模型结构"""
    try:
        from django.contrib.auth.models import User
        
        logger.info("🔍 检查用户模型结构...")
        
        # 获取User模型字段
        logger.info("📋 User模型字段:")
        for field in User._meta.fields:
            logger.info(f"  - {field.name}: {field.get_internal_type()}")
        
        # 检查是否有自定义的用户模型
        from django.contrib.auth import get_user_model
        UserModel = get_user_model()
        logger.info(f"📋 当前使用的用户模型: {UserModel.__name__}")
        
        # 检查是否有Profile模型
        try:
            from accounts.models import Profile
            logger.info("✅ 找到Profile模型")
            
            logger.info("📋 Profile模型字段:")
            for field in Profile._meta.fields:
                logger.info(f"  - {field.name}: {field.get_internal_type()}")
                
        except ImportError:
            logger.warning("⚠️ 未找到Profile模型")
        except Exception as e:
            logger.warning(f"⚠️ 检查Profile模型失败: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 用户模型检查失败: {e}")
        return False

def reset_and_create_users():
    """重置并创建正确角色的用户"""
    try:
        from django.contrib.auth.models import User
        from django.db import transaction
        
        logger.info("🔄 重置并创建用户...")
        
        # 删除现有用户（除了你可能需要的）
        logger.info("🗑️ 清理现有用户...")
        User.objects.all().delete()
        
        # 定义用户角色配置
        users_config = [
            {
                'username': 'superuser01',
                'email': 'admin@company.com',
                'password': 'admin123456',
                'job_title': '系统管理员',
                'department': '信息技术部',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            },
            {
                'username': 'head_manager01',
                'email': 'head@company.com',
                'password': 'manager123456',
                'job_title': '部门主管',
                'department': '管理部',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True
            },
            {
                'username': 'manager01',
                'email': 'manager@company.com',
                'password': 'manager123456',
                'job_title': '经理',
                'department': '业务部',
                'is_staff': True,
                'is_superuser': False,
                'is_active': True
            },
            {
                'username': 'employee01',
                'email': 'employee@company.com',
                'password': 'employee123456',
                'job_title': '普通员工',
                'department': '业务部',
                'is_staff': False,
                'is_superuser': False,
                'is_active': True
            }
        ]
        
        with transaction.atomic():
            for user_config in users_config:
                username = user_config['username']
                logger.info(f"👤 创建用户: {username}")
                
                # 创建用户
                user = User.objects.create_user(
                    username=user_config['username'],
                    email=user_config['email'],
                    password=user_config['password'],
                    is_staff=user_config['is_staff'],
                    is_superuser=user_config['is_superuser'],
                    is_active=user_config['is_active']
                )
                
                logger.info(f"  ✅ 用户 {username} 创建成功")
                logger.info(f"  📋 职位: {user_config['job_title']}")
                logger.info(f"  🏢 部门: {user_config['department']}")
                logger.info(f"  🔑 管理员权限: {user.is_staff}")
                logger.info(f"  👑 超级用户权限: {user.is_superuser}")
                
                # 尝试创建或更新Profile
                try:
                    from accounts.models import Profile
                    
                    # 删除现有profile（如果有）
                    Profile.objects.filter(user=user).delete()
                    
                    # 创建新的profile
                    profile = Profile.objects.create(
                        user=user,
                        job_title=user_config['job_title'],
                        department=user_config['department']
                    )
                    
                    logger.info(f"  📄 Profile创建成功: {profile}")
                    
                except ImportError:
                    logger.warning(f"  ⚠️ Profile模型不存在，跳过Profile创建")
                except Exception as e:
                    logger.warning(f"  ⚠️ Profile创建失败: {e}")
                
                logger.info("")
        
        logger.info("✅ 用户创建完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 用户创建失败: {e}")
        return False

def update_existing_users_roles():
    """更新现有用户的角色（不删除）"""
    try:
        from django.contrib.auth.models import User
        from django.db import transaction
        
        logger.info("🔄 更新现有用户角色...")
        
        # 定义角色更新配置
        role_updates = [
            {
                'username': 'superuser01',
                'job_title': '系统管理员',
                'department': '信息技术部',
                'is_staff': True,
                'is_superuser': True
            },
            {
                'username': 'head_manager01',
                'job_title': '部门主管',
                'department': '管理部',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'manager01',
                'job_title': '经理',
                'department': '业务部',
                'is_staff': True,
                'is_superuser': False
            },
            {
                'username': 'employee01',
                'job_title': '普通员工',
                'department': '业务部',
                'is_staff': False,
                'is_superuser': False
            }
        ]
        
        with transaction.atomic():
            for update_config in role_updates:
                try:
                    user = User.objects.get(username=update_config['username'])
                    
                    # 更新用户权限
                    user.is_staff = update_config['is_staff']
                    user.is_superuser = update_config['is_superuser']
                    user.save()
                    
                    logger.info(f"✅ 更新用户权限: {user.username}")
                    logger.info(f"  📋 职位: {update_config['job_title']}")
                    logger.info(f"  🏢 部门: {update_config['department']}")
                    logger.info(f"  🔑 管理员权限: {user.is_staff}")
                    logger.info(f"  👑 超级用户权限: {user.is_superuser}")
                    
                    # 尝试更新Profile
                    try:
                        from accounts.models import Profile
                        
                        profile, created = Profile.objects.get_or_create(user=user)
                        profile.job_title = update_config['job_title']
                        profile.department = update_config['department']
                        profile.save()
                        
                        action = "创建" if created else "更新"
                        logger.info(f"  📄 Profile {action}成功: {profile}")
                        
                    except ImportError:
                        logger.warning(f"  ⚠️ Profile模型不存在，跳过Profile更新")
                    except Exception as e:
                        logger.warning(f"  ⚠️ Profile更新失败: {e}")
                    
                except User.DoesNotExist:
                    logger.warning(f"⚠️ 用户不存在: {update_config['username']}")
                
                logger.info("")
        
        logger.info("✅ 用户角色更新完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 用户角色更新失败: {e}")
        return False

def verify_user_roles():
    """验证用户角色设置"""
    try:
        from django.contrib.auth.models import User
        
        logger.info("🔍 验证用户角色设置...")
        
        users = User.objects.all()
        logger.info(f"📊 验证 {users.count()} 个用户...")
        
        for user in users:
            logger.info(f"👤 {user.username} ({user.email})")
            logger.info(f"  📋 职位: {getattr(getattr(user, 'profile', None), 'job_title', '未设置')}")
            logger.info(f"  🏢 部门: {getattr(getattr(user, 'profile', None), 'department', '未设置')}")
            logger.info(f"  🔑 管理员: {'✅' if user.is_staff else '❌'}")
            logger.info(f"  👑 超级用户: {'✅' if user.is_superuser else '❌'}")
            logger.info(f"  🟢 活跃: {'✅' if user.is_active else '❌'}")
            
            # 检查权限级别
            if user.is_superuser:
                role = "👑 超级管理员"
            elif user.is_staff:
                role = "🔑 管理员"
            else:
                role = "👤 普通用户"
            
            logger.info(f"  🎯 角色: {role}")
            logger.info("")
        
        logger.info("✅ 用户角色验证完成")
        return True
        
    except Exception as e:
        logger.error(f"❌ 用户角色验证失败: {e}")
        return False

def test_user_login():
    """测试用户登录"""
    try:
        from django.test import Client
        
        logger.info("🔍 测试用户登录...")
        
        test_users = [
            ('superuser01', 'admin123456', '超级管理员'),
            ('head_manager01', 'manager123456', '部门主管'),
            ('manager01', 'manager123456', '经理'),
            ('employee01', 'employee123456', '普通员工')
        ]
        
        for username, password, expected_role in test_users:
            try:
                client = Client()
                response = client.post('/accounts/login/', {
                    'username': username,
                    'password': password,
                    'csrfmiddlewaretoken': 'test'
                }, follow=True)
                
                if response.status_code == 200:
                    logger.info(f"✅ {username} 登录测试成功 (预期角色: {expected_role})")
                else:
                    logger.warning(f"⚠️ {username} 登录测试返回状态码: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ {username} 登录测试失败: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 用户登录测试失败: {e}")
        return False

def main():
    """主函数"""
    logger.info("🚀 开始修复用户角色问题")
    
    # 1. 设置Django环境
    if not setup_django():
        logger.error("❌ Django环境设置失败")
        return False
    
    # 2. 诊断当前状态
    diagnose_user_roles()
    
    # 3. 检查用户模型
    check_user_models()
    
    # 4. 更新现有用户角色
    if not update_existing_users_roles():
        logger.warning("⚠️ 用户角色更新失败，尝试重新创建...")
        if not reset_and_create_users():
            logger.error("❌ 用户创建失败")
            return False
    
    # 5. 验证用户角色
    verify_user_roles()
    
    # 6. 测试登录
    test_user_login()
    
    logger.info("🎉 用户角色修复完成！")
    logger.info("")
    logger.info("📋 用户角色信息:")
    logger.info("  👑 超级管理员: superuser01 / admin123456")
    logger.info("  🔑 部门主管: head_manager01 / manager123456")
    logger.info("  🔑 经理: manager01 / manager123456")
    logger.info("  👤 普通员工: employee01 / employee123456")
    logger.info("")
    logger.info("💡 现在不同用户登录应该会显示不同的角色和权限了！")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("✅ 修复成功！现在启动Gunicorn...")
        # 启动Gunicorn
        os.system('gunicorn employee_management.wsgi --bind 0.0.0.0:$PORT')
    else:
        logger.error("❌ 修复失败！")
        sys.exit(1)