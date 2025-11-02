"""
用户认证相关表单
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User, TaskArea


class CustomUserCreationForm(UserCreationForm):
    """
    自定义用户注册表单
    """
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入邮箱地址'
        })
    )
    
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入手机号码'
        })
    )
    
    department_rank = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入部门'
        })
    )
    
    task_area = forms.ModelChoiceField(
        queryset=TaskArea.objects.all(),
        required=False,
        empty_label='请选择任务区',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    position = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '请输入职位'
        })
    )
    
    # 护照信息字段
    passport_name_pinyin = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '护照姓名拼音全称'
        })
    )
    
    passport_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '护照号码'
        })
    )
    
    passport_issue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    passport_expiry_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    # 在职时间字段
    employment_start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    employment_end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    

    
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    # 总部负责人管辖的任务区（多选）
    managed_task_areas = forms.ModelMultipleChoiceField(
        queryset=TaskArea.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text='仅总部负责人需要设置，可选择多个任务区'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 
                 'department_rank', 'task_area', 'position', 'passport_name_pinyin',
                 'passport_number', 'passport_issue_date', 'passport_expiry_date',
                 'employment_start_date', 'employment_end_date', 'role', 'managed_task_areas')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入用户名'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请输入密码'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '请再次输入密码'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.department_rank = self.cleaned_data['department_rank']
        user.position = self.cleaned_data['position']
        
        # 护照信息
        user.passport_name_pinyin = self.cleaned_data['passport_name_pinyin']
        user.passport_number = self.cleaned_data['passport_number']
        user.passport_issue_date = self.cleaned_data['passport_issue_date']
        user.passport_expiry_date = self.cleaned_data['passport_expiry_date']
        
        # 在职时间
        user.employment_start_date = self.cleaned_data['employment_start_date']
        user.employment_end_date = self.cleaned_data['employment_end_date']
        
        # 角色和任务区
        user.role = self.cleaned_data['role']
        user.task_area_fk = self.cleaned_data['task_area']
        
        if commit:
            user.save()
            # 处理总部负责人的多任务区关联
            if user.role == User.Role.HEAD_MANAGER:
                managed_areas = self.cleaned_data.get('managed_task_areas')
                if managed_areas:
                    user.managed_task_areas.set(managed_areas)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """
    自定义登录表单
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '用户名',
            'autofocus': True
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '密码'
        })


class UserProfileForm(forms.ModelForm):
    """
    用户个人信息编辑表单
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'passport_name_pinyin', 
                 'passport_number', 'passport_issue_date', 'passport_expiry_date', 
                 'employment_start_date', 'employment_end_date', 'phone_number', 
                 'department_rank', 'task_area', 'position']
        
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '姓名'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '姓氏'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': '邮箱地址'
            }),
            'passport_name_pinyin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '护照姓名拼音全称'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '护照号码'
            }),
            'passport_issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'passport_expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employment_start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'employment_end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '手机号码'
            }),
            'department_rank': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '部门'
            }),
            'task_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '任务区'
            }),
            'position': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '职位'
            }),

        }
