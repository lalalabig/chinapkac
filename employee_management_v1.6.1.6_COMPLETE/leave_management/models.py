"""
请假管理模型
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

User = get_user_model()


class LeaveApplication(models.Model):
    """
    请假申请模型
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('草稿')
        PENDING_TASK_AREA = 'pending_task_area', _('待任务区负责人审批')
        PENDING_HEAD = 'pending_head', _('待总部负责人审批')
        APPROVED = 'approved', _('已批准')
        REJECTED = 'rejected', _('已拒绝')
        CANCELLED = 'cancelled', _('已取消')
    
    # 基本信息
    applicant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='leave_applications',
        verbose_name='申请人'
    )
    
    # 时间信息
    leave_start_date = models.DateField(verbose_name='休假开始日期')
    leave_end_date = models.DateField(verbose_name='休假结束日期')
    application_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='申请时间'
    )
    
    # 休假地点
    leave_location = models.CharField(
        max_length=200,
        verbose_name='休假地点名称'
    )
    leave_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='休假地纬度'
    )
    leave_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='休假地经度'
    )
    
    # 休假原因
    leave_reason = models.TextField(verbose_name='休假原因')
    
    # 审批状态
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name='审批状态'
    )
    
    # 当前审批人
    current_approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pending_leave_approvals',
        verbose_name='当前审批人'
    )
    
    # 任务区负责人审批
    task_area_manager_approved = models.BooleanField(
        default=False,
        verbose_name='任务区负责人是否已批准'
    )
    task_area_manager_approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_area_leave_approvals',
        verbose_name='任务区负责人'
    )
    task_area_manager_approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='任务区负责人审批时间'
    )
    
    # 总部负责人审批
    head_manager_approved = models.BooleanField(
        default=False,
        verbose_name='总部负责人是否已批准'
    )
    head_manager_approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='head_leave_approvals',
        verbose_name='总部负责人'
    )
    head_manager_approval_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='总部负责人审批时间'
    )
    
    # 拒绝原因
    rejection_reason = models.TextField(
        blank=True,
        verbose_name='拒绝原因'
    )
    
    # 取消相关
    cancellation_requested = models.BooleanField(
        default=False,
        verbose_name='是否申请取消'
    )
    cancellation_reason = models.TextField(
        blank=True,
        verbose_name='取消原因'
    )
    cancellation_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='取消申请时间'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '请假申请'
        verbose_name_plural = '请假申请'
        db_table = 'leave_applications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.applicant.username} - {self.leave_start_date} 至 {self.leave_end_date}"
    
    @property
    def is_on_leave(self):
        """判断是否正在休假"""
        if self.status != self.Status.APPROVED:
            return False
        today = timezone.now().date()
        return self.leave_start_date <= today <= self.leave_end_date
    
    @property
    def is_planned_leave(self):
        """判断是否计划休假（已批准但未开始）"""
        if self.status != self.Status.APPROVED:
            return False
        today = timezone.now().date()
        return today < self.leave_start_date
    
    @property
    def duration_days(self):
        """休假天数"""
        return (self.leave_end_date - self.leave_start_date).days + 1
    
    @property
    def current_approval_level(self):
        """获取当前审批级别"""
        if self.status == self.Status.PENDING_TASK_AREA:
            return 'task_area'
        elif self.status == self.Status.PENDING_HEAD:
            return 'head'
        return None
    
    def can_be_approved_by(self, user):
        """检查用户是否可以审批此申请"""
        if user.role == User.Role.SUPERUSER:
            return True
        
        if user.role == User.Role.TASK_AREA_MANAGER:
            return (self.status == self.Status.PENDING_TASK_AREA and 
                    self.applicant.task_area == user.task_area)
        
        if user.role == User.Role.HEAD_MANAGER:
            # 这里需要根据用户管理权限检查
            return self.status == self.Status.PENDING_HEAD
        
        return False
    
    def approve_by_task_area_manager(self, manager, comment=''):
        """任务区负责人批准"""
        if not self.can_be_approved_by(manager):
            raise PermissionError("您没有权限审批此申请")
        
        self.status = self.Status.PENDING_HEAD
        self.task_area_manager_approved = True
        self.task_area_manager_approver = manager
        self.task_area_manager_approval_date = timezone.now()
        self.current_approver = None
        self.save()
        
        # 记录审批历史
        ApprovalRecord.objects.create(
            leave_application=self,
            approver=manager,
            action=ApprovalRecord.Action.APPROVED,
            comment=comment
        )
    
    def approve_by_head_manager(self, manager, comment=''):
        """总部负责人批准"""
        if not self.can_be_approved_by(manager):
            raise PermissionError("您没有权限审批此申请")
        
        self.status = self.Status.APPROVED
        self.head_manager_approved = True
        self.head_manager_approver = manager
        self.head_manager_approval_date = timezone.now()
        self.current_approver = None
        self.save()
        
        # 记录审批历史
        ApprovalRecord.objects.create(
            leave_application=self,
            approver=manager,
            action=ApprovalRecord.Action.APPROVED,
            comment=comment
        )
    
    def reject(self, approver, reason, comment=''):
        """拒绝申请"""
        if not self.can_be_approved_by(approver):
            raise PermissionError("您没有权限审批此申请")
        
        self.status = self.Status.REJECTED
        self.rejection_reason = reason
        self.current_approver = None
        self.save()
        
        # 记录审批历史
        ApprovalRecord.objects.create(
            leave_application=self,
            approver=approver,
            action=ApprovalRecord.Action.REJECTED,
            comment=comment
        )
    
    def cancel_by_applicant(self, applicant, reason=''):
        """申请人取消申请"""
        if self.applicant != applicant:
            raise PermissionError("只有申请人可以取消申请")
        
        if self.status in [self.Status.APPROVED, self.Status.PENDING_HEAD, self.Status.PENDING_TASK_AREA]:
            self.status = self.Status.CANCELLED
            self.cancellation_reason = reason
            self.cancellation_date = timezone.now()
            self.save()
            
            # 记录操作历史
            ApprovalRecord.objects.create(
                leave_application=self,
                approver=applicant,
                action=ApprovalRecord.Action.CANCELLED,
                comment=reason
            )
    
    def submit_for_approval(self):
        """提交申请待审批"""
        if self.status != self.Status.DRAFT:
            raise ValueError("只有草稿状态的申请才能提交")
        
        self.status = self.Status.PENDING_TASK_AREA
        self.current_approver = None  # 暂时不使用单点审批人
        self.save()
        
        # 记录提交历史
        ApprovalRecord.objects.create(
            leave_application=self,
            approver=self.applicant,
            action=ApprovalRecord.Action.SUBMITTED,
            comment='提交申请待审批'
        )


class FlightSegment(models.Model):
    """
    机票行程段模型
    """
    
    class SegmentType(models.TextChoices):
        OUTBOUND = 'outbound', _('回国行程')
        RETURN = 'return', _('返回任务区行程')
    
    leave_application = models.ForeignKey(
        LeaveApplication,
        on_delete=models.CASCADE,
        related_name='flight_segments',
        verbose_name='关联请假申请'
    )
    
    segment_type = models.CharField(
        max_length=10,
        choices=SegmentType.choices,
        verbose_name='行程类型'
    )
    
    sequence = models.PositiveIntegerField(
        default=1,
        verbose_name='行程段序号'
    )
    
    departure = models.CharField(
        max_length=100,
        verbose_name='出发地'
    )
    
    destination = models.CharField(
        max_length=100,
        verbose_name='目的地'
    )
    
    flight_number = models.CharField(
        max_length=20,
        verbose_name='航班号'
    )
    
    flight_date = models.DateField(verbose_name='航班日期')
    
    flight_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name='航班时间'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '机票行程段'
        verbose_name_plural = '机票行程段'
        db_table = 'flight_segments'
        ordering = ['segment_type', 'sequence']
    
    def __str__(self):
        return f"{self.get_segment_type_display()} - {self.departure} → {self.destination}"


class ApprovalRecord(models.Model):
    """
    审批记录模型
    """
    
    class Action(models.TextChoices):
        APPROVED = 'approved', _('批准')
        REJECTED = 'rejected', _('拒绝')
        CANCELLED = 'cancelled', _('取消')
        SUBMITTED = 'submitted', _('提交')
    
    leave_application = models.ForeignKey(
        LeaveApplication,
        on_delete=models.CASCADE,
        related_name='approval_records',
        verbose_name='关联请假申请'
    )
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='审批人'
    )
    
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name='操作'
    )
    
    comment = models.TextField(
        blank=True,
        verbose_name='审批意见'
    )
    
    approval_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='审批时间'
    )
    
    class Meta:
        verbose_name = '审批记录'
        verbose_name_plural = '审批记录'
        db_table = 'approval_records'
        ordering = ['-approval_date']
    
    def __str__(self):
        return f"{self.approver.username if self.approver else '系统'} - {self.get_action_display()}"
