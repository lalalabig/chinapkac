"""
用户认证相关视图
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils.translation import gettext_lazy as _
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User
from accounts.permissions import get_user_permissions, get_role_display_name


class CustomLoginView(LoginView):
    """
    自定义登录视图
    """
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard:home')
    
    def form_valid(self, form):
        messages.success(self.request, f'欢迎回来，{form.get_user().username}！')
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """
    自定义登出视图
    """
    next_page = reverse_lazy('accounts:login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.info(request, '您已成功登出。')
        return super().dispatch(request, *args, **kwargs)


class RegisterView(CreateView):
    """
    用户注册视图
    """
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        messages.success(self.request, f'注册成功！欢迎您，{username}！请登录您的账户。')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """
    用户个人信息查看
    """
    user_permissions = get_user_permissions(request.user)
    
    context = {
        'user': request.user,
        'permissions': user_permissions,
        'role_display': get_role_display_name(request.user.role),
    }
    return render(request, 'accounts/profile.html', context)


@login_required  
def edit_profile_view(request):
    """
    编辑个人信息
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '个人信息更新成功！')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
def change_password_view(request):
    """
    修改密码
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # 保持用户登录状态
            messages.success(request, '密码修改成功！')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'user': request.user
    }
    return render(request, 'accounts/change_password.html', context)


def register_view(request):
    """
    用户注册视图（函数式）
    """
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'注册成功！欢迎您，{username}！请登录您的账户。')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
