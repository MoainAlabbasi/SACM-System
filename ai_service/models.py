"""
نماذج خدمات الذكاء الاصطناعي
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class AISummary(models.Model):
    """جدول ملخصات AI"""
    SUMMARY_TYPE_CHOICES = [
        ('brief', 'ملخص موجز'),
        ('detailed', 'ملخص تفصيلي'),
        ('key_points', 'نقاط رئيسية'),
    ]
    
    file = models.ForeignKey('core.LectureFile', on_delete=models.CASCADE, related_name='ai_summaries', verbose_name='الملف')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_summaries', verbose_name='المستخدم')
    
    summary_type = models.CharField(max_length=20, choices=SUMMARY_TYPE_CHOICES, default='brief', verbose_name='نوع الملخص')
    summary_text = models.TextField(verbose_name='نص الملخص')  # Markdown format
    
    # البيانات الوصفية
    word_count = models.PositiveIntegerField(default=0, verbose_name='عدد الكلمات')
    processing_time = models.FloatField(default=0, verbose_name='وقت المعالجة (ثانية)')
    
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التوليد')
    
    class Meta:
        verbose_name = 'ملخص AI'
        verbose_name_plural = 'ملخصات AI'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"ملخص: {self.file.title}"


class AIQuestion(models.Model):
    """جدول أسئلة AI"""
    DIFFICULTY_CHOICES = [
        ('easy', 'سهل'),
        ('medium', 'متوسط'),
        ('hard', 'صعب'),
    ]
    
    file = models.ForeignKey('core.LectureFile', on_delete=models.CASCADE, related_name='ai_questions', verbose_name='الملف')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_questions', verbose_name='المستخدم')
    
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium', verbose_name='مستوى الصعوبة')
    questions_json = models.JSONField(verbose_name='الأسئلة')  # JSON array of questions
    questions_count = models.PositiveIntegerField(default=0, verbose_name='عدد الأسئلة')
    
    processing_time = models.FloatField(default=0, verbose_name='وقت المعالجة (ثانية)')
    generated_at = models.DateTimeField(auto_now_add=True, verbose_name='تاريخ التوليد')
    
    class Meta:
        verbose_name = 'أسئلة AI'
        verbose_name_plural = 'أسئلة AI'
        ordering = ['-generated_at']
    
    def __str__(self):
        return f"أسئلة: {self.file.title}"


class AIChat(models.Model):
    """جدول محادثات AI (المساعد الذكي)"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_chats', verbose_name='المستخدم')
    file = models.ForeignKey('core.LectureFile', on_delete=models.CASCADE, blank=True, null=True, related_name='ai_chats', verbose_name='الملف')
    
    question = models.TextField(verbose_name='السؤال')
    answer = models.TextField(verbose_name='الإجابة')
    
    is_helpful = models.BooleanField(blank=True, null=True, verbose_name='مفيد')  # تقييم المستخدم
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='التاريخ')
    
    class Meta:
        verbose_name = 'محادثة AI'
        verbose_name_plural = 'محادثات AI'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"سؤال من {self.user.full_name}"


class AIRateLimit(models.Model):
    """جدول تتبع حدود استخدام AI"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_rate_limits')
    request_type = models.CharField(max_length=50, verbose_name='نوع الطلب')  # summary, questions, chat
    request_time = models.DateTimeField(auto_now_add=True, verbose_name='وقت الطلب')
    
    class Meta:
        verbose_name = 'حد استخدام AI'
        verbose_name_plural = 'حدود استخدام AI'
        ordering = ['-request_time']
    
    @classmethod
    def check_rate_limit(cls, user, request_type='all'):
        """التحقق من حد الاستخدام"""
        from django.conf import settings
        
        limit = getattr(settings, 'AI_RATE_LIMIT', 10)
        period = getattr(settings, 'AI_RATE_LIMIT_PERIOD', 3600)
        
        cutoff_time = timezone.now() - timezone.timedelta(seconds=period)
        
        query = cls.objects.filter(user=user, request_time__gte=cutoff_time)
        if request_type != 'all':
            query = query.filter(request_type=request_type)
        
        count = query.count()
        return count < limit, limit - count
    
    @classmethod
    def record_request(cls, user, request_type):
        """تسجيل طلب جديد"""
        return cls.objects.create(user=user, request_type=request_type)
