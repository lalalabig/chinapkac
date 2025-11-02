from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()

class EmergencyAlert(models.Model):
    """
    紧急报警模型
    """
    
    class AlertStatus(models.TextChoices):
        ACTIVE = 'active', '活跃'
        HANDLED = 'handled', '已处理'
        RESOLVED = 'resolved', '已解决'
        CANCELLED = 'cancelled', '已取消'
    
    class AlertType(models.TextChoices):
        EMERGENCY = 'emergency', '紧急情况'
        MEDICAL = 'medical', '医疗急救'
        SECURITY = 'security', '安全威胁'
        LOCATION = 'location', '位置报警'
        OTHER = 'other', '其他'
    
    # 报警基本信息
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_alerts',
        verbose_name='发送人'
    )
    
    # 报警类型和状态
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        default=AlertType.EMERGENCY,
        verbose_name='报警类型'
    )
    
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.ACTIVE,
        verbose_name='状态'
    )
    
    # 位置信息
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='纬度'
    )
    
    longitude = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='经度'
    )
    
    location_address = models.CharField(
        max_length=500,
        default='未知位置',
        verbose_name='地址描述'
    )
    
    # 报警详情
    alert_message = models.TextField(
        default='紧急情况报警',
        verbose_name='报警描述',
        help_text='请详细描述紧急情况'
    )
    
    # 处理信息
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_emergency_alerts',
        verbose_name='处理人'
    )
    
    handled_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='处理时间'
    )
    
    handling_notes = models.TextField(
        blank=True,
        verbose_name='处理说明'
    )
    
    # 通知信息
    notification_sent = models.BooleanField(
        default=False,
        verbose_name='是否已发送通知'
    )
    
    notification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='通知发送时间'
    )
    
    # 时间戳
    alert_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='报警时间'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        verbose_name = '紧急报警'
        verbose_name_plural = '紧急报警'
        db_table = 'emergency_alerts'
        ordering = ['-alert_time']
    
    def __str__(self):
        return f"{self.sender.get_full_name()} - {self.get_alert_type_display()} - {self.alert_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_urgent(self):
        """判断是否为紧急报警（5分钟内）"""
        if not self.alert_time:
            return False
        time_diff = timezone.now() - self.alert_time
        return time_diff.total_seconds() < 300  # 5分钟
    
    @property
    def duration_minutes(self):
        """计算报警持续时间（分钟）"""
        if not self.alert_time:
            return 0
        time_diff = timezone.now() - self.alert_time
        return int(time_diff.total_seconds() / 60)
    
    def mark_as_handled(self, handler, notes=''):
        """标记为已处理"""
        self.status = self.AlertStatus.HANDLED
        self.handled_by = handler
        self.handled_at = timezone.now()
        self.handling_notes = notes
        self.save()
    
    def mark_as_resolved(self, handler, notes=''):
        """标记为已解决"""
        self.status = self.AlertStatus.RESOLVED
        self.handled_by = handler
        self.handled_at = timezone.now()
        self.handling_notes = notes
        self.save()
    
    def send_notification(self):
        """发送通知（模拟实现）"""
        # 这里可以实现实际的通知逻辑
        # 如：发送邮件、短信、WebSocket通知等
        self.notification_sent = True
        self.notification_sent_at = timezone.now()
        self.save()
        
        # 记录通知日志
        NotificationLog.objects.create(
            alert=self,
            notification_type='browser',
            status='sent'
        )


class NotificationLog(models.Model):
    """
    通知日志
    """
    
    class NotificationType(models.TextChoices):
        BROWSER = 'browser', '浏览器通知'
        EMAIL = 'email', '邮件通知'
        SMS = 'sms', '短信通知'
        WEBSOCKET = 'websocket', 'WebSocket通知'
    
    class NotificationStatus(models.TextChoices):
        PENDING = 'pending', '待发送'
        SENT = 'sent', '已发送'
        FAILED = 'failed', '发送失败'
    
    alert = models.ForeignKey(
        EmergencyAlert,
        on_delete=models.CASCADE,
        related_name='notification_logs',
        verbose_name='关联报警'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        verbose_name='通知类型'
    )
    
    status = models.CharField(
        max_length=20,
        choices=NotificationStatus.choices,
        default=NotificationStatus.PENDING,
        verbose_name='状态'
    )
    
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='发送时间'
    )
    
    error_message = models.TextField(
        blank=True,
        verbose_name='错误信息'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '通知日志'
        verbose_name_plural = '通知日志'
        db_table = 'notification_logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert} - {self.get_notification_type_display()} - {self.get_status_display()}"


class EmergencyContact(models.Model):
    """
    紧急联系人
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='emergency_contacts',
        verbose_name='用户'
    )
    
    contact_name = models.CharField(max_length=100, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=20, verbose_name='联系电话')
    contact_email = models.EmailField(blank=True, verbose_name='联系邮箱')
    relationship = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='关系'
    )
    
    is_primary = models.BooleanField(default=False, verbose_name='是否为主要联系人')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '紧急联系人'
        verbose_name_plural = '紧急联系人'
        db_table = 'emergency_contacts'
        ordering = ['-is_primary', 'contact_name']
    
    def __str__(self):
        return f"{self.contact_name} ({self.contact_phone})"
