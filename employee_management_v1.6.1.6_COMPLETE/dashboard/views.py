"""
dashboard 视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from accounts.models import User
from leave_management.models import LeaveApplication, ApprovalRecord
from accounts.permissions import (
    get_user_permissions, 
    role_required, 
    ROLES,
    get_role_display_name
)


@login_required
def home(request):
    """
    仪表盘主页 - 根据用户角色显示不同内容
    """
    user = request.user
    user_permissions = get_user_permissions(user)
    
    # 根据用户权限获取相应的统计数据
    context = {
        'user': user,
        'permissions': user_permissions,
        'role_display': get_role_display_name(user.role),
        'current_time': timezone.now(),
    }
    
    # 根据角色添加不同的统计数据
    if user_permissions['can_view_reports']:
        # 任务区负责人及以上可以看到统计信息
        context.update(get_manager_dashboard_data(user))
    else:
        # 普通员工看到基础信息
        context.update(get_employee_dashboard_data(user))
    
    return render(request, 'dashboard/home.html', context)

def get_employee_dashboard_data(user):
    """获取普通员工仪表板数据"""
    return {
        'my_info': {
            'department': user.department_rank,
            'position': user.position,
            'task_area': user.task_area_fk.name if user.task_area_fk else user.task_area,
            'hire_date': user.employment_start_date,
        },
        'pending_tasks': 0,      # 待处理任务
        'completed_reports': 0,   # 已完成报告
        'notifications': [],      # 通知消息
        # 添加模板需要的基础统计数据（简化版）
        'total_users': 0,
        'active_users': 0,
        'user_stats': {
            'superuser': 0,
            'head_manager': 0,
            'task_area_manager': 0,
            'employee': 1,  # 至少显示自己
        },
        'recent_logins': [],
        'task_area_stats': [],
    }

def get_manager_dashboard_data(user):
    """获取管理员仪表板数据"""
    # 分公司负责人可以看到的数据
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # 请假统计
    if user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人：只统计本任务区的请假
        leave_base_query = LeaveApplication.objects.filter(applicant__task_area_fk=user.task_area_fk)
    elif user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人：统计管辖任务区的请假
        managed_areas = user.managed_task_areas.all()
        leave_base_query = LeaveApplication.objects.filter(applicant__task_area_fk__in=managed_areas)
    else:
        # 超级管理员：统计所有请假
        leave_base_query = LeaveApplication.objects.all()
    
    # 统计数据
    total_applications = leave_base_query.count()
    pending_applications = leave_base_query.filter(
        status__in=[
            LeaveApplication.Status.PENDING_TASK_AREA,
            LeaveApplication.Status.PENDING_HEAD
        ]
    ).count()
    approved_applications = leave_base_query.filter(
        status=LeaveApplication.Status.APPROVED
    ).count()
    rejected_applications = leave_base_query.filter(
        status=LeaveApplication.Status.REJECTED
    ).count()
    
    return {
        'team_overview': {
            'total_members': User.objects.filter(role=ROLES['EMPLOYEE']).count(),
            'active_members': User.objects.filter(role=ROLES['EMPLOYEE'], is_active=True).count(),
        },
        'leave_statistics': {
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'approved_applications': approved_applications,
            'rejected_applications': rejected_applications,
        },
        'pending_approvals': pending_applications,   # 待审批请假
        'recent_reports': [],     # 最近报告
        'team_locations': [],     # 团队位置信息
        # 添加模板需要的基础统计数据
        'total_users': total_users,
        'active_users': active_users,
        'user_stats': {
            'superuser': User.objects.filter(role=ROLES['SUPERUSER']).count(),
            'head_manager': User.objects.filter(role=ROLES['HEAD_MANAGER']).count(),
            'task_area_manager': User.objects.filter(role=ROLES['TASK_AREA_MANAGER']).count(),
            'employee': User.objects.filter(role=ROLES['EMPLOYEE']).count(),
        },
        'recent_logins': User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:5],
        'task_area_stats': User.objects.select_related('task_area_fk').values('task_area_fk__name').annotate(
            count=Count('id')
        ).exclude(task_area_fk__isnull=True).order_by('-count')[:5],
    }

def get_admin_dashboard_data(user):
    """获取高级管理员仪表板数据"""
    # 基本统计数据
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    # 按角色统计用户
    user_stats = {
        'superuser': User.objects.filter(role=ROLES['SUPERUSER']).count(),
        'head_manager': User.objects.filter(role=ROLES['HEAD_MANAGER']).count(),
        'task_area_manager': User.objects.filter(role=ROLES['TASK_AREA_MANAGER']).count(),
        'employee': User.objects.filter(role=ROLES['EMPLOYEE']).count(),
    }
    
    # 请假统计数据 - 管理员查看所有
    total_applications = LeaveApplication.objects.count()
    pending_applications = LeaveApplication.objects.filter(
        status__in=[
            LeaveApplication.Status.PENDING_TASK_AREA,
            LeaveApplication.Status.PENDING_HEAD
        ]
    ).count()
    approved_applications = LeaveApplication.objects.filter(
        status=LeaveApplication.Status.APPROVED
    ).count()
    rejected_applications = LeaveApplication.objects.filter(
        status=LeaveApplication.Status.REJECTED
    ).count()
    
    # 最近登录的用户
    recent_logins = User.objects.filter(
        last_login__isnull=False
    ).order_by('-last_login')[:5]
    
    # 任务区分布
    task_area_stats = User.objects.select_related('task_area_fk').values('task_area_fk__name').annotate(
        count=Count('id')
    ).exclude(task_area_fk__isnull=True).order_by('-count')[:5]
    
    return {
        'total_users': total_users,
        'active_users': active_users,
        'user_stats': user_stats,
        'leave_statistics': {
            'total_applications': total_applications,
            'pending_applications': pending_applications,
            'approved_applications': approved_applications,
            'rejected_applications': rejected_applications,
        },
        'recent_logins': recent_logins,
        'task_area_stats': task_area_stats,
        'system_status': 'normal',  # 系统状态
    }


@login_required
@role_required([ROLES['HEAD_MANAGER'], ROLES['SUPERUSER']])
def user_management(request):
    """
    用户管理页面（仅总部负责人和超级管理员可访问）
    """
    user_permissions = get_user_permissions(request.user)
    
    # 根据用户权限获取可访问的用户
    from accounts.permissions import filter_users_by_task_area_permission
    users = User.objects.all().order_by('-date_joined')
    users = filter_users_by_task_area_permission(users, request.user)
    
    # 根据用户权限限制可见用户范围
    if request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人不能管理超级管理员
        users = users.exclude(role=ROLES['SUPERUSER'])
    elif request.user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人不能管理超级管理员和总部负责人
        users = users.exclude(role__in=[ROLES['SUPERUSER'], ROLES['HEAD_MANAGER']])
    
    # 搜索功能
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(department_rank__icontains=search) |
            Q(task_area_fk__name__icontains=search)
        )
    
    # 角色筛选
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    # 根据当前用户权限过滤角色选择
    available_roles = User.Role.choices
    if request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人不能创建超级管理员
        available_roles = [choice for choice in User.Role.choices if choice[0] != ROLES['SUPERUSER']]
    elif request.user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人只能创建普通员工
        available_roles = [choice for choice in User.Role.choices if choice[0] == ROLES['EMPLOYEE']]
    
    # 获取任务区信息 - 只显示有实际用户的任务区
    from accounts.models import TaskArea
    # 获取有用户分配的任务区（普通员工和任务区负责人）
    task_areas_with_users = TaskArea.objects.filter(
        Q(users__role=ROLES['EMPLOYEE']) | 
        Q(users__role=ROLES['TASK_AREA_MANAGER'])
    ).distinct()
    
    if request.user.role == ROLES['SUPERUSER']:
        task_areas = task_areas_with_users
    elif request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人只能看到自己管辖的且有用户的任务区
        task_areas = request.user.managed_task_areas.filter(
            Q(users__role=ROLES['EMPLOYEE']) | 
            Q(users__role=ROLES['TASK_AREA_MANAGER'])
        ).distinct()
    elif request.user.role == ROLES['TASK_AREA_MANAGER']:
        if request.user.task_area_fk:
            task_areas = TaskArea.objects.filter(id=request.user.task_area_fk.id)
        else:
            task_areas = TaskArea.objects.none()
    
    context = {
        'users': users,
        'search': search,
        'role_filter': role_filter,
        'role_choices': available_roles,
        'permissions': user_permissions,
        'can_edit_users': user_permissions['can_manage_employees'],
        'is_superuser': request.user.role == ROLES['SUPERUSER'],
        'task_areas': task_areas,
        'task_areas_count': task_areas.count(),
    }
    
    return render(request, 'dashboard/user_management.html', context)


@login_required
@role_required([ROLES['SUPERUSER'], ROLES['HEAD_MANAGER'], ROLES['TASK_AREA_MANAGER']])
def create_user(request):
    """
    创建新用户（超级管理员、总部负责人、任务区负责人）
    """
    from accounts.forms import CustomUserCreationForm
    from accounts.models import TaskArea
    
    if request.method == 'POST':
        # 处理任务区分配
        role = request.POST.get('role')
        new_user_data = request.POST.copy()
        
        # 根据角色处理任务区
        if role == 'superuser':
            # 超级管理员：创建或获取"全球"任务区
            global_area, created = TaskArea.objects.get_or_create(
                name='全球',
                defaults={'description': '超级管理员默认管辖区域'}
            )
            new_user_data['task_area_fk'] = global_area.id
            
        elif role == 'head_manager':
            # 总部负责人：处理多个管辖任务区，不设置单一task_area_fk
            managed_areas = request.POST.getlist('managed_task_areas[]')
            if not managed_areas or not any(area.strip() for area in managed_areas):
                messages.error(request, '总部负责人必须至少管辖一个任务区')
                return render(request, 'dashboard/user_form.html', get_form_context(request, 'create'))
            
            # 确保不设置task_area_fk，总部负责人通过managed_task_areas管理
            new_user_data['task_area_fk'] = None
            
        else:
            # 任务区负责人和普通员工
            task_area_value = request.POST.get('task_area_fk')
            
            if task_area_value and task_area_value.startswith('new_'):
                # 创建新任务区
                new_area_name = task_area_value[4:]  # 去掉 'new_' 前缀
                if new_area_name:
                    task_area_obj, created = TaskArea.objects.get_or_create(
                        name=new_area_name,
                        defaults={'description': f'用户创建的任务区：{new_area_name}'}
                    )
                    new_user_data['task_area_fk'] = task_area_obj.id
            elif task_area_value and task_area_value != '__new__':
                # 选择现有任务区
                try:
                    TaskArea.objects.get(id=task_area_value)
                    new_user_data['task_area_fk'] = task_area_value
                except TaskArea.DoesNotExist:
                    messages.error(request, '选择的任务区不存在')
                    return render(request, 'dashboard/user_form.html', get_form_context(request, 'create'))
            else:
                messages.error(request, '请选择或创建任务区')
                return render(request, 'dashboard/user_form.html', get_form_context(request, 'create'))
        
        # 创建用户
        form = CustomUserCreationForm(new_user_data)
        if form.is_valid():
            try:
                user = form.save()
                
                # 处理总部负责人的管辖任务区
                if role == 'head_manager':
                    managed_areas = request.POST.getlist('managed_task_areas[]')
                    for area_name in managed_areas:
                        area_name = area_name.strip()
                        if area_name:
                            task_area_obj, created = TaskArea.objects.get_or_create(
                                name=area_name,
                                defaults={'description': f'总部负责人管辖的任务区：{area_name}'}
                            )
                            user.managed_task_areas.add(task_area_obj)
                
                messages.success(request, f'用户 {user.username} 创建成功！角色：{user.get_role_display()}')
                return redirect('dashboard:user_management')
            except Exception as e:
                messages.error(request, f'用户创建失败：{str(e)}')
        else:
            # 显示具体的验证错误信息
            error_messages = []
            for field, errors in form.errors.items():
                field_name = form.fields.get(field)
                if field_name and hasattr(field_name, 'label') and field_name.label:
                    field_label = field_name.label
                else:
                    # 字段名称映射
                    field_mappings = {
                        'username': '用户名',
                        'email': '邮箱',
                        'password1': '密码',
                        'password2': '确认密码',
                        'role': '角色',
                        'passport_number': '护照号码',
                        'task_area_fk': '任务区',
                    }
                    field_label = field_mappings.get(field, field)
                
                for error in errors:
                    error_messages.append(f"{field_label}: {error}")
            
            if error_messages:
                messages.error(request, f"创建用户失败，请修正以下问题：{'; '.join(error_messages[:3])}")  # 只显示前3个错误
            else:
                messages.error(request, '请检查表单信息是否正确填写')
    
    return render(request, 'dashboard/user_form.html', get_form_context(request, 'create'))

def is_valid_task_area_name(name):
    """
    验证任务区名称是否有效
    返回 True 如果有效，否则返回 False
    """
    if not name or not name.strip():
        return False
    
    # 定义无效关键词列表（与 cleanup_invalid_task_areas.py 保持一致）
    invalid_keywords = [
        '等级', '员工等', '权限', '禁止', '系统',
        '护照', '信息', '密码', '邮箱', '电话',
        '部门', '职位', '姓名', '拼音', '号码',
        '日期', '时间', '开始', '结束', '签发', '到期',
        '测试', '等待', '确认', '未分类', '头等',
        '无等级', '成功职', '阿卡部', '管理层',
        '_new_', '__new__', 'new_', '未分级'
    ]
    
    # 检查是否包含无效关键词
    for keyword in invalid_keywords:
        if keyword in name:
            return False
    
    # 检查是否包含特殊字符
    if any(c in name for c in ['<', '>', '{', '}', '[', ']', '|', '\\']):
        return False
    
    return True


def get_form_context(request, action, target_user=None):
    """获取表单上下文数据"""
    from accounts.models import TaskArea
    
    # 根据用户权限过滤角色选择
    available_roles = User.Role.choices
    if request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人不能创建超级管理员
        available_roles = [choice for choice in User.Role.choices if choice[0] != ROLES['SUPERUSER']]
    elif request.user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人只能创建普通员工
        available_roles = [choice for choice in User.Role.choices if choice[0] == ROLES['EMPLOYEE']]
    
    # 获取现有的任务区选项供下拉选择（只显示有效的任务区）
    existing_task_areas = []
    if request.user.role == ROLES['SUPERUSER']:
        # 超级管理员可以看到所有有效任务区
        all_areas = TaskArea.objects.all().order_by('name')
        existing_task_areas = [area for area in all_areas if is_valid_task_area_name(area.name)]
    elif request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人可以看到自己管辖的有效任务区
        all_areas = request.user.managed_task_areas.all().order_by('name')
        existing_task_areas = [area for area in all_areas if is_valid_task_area_name(area.name)]
    elif request.user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人只能看到自己的任务区
        if request.user.task_area_fk:
            all_areas = TaskArea.objects.filter(id=request.user.task_area_fk.id)
            existing_task_areas = [area for area in all_areas if is_valid_task_area_name(area.name)]
        else:
            existing_task_areas = []
    
    context = {
        'role_choices': available_roles,
        'action': action,
        'current_user_role': request.user.role,
        'existing_task_areas': existing_task_areas,  # 添加现有任务区选项
    }
    
    if target_user:
        context['target_user'] = target_user
    
    return context


@login_required  
@role_required([ROLES['SUPERUSER'], ROLES['HEAD_MANAGER'], ROLES['TASK_AREA_MANAGER']])
def edit_user(request, user_id):
    """
    编辑用户（超级管理员、总部负责人、任务区负责人）
    """
    from accounts.models import TaskArea
    
    target_user = get_object_or_404(User, id=user_id)
    
    # 检查当前用户是否有权限编辑目标用户
    if not request.user.can_manage_user(target_user):
        messages.error(request, '您没有权限编辑此用户')
        return redirect('dashboard:user_management')
    
    if request.method == 'POST':
        # 更新基本信息
        target_user.username = request.POST.get('username', target_user.username)
        target_user.email = request.POST.get('email', target_user.email)
        target_user.first_name = request.POST.get('first_name', target_user.first_name)
        target_user.last_name = request.POST.get('last_name', target_user.last_name)
        target_user.phone_number = request.POST.get('phone_number', target_user.phone_number)
        target_user.department_rank = request.POST.get('department_rank', target_user.department_rank)
        target_user.position = request.POST.get('position', target_user.position)
        target_user.is_active = bool(request.POST.get('is_active'))
        
        # 护照信息
        target_user.passport_name_pinyin = request.POST.get('passport_name_pinyin', target_user.passport_name_pinyin)
        target_user.passport_number = request.POST.get('passport_number', target_user.passport_number)
        
        # 处理日期字段
        passport_issue_date = request.POST.get('passport_issue_date')
        if passport_issue_date:
            target_user.passport_issue_date = passport_issue_date
            
        passport_expiry_date = request.POST.get('passport_expiry_date')
        if passport_expiry_date:
            target_user.passport_expiry_date = passport_expiry_date
            
        employment_start_date = request.POST.get('employment_start_date')
        if employment_start_date:
            target_user.employment_start_date = employment_start_date
            
        employment_end_date = request.POST.get('employment_end_date')
        if employment_end_date:
            target_user.employment_end_date = employment_end_date
        
        # 处理角色和任务区
        new_role = request.POST.get('role', target_user.role)
        old_role = target_user.role
        target_user.role = new_role
        
        # 根据新角色设置任务区
        if new_role == 'superuser':
            # 超级管理员：清除所有关联，设置为全球
            target_user.managed_task_areas.clear()
            global_area, created = TaskArea.objects.get_or_create(
                name='全球',
                defaults={'description': '超级管理员默认管辖区域'}
            )
            target_user.task_area_fk = global_area
            
        elif new_role == 'head_manager':
            # 总部负责人：处理多个管辖任务区，不设置单一task_area_fk
            target_user.task_area_fk = None  # 确保总部负责人没有单一任务区
            # 重要：先清除旧的管辖任务区，避免累加
            target_user.managed_task_areas.clear()
            
            managed_areas = request.POST.getlist('managed_task_areas[]')
            if managed_areas and any(area.strip() for area in managed_areas):
                for area_name in managed_areas:
                    area_name = area_name.strip()
                    if area_name:
                        task_area_obj, created = TaskArea.objects.get_or_create(
                            name=area_name,
                            defaults={'description': f'总部负责人管辖的任务区：{area_name}'}
                        )
                        target_user.managed_task_areas.add(task_area_obj)
            else:
                messages.error(request, '总部负责人必须至少管辖一个任务区')
                return render(request, 'dashboard/user_form.html', get_form_context(request, 'edit', target_user))
                
        else:
            # 任务区负责人和普通员工：清除管辖任务区，只设置单一任务区
            target_user.managed_task_areas.clear()
            task_area_value = request.POST.get('task_area_fk')
            
            if task_area_value and task_area_value.startswith('new_'):
                # 创建新任务区
                new_area_name = task_area_value[4:]  # 去掉 'new_' 前缀
                if new_area_name:
                    task_area_obj, created = TaskArea.objects.get_or_create(
                        name=new_area_name,
                        defaults={'description': f'用户创建的任务区：{new_area_name}'}
                    )
                    target_user.task_area_fk = task_area_obj
            elif task_area_value and task_area_value != '__new__':
                # 选择现有任务区
                try:
                    task_area_obj = TaskArea.objects.get(id=task_area_value)
                    target_user.task_area_fk = task_area_obj
                except TaskArea.DoesNotExist:
                    messages.error(request, '选择的任务区不存在')
                    return render(request, 'dashboard/user_form.html', get_form_context(request, 'edit', target_user))
            else:
                messages.error(request, '请选择或创建任务区')
                return render(request, 'dashboard/user_form.html', get_form_context(request, 'edit', target_user))
        
        target_user.save()
        messages.success(request, f'用户 {target_user.username} 信息更新成功')
        return redirect('dashboard:user_management')
    
    return render(request, 'dashboard/user_form.html', get_form_context(request, 'edit', target_user))


@login_required
@role_required([ROLES['SUPERUSER']])
def delete_user(request, user_id):
    """
    删除用户（仅超级管理员）
    """
    target_user = get_object_or_404(User, id=user_id)
    
    # 不能删除自己
    if target_user.id == request.user.id:
        messages.error(request, '不能删除自己的账户')
        return redirect('dashboard:user_management')
    
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'用户 {username} 已被删除')
        return redirect('dashboard:user_management')
    
    context = {
        'target_user': target_user
    }
    
    return render(request, 'dashboard/delete_user_confirm.html', context)



@login_required
@role_required([ROLES['TASK_AREA_MANAGER'], ROLES['HEAD_MANAGER'], ROLES['SUPERUSER']])
def team_management(request):
    """
    员工列表页面（任务区负责人及以上可访问）
    增强功能：搜索、筛选、自定义排序
    """
    from pypinyin import lazy_pinyin
    from accounts.models import TaskArea
    
    user_permissions = get_user_permissions(request.user)
    
    # 根据用户权限获取可管理的用户
    if request.user.role == ROLES['TASK_AREA_MANAGER']:
        # 任务区负责人只能管理同任务区的普通员工
        if request.user.task_area_fk:
            team_members = User.objects.filter(
                role=ROLES['EMPLOYEE'],
                task_area_fk=request.user.task_area_fk
            )
        else:
            team_members = User.objects.none()
    elif request.user.role == ROLES['HEAD_MANAGER']:
        # 总部负责人可以管理其管辖任务区内的用户
        managed_areas = request.user.managed_task_areas.all()
        if managed_areas.exists():
            team_members = User.objects.filter(
                Q(task_area_fk__in=managed_areas) | 
                Q(role=ROLES['TASK_AREA_MANAGER'], task_area_fk__in=managed_areas)
            )
        else:
            team_members = User.objects.none()
    else:
        # 超级管理员可以管理所有下级
        team_members = User.objects.exclude(role=ROLES['SUPERUSER'])
    
    # 搜索功能
    search = request.GET.get('search', '').strip()
    if search:
        team_members = team_members.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(department_rank__icontains=search) |
            Q(position__icontains=search)
        )
    
    # 任务区筛选
    task_area_filter = request.GET.get('task_area', '').strip()
    if task_area_filter:
        try:
            task_area_filter_id = int(task_area_filter)
            team_members = team_members.filter(task_area_fk_id=task_area_filter_id)
        except (ValueError, TypeError):
            pass
    
    # 角色筛选
    role_filter = request.GET.get('role', '').strip()
    if role_filter:
        team_members = team_members.filter(role=role_filter)
    
    # 获取所有数据到列表中进行 Python 级别排序
    team_members_list = list(team_members.select_related('task_area_fk'))
    
    # 根据用户角色进行自定义排序
    def get_sort_key(user_obj):
        """\u751f\u6210\u6392\u5e8f\u952e"""
        # 获取任务区名称的拼音
        task_area_name = user_obj.task_area_fk.name if user_obj.task_area_fk else "\u672a\u8bbe\u7f6e"
        task_area_pinyin = ''.join(lazy_pinyin(task_area_name))
        
        # 获取用户姓氏的拼音
        last_name = user_obj.last_name or user_obj.username[0] if user_obj.username else "z"
        last_name_pinyin = ''.join(lazy_pinyin(last_name))
        
        if request.user.role == ROLES['SUPERUSER']:
            # 超级管理员：
            # 1. 总部负责人最前（role=3）
            # 2. 任务区按拼音排序
            # 3. 同一任务区：任务区负责人在前（role=2），普通员工在后（role=1）
            # 4. 同角色内按姓氏拼音排序
            if user_obj.role == ROLES['HEAD_MANAGER']:
                return (0, '', 0, last_name_pinyin)  # 总部负责人最前
            elif user_obj.role == ROLES['TASK_AREA_MANAGER']:
                return (1, task_area_pinyin, 0, last_name_pinyin)  # 任务区负责人
            else:  # EMPLOYEE
                return (1, task_area_pinyin, 1, last_name_pinyin)  # 普通员工
                
        elif request.user.role == ROLES['HEAD_MANAGER']:
            # 总部负责人：
            # 1. 任务区按拼音排序
            # 2. 同一任务区：任务区负责人在前，普通员工在后
            # 3. 同角色内按姓氏拼音排序
            if user_obj.role == ROLES['TASK_AREA_MANAGER']:
                return (task_area_pinyin, 0, last_name_pinyin)
            else:  # EMPLOYEE
                return (task_area_pinyin, 1, last_name_pinyin)
                
        else:  # TASK_AREA_MANAGER
            # 任务区负责人：
            # 普通员工按姓氏拼音排序
            return (last_name_pinyin,)
    
    team_members_list.sort(key=get_sort_key)
    
    # 获取筛选选项
    if request.user.role == ROLES['SUPERUSER']:
        available_task_areas = TaskArea.objects.filter(
            Q(users__isnull=False) | Q(managers__isnull=False)
        ).distinct().order_by('name')
        available_roles = [
            (ROLES['HEAD_MANAGER'], '总部负责人'),
            (ROLES['TASK_AREA_MANAGER'], '任务区负责人'),
            (ROLES['EMPLOYEE'], '普通员工'),
        ]
    elif request.user.role == ROLES['HEAD_MANAGER']:
        managed_areas = request.user.managed_task_areas.all()
        available_task_areas = managed_areas.order_by('name')
        available_roles = [
            (ROLES['TASK_AREA_MANAGER'], '任务区负责人'),
            (ROLES['EMPLOYEE'], '普通员工'),
        ]
    else:  # TASK_AREA_MANAGER
        if request.user.task_area_fk:
            available_task_areas = TaskArea.objects.filter(id=request.user.task_area_fk.id)
        else:
            available_task_areas = TaskArea.objects.none()
        available_roles = [(ROLES['EMPLOYEE'], '普通员工')]
    
    context = {
        'team_members': team_members_list,
        'permissions': user_permissions,
        'user_role': get_role_display_name(request.user.role),
        'search': search,
        'task_area_filter': task_area_filter,
        'role_filter': role_filter,
        'available_task_areas': available_task_areas,
        'available_roles': available_roles,
    }
    
    return render(request, 'dashboard/team_management.html', context)


@login_required
def profile(request):
    """
    个人资料页面（所有用户可访问）
    """
    user_permissions = get_user_permissions(request.user)
    
    context = {
        'user': request.user,
        'permissions': user_permissions,
        'role_display': get_role_display_name(request.user.role),
    }
    
    return render(request, 'dashboard/profile.html', context)


@login_required
@role_required([ROLES['HEAD_MANAGER'], ROLES['SUPERUSER']])
def system_settings(request):
    """
    系统设置页面（仅总部负责人和超级管理员可访问）
    """
    user_permissions = get_user_permissions(request.user)
    
    # 系统配置信息
    system_info = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'system_version': '1.0.0',
        'last_backup': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    context = {
        'permissions': user_permissions,
        'system_info': system_info,
        'can_manage_system': user_permissions['can_manage_system'],
    }
    
    return render(request, 'dashboard/system_settings.html', context)


@login_required
def access_denied(request):
    """
    权限不足页面
    """
    return render(request, 'dashboard/access_denied.html', {
        'user': request.user,
        'role_display': get_role_display_name(request.user.role),
    })
