#!/usr/bin/env python3
"""
员工管理系统 v1.6.1.10 部署验证脚本
用于验证修复后的系统功能是否正常
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings')
django.setup()

from django.conf import settings
from django.core.management import execute_from_command_line
from accounts.models import User
from django.db import connection

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_status(item, status, details=""):
    """打印检查状态"""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {item}")
    if details:
        print(f"   {details}")

def check_python_version():
    """检查Python版本"""
    print_header("Python环境检查")
    
    version = sys.version_info
    version_ok = version.major == 3 and version.minor >= 8
    
    print_status(
        f"Python版本: {version.major}.{version.minor}.{version.micro}",
        version_ok,
        "需要Python 3.8或更高版本" if not version_ok else "版本兼容"
    )
    
    return version_ok

def check_dependencies():
    """检查依赖包"""
    print_header("依赖包检查")
    
    required_packages = [
        'django',
        'pillow',
        'python_dateutil',
        'pytz',
        'requests',
        'pypinyin'
    ]
    
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"{package}", True)
        except ImportError:
            print_status(f"{package}", False, "请运行: pip install -r requirements.txt")
            all_ok = False
    
    return all_ok

def check_file_structure():
    """检查文件结构"""
    print_header("文件结构检查")
    
    required_dirs = [
        'accounts',
        'dashboard', 
        'leave_management',
        'reports',
        'location',
        'emergency',
        'usermanagement',
        'location_tracking',
        'templates',
        'static'
    ]
    
    required_files = [
        'manage.py',
        'requirements.txt',
        'employee_management/__init__.py',
        'employee_management/settings.py'
    ]
    
    all_ok = True
    
    # 检查目录
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        exists = dir_path.exists() and dir_path.is_dir()
        print_status(f"目录: {dir_name}", exists)
        if not exists:
            all_ok = False
    
    # 检查文件
    for file_name in required_files:
        file_path = Path(file_name)
        exists = file_path.exists() and file_path.is_file()
        print_status(f"文件: {file_name}", exists)
        if not exists:
            all_ok = False
    
    return all_ok

def check_django_config():
    """检查Django配置"""
    print_header("Django配置检查")
    
    try:
        # 检查基础配置
        debug_ok = settings.DEBUG == False
        print_status("生产环境配置(DEBUG=False)", debug_ok)
        
        # 检查数据库配置
        db_engine = settings.DATABASES['default']['ENGINE']
        db_ok = 'sqlite3' in db_engine or 'postgresql' in db_engine
        print_status(f"数据库引擎: {db_engine}", db_ok)
        
        # 检查静态文件配置
        static_url_ok = hasattr(settings, 'STATIC_URL')
        print_status("静态文件配置", static_url_ok)
        
        # 检查已安装的应用
        installed_apps = settings.INSTALLED_APPS
        required_apps = [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'accounts',
            'dashboard',
            'leave_management',
            'reports',
            'location',
            'emergency',
            'usermanagement',
            'location_tracking'
        ]
        
        apps_ok = all(app in installed_apps for app in required_apps)
        print_status("应用配置", apps_ok)
        
        return debug_ok and db_ok and static_url_ok and apps_ok
        
    except Exception as e:
        print_status("Django配置检查", False, f"错误: {str(e)}")
        return False

def check_database():
    """检查数据库"""
    print_header("数据库检查")
    
    try:
        # 检查数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print_status("数据库连接", True)
        
        # 检查表是否存在
        from django.core.management.color import no_style
        from django.db import connection
        
        style = no_style()
        tables = connection.introspection.table_names()
        
        required_tables = [
            'accounts_user',
            'accounts_taskarea',
            'leave_management_leaveapplication',
            'reports_report',
            'location_locationrecord',
            'emergency_emergencyalert'
        ]
        
        tables_ok = True
        for table in required_tables:
            table_exists = table in tables
            print_status(f"表: {table}", table_exists)
            if not table_exists:
                tables_ok = False
        
        if not tables_ok:
            print("\n💡 提示: 如果表不存在，请运行以下命令:")
            print("   python manage.py makemigrations")
            print("   python manage.py migrate")
        
        return tables_ok
        
    except Exception as e:
        print_status("数据库检查", False, f"错误: {str(e)}")
        return False

def check_permissions():
    """检查用户权限配置"""
    print_header("权限配置检查")
    
    try:
        # 检查权限模块
        from accounts.permissions import role_required
        print_status("权限模块加载", True)
        
        # 检查角色定义
        from accounts.models import User
        roles_ok = hasattr(User, 'Role') and hasattr(User.Role, 'choices')
        print_status("角色定义", roles_ok)
        
        # 检查任务区模型
        from accounts.models import TaskArea
        task_area_ok = hasattr(TaskArea, 'objects')
        print_status("任务区模型", task_area_ok)
        
        return roles_ok and task_area_ok
        
    except Exception as e:
        print_status("权限配置检查", False, f"错误: {str(e)}")
        return False

def check_url_config():
    """检查URL配置"""
    print_header("URL配置检查")
    
    try:
        from django.urls import get_resolver
        resolver = get_resolver()
        
        # 检查主要URL模式
        url_patterns = [pattern.pattern.regex.pattern for pattern in resolver.url_patterns]
        
        required_patterns = [
            r'^admin/',
            r'^accounts/',
            r'^dashboard/',
            r'^leave/',
            r'^reports/',
            r'^location/',
            r'^emergency/',
            r'^usermanagement/'
        ]
        
        urls_ok = True
        for pattern in required_patterns:
            pattern_exists = any(pattern in p for p in url_patterns)
            print_status(f"URL模式: {pattern}", pattern_exists)
            if not pattern_exists:
                urls_ok = False
        
        return urls_ok
        
    except Exception as e:
        print_status("URL配置检查", False, f"错误: {str(e)}")
        return False

def check_fixed_issues():
    """检查v1.6.1.10修复的问题"""
    print_header("v1.6.1.10修复验证")
    
    try:
        issues_fixed = []
        
        # 检查快捷操作中的工作报告链接统一
        from django.template import engines
        from django.template.loader import get_template
        
        try:
            home_template = get_template('dashboard/home.html')
            template_content = home_template.template.source
            
            # 检查任务区负责人是否只显示工作报告按钮
            task_area_manager_section = template_content[
                template_content.find("user.role == 'task_area_manager'"):
                template_content.find("{% elif user.role == 'head_manager'", 
                template_content.find("user.role == 'task_area_manager'"))
            ]
            
            has_upload_button = 'reports:upload' in task_area_manager_section
            has_reports_button = 'reports:my_reports' in task_area_manager_section
            
            reports_button_only = has_reports_button and not has_upload_button
            
            print_status("任务区负责人快捷操作优化", reports_button_only,
                        "✅ 已删除上传报告按钮" if reports_button_only else "❌ 仍有重复按钮")
            
            issues_fixed.append(reports_button_only)
            
        except Exception as e:
            print_status("快捷操作检查", False, f"模板检查失败: {str(e)}")
            issues_fixed.append(False)
        
        # 检查reports视图中的任务区筛选权限
        try:
            from reports.views import my_reports
            
            # 检查函数是否存在且可调用
            function_exists = callable(my_reports)
            print_status("my_reports视图函数", function_exists)
            
            # 检查manage_reports视图中的任务区筛选权限优化
            from reports.views import manage_reports
            
            # 通过源代码检查是否修复了任务区筛选问题
            import inspect
            source = inspect.getsource(manage_reports)
            
            has_proper_filter_logic = "task_areas = []" in source and "任务区负责人不需要任务区筛选" in source
            
            print_status("任务区筛选权限优化", has_proper_filter_logic,
                        "✅ 任务区负责人不再显示筛选选项" if has_proper_filter_logic else "❌ 筛选逻辑未优化")
            
            issues_fixed.append(has_proper_filter_logic)
            
        except Exception as e:
            print_status("视图函数检查", False, f"函数检查失败: {str(e)}")
            issues_fixed.append(False)
        
        return all(issues_fixed)
        
    except Exception as e:
        print_status("修复验证检查", False, f"验证失败: {str(e)}")
        return False

def run_migrations():
    """运行数据库迁移"""
    print_header("数据库迁移")
    
    try:
        # 检查是否需要迁移
        result = subprocess.run([
            sys.executable, 'manage.py', 'makemigrations', '--dry-run'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and not result.stdout.strip():
            print_status("数据库迁移状态", True, "无需迁移")
            return True
        else:
            print_status("数据库迁移状态", False, "需要运行迁移")
            print("\n💡 解决步骤:")
            print("   python manage.py makemigrations")
            print("   python manage.py migrate")
            return False
            
    except Exception as e:
        print_status("迁移检查", False, f"检查失败: {str(e)}")
        return False

def create_test_user():
    """创建测试用户"""
    print_header("测试用户创建")
    
    try:
        from accounts.models import User, TaskArea
        
        # 检查是否已存在管理员用户
        admin_exists = User.objects.filter(is_superuser=True).exists()
        print_status("管理员用户", admin_exists, "已存在" if admin_exists else "请创建管理员用户")
        
        # 检查测试用户
        test_user_exists = User.objects.filter(username='test_manager').exists()
        print_status("测试用户", test_user_exists, "已存在" if test_user_exists else "可创建测试用户")
        
        return admin_exists
        
    except Exception as e:
        print_status("用户检查", False, f"检查失败: {str(e)}")
        return False

def main():
    """主检查函数"""
    print("🔍 员工管理系统 v1.6.1.10 部署验证")
    print("=" * 60)
    
    checks = [
        ("Python环境", check_python_version),
        ("依赖包", check_dependencies),
        ("文件结构", check_file_structure),
        ("Django配置", check_django_config),
        ("数据库", check_database),
        ("权限配置", check_permissions),
        ("URL配置", check_url_config),
        ("修复验证", check_fixed_issues),
        ("数据库迁移", run_migrations),
        ("测试用户", create_test_user)
    ]
    
    results = {}
    for check_name, check_func in checks:
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"\n❌ {check_name}检查失败: {str(e)}")
            results[check_name] = False
    
    # 总结
    print_header("验证总结")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} {check_name}")
    
    print(f"\n📊 验证结果: {passed}/{total} 项检查通过")
    
    if passed == total:
        print("\n🎉 系统验证通过！所有修复功能正常工作。")
        print("\n📋 后续步骤:")
        print("1. 运行数据库迁移 (如需要)")
        print("2. 创建管理员用户")
        print("3. 启动服务器: python manage.py runserver")
        print("4. 访问 http://127.0.0.1:8000/admin/ 进行管理")
        
        return True
    else:
        print(f"\n⚠️  发现 {total - passed} 个问题需要解决")
        print("\n🔧 建议解决方案:")
        print("1. 检查并安装缺失的依赖: pip install -r requirements.txt")
        print("2. 运行数据库迁移: python manage.py migrate")
        print("3. 检查文件完整性，确保所有文件已正确部署")
        print("4. 查看错误日志获取详细信息")
        
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
