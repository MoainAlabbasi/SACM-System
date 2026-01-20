"""
عروض المصادقة والتفعيل
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from .forms import (
    LoginForm, IdentityVerificationForm, EmailForm,
    OTPVerificationForm, SetPasswordForm, ForgotPasswordForm, ResetPasswordForm
)
from .models import User, VerificationCode, PasswordResetToken, UserActivity
from .email_service import send_otp_email, send_password_reset_email


def login_view(request):
    """صفحة تسجيل الدخول"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=get_client_ip(request)
            )
            
            messages.success(request, f'مرحباً {user.full_name}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('core:dashboard_redirect')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """تسجيل الخروج"""
    if request.user.is_authenticated:
        UserActivity.objects.create(
            user=request.user,
            action='logout',
            ip_address=get_client_ip(request)
        )
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('core:home')


def activate_step1_view(request):
    """الخطوة 1: التحقق من الهوية"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = IdentityVerificationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            request.session['activation_user_id'] = user.id
            return redirect('accounts:activate_step2')
    else:
        form = IdentityVerificationForm()
    
    return render(request, 'accounts/activate_step1.html', {'form': form})


def activate_step2_view(request):
    """الخطوة 2: إدخال البريد الإلكتروني وإرسال OTP"""
    user_id = request.session.get('activation_user_id')
    if not user_id:
        messages.error(request, 'يرجى البدء من الخطوة الأولى.')
        return redirect('accounts:activate_step1')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'حدث خطأ. يرجى المحاولة مرة أخرى.')
        return redirect('accounts:activate_step1')
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            otp = VerificationCode.generate_code(user, email)
            
            if send_otp_email(user, otp.code, email):
                request.session['activation_email'] = email
                request.session['activation_otp_id'] = otp.id
                messages.success(request, f'تم إرسال رمز التحقق إلى {email}')
                return redirect('accounts:activate_step3')
            else:
                messages.error(request, 'فشل إرسال البريد الإلكتروني. يرجى المحاولة لاحقاً.')
    else:
        form = EmailForm()
    
    return render(request, 'accounts/activate_step2.html', {'form': form, 'user': user})


def activate_step3_view(request):
    """الخطوة 3: التحقق من OTP"""
    user_id = request.session.get('activation_user_id')
    otp_id = request.session.get('activation_otp_id')
    
    if not user_id or not otp_id:
        messages.error(request, 'يرجى البدء من الخطوة الأولى.')
        return redirect('accounts:activate_step1')
    
    try:
        user = User.objects.get(id=user_id)
        otp = VerificationCode.objects.get(id=otp_id)
    except (User.DoesNotExist, VerificationCode.DoesNotExist):
        messages.error(request, 'حدث خطأ. يرجى المحاولة مرة أخرى.')
        return redirect('accounts:activate_step1')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_code = form.cleaned_data['otp_code']
            
            if otp.code == entered_code and otp.is_valid():
                otp.is_used = True
                otp.save()
                request.session['otp_verified'] = True
                return redirect('accounts:activate_step4')
            else:
                messages.error(request, 'رمز التحقق غير صحيح أو منتهي الصلاحية.')
    else:
        form = OTPVerificationForm()
    
    email = request.session.get('activation_email', '')
    return render(request, 'accounts/activate_step3.html', {'form': form, 'email': email})


def activate_step4_view(request):
    """الخطوة 4: تعيين كلمة المرور"""
    user_id = request.session.get('activation_user_id')
    otp_verified = request.session.get('otp_verified')
    email = request.session.get('activation_email')
    
    if not user_id or not otp_verified:
        messages.error(request, 'يرجى البدء من الخطوة الأولى.')
        return redirect('accounts:activate_step1')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'حدث خطأ. يرجى المحاولة مرة أخرى.')
        return redirect('accounts:activate_step1')
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            
            user.set_password(password)
            user.email = email
            user.account_status = 'active'
            user.save()
            
            for key in ['activation_user_id', 'activation_email', 'activation_otp_id', 'otp_verified']:
                request.session.pop(key, None)
            
            messages.success(request, 'تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('accounts:login')
    else:
        form = SetPasswordForm()
    
    return render(request, 'accounts/activate_step4.html', {'form': form})


def forgot_password_view(request):
    """صفحة نسيت كلمة المرور"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = form.user
            
            token = PasswordResetToken.generate_token(user)
            
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', args=[token.token])
            )
            
            if send_password_reset_email(user, reset_url):
                messages.success(request, 'تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.')
            else:
                messages.error(request, 'فشل إرسال البريد الإلكتروني. يرجى المحاولة لاحقاً.')
            
            return redirect('accounts:login')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    """صفحة إعادة تعيين كلمة المرور"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(request, 'رابط إعادة التعيين منتهي الصلاحية أو مستخدم.')
            return redirect('accounts:forgot_password')
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'رابط إعادة التعيين غير صالح.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            reset_token.is_used = True
            reset_token.save()
            
            messages.success(request, 'تم تغيير كلمة المرور بنجاح! يمكنك الآن تسجيل الدخول.')
            return redirect('accounts:login')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'accounts/reset_password.html', {'form': form})


def resend_otp_view(request):
    """إعادة إرسال رمز التحقق"""
    user_id = request.session.get('activation_user_id')
    email = request.session.get('activation_email')
    
    if not user_id or not email:
        messages.error(request, 'يرجى البدء من الخطوة الأولى.')
        return redirect('accounts:activate_step1')
    
    try:
        user = User.objects.get(id=user_id)
        
        otp = VerificationCode.generate_code(user, email)
        
        if send_otp_email(user, otp.code, email):
            request.session['activation_otp_id'] = otp.id
            messages.success(request, 'تم إرسال رمز تحقق جديد.')
        else:
            messages.error(request, 'فشل إرسال البريد الإلكتروني.')
        
    except User.DoesNotExist:
        messages.error(request, 'حدث خطأ.')
    
    return redirect('accounts:activate_step3')


def get_client_ip(request):
    """الحصول على عنوان IP للمستخدم"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
