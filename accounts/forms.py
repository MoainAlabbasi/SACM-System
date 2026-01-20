"""
نماذج المصادقة والتفعيل
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class LoginForm(forms.Form):
    """نموذج تسجيل الدخول"""
    academic_id = forms.CharField(
        label='الرقم الأكاديمي/الوظيفي',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل الرقم الأكاديمي',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        academic_id = cleaned_data.get('academic_id')
        password = cleaned_data.get('password')
        
        if academic_id and password:
            # التحقق من وجود المستخدم
            try:
                user = User.objects.get(academic_id=academic_id)
                
                # التحقق من حالة الحساب
                if user.account_status == 'inactive':
                    raise forms.ValidationError(
                        'حسابك غير مفعّل. يرجى الضغط على "إنشاء حساب" لتفعيل حسابك.',
                        code='inactive_account'
                    )
                elif user.account_status == 'suspended':
                    raise forms.ValidationError(
                        'حسابك موقوف. يرجى التواصل مع الإدارة.',
                        code='suspended_account'
                    )
                
                # التحقق من كلمة المرور
                user = authenticate(academic_id=academic_id, password=password)
                if user is None:
                    raise forms.ValidationError('كلمة المرور غير صحيحة.')
                
                cleaned_data['user'] = user
                
            except User.DoesNotExist:
                raise forms.ValidationError('الرقم الأكاديمي غير موجود في النظام.')
        
        return cleaned_data


class IdentityVerificationForm(forms.Form):
    """نموذج التحقق من الهوية (الخطوة الأولى من التفعيل)"""
    academic_id = forms.CharField(
        label='الرقم الأكاديمي/الوظيفي',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل الرقم الأكاديمي',
            'autofocus': True
        })
    )
    id_card_number = forms.CharField(
        label='رقم البطاقة الشخصية',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل رقم البطاقة الشخصية'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        academic_id = cleaned_data.get('academic_id')
        id_card_number = cleaned_data.get('id_card_number')
        
        if academic_id and id_card_number:
            try:
                user = User.objects.get(
                    academic_id=academic_id,
                    id_card_number=id_card_number
                )
                
                if user.account_status == 'active':
                    raise forms.ValidationError('هذا الحساب مفعّل بالفعل. يمكنك تسجيل الدخول.')
                
                cleaned_data['user'] = user
                
            except User.DoesNotExist:
                raise forms.ValidationError(
                    'البيانات المدخلة غير صحيحة. يرجى مراجعة قسم شؤون الطلاب/الموظفين.'
                )
        
        return cleaned_data


class EmailForm(forms.Form):
    """نموذج إدخال البريد الإلكتروني"""
    email = forms.EmailField(
        label='البريد الإلكتروني',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل بريدك الإلكتروني',
            'autofocus': True
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مستخدم بالفعل.')
        return email


class OTPVerificationForm(forms.Form):
    """نموذج التحقق من رمز OTP"""
    otp_code = forms.CharField(
        label='رمز التحقق',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-center',
            'placeholder': '000000',
            'style': 'font-size: 24px; letter-spacing: 10px;',
            'autofocus': True,
            'maxlength': '6'
        })
    )


class SetPasswordForm(forms.Form):
    """نموذج تعيين كلمة المرور"""
    password = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الجديدة',
            'autofocus': True
        })
    )
    password_confirm = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('كلمتا المرور غير متطابقتين.')
            
            # التحقق من قوة كلمة المرور
            try:
                validate_password(password)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)
        
        return cleaned_data


class ForgotPasswordForm(forms.Form):
    """نموذج نسيت كلمة المرور"""
    academic_id = forms.CharField(
        label='الرقم الأكاديمي/الوظيفي',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل الرقم الأكاديمي',
            'autofocus': True
        })
    )
    
    def clean_academic_id(self):
        academic_id = self.cleaned_data.get('academic_id')
        try:
            user = User.objects.get(academic_id=academic_id)
            if not user.email:
                raise forms.ValidationError('لم يتم تسجيل بريد إلكتروني لهذا الحساب.')
            if user.account_status != 'active':
                raise forms.ValidationError('هذا الحساب غير مفعّل.')
            self.user = user
        except User.DoesNotExist:
            raise forms.ValidationError('الرقم الأكاديمي غير موجود.')
        return academic_id


class ResetPasswordForm(forms.Form):
    """نموذج إعادة تعيين كلمة المرور"""
    password = forms.CharField(
        label='كلمة المرور الجديدة',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أدخل كلمة المرور الجديدة',
            'autofocus': True
        })
    )
    password_confirm = forms.CharField(
        label='تأكيد كلمة المرور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'أعد إدخال كلمة المرور'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('كلمتا المرور غير متطابقتين.')
            try:
                validate_password(password)
            except forms.ValidationError as e:
                raise forms.ValidationError(e.messages)
        
        return cleaned_data
