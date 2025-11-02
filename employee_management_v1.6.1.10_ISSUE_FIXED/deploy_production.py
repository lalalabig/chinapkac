#!/usr/bin/env python3
"""
Railway.app deployment script for Employee Management System
Supports custom domain: www.chinapkac.com
"""

import os
import sys
import subprocess
import django
from django.core.management import execute_from_command_line

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'employee_management.settings_production')
django.setup()

def run_migrations():
    """Run database migrations"""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--noinput'])
        print("✅ Database migrations completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def collect_static():
    """Collect static files"""
    print("📁 Collecting static files...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Static files collected successfully!")
        return True
    except Exception as e:
        print(f"❌ Static collection failed: {e}")
        return False

def create_superuser():
    """Create initial superuser if not exists"""
    print("👤 Checking for superuser...")
    from django.contrib.auth.models import User
    
    # Try to create superuser only if it doesn't exist
    if not User.objects.filter(is_superuser=True).exists():
        print("Creating default superuser...")
        # We'll create this via environment variables or later
        print("⚠️  Please create superuser manually via Django admin or add environment variables")
    else:
        print("✅ Superuser already exists")

def create_sample_data():
    """Create sample data for testing"""
    print("📊 Creating sample data...")
    try:
        # Import and run fixture loading
        from accounts.models import User
        from location.models import TaskArea
        
        # Create sample users if they don't exist
        sample_users = [
            {'username': 'admin', 'email': 'admin@chinapkac.com', 'role': 'SUPERUSER'},
            {'username': 'manager', 'email': 'manager@chinapkac.com', 'role': 'HEAD_MANAGER'},
            {'username': 'taskmanager', 'email': 'taskmanager@chinapkac.com', 'role': 'TASK_AREA_MANAGER'},
            {'username': 'employee', 'email': 'employee@chinapkac.com', 'role': 'EMPLOYEE'},
        ]
        
        created_count = 0
        for user_data in sample_users:
            if not User.objects.filter(username=user_data['username']).exists():
                User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password='password123',
                    role=user_data['role']
                )
                created_count += 1
        
        print(f"✅ Created {created_count} sample users")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 Starting Employee Management System deployment...")
    print("🌐 Supporting custom domain: www.chinapkac.com")
    print("👥 Multi-user concurrent login: Enabled")
    print("=" * 60)
    
    # Run deployment steps
    success = True
    
    # Step 1: Run migrations
    if not run_migrations():
        success = False
    
    # Step 2: Collect static files
    if not collect_static():
        success = False
    
    # Step 3: Create sample data
    if not create_sample_data():
        success = False
    
    # Step 4: Check superuser
    create_superuser()
    
    print("=" * 60)
    if success:
        print("✅ Deployment completed successfully!")
        print("🌐 Your app is ready at: https://chinapkac.railway.app")
        print("👤 Admin access: https://chinapkac.railway.app/admin")
        print("📝 Sample login accounts:")
        print("   - admin / password123 (Superuser)")
        print("   - manager / password123 (Head Manager)")
        print("   - taskmanager / password123 (Task Area Manager)")
        print("   - employee / password123 (Employee)")
    else:
        print("❌ Deployment completed with errors")
        sys.exit(1)

if __name__ == '__main__':
    main()
