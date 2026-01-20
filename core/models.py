"""
نماذج المقررات والملفات والإشعارات
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import os


class Semester(models.Model):
    """جدول الفصول الدراسية"""
    name = models.CharField(max_length=100, unique=True, verbose_name='اسم الفصل')
    academic_year = models.CharField(max_length=20, verbose_name='العام الدراسي')
    semester_number = models.PositiveIntegerField(verbose_name='رقم الفصل')
    start_date = models.DateField(verbose_name='تاريخ البداية')
    end_date = models.DateField(verbose_name='تاريخ النهاية')
    is_current = models.BooleanField(default=False, verbose_name='الفصل الحالي')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'فصل دراسي'
        verbose_name_plural = 'الفصول الدراسية'
        ordering = ['-academic_year', '-semester_number']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # التأكد من وجود فصل حالي واحد فقط
        if self.is_current:
            Semester.objects.filter(is_current=True).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Course(models.Model):
    """جدول المقررات الدراسية"""
    name = models.CharField(max_length=150, verbose_name='اسم المقرر')
    code = models.CharField(max_length=20, unique=True, verbose_name='رمز المقرر')
    description = models.TextField(blank=True, null=True, verbose_name='وصف المقرر')
    level = models.ForeignKey('accounts.Level', on_delete=models.CASCADE, related_name='courses', verbose_name='المستوى')
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, related_name='courses', verbose_name='الفصل الدراسي')
    majors = models.ManyToManyField('accounts.Major', through='CourseMajor', related_name='courses', verbose_name='التخصصات')
    instructors = models.ManyToManyField(settings.AUTH_USER_MODEL, through='InstructorCourse', related_name='teaching_courses', verbose_name='المدرسين')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'مقرر'
        verbose_name_plural = 'المقررات'
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class CourseMajor(models.Model):
    """جدول ربط المقررات بالتخصصات"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    major = models.ForeignKey('accounts.Major', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = 'تخصص المقرر'
        verbose_name_plural = 'تخصصات المقررات'
        unique_together = ['course', 'major']
    
    def __str__(self):
        return f"{self.course.code} - {self.major.name}"


class InstructorCourse(models.Model):
    """جدول ربط المدرسين بالمقررات"""
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    assigned_date = models.DateField(auto_now_add=True, verbose_name='تاريخ التعيين')
    
    class Meta:
        verbose_name = 'تعيين مدرس'
        verbose_name_plural = 'تعيينات المدرسين'
        unique_together = ['instructor', 'course']
    
    def __str__(self):
        return f"{self.instructor.full_name} - {self.course.code}"


def lecture_file_path(instance, filename):
    """مسار حفظ الملفات"""
    ext = filename.split('.')[-1]
    new_filename = f"{instance.course.code}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    return os.path.join('uploads', instance.course.code, new_filename)


class LectureFile(models.Model):
    """جدول ملفات المحاضرات"""
    FILE_TYPE_CHOICES = [
        ('lecture', 'محاضرة'),
        ('summary', 'ملخص'),
        ('exam', 'اختبار'),
        ('assignment', 'واجب'),
        ('reference', 'مرجع'),
        ('other', 'أخرى'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('local_file', 'ملف محلي'),
        ('external_link', 'رابط خارجي'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='files', verbose_name='المقرر')
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_files', verbose_name='الرافع')
    title = models.CharField(max_length=255, verbose_name='العنوان')
    description = models.TextField(blank=True, null=True, verbose_name='الوصف')
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='local_file', verbose_name='نوع المحتوى')
    file = models.FileField(upload_to=lecture_file_path, blank=True, null=True, verbose_name='الملف')
    external_url = models.URLField(blank=True, null=True, verbose_name='الرابط الخارجي')
    
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES, default='lecture', verbose_name='نوع الملف')
    file_size = models.BigIntegerField(blank=True, null=True, verbose_name='حجم الملف')
    
    is_visible = models.BooleanField(default=True, verbose_name='مرئي')
    is_deleted = models.BooleanField(default=False, verbose_name='محذوف')  # Soft delete
    
    download_count = models.PositiveIntegerField(default=0, verbose_name='عدد التحميلات')
    view_count = models.PositiveIntegerField(default=0, verbose_name='عدد المشاهدات')
    
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الرفع')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاريخ التحديث')
    
    class Meta:
        verbose_name = 'ملف محاضرة'
        verbose_name_plural = 'ملفات المحاضرات'
        ordering = ['-upload_date']
    
    def __str__(self):
        return self.title
    
    def get_file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].lower()
        return None
    
    def increment_download(self):
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def increment_view(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])
    
    def soft_delete(self):
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])
    
    def restore(self):
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])


class Notification(models.Model):
    """جدول الإشعارات"""
    NOTIFICATION_TYPE_CHOICES = [
        ('file_upload', 'رفع ملف جديد'),
        ('announcement', 'إعلان'),
        ('system', 'نظام'),
    ]
    
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name='المرسل')
    title = models.CharField(max_length=255, verbose_name='العنوان')
    body = models.TextField(verbose_name='المحتوى')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPE_CHOICES, default='announcement', verbose_name='نوع الإشعار')
    
    # الاستهداف
    course = models.ForeignKey(Course, on_delete=models.CASCADE, blank=True, null=True, related_name='notifications', verbose_name='المقرر')
    target_all_students = models.BooleanField(default=False, verbose_name='لجميع الطلاب')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ الإنشاء')
    
    class Meta:
        verbose_name = 'إشعار'
        verbose_name_plural = 'الإشعارات'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NotificationRecipient(models.Model):
    """جدول مستلمي الإشعارات"""
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_notifications')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='تاريخ القراءة')

    
    class Meta:
        verbose_name = 'مستلم إشعار'
        verbose_name_plural = 'مستلمي الإشعارات'
        unique_together = ['notification', 'user']
    
    def __str__(self):
        return f"{self.notification.title} -> {self.user.full_name}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
