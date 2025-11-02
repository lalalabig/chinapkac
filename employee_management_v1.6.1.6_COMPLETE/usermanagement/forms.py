"""
用户管理表单
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from accounts.models import User, TaskArea


class UserCreateForm(forms.ModelForm):
    """创建用户表单"""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='密码',
        help_text='至少6个字符，包含字母和数字'
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='确认密码'
    )
    
    # 任务区相关字段
    task_area_fk = forms.ModelChoiceField(
        queryset=TaskArea.objects.all(),
        required=False,
        empty_label="请选择任务区",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='任务区'
    )
    
    new_task_area = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='新任务区名称'
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'role', 'phone_number', 
            'department_rank', 'position',
            'passport_name_pinyin', 'passport_number', 'passport_issue_date', 'passport_expiry_date',
            'employment_start_date', 'employment_end_date'
        ]
        labels = {
            'username': '用户名',
            'email': '邮箱',
            'first_name': '姓',
            'last_name': '名',
            'role': '角色',
            'phone_number': '手机号码',
            'department_rank': '部门',
            'position': '职位',
            'passport_name_pinyin': '护照姓名拼音',
            'passport_number': '护照号码',
            'passport_issue_date': '护照签发日期',
            'passport_expiry_date': '护照到期日期',
            'employment_start_date': '在职开始时间',
            'employment_end_date': '在职结束时间',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department_rank': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_name_pinyin': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employment_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employment_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('两次输入的密码不一致。')
        
        return confirm_password

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                raise ValidationError('用户名已存在，请选择其他用户名。')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # 检查邮箱是否已存在
            if User.objects.filter(email=email).exists():
                raise ValidationError('该邮箱已被使用，请使用其他邮箱。')
        return email

    def clean_passport_number(self):
        passport_number = self.cleaned_data.get('passport_number')
        if passport_number:
            # 检查护照号码是否已存在
            if User.objects.filter(passport_number=passport_number).exists():
                raise ValidationError('该护照号码已被使用，请检查输入是否正确。')
        return passport_number

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            # 自定义简单密码验证：只需要大于6位，包含字母和数字
            if len(password) < 6:
                raise ValidationError('密码长度至少6位。')
            
            has_letter = any(c.isalpha() for c in password)
            has_digit = any(c.isdigit() for c in password)
            
            if not has_letter:
                raise ValidationError('密码必须包含至少一个字母。')
            if not has_digit:
                raise ValidationError('密码必须包含至少一个数字。')
        
        return password
    
    def clean_new_task_area(self):
        new_task_area = self.cleaned_data.get('new_task_area')
        if new_task_area:
            # 检查任务区名称是否已存在
            if TaskArea.objects.filter(name=new_task_area).exists():
                raise ValidationError('该任务区已存在，请选择其他名称。')
            # 检查名称长度
            if len(new_task_area.strip()) < 2:
                raise ValidationError('任务区名称至少2个字符。')
        return new_task_area

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        task_area_fk = cleaned_data.get('task_area_fk')
        new_task_area = cleaned_data.get('new_task_area')
        
        # 验证任务区分配规则
        if role == User.Role.SUPERUSER:
            # 超级管理员不需要任务区，系统自动分配"全球"
            pass
        elif role in [User.Role.TASK_AREA_MANAGER, User.Role.EMPLOYEE]:
            # 任务区负责人和普通员工必须有任务区
            if not task_area_fk and not new_task_area:
                raise ValidationError('任务区负责人和普通员工必须分配任务区。')
        elif role == User.Role.HEAD_MANAGER:
            # 总部负责人在视图中处理多任务区逻辑
            pass
            
        return cleaned_data


class UserEditForm(forms.ModelForm):
    """编辑用户表单"""
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='新密码',
        required=False,
        help_text='留空则不修改密码'
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label='确认新密码',
        required=False
    )
    
    # 任务区相关字段
    task_area_fk = forms.ModelChoiceField(
        queryset=TaskArea.objects.all(),
        required=False,
        empty_label="请选择任务区",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='任务区'
    )
    
    new_task_area = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='新任务区名称'
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'role', 'phone_number', 
            'department_rank', 'position',
            'passport_name_pinyin', 'passport_number', 'passport_issue_date', 'passport_expiry_date',
            'employment_start_date', 'employment_end_date', 'is_active'
        ]
        labels = {
            'username': '用户名',
            'email': '邮箱',
            'first_name': '姓',
            'last_name': '名',
            'role': '角色',
            'phone_number': '手机号码',
            'department_rank': '部门',
            'position': '职位',
            'passport_name_pinyin': '护照姓名拼音',
            'passport_number': '护照号码',
            'passport_issue_date': '护照签发日期',
            'passport_expiry_date': '护照到期日期',
            'employment_start_date': '在职开始时间',
            'employment_end_date': '在职结束时间',
            'is_active': '激活状态',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'department_rank': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_name_pinyin': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_number': forms.TextInput(attrs={'class': 'form-control'}),
            'passport_issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'passport_expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employment_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'employment_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_confirm_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_new_password = self.cleaned_data.get('confirm_new_password')
        
        if new_password and confirm_new_password:
            if new_password != confirm_new_password:
                raise ValidationError('两次输入的新密码不一致。')
        elif new_password and not confirm_new_password:
            raise ValidationError('请确认新密码。')
        
        return confirm_new_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            # 自定义简单密码验证：只需要大于6位，包含字母和数字
            if len(new_password) < 6:
                raise ValidationError('密码长度至少6位。')
            
            has_letter = any(c.isalpha() for c in new_password)
            has_digit = any(c.isdigit() for c in new_password)
            
            if not has_letter:
                raise ValidationError('密码必须包含至少一个字母。')
            if not has_digit:
                raise ValidationError('密码必须包含至少一个数字。')
        
        return new_password
        
    def clean_new_task_area(self):
        new_task_area = self.cleaned_data.get('new_task_area')
        if new_task_area:
            # 检查任务区名称是否已存在
            if TaskArea.objects.filter(name=new_task_area).exists():
                raise ValidationError('该任务区已存在，请选择其他名称。')
            # 检查名称长度
            if len(new_task_area.strip()) < 2:
                raise ValidationError('任务区名称至少2个字符。')
        return new_task_area

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        task_area_fk = cleaned_data.get('task_area_fk')
        new_task_area = cleaned_data.get('new_task_area')
        
        # 验证任务区分配规则
        if role == User.Role.SUPERUSER:
            # 超级管理员不需要任务区，系统自动分配"全球"
            pass
        elif role in [User.Role.TASK_AREA_MANAGER, User.Role.EMPLOYEE]:
            # 任务区负责人和普通员工必须有任务区
            if not task_area_fk and not new_task_area:
                raise ValidationError('任务区负责人和普通员工必须分配任务区。')
        elif role == User.Role.HEAD_MANAGER:
            # 总部负责人在视图中处理多任务区逻辑
            pass
            
        return cleaned_data
