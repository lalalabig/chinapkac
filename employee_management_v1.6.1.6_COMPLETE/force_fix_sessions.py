#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
强力修复Django Session表问题
专门解决 "No migrations to apply" 但表不存在的情况
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

def reset_session_migrations():
    """重置sessions应用迁移状态"""
    try:
        from django.db import connection
        
        logger.info("🔄 重置sessions迁移状态...")
        
        # 删除sessions相关的迁移记录
        with connection.cursor() as cursor:
            # 删除django_migrations表中sessions相关的记录
            cursor.execute("""
                DELETE FROM django_migrations 
                WHERE app = 'sessions'
            """)
            
            logger.info("✅ 删除sessions迁移记录")
        
        return True
    except Exception as e:
        logger.warning(f"⚠️ 重置迁移状态失败: {e}")
        return False

def check_and_create_session_table():
    """检查并创建session表"""
    try:
        from django.db import connection
        
        logger.info("🔍 检查django_session表...")
        
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'django_session'
                )
            """)
            
            table_exists = cursor.fetchone()[0]
            
            if table_exists:
                logger.info("✅ django_session表已存在")
                
                # 检查表结构
                cursor.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'django_session'
                """)
                
                columns = cursor.fetchall()
                logger.info("📋 django_session表结构:")
                for col_name, col_type in columns:
                    logger.info(f"  - {col_name}: {col_type}")
                
                return True
            else:
                logger.info("🔧 django_session表不存在，开始创建...")
                
                # 创建表
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
                
                # 手动插入迁移记录，标记为已应用
                cursor.execute("""
                    INSERT INTO django_migrations (app, name, applied)
                    VALUES ('sessions', '0001_initial', NOW())
                    ON CONFLICT (app, name) DO NOTHING
                """)
                
                logger.info("✅ 标记sessions迁移为已应用")
                
                return True
                
    except Exception as e:
        logger.error(f"❌ 检查/创建session表失败: {e}")
        return False

def run_migrations_with_force():
    """强制运行迁移"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        logger.info("🔄 强制运行Django迁移...")
        
        # 首先运行fake migrations，标记所有现有迁移为已应用
        try:
            call_command('migrate', '--fake', verbosity=0)
            logger.info("✅ 标记现有迁移为已应用")
        except Exception as e:
            logger.warning(f"⚠️ fake migration失败: {e}")
        
        # 然后运行sessions迁移
        try:
            output = StringIO()
            call_command('migrate', 'sessions', '--run-syncdb', stdout=output, verbosity=1)
            logger.info("✅ 强制创建sessions表")
        except Exception as e:
            logger.warning(f"⚠️ sessions迁移失败: {e}")
        
        # 最后运行所有迁移
        try:
            output = StringIO()
            call_command('migrate', stdout=output, verbosity=1)
            logger.info("✅ 运行所有迁移")
        except Exception as e:
            logger.warning(f"⚠️ 完整迁移失败: {e}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 迁移执行失败: {e}")
        return False

def verify_session_functionality():
    """验证session功能"""
    try:
        from django.contrib.sessions.backends.db import SessionStore
        from django.contrib.auth.models import User
        from django.test import Client
        
        logger.info("🔍 测试session功能...")
        
        # 测试1：会话创建
        session = SessionStore()
        session['test_data'] = 'test_value'
        session.save()
        
        session_key = session.session_key
        if session_key:
            logger.info("✅ 会话创建成功")
            
            # 测试2：会话读取
            session2 = SessionStore(session_key=session_key)
            if session2.get('test_data') == 'test_value':
                logger.info("✅ 会话读取成功")
                
                # 测试3：网站访问
                client = Client()
                response = client.get('/accounts/login/')
                if response.status_code == 200:
                    logger.info("✅ 网站访问测试成功")
                    
                    # 清理测试数据
                    session.delete()
                    logger.info("✅ 清理测试数据")
                    
                    return True
                else:
                    logger.warning(f"⚠️ 网站访问状态码: {response.status_code}")
                    return False
            else:
                logger.error("❌ 会话数据读取失败")
                return False
        else:
            logger.error("❌ 会话创建失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 会话功能测试失败: {e}")
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

def main():
    """主函数"""
    logger.info("🚀 开始强力修复django_session表问题")
    
    # 1. 设置Django环境
    if not setup_django():
        logger.error("❌ Django环境设置失败")
        return False
    
    # 2. 重置session迁移状态
    reset_session_migrations()
    
    # 3. 检查并创建session表
    if not check_and_create_session_table():
        logger.error("❌ session表创建失败")
        return False
    
    # 4. 强制运行迁移
    if not run_migrations_with_force():
        logger.warning("⚠️ 迁移执行有问题，但继续...")
    
    # 5. 验证session功能
    if not verify_session_functionality():
        logger.error("❌ session功能验证失败")
        return False
    
    # 6. 创建默认用户
    create_default_users()
    
    logger.info("🎉 强力修复完成！")
    logger.info("🌐 网站现在应该可以正常登录了")
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