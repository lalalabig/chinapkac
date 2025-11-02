from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone
import os
import zipfile
from io import BytesIO

User = get_user_model()

class Report(models.Model):
    """报告模型"""
    
    class ReportType(models.TextChoices):
        WEEKLY = 'weekly', '周报'
        MONTHLY = 'monthly', '月报'
        SUMMARY = 'summary', '汇总报告'
    
    class ReportStatus(models.TextChoices):
        DRAFT = 'draft', '草稿'
        SUBMITTED = 'submitted', '已提交'
        REVIEWED = 'reviewed', '已查看'
        APPROVED = 'approved', '已批准'
    
    # 基本信息
    uploader = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uploaded_reports',
        verbose_name='上传人'
    )
    
    report_type = models.CharField(
        max_length=20,
        choices=ReportType.choices,
        verbose_name='报告类型'
    )
    
    # 报告周期和标识
    report_period = models.CharField(
        max_length=20, 
        help_text='如：2025-W10 或 2025-M03',
        verbose_name='报告周期'
    )
    
    # 文件信息
    file = models.FileField(
        upload_to='reports/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'])],
        verbose_name='报告文件'
    )
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小(字节)')
    
    # 所属任务区
    task_area = models.ForeignKey(
        'accounts.TaskArea',
        on_delete=models.CASCADE,
        related_name='reports',
        verbose_name='所属任务区'
    )
    
    # 状态管理
    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.SUBMITTED,
        verbose_name='状态'
    )
    
    is_viewed = models.BooleanField(default=False, verbose_name='是否已查看')
    viewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='viewed_reports',
        verbose_name='查看人'
    )
    viewed_at = models.DateTimeField(null=True, blank=True, verbose_name='查看时间')
    
    # 审批信息
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_reports',
        verbose_name='审批人'
    )
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name='审批时间')
    
    # 时间戳
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '报告'
        verbose_name_plural = '报告'
        ordering = ['-upload_date']
        unique_together = ['uploader', 'report_type', 'report_period', 'task_area']
    
    def __str__(self):
        return f"{self.uploader.get_full_name()} - {self.get_report_type_display()} - {self.report_period}"
    
    def save(self, *args, **kwargs):
        """保存时自动计算文件大小"""
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_extension(self):
        """获取文件扩展名"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ''
    
    @property
    def human_readable_size(self):
        """获取可读的文件大小"""
        if self.file_size == 0:
            return '0 B'
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if self.file_size < 1024.0:
                return f"{self.file_size:.1f} {unit}"
            self.file_size /= 1024.0
        return f"{self.file_size:.1f} TB"
    
    def mark_as_viewed(self, viewer):
        """标记为已查看"""
        self.is_viewed = True
        self.viewed_by = viewer
        self.viewed_at = timezone.now()
        self.save()
    
    def approve(self, approver):
        """批准报告"""
        self.status = self.ReportStatus.APPROVED
        self.approver = approver
        self.approved_at = timezone.now()
        self.save()
    
    def get_display_name(self):
        """获取显示名称"""
        if self.uploader:
            return f"{self.uploader.get_full_name()} - {self.get_report_type_display()} - {self.report_period}"
        return f"未知用户 - {self.get_report_type_display()} - {self.report_period}"


class ReportDownloadLog(models.Model):
    """报告下载日志"""
    
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='download_logs',
        verbose_name='关联报告'
    )
    
    downloader = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='report_downloads',
        verbose_name='下载人'
    )
    
    download_time = models.DateTimeField(auto_now_add=True, verbose_name='下载时间')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    
    class Meta:
        verbose_name = '下载日志'
        verbose_name_plural = '下载日志'
        ordering = ['-download_time']
    
    def __str__(self):
        return f"{self.downloader.get_full_name()} 下载 {self.report.get_display_name()}"


class BulkDownloadPackage(models.Model):
    """批量下载包"""
    
    class PackageStatus(models.TextChoices):
        PENDING = 'pending', '待处理'
        PROCESSING = 'processing', '处理中'
        COMPLETED = 'completed', '已完成'
        FAILED = 'failed', '失败'
    
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_download_packages',
        verbose_name='创建人'
    )
    
    package_name = models.CharField(max_length=200, verbose_name='包名称')
    zip_file = models.FileField(
        upload_to='download_packages/',
        null=True,
        blank=True,
        verbose_name='ZIP文件'
    )
    
    status = models.CharField(
        max_length=20,
        choices=PackageStatus.choices,
        default=PackageStatus.PENDING,
        verbose_name='状态'
    )
    
    # 包含的报告
    reports = models.ManyToManyField(
        Report,
        through='PackageReport',
        related_name='bulk_download_packages',
        verbose_name='包含的报告'
    )
    
    # 统计信息
    total_reports = models.PositiveIntegerField(default=0, verbose_name='报告总数')
    total_size = models.BigIntegerField(default=0, verbose_name='总大小(字节)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    
    class Meta:
        verbose_name = '批量下载包'
        verbose_name_plural = '批量下载包'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.package_name} - {self.get_status_display()}"
    
    def generate_zip(self):
        """生成ZIP文件"""
        if self.status != self.PackageStatus.PENDING:
            return False
        
        self.status = self.PackageStatus.PROCESSING
        self.save()
        
        try:
            # 创建ZIP文件
            from django.core.files.base import ContentFile
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                total_size = 0
                
                for package_report in self.package_reports.all():
                    report = package_report.report
                    
                    if report.file:
                        # 文件名格式: "姓名+任务区+时间段+报告类型"
                        task_area_name = report.task_area.name if report.task_area else "未知任务区"
                        filename = f"{report.uploader.get_full_name()}_{task_area_name}_{report.report_period}_{report.get_report_type_display()}{report.file_extension}"
                        # 添加报告文件到ZIP
                        zip_file.write(
                            report.file.path,
                            arcname=filename
                        )
                        total_size += report.file.size
            
            # 保存ZIP文件
            zip_content = ContentFile(zip_buffer.getvalue())
            self.zip_file.save(f"{self.package_name}.zip", zip_content, save=False)
            self.total_size = total_size
            self.status = self.PackageStatus.COMPLETED
            self.completed_at = timezone.now()
            self.save()
            
            return True
            
        except Exception as e:
            self.status = self.PackageStatus.FAILED
            self.save()
            print(f"生成ZIP文件失败: {e}")
            return False


class PackageReport(models.Model):
    """批量下载包与报告的关联表"""
    
    package = models.ForeignKey(BulkDownloadPackage, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    
    class Meta:
        verbose_name = '包报告关联'
        verbose_name_plural = '包报告关联'
        unique_together = ['package', 'report']
    
    def __str__(self):
        return f"{self.package.package_name} - {self.report.get_display_name()}"
