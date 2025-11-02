"""
用户管理视图（超级管理员专用）
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from accounts.models import User, TaskArea
from .forms import UserCreateForm, UserEditForm


def is_valid_task_area_name(name):
    """
    验证任务区名称是否合法
    """
    if not name or not name.strip():
        return False, "任务区名称不能为空"
    
    name = name.strip()
    
    # 长度检查
    if len(name) < 2:
        return False, "任务区名称至少2个字符"
    if len(name) > 30:
        return False, "任务区名称不能超过30个字符"
    
    # 无效的关键词列表（这些通常是其他表单字段的内容）
    invalid_keywords = [
        '等级', '员工等', '权限', '禁止', '系统',
        '护照', '信息', '密码', '邮箱', '电话',
        '部门', '职位', '姓名', '拼音', '号码',
        '日期', '时间', '开始', '结束', '签发', '到期'
    ]
    
    # 检查是否包含无效关键词
    for keyword in invalid_keywords:
        if keyword in name:
            return False, f"任务区名称不能包含'{keyword}'等描述性词汇"
    
    return True, None


@login_required
def user_list(request):
    """用户列表"""
    # 检查用户权限：超级管理员、总部负责人、任务区负责人可以访问
    if not (request.user.is_superuser_role or request.user.is_head_manager or request.user.is_task_area_manager):
        messages.error(request, '您没有权限访问此页面。')
        return redirect('dashboard:dashboard')
    
    # 根据用户角色获取可管理的用户列表
    if request.user.is_superuser_role:
        # 超级管理员可以看到所有用户
        users = User.objects.all()
    elif request.user.is_head_manager:
        # 总部负责人只能看到其管辖任务区内的用户
        managed_task_areas = request.user.managed_task_areas.all()
        users = User.objects.filter(task_area_fk__in=managed_task_areas)
    elif request.user.is_task_area_manager:
        # 任务区负责人只能看到同任务区的普通员工和自己
        if request.user.task_area_fk:
            users = User.objects.filter(
                Q(task_area_fk=request.user.task_area_fk, role=User.Role.EMPLOYEE) |
                Q(id=request.user.id)
            )
        else:
            users = User.objects.filter(id=request.user.id)
    else:
        users = User.objects.none()
    
    users = users.order_by('-created_at')
    
    # 搜索功能
    query = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    company_filter = request.GET.get('company', '')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    if company_filter:
        users = users.filter(task_area_fk__name__icontains=company_filter)
    
    # 分页
    paginator = Paginator(users, 20)  # 每页20个用户
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 获取所有公司名称用于筛选
    task_areas = User.objects.exclude(
        Q(task_area_fk__isnull=True) | Q(task_area_fk__name='')
    ).values_list('task_area_fk__name', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'role_filter': role_filter,
        'company_filter': company_filter,
        'role_choices': User.Role.choices,
        'task_areas': task_areas,
        'total_users': users.count()
    }
    
    return render(request, 'usermanagement/user_list.html', context)


def _get_user_form_context(request):
    """获取用户表单的通用上下文数据"""
    from accounts.models import TaskArea
    
    return {
        'role_choices': User.Role.choices,
        'existing_task_areas': TaskArea.objects.all().order_by('name'),
    }


@login_required
def user_create(request):
    """创建用户"""
    # 只有超级管理员和总部负责人可以创建用户
    if not (request.user.is_superuser_role or request.user.is_head_manager):
        messages.error(request, '您没有权限创建用户。')
        return redirect('usermanagement:user_list')
    
    if request.method == 'POST':
        # 不使用标准Django Form，直接处理POST数据
        try:
            # 基本字段验证
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            role = request.POST.get('role', '')
            
            # 验证必填字段
            if not all([username, email, password, role]):
                context = _get_user_form_context(request)
                context['action'] = 'create'
                messages.error(request, '请填写所有必填字段。')
                return render(request, 'dashboard/user_form.html', context)
            
            # 检查用户名和邮箱唯一性
            if User.objects.filter(username=username).exists():
                context = _get_user_form_context(request)
                context['action'] = 'create'
                messages.error(request, '用户名已存在，请选择其他用户名。')
                return render(request, 'dashboard/user_form.html', context)
                
            if User.objects.filter(email=email).exists():
                context = _get_user_form_context(request)
                context['action'] = 'create'
                messages.error(request, '该邮箱已被使用，请使用其他邮箱。')
                return render(request, 'dashboard/user_form.html', context)
            
            # 密码验证
            if len(password) < 6:
                context = _get_user_form_context(request)
                context['action'] = 'create'
                messages.error(request, '密码长度至少6位。')
                return render(request, 'dashboard/user_form.html', context)
            
            # 创建用户对象
            user = User(
                username=username,
                email=email,
                first_name=request.POST.get('first_name', '').strip(),
                last_name=request.POST.get('last_name', '').strip(),
                role=role,
                phone_number=request.POST.get('phone_number', '').strip(),
                department_rank=request.POST.get('department_rank', '').strip(),
                position=request.POST.get('position', '').strip(),
                passport_name_pinyin=request.POST.get('passport_name_pinyin', '').strip(),
                passport_number=request.POST.get('passport_number', '').strip() or None,
            )
            
            # 处理日期字段
            for date_field in ['passport_issue_date', 'passport_expiry_date', 'employment_start_date', 'employment_end_date']:
                date_value = request.POST.get(date_field, '').strip()
                if date_value:
                    setattr(user, date_field, date_value)
            
            # 设置密码
            user.password = make_password(password)
            
            # 处理任务区分配逻辑
            task_area_obj = None
            
            if role == User.Role.SUPERUSER:
                # 超级管理员：自动分配或创建"全球"任务区
                global_area, created = TaskArea.objects.get_or_create(
                    name='全球',
                    defaults={'description': '超级管理员全球任务区'}
                )
                task_area_obj = global_area
                
            elif role in [User.Role.TASK_AREA_MANAGER, User.Role.EMPLOYEE]:
                # 任务区负责人和普通员工：需要单一任务区
                task_area_id = request.POST.get('task_area_fk', '').strip()
                new_task_area_name = request.POST.get('new_task_area', '').strip()
                
                if new_task_area_name:
                    # 验证任务区名称
                    is_valid, error_msg = is_valid_task_area_name(new_task_area_name)
                    if not is_valid:
                        context = _get_user_form_context(request)
                        context['action'] = 'create'
                        messages.error(request, f'无效的任务区名称：{error_msg}')
                        return render(request, 'dashboard/user_form.html', context)
                    
                    # 创建新任务区
                    if TaskArea.objects.filter(name=new_task_area_name).exists():
                        context = _get_user_form_context(request)
                        context['action'] = 'create'
                        messages.error(request, f'任务区"{new_task_area_name}"已存在。')
                        return render(request, 'dashboard/user_form.html', context)
                    
                    task_area_obj = TaskArea.objects.create(
                        name=new_task_area_name,
                        description=f'任务区: {new_task_area_name}'
                    )
                elif task_area_id and task_area_id != '__new__':
                    # 选择现有任务区
                    try:
                        task_area_obj = TaskArea.objects.get(id=task_area_id)
                    except TaskArea.DoesNotExist:
                        context = _get_user_form_context(request)
                        context['action'] = 'create'
                        messages.error(request, '选择的任务区不存在。')
                        return render(request, 'dashboard/user_form.html', context)
                else:
                    context = _get_user_form_context(request)
                    context['action'] = 'create'
                    messages.error(request, '任务区负责人和普通员工必须分配任务区。')
                    return render(request, 'dashboard/user_form.html', context)
                    
            elif role == User.Role.HEAD_MANAGER:
                # 总部负责人：不设置主要任务区，只管理多个任务区
                task_area_obj = None  # 总部负责人不需要主要任务区
            
            # 设置任务区
            user.task_area_fk = task_area_obj
            # 同时设置旧的 task_area CharField 以保持数据一致性
            if task_area_obj:
                user.task_area = task_area_obj.name
            else:
                user.task_area = ''
            
            # 保存用户
            user.save()
            
            # 处理总部负责人的多任务区管理
            if role == User.Role.HEAD_MANAGER:
                managed_areas = request.POST.getlist('managed_task_areas[]')
                for area_name in managed_areas:
                    area_name = area_name.strip()
                    if area_name:
                        # 验证任务区名称
                        is_valid, error_msg = is_valid_task_area_name(area_name)
                        if not is_valid:
                            # 跳过无效的任务区名称，不创建
                            continue
                        
                        area_obj, created = TaskArea.objects.get_or_create(
                            name=area_name,
                            defaults={'description': f'任务区: {area_name}'}
                        )
                        user.managed_task_areas.add(area_obj)
            
            messages.success(request, f'用户 {user.username} 创建成功！角色：{user.get_role_display()}')
            return redirect('usermanagement:user_list')
            
        except Exception as e:
            context = _get_user_form_context(request)
            context['action'] = 'create'
            messages.error(request, f'创建用户时发生错误：{str(e)}')
            return render(request, 'dashboard/user_form.html', context)
    
    # GET请求：显示创建表单
    context = _get_user_form_context(request)
    context['action'] = 'create'
    return render(request, 'dashboard/user_form.html', context)


@login_required
def user_edit(request, user_id):
    """编辑用户"""
    target_user = get_object_or_404(User, id=user_id)
    
    # 检查当前用户是否有权限管理目标用户
    if not request.user.can_manage_user(target_user):
        messages.error(request, '您没有权限编辑此用户。')
        return redirect('usermanagement:user_list')
    
    if request.method == 'POST':
        try:
            # 基本字段验证
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            role = request.POST.get('role', '')
            
            # 验证必填字段
            if not all([username, email, role]):
                context = _get_user_form_context(request)
                context.update({
                    'action': 'edit', 
                    'target_user': target_user
                })
                messages.error(request, '请填写所有必填字段。')
                return render(request, 'dashboard/user_form.html', context)
            
            # 检查用户名和邮箱唯一性（排除当前用户）
            if User.objects.filter(username=username).exclude(id=target_user.id).exists():
                context = _get_user_form_context(request)
                context.update({
                    'action': 'edit', 
                    'target_user': target_user
                })
                messages.error(request, '用户名已存在，请选择其他用户名。')
                return render(request, 'dashboard/user_form.html', context)
                
            if User.objects.filter(email=email).exclude(id=target_user.id).exists():
                context = _get_user_form_context(request)
                context.update({
                    'action': 'edit', 
                    'target_user': target_user
                })
                messages.error(request, '该邮箱已被使用，请使用其他邮箱。')
                return render(request, 'dashboard/user_form.html', context)
            
            # 更新基本信息
            target_user.username = username
            target_user.email = email
            target_user.first_name = request.POST.get('first_name', '').strip()
            target_user.last_name = request.POST.get('last_name', '').strip()
            target_user.role = role
            target_user.phone_number = request.POST.get('phone_number', '').strip()
            target_user.department_rank = request.POST.get('department_rank', '').strip()
            target_user.position = request.POST.get('position', '').strip()
            target_user.passport_name_pinyin = request.POST.get('passport_name_pinyin', '').strip()
            
            # 处理护照号码
            passport_number = request.POST.get('passport_number', '').strip()
            target_user.passport_number = passport_number if passport_number else None
            
            # 处理激活状态
            target_user.is_active = request.POST.get('is_active') == 'on'
            
            # 处理日期字段
            for date_field in ['passport_issue_date', 'passport_expiry_date', 'employment_start_date', 'employment_end_date']:
                date_value = request.POST.get(date_field, '').strip()
                if date_value:
                    setattr(target_user, date_field, date_value)
                else:
                    setattr(target_user, date_field, None)
            
            # 处理密码更新
            new_password = request.POST.get('password', '').strip()
            if new_password:
                if len(new_password) < 6:
                    context = _get_user_form_context(request)
                    context.update({
                        'action': 'edit', 
                        'target_user': target_user
                    })
                    messages.error(request, '密码长度至少6位。')
                    return render(request, 'dashboard/user_form.html', context)
                target_user.password = make_password(new_password)
            
            # 处理任务区分配逻辑
            task_area_obj = None
            
            if role == User.Role.SUPERUSER:
                # 超级管理员：自动分配或创建"全球"任务区
                global_area, created = TaskArea.objects.get_or_create(
                    name='全球',
                    defaults={'description': '超级管理员全球任务区'}
                )
                task_area_obj = global_area
                
            elif role in [User.Role.TASK_AREA_MANAGER, User.Role.EMPLOYEE]:
                # 任务区负责人和普通员工：需要单一任务区
                task_area_id = request.POST.get('task_area_fk', '').strip()
                new_task_area_name = request.POST.get('new_task_area', '').strip()
                
                if new_task_area_name:
                    # 验证任务区名称
                    is_valid, error_msg = is_valid_task_area_name(new_task_area_name)
                    if not is_valid:
                        context = _get_user_form_context(request)
                        context.update({
                            'action': 'edit', 
                            'target_user': target_user
                        })
                        messages.error(request, f'无效的任务区名称：{error_msg}')
                        return render(request, 'dashboard/user_form.html', context)
                    
                    # 创建新任务区
                    if TaskArea.objects.filter(name=new_task_area_name).exists():
                        context = _get_user_form_context(request)
                        context.update({
                            'action': 'edit', 
                            'target_user': target_user
                        })
                        messages.error(request, f'任务区"{new_task_area_name}"已存在。')
                        return render(request, 'dashboard/user_form.html', context)
                    
                    task_area_obj = TaskArea.objects.create(
                        name=new_task_area_name,
                        description=f'任务区: {new_task_area_name}'
                    )
                elif task_area_id and task_area_id != '__new__':
                    # 选择现有任务区
                    try:
                        task_area_obj = TaskArea.objects.get(id=task_area_id)
                    except TaskArea.DoesNotExist:
                        context = _get_user_form_context(request)
                        context.update({
                            'action': 'edit', 
                            'target_user': target_user
                        })
                        messages.error(request, '选择的任务区不存在。')
                        return render(request, 'dashboard/user_form.html', context)
                else:
                    context = _get_user_form_context(request)
                    context.update({
                        'action': 'edit', 
                        'target_user': target_user
                    })
                    messages.error(request, '任务区负责人和普通员工必须分配任务区。')
                    return render(request, 'dashboard/user_form.html', context)
                    
            elif role == User.Role.HEAD_MANAGER:
                # 总部负责人：不设置主要任务区，只管理多个任务区
                task_area_obj = None  # 总部负责人不需要主要任务区
            
            # 设置任务区
            target_user.task_area_fk = task_area_obj
            # 同时设置旧的 task_area CharField 以保持数据一致性
            if task_area_obj:
                target_user.task_area = task_area_obj.name
            else:
                target_user.task_area = ''
            
            # 清除原有的管辖任务区关系（总部负责人）
            target_user.managed_task_areas.clear()
            
            # 保存用户
            target_user.save()
            
            # 处理总部负责人的多任务区管理
            if role == User.Role.HEAD_MANAGER:
                managed_areas = request.POST.getlist('managed_task_areas[]')
                
                # 清空现有的管辖任务区
                target_user.managed_task_areas.clear()
                
                # 添加新提交的管辖任务区
                for area_name in managed_areas:
                    area_name = area_name.strip()
                    if area_name:
                        # 验证任务区名称
                        is_valid, error_msg = is_valid_task_area_name(area_name)
                        if not is_valid:
                            # 跳过无效的任务区名称，不创建
                            continue
                        
                        area_obj, created = TaskArea.objects.get_or_create(
                            name=area_name,
                            defaults={'description': f'任务区: {area_name}'}
                        )
                        target_user.managed_task_areas.add(area_obj)
            
            messages.success(request, f'用户 {target_user.username} 更新成功！')
            return redirect('usermanagement:user_list')
            
        except Exception as e:
            context = _get_user_form_context(request)
            context.update({
                'action': 'edit', 
                'target_user': target_user
            })
            messages.error(request, f'更新用户时发生错误：{str(e)}')
            return render(request, 'dashboard/user_form.html', context)
    
    # GET请求：显示编辑表单
    context = _get_user_form_context(request)
    context.update({
        'action': 'edit', 
        'target_user': target_user
    })
    return render(request, 'dashboard/user_form.html', context)


@login_required
def user_delete(request, user_id):
    """删除用户"""
    user = get_object_or_404(User, id=user_id)
    
    # 检查当前用户是否有权限管理目标用户
    if not request.user.can_manage_user(user):
        messages.error(request, '您没有权限删除此用户。')
        return redirect('usermanagement:user_list')
    
    # 防止删除自己
    if user == request.user:
        messages.error(request, '不能删除自己的账户！')
        return redirect('usermanagement:user_list')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'用户 {username} 已删除！')
        return redirect('usermanagement:user_list')
    
    return render(request, 'usermanagement/user_confirm_delete.html', {
        'user_obj': user
    })


@login_required
def user_detail(request, user_id):
    """用户详情"""
    user = get_object_or_404(User, id=user_id)
    
    # 检查当前用户是否有权限查看目标用户详情
    if not request.user.can_manage_user(user):
        messages.error(request, '您没有权限查看此用户详情。')
        return redirect('usermanagement:user_list')
    
    return render(request, 'usermanagement/user_detail.html', {
        'user_obj': user
    })
