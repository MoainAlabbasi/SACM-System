"""
نماذج إدارة المستخدمين والأدوار والصلاحيات
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
import secrets


class Role(models.Model):
    """جدول الأدوار - Admin, Instructor, Student"""
    ADMIN = 'admin'
    INSTRUCTOR = 'instructor'
    STUDENT = 'student'
    
    ROLE_CHOICES = [
        (ADMIN, 'مسؤول'),
        (INSTRUCTOR, 'مدرس'),
        (STUDENT, 'طالب'),
    ]
    
    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES, verbose_name='اسم الدور')
    description = models.TextField(blank=True, null=True, verbose_name='وصف الدور')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'دور'
        verbose_name_plural = 'الأدوار'
    
    def __str__(self):
        return self.get_name_display()


class Permission(models.Model):
    """جدول الصلاحيات"""
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم الصلاحية')
    codename = models.CharField(max_length=100, unique=True, verbose_name='الرمز البرمجي')
    description = models.TextField(blank=True, null=True, verbose_name='وصف الصلاحية')
    
    class Meta:
        verbose_name = 'صلاحية'
        verbose_name_plural = 'الصلاحيات'
    
    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """جدول ربط الأدوار بالصلاحيات"""
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_permissions')
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name='permission_roles')
    
    class Meta:
        verbose_name = 'صلاحية الدور'
        verbose_name_plural = 'صلاحيات الأدوار'
        unique_together = ['role', 'permission']
    
    def __str__(self):
        return f"{self.role} - {self.permission}"


class Major(models.Model):
    """جدول التخصصات"""
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم التخصص')
    description = models.TextField(blank=True, null=True, verbose_name='وصف التخصص')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'تخصص'
        verbose_name_plural = 'التخصصات'
    
    def __str__(self):
        return self.name


class Level(models.Model):
    """جدول المستويات الدراسية"""
    name = models.CharField(max_length=50, unique=True, verbose_name='اسم المستوى')
    level_number = models.PositiveIntegerField(unique=True, verbose_name='رقم المستوى')
    
    class Meta:
        verbose_name = 'مستوى'
        verbose_name_plural = 'المستويات'
        ordering = ['level_number']
    
    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """مدير المستخدمين المخصص"""
    
    def create_user(self, academic_id, password=None, **extra_fields):
        if not academic_id:
            raise ValueError('الرقم الأكاديمي مطلوب')
        user = self.model(academic_id=academic_id, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, academic_id, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('account_status', 'active')
        return self.create_user(academic_id, password, **extra_fields)


class User(AbstractUser):
    """نموذج المستخدم المخصص"""
    
    ACCOUNT_STATUS_CHOICES = [
        ('inactive', 'غير مفعل'),
        ('active', 'مفعل'),
        ('suspended', 'موقوف'),
    ]
    
    username = None
    
    academic_id = models.CharField(max_length=50, unique=True, verbose_name='الرقم الأكاديمي/الوظيفي')
    id_card_number = models.CharField(max_length=50, unique=True, verbose_name='رقم البطاقة الشخصية')
    full_name = models.CharField(max_length=150, verbose_name='الاسم الكامل')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='البريد الإلكتروني')
    
    account_status = models.CharField(
        max_length=20, 
        choices=ACCOUNT_STATUS_CHOICES, 
        default='inactive',
        verbose_name='حالة الحساب'
    )
    
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users', verbose_name='الدور')
    major = models.ForeignKey(Major, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='التخصص')
    level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name='students', verbose_name='المستوى')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    objects = UserManager()
    
    USERNAME_FIELD = 'academic_id'
    REQUIRED_FIELDS = ['full_name', 'id_card_number']
    
    class Meta:
        verbose_name = 'مستخدم'
        verbose_name_plural = 'المستخدمين'
    
    def __str__(self):
        return f"{self.full_name} ({self.academic_id})"
    
    def is_admin(self):
        return self.role and self.role.name == Role.ADMIN
    
    def is_instructor(self):
        return self.role and self.role.name == Role.INSTRUCTOR
    
    def is_student(self):
        return self.role and self.role.name == Role.STUDENT
    
    def has_permission(self, codename):
        if not self.role:
            return False
        return RolePermission.objects.filter(role=self.role, permission__codename=codename).exists()


class VerificationCode(models.Model):
    """جدول رموز التحقق OTP"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(max_length=10, verbose_name='رمز التحقق')
    email = models.EmailField(verbose_name='البريد الإلكتروني')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    is_used = models.BooleanField(default=False, verbose_name='مستخدم')
    
    class Meta:
        verbose_name = 'رمز تحقق'
        verbose_name_plural = 'رموز التحقق'
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    @classmethod
    def generate_code(cls, user, email, expiry_minutes=10):
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        expires_at = timezone.now() + timezone.timedelta(minutes=expiry_minutes)
        return cls.objects.create(user=user, code=code, email=email, expires_at=expires_at)


class PasswordResetToken(models.Model):
    """جدول رموز إعادة تعيين كلمة المرور"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=255, unique=True, verbose_name='التوكن')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(verbose_name='تاريخ الانتهاء')
    is_used = models.BooleanField(default=False, verbose_name='مستخدم')
    
    class Meta:
        verbose_name = 'رمز إعادة تعيين'
        verbose_name_plural = 'رموز إعادة التعيين'
    
    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
    
    @classmethod
    def generate_token(cls, user, expiry_hours=24):
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timezone.timedelta(hours=expiry_hours)
        return cls.objects.create(user=user, token=token, expires_at=expires_at)


class UserActivity(models.Model):
    """جدول نشاط المستخدمين - يسجل جميع الأنشطة المهمة"""
    
    # أنواع الأنشطة
    LOGIN = 'login'
    LOGOUT = 'logout'
    FILE_UPLOAD = 'file_upload'
    FILE_DOWNLOAD = 'file_download'
    FILE_VIEW = 'file_view'
    AI_SUMMARY = 'ai_summary'
    AI_QUESTIONS = 'ai_questions'
    AI_CHAT = 'ai_chat'
    NOTIFICATION_SENT = 'notification_sent'
    ACCOUNT_ACTIVATED = 'account_activated'
    PASSWORD_RESET = 'password_reset'
    
    ACTION_CHOICES = [
        (LOGIN, 'تسجيل دخول'),
        (LOGOUT, 'تسجيل خروج'),
        (FILE_UPLOAD, 'رفع ملف'),
        (FILE_DOWNLOAD, 'تحميل ملف'),
        (FILE_VIEW, 'عرض ملف'),
        (AI_SUMMARY, 'توليد ملخص AI'),
        (AI_QUESTIONS, 'توليد أسئلة AI'),
        (AI_CHAT, 'محادثة AI'),
        (NOTIFICATION_SENT, 'إرسال إشعار'),
        (ACCOUNT_ACTIVATED, 'تفعيل حساب'),
        (PASSWORD_RESET, 'إعادة تعيين كلمة المرور'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name='الإجراء')
    details = models.JSONField(blank=True, null=True, verbose_name='التفاصيل')
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name='عنوان IP')
    user_agent = models.TextField(blank=True, null=True, verbose_name='المتصفح')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')
    
    class Meta:
        verbose_name = 'نشاط'
        verbose_name_plural = 'الأنشطة'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.academic_id} - {self.get_action_display()}"
    
    @classmethod
    def log(cls, user, action, request=None, details=None):
        """
        تسجيل نشاط جديد
        
        Args:
            user: المستخدم
            action: نوع النشاط (استخدم الثوابت مثل UserActivity.AI_SUMMARY)
            request: طلب HTTP (اختياري) لاستخراج IP و User-Agent
            details: تفاصيل إضافية (dict)
        
        Returns:
            UserActivity: سجل النشاط المُنشأ
        """
        ip_address = None
        user_agent = None
        
        if request:
            # استخراج IP
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
            
            # استخراج User-Agent
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        
        return cls.objects.create(
            user=user,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
