"""
报告上传管理系统视图
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse, FileResponse
from django.utils import timezone
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.core.management import call_command
from django.conf import settings
from django.urls import reverse
import os
import zipfile
from io import BytesIO
import logging

from .models import Report, ReportDownloadLog, BulkDownloadPackage, PackageReport
from accounts.models import User, TaskArea
from accounts.permissions import role_required

logger = logging.getLogger(__name__)


@login_required
def upload_report(request):
    """
    上传报告
    """
    if request.method == 'POST':
        # 处理文件上传
        try:
            file = request.FILES.get('report_file')
            report_type = request.POST.get('report_type')
            report_period = request.POST.get('report_period')
            
            if not all([file, report_type, report_period]):
                messages.error(request, '请填写所有必填字段')
                return redirect('reports:upload')
            
            # 根据当前用户自动分配任务区
            task_area = request.user.task_area_fk
            if not task_area:
                messages.error(request, '用户未设置任务区，请联系管理员')
                return redirect('reports:upload')
            
            # 检查是否已存在相同报告
            existing_report = Report.objects.filter(
                uploader=request.user,
                report_type=report_type,
                report_period=report_period,
                task_area=task_area
            ).first()
            
            if existing_report:
                messages.error(request, f'您已经上传过 {report_type} 的 {report_period} 报告')
                return redirect('reports:upload')
            
            # 创建报告记录
            report = Report.objects.create(
                uploader=request.user,
                report_type=report_type,
                report_period=report_period,
                task_area=task_area,
                file=file,
                file_size=file.size
            )
            
            messages.success(request, '报告上传成功！')
            return redirect('reports:my_reports')
            
        except Exception as e:
            logger.error(f"报告上传失败: {e}")
            messages.error(request, f'上传失败：{str(e)}')
            return redirect('reports:upload')
    
    context = {
        'report_types': Report.ReportType.choices,
    }
    return render(request, 'reports/upload_report.html', context)


@login_required
def my_reports(request):
    """
    我的报告列表（根据角色显示不同内容）
    """
    user = request.user
    reports = None
    can_upload = False
    can_manage = False
    title = '我的报告'
    subtitle = ''
    
    if user.role == User.Role.EMPLOYEE:
        # 普通员工：只能看到自己上传的报告
        reports = Report.objects.filter(uploader=user).order_by('-upload_date')
        can_upload = True
        title = '我的报告'
        subtitle = '查看和管理您上传的报告'
        
    elif user.role == User.Role.TASK_AREA_MANAGER:
        # 任务区负责人:可以看到本任务区普通员工上传的报告,也可以上传自己的报告给总部
        reports = Report.objects.filter(
            Q(task_area=user.task_area_fk, uploader__role=User.Role.EMPLOYEE) |  # 普通员工的报告
            Q(uploader=user)  # 自己上传的报告
        ).order_by('-upload_date')
        can_upload = True
        can_manage = True
        title = '任务区报告管理'
        subtitle = f'管理 {user.task_area_fk.name} 任务区的员工报告'
        
    elif user.role == User.Role.HEAD_MANAGER:
        # 总部负责人：可以看到管辖任务区任务区负责人上传的报告
        managed_areas = user.managed_task_areas.all()
        reports = Report.objects.filter(
            task_area__in=managed_areas,
            uploader__role=User.Role.TASK_AREA_MANAGER  # 只显示任务区负责人上传的报告
        ).order_by('-upload_date')
        title = '总部报告管理'
        subtitle = '查看管辖任务区负责人提交的报告'
        
    elif user.role == User.Role.SUPERUSER:
        # 超级管理员：可以看到所有任务区负责人提交的报告
        reports = Report.objects.filter(
            uploader__role=User.Role.TASK_AREA_MANAGER  # 只显示任务区负责人上传的报告
        ).order_by('-upload_date')
        title = '系统报告管理'
        subtitle = '查看所有任务区负责人提交的报告'
    
    # 搜索和筛选
    search = request.GET.get('search')
    report_type = request.GET.get('report_type')
    status = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    task_area_filter = request.GET.get('task_area')
    name_filter = request.GET.get('name')
    
    if search:
        reports = reports.filter(
            Q(report_period__icontains=search) |
            Q(uploader__first_name__icontains=search) |
            Q(uploader__last_name__icontains=search) |
            Q(task_area__name__icontains=search)
        )
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    if status:
        reports = reports.filter(status=status)
    
    # 时间段筛选（适用于任务区负责人、总部负责人、超级管理员）
    if date_from:
        reports = reports.filter(upload_date__gte=date_from)
    
    if date_to:
        reports = reports.filter(upload_date__lte=date_to)
    
    # 按任务区筛选（仅总部负责人和超级管理员）
    if task_area_filter and user.role in [User.Role.HEAD_MANAGER, User.Role.SUPERUSER]:
        reports = reports.filter(task_area_id=task_area_filter)
    
    # 按姓名筛选（仅总部负责人和超级管理员）
    if name_filter and user.role in [User.Role.HEAD_MANAGER, User.Role.SUPERUSER]:
        reports = reports.filter(
            Q(uploader__first_name__icontains=name_filter) |
            Q(uploader__last_name__icontains=name_filter) |
            Q(uploader__username__icontains=name_filter)
        )
    
    # 分页
    paginator = Paginator(reports, 15)  # 管理层显示更多报告
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计数据
    stats = {
        'total': reports.count(),
        'submitted': reports.filter(status=Report.ReportStatus.SUBMITTED).count(),
        'viewed': reports.filter(status=Report.ReportStatus.REVIEWED).count(),
        'approved': reports.filter(status=Report.ReportStatus.APPROVED).count(),
    }
    
    if can_manage:
        stats['new'] = reports.filter(is_viewed=False).count()
    
    # 获取任务区列表（仅总部负责人和超级管理员用于筛选）
    if user.role == User.Role.HEAD_MANAGER:
        task_areas = user.managed_task_areas.all()
    elif user.role == User.Role.SUPERUSER:
        task_areas = TaskArea.objects.all()
    else:
        task_areas = []
    
    context = {
        'reports': page_obj,
        'stats': stats,
        'report_types': Report.ReportType.choices,
        'status_choices': Report.ReportStatus.choices,
        'task_areas': task_areas if user.role in [User.Role.HEAD_MANAGER, User.Role.SUPERUSER] else [],
        'can_upload': can_upload,
        'can_manage': can_manage,
        'title': title,
        'subtitle': subtitle,
        'date_from': date_from,
        'date_to': date_to,
        'task_area_filter': task_area_filter,
        'name_filter': name_filter,
    }
    return render(request, 'reports/role_based_reports.html', context)


@login_required
@role_required([User.Role.TASK_AREA_MANAGER, User.Role.HEAD_MANAGER, User.Role.SUPERUSER])
def manage_reports(request):
    """
    管理报告（任务区负责人、总部负责人）
    """
    # 根据角色获取可管理的报告
    if request.user.role == User.Role.TASK_AREA_MANAGER:
        # 任务区负责人：只能看本任务区的报告
        reports = Report.objects.filter(
            task_area=request.user.task_area_fk
        ).order_by('-upload_date')
    elif request.user.role == User.Role.HEAD_MANAGER:
        # 总部负责人：看管辖任务区的报告
        managed_areas = request.user.managed_task_areas.all()
        reports = Report.objects.filter(
            task_area__in=managed_areas
        ).order_by('-upload_date')
    else:
        # 超级管理员：看所有报告
        reports = Report.objects.all().order_by('-upload_date')
    
    # 搜索和筛选
    search = request.GET.get('search')
    report_type = request.GET.get('report_type')
    status = request.GET.get('status')
    task_area = request.GET.get('task_area')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    if search:
        reports = reports.filter(
            Q(report_period__icontains=search) |
            Q(uploader__first_name__icontains=search) |
            Q(uploader__last_name__icontains=search) |
            Q(task_area__name__icontains=search)
        )
    
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    if status:
        reports = reports.filter(status=status)
    
    if task_area:
        reports = reports.filter(task_area_id=task_area)
    
    if date_from:
        reports = reports.filter(upload_date__gte=date_from)
    
    if date_to:
        reports = reports.filter(upload_date__lte=date_to)
    
    # 分页
    paginator = Paginator(reports, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计数据
    stats = {
        'total': reports.count(),
        'new': reports.filter(is_viewed=False).count(),
        'submitted': reports.filter(status=Report.ReportStatus.SUBMITTED).count(),
        'approved': reports.filter(status=Report.ReportStatus.APPROVED).count(),
        'total_size': reports.aggregate(total=Sum('file_size'))['total'] or 0,
    }
    
    # 获取任务区列表（用于筛选）- 只有总部负责人和超级管理员可以看到筛选选项
    if request.user.role == User.Role.HEAD_MANAGER:
        task_areas = request.user.managed_task_areas.all()
    elif request.user.role == User.Role.SUPERUSER:
        task_areas = TaskArea.objects.all()
    else:
        # 任务区负责人不需要任务区筛选，因为他们只能查看自己任务区的报告
        task_areas = []
    
    context = {
        'reports': page_obj,
        'stats': stats,
        'task_areas': task_areas,
        'report_types': Report.ReportType.choices,
        'status_choices': Report.ReportStatus.choices,
    }
    return render(request, 'reports/manage_reports.html', context)


@login_required
def report_detail(request, report_id):
    """
    报告详情
    """
    report = get_object_or_404(Report, id=report_id)
    
    # 权限检查
    if not can_view_report(request.user, report):
        messages.error(request, '您没有权限查看此报告')
        return redirect('reports:my_reports')
    
    # 如果是查看权限，记录查看日志
    if request.user != report.uploader and not report.is_viewed:
        report.mark_as_viewed(request.user)
        
        # 记录下载日志
        ReportDownloadLog.objects.create(
            report=report,
            downloader=request.user,
            ip_address=get_client_ip(request)
        )
    
    # 获取下载日志
    download_logs = report.download_logs.select_related('downloader').order_by('-download_time')[:10]
    
    context = {
        'report': report,
        'download_logs': download_logs,
        'can_download': can_download_report(request.user, report),
        'can_approve': can_approve_report(request.user, report),
    }
    return render(request, 'reports/report_detail.html', context)


@login_required
def download_report(request, report_id):
    """
    下载单个报告
    """
    report = get_object_or_404(Report, id=report_id)
    
    # 权限检查
    if not can_download_report(request.user, report):
        messages.error(request, '您没有权限下载此报告')
        return redirect('reports:my_reports')
    
    try:
        # 记录下载日志
        ReportDownloadLog.objects.create(
            report=report,
            downloader=request.user,
            ip_address=get_client_ip(request)
        )
        
        # 生成下载文件名: "姓名+任务区+时间段+报告类型"
        task_area_name = report.task_area.name if report.task_area else "未知任务区"
        file_extension = os.path.splitext(report.file.name)[1]
        filename = f"{report.uploader.get_full_name()}_{task_area_name}_{report.report_period}_{report.get_report_type_display()}{file_extension}"
        
        # 返回文件
        response = FileResponse(
            report.file.open('rb'),
            as_attachment=True,
            filename=filename
        )
        return response
        
    except Exception as e:
        logger.error(f"下载报告失败: {e}")
        messages.error(request, '下载失败，请稍后重试')
        return redirect('reports:report_detail', report_id=report_id)


@login_required
@role_required([User.Role.TASK_AREA_MANAGER, User.Role.HEAD_MANAGER, User.Role.SUPERUSER])
def bulk_download(request):
    """
    批量下载功能
    """
    if request.method == 'POST':
        # 获取选中的报告ID
        report_ids = request.POST.getlist('report_ids')
        package_name = request.POST.get('package_name', f'报告下载_{timezone.now().strftime("%Y%m%d_%H%M%S")}')
        
        if not report_ids:
            messages.error(request, '请选择要下载的报告')
            return redirect('reports:manage_reports')
        
        try:
            # 获取报告列表
            reports = Report.objects.filter(id__in=report_ids)
            
            # 检查权限
            for report in reports:
                if not can_download_report(request.user, report):
                    messages.error(request, f'您没有权限下载 {report.get_display_name()}')
                    return redirect('reports:manage_reports')
            
            # 创建批量下载包
            bulk_package = BulkDownloadPackage.objects.create(
                creator=request.user,
                package_name=package_name,
                total_reports=reports.count()
            )
            
            # 添加报告到包中
            for report in reports:
                PackageReport.objects.create(
                    package=bulk_package,
                    report=report
                )
            
            # 异步生成ZIP文件（在实际应用中应该使用Celery）
            # 这里简化处理，立即生成
            if bulk_package.generate_zip():
                messages.success(request, f'下载包 "{package_name}" 已生成完成')
                return redirect('reports:download_package', package_id=bulk_package.id)
            else:
                messages.error(request, '下载包生成失败，请重试')
                return redirect('reports:manage_reports')
                
        except Exception as e:
            logger.error(f"批量下载失败: {e}")
            messages.error(request, '批量下载失败，请稍后重试')
            return redirect('reports:manage_reports')
    
    # GET请求，显示批量下载页面
    # 获取可选的报告列表
    if request.user.role == User.Role.TASK_AREA_MANAGER:
        reports = Report.objects.filter(task_area=request.user.task_area_fk)
    elif request.user.role == User.Role.HEAD_MANAGER:
        managed_areas = request.user.managed_task_areas.all()
        reports = Report.objects.filter(task_area__in=managed_areas)
    else:
        reports = Report.objects.all()
    
    context = {
        'reports': reports.order_by('-upload_date')[:100],  # 限制显示数量
    }
    return render(request, 'reports/bulk_download.html', context)


@login_required
def download_package(request, package_id):
    """
    下载批量下载包
    """
    package = get_object_or_404(BulkDownloadPackage, id=package_id)
    
    # 权限检查
    if request.user != package.creator and request.user.role != User.Role.SUPERUSER:
        messages.error(request, '您没有权限下载此包')
        return redirect('reports:my_reports')
    
    if package.status != BulkDownloadPackage.PackageStatus.COMPLETED:
        messages.error(request, '下载包还未生成完成')
        return redirect('reports:my_reports')
    
    try:
        response = FileResponse(
            package.zip_file.open('rb'),
            as_attachment=True,
            filename=os.path.basename(package.zip_file.name)
        )
        return response
        
    except Exception as e:
        logger.error(f"下载包失败: {e}")
        messages.error(request, '下载包下载失败')
        return redirect('reports:my_reports')


@login_required
@role_required([User.Role.SUPERUSER])
def cleanup_old_reports(request):
    """
    清理6个月前的报告（仅超级管理员）
    """
    if request.method == 'POST':
        try:
            # 计算6个月前的日期
            cutoff_date = timezone.now() - timezone.timedelta(days=180)
            
            # 查找要删除的报告
            old_reports = Report.objects.filter(upload_date__lt=cutoff_date)
            count = old_reports.count()
            
            if count == 0:
                messages.info(request, '没有找到需要清理的报告')
                return redirect('reports:manage_reports')
            
            # 删除文件
            for report in old_reports:
                if report.file:
                    if os.path.exists(report.file.path):
                        os.remove(report.file.path)
            
            # 删除数据库记录
            old_reports.delete()
            
            messages.success(request, f'成功清理了 {count} 份报告')
            return redirect('reports:manage_reports')
            
        except Exception as e:
            logger.error(f"清理报告失败: {e}")
            messages.error(request, '清理报告失败，请重试')
            return redirect('reports:manage_reports')
    
    # GET请求显示确认页面
    cutoff_date = timezone.now() - timezone.timedelta(days=180)
    old_count = Report.objects.filter(upload_date__lt=cutoff_date).count()
    
    context = {
        'old_count': old_count,
        'cutoff_date': cutoff_date,
    }
    return render(request, 'reports/cleanup_confirm.html', context)


# 辅助函数

def can_view_report(user, report):
    """检查用户是否可以查看报告"""
    if user == report.uploader:
        return True
    if user.role == User.Role.SUPERUSER:
        return True
    if user.role == User.Role.TASK_AREA_MANAGER:
        return report.task_area == user.task_area_fk
    if user.role == User.Role.HEAD_MANAGER:
        return report.task_area in user.managed_task_areas.all()
    return False


def can_download_report(user, report):
    """检查用户是否可以下载报告"""
    return can_view_report(user, report)


def can_approve_report(user, report):
    """检查用户是否可以审批报告"""
    if user.role == User.Role.SUPERUSER:
        return True
    if user.role == User.Role.TASK_AREA_MANAGER:
        return report.task_area == user.task_area_fk
    if user.role == User.Role.HEAD_MANAGER:
        return report.task_area in user.managed_task_areas.all()
    return False


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
