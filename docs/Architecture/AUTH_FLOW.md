# تدفق المصادقة والتفعيل

## نظرة عامة

يوفر النظام آلية مصادقة متعددة الخطوات لضمان أمان الحسابات.

## 1. تسجيل الدخول

### 1.1 مخطط التدفق

```
┌─────────────────┐
│   صفحة الدخول   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  إدخال البيانات │
│ الرقم الأكاديمي │
│  + كلمة المرور  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ✗
│  التحقق من     │────────────┐
│   البيانات     │            │
└────────┬────────┘            │
         │ ✓                   │
         ▼                     ▼
┌─────────────────┐    ┌─────────────────┐
│  التحقق من     │    │   رسالة خطأ    │
│ حالة الحساب    │    │                 │
└────────┬────────┘    └─────────────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌───────┐ ┌───────────┐
│ active│ │  pending  │
└───┬───┘ └─────┬─────┘
    │           │
    ▼           ▼
┌───────────┐ ┌───────────┐
│  لوحة    │ │  صفحة    │
│  التحكم  │ │  التفعيل │
└───────────┘ └───────────┘
```

### 1.2 الكود

```python
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            
            # تسجيل الدخول
            login(request, user)
            
            # تسجيل النشاط
            UserActivity.objects.create(
                user=user,
                action='login',
                ip_address=get_client_ip(request)
            )
            
            # إعادة التوجيه
            return redirect('core:dashboard_redirect')
    
    return render(request, 'accounts/login.html', {'form': form})
```

## 2. تفعيل الحساب

### 2.1 الخطوات الأربع

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         تفعيل الحساب                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ الخطوة 1 │───▶│ الخطوة 2 │───▶│ الخطوة 3 │───▶│ الخطوة 4 │          │
│  │          │    │          │    │          │    │          │          │
│  │ التحقق   │    │ البريد   │    │   OTP    │    │ كلمة     │          │
│  │ من       │    │ الإلكتروني│    │          │    │ المرور   │          │
│  │ الهوية   │    │          │    │          │    │          │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │               │               │               │                 │
│       ▼               ▼               ▼               ▼                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ الرقم    │    │ إرسال    │    │ التحقق   │    │ تفعيل    │          │
│  │ الأكاديمي│    │ OTP      │    │ من الرمز │    │ الحساب   │          │
│  │ + الهوية │    │ للبريد   │    │          │    │          │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 الخطوة 1: التحقق من الهوية

**الغرض:** التأكد من أن المستخدم موجود في النظام

**المدخلات:**
- الرقم الأكاديمي
- رقم الهوية الوطنية

**المخرجات:**
- نجاح: الانتقال للخطوة 2
- فشل: رسالة خطأ

```python
def activate_step1_view(request):
    if request.method == 'POST':
        form = IdentityVerificationForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            request.session['activation_user_id'] = user.id
            return redirect('accounts:activate_step2')
    
    return render(request, 'accounts/activate_step1.html', {'form': form})
```

### 2.3 الخطوة 2: البريد الإلكتروني

**الغرض:** ربط البريد الإلكتروني بالحساب وإرسال OTP

**المدخلات:**
- البريد الإلكتروني

**المخرجات:**
- إرسال رمز OTP (6 أرقام) للبريد
- صلاحية الرمز: 10 دقائق

```python
def activate_step2_view(request):
    user_id = request.session.get('activation_user_id')
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            # إنشاء OTP
            otp = VerificationCode.generate_code(user, email)
            
            # إرسال البريد
            send_otp_email(user, otp.code, email)
            
            request.session['activation_email'] = email
            request.session['activation_otp_id'] = otp.id
            
            return redirect('accounts:activate_step3')
    
    return render(request, 'accounts/activate_step2.html', {'form': form})
```

### 2.4 الخطوة 3: التحقق من OTP

**الغرض:** التأكد من ملكية البريد الإلكتروني

**المدخلات:**
- رمز OTP (6 أرقام)

**المخرجات:**
- نجاح: الانتقال للخطوة 4
- فشل: رسالة خطأ (رمز خاطئ أو منتهي)

```python
def activate_step3_view(request):
    user_id = request.session.get('activation_user_id')
    otp_id = request.session.get('activation_otp_id')
    
    otp = VerificationCode.objects.get(id=otp_id)
    
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
                messages.error(request, 'رمز التحقق غير صحيح')
    
    return render(request, 'accounts/activate_step3.html', {'form': form})
```

### 2.5 الخطوة 4: تعيين كلمة المرور

**الغرض:** إنشاء كلمة مرور للحساب

**المدخلات:**
- كلمة المرور الجديدة
- تأكيد كلمة المرور

**متطلبات كلمة المرور:**
- 8 أحرف على الأقل
- حرف كبير واحد على الأقل
- حرف صغير واحد على الأقل
- رقم واحد على الأقل

```python
def activate_step4_view(request):
    user_id = request.session.get('activation_user_id')
    email = request.session.get('activation_email')
    
    user = User.objects.get(id=user_id)
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            
            # تحديث المستخدم
            user.set_password(password)
            user.email = email
            user.account_status = 'active'
            user.save()
            
            # مسح الجلسة
            for key in ['activation_user_id', 'activation_email', 
                       'activation_otp_id', 'otp_verified']:
                request.session.pop(key, None)
            
            messages.success(request, 'تم تفعيل حسابك بنجاح!')
            return redirect('accounts:login')
    
    return render(request, 'accounts/activate_step4.html', {'form': form})
```

## 3. نسيت كلمة المرور

### 3.1 مخطط التدفق

```
┌─────────────────┐
│  نسيت كلمة     │
│   المرور       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  إدخال البريد  │
│  الإلكتروني    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ✗
│  التحقق من     │────────────┐
│  وجود البريد   │            │
└────────┬────────┘            │
         │ ✓                   │
         ▼                     ▼
┌─────────────────┐    ┌─────────────────┐
│  إنشاء رمز     │    │  رسالة عامة    │
│  إعادة التعيين │    │  (للأمان)      │
└────────┬────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐
│  إرسال الرابط  │
│  للبريد        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  المستخدم      │
│  يفتح الرابط   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  تعيين كلمة    │
│  مرور جديدة   │
└─────────────────┘
```

### 3.2 الكود

```python
def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            user = form.user
            
            # إنشاء رمز
            token = PasswordResetToken.generate_token(user)
            
            # إنشاء الرابط
            reset_url = request.build_absolute_uri(
                reverse('accounts:reset_password', args=[token.token])
            )
            
            # إرسال البريد
            send_password_reset_email(user, reset_url)
            
            messages.success(request, 'تم إرسال رابط إعادة التعيين')
            return redirect('accounts:login')
    
    return render(request, 'accounts/forgot_password.html', {'form': form})


def reset_password_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        
        if not reset_token.is_valid():
            messages.error(request, 'الرابط منتهي الصلاحية')
            return redirect('accounts:forgot_password')
        
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'رابط غير صالح')
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
            
            messages.success(request, 'تم تغيير كلمة المرور بنجاح!')
            return redirect('accounts:login')
    
    return render(request, 'accounts/reset_password.html', {'form': form})
```

## 4. الأمان

### 4.1 تشفير كلمات المرور

```python
# Django يستخدم PBKDF2 افتراضياً
user.set_password('plain_password')  # يشفر تلقائياً
user.check_password('plain_password')  # للتحقق
```

### 4.2 حماية الجلسات

```python
# settings.py
SESSION_COOKIE_SECURE = True  # HTTPS فقط
SESSION_COOKIE_HTTPONLY = True  # لا يمكن الوصول من JS
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### 4.3 حماية CSRF

```html
<!-- في كل form -->
<form method="post">
    {% csrf_token %}
    ...
</form>
```

### 4.4 Rate Limiting للمحاولات

```python
# يمكن إضافة django-axes للحماية من brute force
AXES_FAILURE_LIMIT = 5  # 5 محاولات فاشلة
AXES_COOLOFF_TIME = 1  # ساعة انتظار
```

## 5. قالب البريد الإلكتروني

### 5.1 OTP

```
الموضوع: رمز التحقق - S-ACM

مرحباً {full_name}،

رمز التحقق الخاص بك هو: {otp_code}

هذا الرمز صالح لمدة 10 دقائق.

إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.

مع تحيات،
فريق S-ACM
```

### 5.2 إعادة تعيين كلمة المرور

```
الموضوع: إعادة تعيين كلمة المرور - S-ACM

مرحباً {full_name}،

تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بك.

اضغط على الرابط التالي لإعادة تعيين كلمة المرور:
{reset_url}

هذا الرابط صالح لمدة ساعة واحدة.

إذا لم تطلب إعادة التعيين، يرجى تجاهل هذه الرسالة.

مع تحيات،
فريق S-ACM
```
