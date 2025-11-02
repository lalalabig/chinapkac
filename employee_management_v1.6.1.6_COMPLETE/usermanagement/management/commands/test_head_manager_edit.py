"""
Django管理命令：测试总部负责人编辑功能
"""
from django.core.management.base import BaseCommand
from django.test import Client
from django.urls import reverse
from accounts.models import User, TaskArea

class Command(BaseCommand):
    help = '测试总部负责人编辑功能'
    
    def handle(self, *args, **options):
        print("=== 测试总部负责人编辑功能 ===")
        
        # 创建测试用户（超级管理员）
        print("1. 创建测试超级管理员...")
        admin_user, created = User.objects.get_or_create(
            username='test_admin',
            defaults={
                'email': 'admin@test.com',
                'role': User.Role.SUPERUSER
            }
        )
        if created:
            admin_user.set_password('testpass123')
            admin_user.save()
        
        # 创建测试任务区
        print("2. 创建测试任务区...")
        area1, _ = TaskArea.objects.get_or_create(name='北京测试', defaults={'description': '北京任务区'})
        area2, _ = TaskArea.objects.get_or_create(name='上海测试', defaults={'description': '上海任务区'})
        area3, _ = TaskArea.objects.get_or_create(name='全球测试', defaults={'description': '全球任务区'})
        
        # 创建总部负责人
        print("3. 创建总部负责人...")
        head_manager, created = User.objects.get_or_create(
            username='test_head_manager',
            defaults={
                'email': 'head@test.com',
                'role': User.Role.HEAD_MANAGER,
                'first_name': '张',
                'last_name': '总部',
                'task_area_fk': area3
            }
        )
        if created:
            head_manager.set_password('testpass123')
            head_manager.save()
        
        # 分配初始管辖任务区
        head_manager.managed_task_areas.clear()
        head_manager.managed_task_areas.add(area1, area3)
        initial_areas = list(head_manager.managed_task_areas.values_list('name', flat=True))
        print(f"   初始管辖任务区: {initial_areas}")
        
        # 创建客户端并登录
        print("4. 测试编辑功能...")
        client = Client()
        login_success = client.login(username='test_admin', password='testpass123')
        print(f"   登录状态: {login_success}")
        
        if login_success:
            # 模拟编辑请求：改为只管辖"上海测试"和"全球测试"
            edit_data = {
                'username': 'test_head_manager',
                'email': 'head@test.com',
                'first_name': '张',
                'last_name': '总部',
                'role': User.Role.HEAD_MANAGER,
                'managed_task_areas[]': ['上海测试', '全球测试']  # 新的管辖任务区
            }
            
            edit_url = reverse('usermanagement:user_edit', args=[head_manager.id])
            response = client.post(edit_url, edit_data)
            
            print(f"   响应状态码: {response.status_code}")
            if response.status_code == 302:
                print("   编辑请求成功提交")
            elif response.status_code == 200:
                print("   编辑页面正常显示")
                # 检查是否有错误信息
                content = response.content.decode()
                if 'error' in content.lower() or 'alert-danger' in content:
                    print("   可能存在验证错误")
                    
            # 刷新数据并检查结果
            head_manager.refresh_from_db()
            current_areas = list(head_manager.managed_task_areas.values_list('name', flat=True))
            print(f"   编辑后管辖任务区: {current_areas}")
            
            # 验证结果
            expected_areas = ['上海测试', '全球测试']
            if set(current_areas) == set(expected_areas):
                print("✅ 编辑功能正常工作！")
            else:
                print("❌ 编辑功能存在问题！")
                print(f"   期望: {expected_areas}")
                print(f"   实际: {current_areas}")
        else:
            print("❌ 登录失败，无法测试编辑功能")
        
        # 清理测试数据
        print("5. 清理测试数据...")
        User.objects.filter(username__startswith='test_').delete()
        TaskArea.objects.filter(name__endswith='测试').delete()
        
        print("=== 测试完成 ===")