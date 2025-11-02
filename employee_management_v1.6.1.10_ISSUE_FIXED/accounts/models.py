"""
用户和权限管理模型
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    自定义用户模型
    """
    
    class Role(models.TextChoices):
        SUPERUSER = 'superuser', _('超级管理员')
        HEAD_MANAGER = 'head_manager', _('总部负责人')
        TASK_AREA_MANAGER = 'task_area_manager', _('任务区负责人')
        EMPLOYEE = 'employee', _('普通员工')
    
    # 护照信息
    passport_name_pinyin = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='护照姓名拼音',
        help_text='护照上的姓名拼音全称'
    )
    
    passport_number = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name='护照号码',
        help_text='护照号码'
    )
    
    passport_issue_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='护照签发日期',
        help_text='护照签发日期'
    )
    
    passport_expiry_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='护照到期日期',
        help_text='护照到期日期'
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='手机号码'
    )
    
    department_rank = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='部门',
        help_text='部门和职别信息，自由填写'
    )
    
    # 旧的任务区字段（字符串）
    task_area = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='任务区',
        help_text='工作任务区域'
    )
    
    # 新的任务区外键关联
    task_area_fk = models.ForeignKey(
        'TaskArea',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        verbose_name='任务区关联',
        help_text='所属任务区（外键）'
    )
    
    # 多任务区关联（用于总部负责人）
    managed_task_areas = models.ManyToManyField(
        'TaskArea',
        blank=True,
        related_name='managers',
        verbose_name='管辖任务区',
        help_text='总部负责人可管理的任务区'
    )
    
    position = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='职位'
    )
    
    employment_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='在职开始时间',
        help_text='在职开始日期'
    )
    
    employment_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='在职结束时间',
        help_text='在职结束日期（如仍在职可留空）'
    )
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name='角色'
    )
    
    # 位置信息
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='纬度',
        help_text='当前位置纬度'
    )
    
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='经度',
        help_text='当前位置经度'
    )
    
    location_address = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='详细地址',
        help_text='当前位置的详细地址'
    )
    
    location_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='位置更新时间'
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
        verbose_name = '用户'
        verbose_name_plural = '用户'
        db_table = 'users'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_superuser_role(self):
        """是否为超级管理员角色"""
        return self.role == self.Role.SUPERUSER
    
    @property
    def is_head_manager(self):
        """是否为总部负责人"""
        return self.role == self.Role.HEAD_MANAGER
    
    @property
    def is_task_area_manager(self):
        """是否为任务区负责人"""
        return self.role == self.Role.TASK_AREA_MANAGER
    
    @property
    def is_employee(self):
        """是否为普通员工"""
        return self.role == self.Role.EMPLOYEE
    
    @property
    def can_approve_leave(self):
        """是否有审批权限"""
        return self.role in [self.Role.HEAD_MANAGER, self.Role.TASK_AREA_MANAGER]
    
    @property
    def needs_leave_approval(self):
        """是否需要请假审批（超级管理员和总部负责人不需要请假）"""
        return self.role in [self.Role.TASK_AREA_MANAGER, self.Role.EMPLOYEE]
    
    def get_accessible_task_areas(self):
        """获取用户可访问的任务区"""
        if self.role == self.Role.SUPERUSER:
            # 超级管理员可以访问所有任务区
            return TaskArea.objects.all()
        elif self.role == self.Role.HEAD_MANAGER:
            # 总部负责人可以访问其管辖的任务区
            return self.managed_task_areas.all()
        elif self.role in [self.Role.TASK_AREA_MANAGER, self.Role.EMPLOYEE]:
            # 任务区负责人和普通员工只能访问自己的任务区
            if self.task_area_fk:
                return TaskArea.objects.filter(id=self.task_area_fk.id)
            return TaskArea.objects.none()
        return TaskArea.objects.none()
    
    def can_manage_user(self, target_user):
        """检查是否可以管理目标用户"""
        if self.role == self.Role.SUPERUSER:
            return True
        elif self.role == self.Role.HEAD_MANAGER:
            # 总部负责人可以管理其管辖任务区内的用户
            if target_user.task_area_fk:
                return self.managed_task_areas.filter(id=target_user.task_area_fk.id).exists()
            return False
        elif self.role == self.Role.TASK_AREA_MANAGER:
            # 任务区负责人只能管理同任务区的普通员工
            return (target_user.role == self.Role.EMPLOYEE and 
                    self.task_area_fk and target_user.task_area_fk and 
                    self.task_area_fk.id == target_user.task_area_fk.id)
        return False
    
    @property
    def task_area_obj(self):
        """获取任务区对象（临时兼容属性）"""
        return self.task_area_fk
    
    def save(self, *args, **kwargs):
        # 如果是超级管理员角色，自动设置为超级用户
        if self.role == self.Role.SUPERUSER:
            self.is_superuser = True
            self.is_staff = True
        super().save(*args, **kwargs)


class TaskArea(models.Model):
    """
    任务区域管理
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='任务区名称'
    )
    
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    class Meta:
        verbose_name = '任务区'
        verbose_name_plural = '任务区'
        db_table = 'task_areas'
    
    def __str__(self):
        return self.name
    
    @property
    def task_area_manager(self):
        """获取该任务区的负责人"""
        return self.users.filter(role=User.Role.TASK_AREA_MANAGER).first()
    
    @property  
    def employees_count(self):
        """获取该任务区的员工数量"""
        return self.users.filter(role=User.Role.EMPLOYEE).count()
    
    @property
    def all_users_count(self):
        """获取该任务区的总用户数量"""
        return self.users.count()
