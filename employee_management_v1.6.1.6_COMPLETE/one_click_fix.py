#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一键修复Django部署问题脚本
专门解决Render部署中django_session表缺失问题
"""

import os
import sys
import django
import logging
import subprocess
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def change_to_project_directory():
    """切换到项目目录"""
    possible_paths = [
        '/opt/render/project/src',
        '/opt/render/project/src/employee_management_v1.6.1.6_COMPLETE',
        './',
        '../'
    ]
    
    for path in possible_paths:
        project_path = Path(path) / 'employee_management'
        if project_path.exists():
            os.chdir(Path(path))
            logger.info(f"✅ 已切换到项目目录: {Path(path).absolute()}")
            return True
    
    logger.warning("⚠️ 未找到标准项目目录，使用当前目录")
    return False

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

def run_command(command, description=""):
    """运行shell命令"""
    try:
        logger.info(f"🔄 {description}: {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info(f"✅ {description} 成功")
            if result.stdout:
                logger.info(f"输出: {result.stdout[:200]}...")
            return True
        else:
            logger.error(f"❌ {description} 失败")
            if result.stderr:
                logger.error(f"错误: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.error(f"⏰ {description} 超时")
        return False
    except Exception as e:
        logger.error(f"❌ {description} 执行异常: {e}")
        return False

def check_and_fix_database():
    """检查并修复数据库"""
    try:
        from django.db import connection
        
        # 检查django_session表是否存在
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_session'
                )
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if not table_exists:
                logger.info("🔧 发现django_session表缺失，开始修复...")
                
                # 直接创建表
                create_table_sql = """
                CREATE TABLE django_session (
                    session_key varchar(40) NOT NULL PRIMARY KEY,
                    session_data text NOT NULL,
                    expire_date timestamp with time zone NOT NULL
                );
                
                CREATE INDEX django_session_expire_date ON django_session (expire_date);
                CREATE INDEX django_session_session_key ON django_session (session_key);
                """
                
                cursor.execute(create_table_sql)
                logger.info("✅ django_session表创建成功")
            else:
                logger.info("✅ django_session表已存在")
                
        return True
    except Exception as e:
        logger.error(f"❌ 数据库检查/修复失败: {e}")
        return False

def run_migrations():
    """运行Django迁移"""
    try:
        from django.core.management import call_command
        
        logger.info("🔄 开始运行Django迁移...")
        
        # 先运行contenttypes迁移
        try:
            call_command('migrate', 'contenttypes', verbosity=0)
            logger.info("✅ contenttypes迁移完成")
        except:
            logger.warning("⚠️ contenttypes迁移跳过（可能已存在）")
        
        # 运行sessions迁移
        try:
            call_command('migrate', 'sessions', verbosity=0)
            logger.info("✅ sessions迁移完成")
        except:
            logger.warning("⚠️ sessions迁移跳过（可能已存在）")
        
        # 运行auth迁移
        try:
            call_command('migrate', 'auth', verbosity=0)
            logger.info("✅ auth迁移完成")
        except:
            logger.warning("⚠️ auth迁移跳过（可能已存在）")
        
        # 运行所有应用迁移
        call_command('migrate', verbosity=1)
        logger.info("✅ 所有迁移完成")
        
        return True
    except Exception as e:
        logger.error(f"❌ 迁移执行失败: {e}")
        return False

def collect_static():
    """收集静态文件"""
    try:
        from django.core.management import call_command
        
        logger.info("🔄 开始收集静态文件...")
        call_command('collectstatic', '--noinput', verbosity=0)
        logger.info("✅ 静态文件收集完成")
        return True
    except Exception as e:
        logger.warning(f"⚠️ 静态文件收集失败: {e}")
        return False

def create_default_users():
    """创建默认用户"""
    try:
        from django.contrib.auth.models import User
        from django.db import transaction
        
        # 默认用户列表
        default_users = [
            ('superuser01', 'admin@company.com', True, True, 'admin123456'),
            ('head_manager01', 'head@company.com', True, False, 'manager123456'),
            ('manager01', 'manager@company.com', False, False, 'manager123456'),
            ('employee01', 'employee@company.com', False, False, 'employee123456'),
        ]
        
        logger.info("🔄 开始创建默认用户...")
        
        with transaction.atomic():
            for username, email, is_staff, is_superuser, password in default_users:
                if not User.objects.filter(username=username).exists():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        is_staff=is_staff,
                        is_superuser=is_superuser
                    )
                    logger.info(f"✅ 创建用户: {username}")
                else:
                    logger.info(f"ℹ️ 用户已存在: {username}")
        
        logger.info("✅ 默认用户创建完成")
        return True
    except Exception as e:
        logger.warning(f"⚠️ 用户创建失败: {e}")
        return False

def test_deployment():
    """测试部署状态"""
    try:
        from django.test.utils import setup_test_environment, teardown_test_environment
        from django.test.client import Client
        
        setup_test_environment()
        
        client = Client()
        response = client.get('/accounts/login/')
        
        if response.status_code == 200:
            logger.info("✅ 网站访问测试成功")
            logger.info("✅ Django session功能正常")
            return True
        else:
            logger.warning(f"⚠️ 网站访问返回状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.warning(f"⚠️ 部署测试失败: {e}")
        return False
    finally:
        try:
            teardown_test_environment()
        except:
            pass

def main():
    """主函数"""
    logger.info("🚀 开始一键修复Django部署问题")
    
    # 1. 切换到项目目录
    change_to_project_directory()
    
    # 2. 设置Django环境
    if not setup_django():
        logger.error("❌ Django环境设置失败")
        return False
    
    # 3. 检查并修复数据库
    if not check_and_fix_database():
        logger.error("❌ 数据库修复失败")
        return False
    
    # 4. 运行迁移
    if not run_migrations():
        logger.error("❌ 迁移执行失败")
        return False
    
    # 5. 收集静态文件
    collect_static()
    
    # 6. 创建默认用户
    create_default_users()
    
    # 7. 测试部署
    test_deployment()
    
    logger.info("🎉 一键修复完成！")
    logger.info("🌐 网站现在应该可以正常访问了")
    logger.info("🔑 默认登录凭据:")
    logger.info("   - 管理员: superuser01 / admin123456")
    logger.info("   - 部门主管: head_manager01 / manager123456")
    logger.info("   - 经理: manager01 / manager123456")
    logger.info("   - 员工: employee01 / employee123456")
    
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