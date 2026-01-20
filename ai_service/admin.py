"""
إدارة نماذج خدمات الذكاء الاصطناعي في لوحة Django Admin
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import AISummary, AIQuestion, AIConversation, AIMessage, AIRateLimit


@admin.register(AISummary)
class AISummaryAdmin(admin.ModelAdmin):
    """إدارة الملخصات الذكية"""
    list_display = [
        'file', 'user', 'summary_type_badge', 
        'content_preview', 'created_at'
    ]
    list_filter = ['summary_type', 'created_at']
    search_fields = ['file__title', 'user__full_name', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def summary_type_badge(self, obj):
        colors = {
            'brief': '#2563eb',
            'detailed': '#10b981',
            'bullet_points': '#f59e0b',
            'key_concepts': '#8b5cf6',
        }
        labels = {
            'brief': 'موجز',
            'detailed': 'تفصيلي',
            'bullet_points': 'نقاط',
            'key_concepts': 'مفاهيم',
        }
        color = colors.get(obj.summary_type, '#6b7280')
        label = labels.get(obj.summary_type, obj.summary_type)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    summary_type_badge.short_description = 'نوع الملخص'
    
    def content_preview(self, obj):
        if obj.content:
            preview = obj.content[:100]
            if len(obj.content) > 100:
                preview += '...'
            return preview
        return '-'
    content_preview.short_description = 'معاينة المحتوى'


@admin.register(AIQuestion)
class AIQuestionAdmin(admin.ModelAdmin):
    """إدارة الأسئلة المولدة"""
    list_display = [
        'file', 'user', 'question_type_badge', 'difficulty_badge',
        'questions_count', 'created_at'
    ]
    list_filter = ['question_type', 'difficulty', 'created_at']
    search_fields = ['file__title', 'user__full_name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def question_type_badge(self, obj):
        colors = {
            'mcq': '#2563eb',
            'true_false': '#10b981',
            'short_answer': '#f59e0b',
            'essay': '#8b5cf6',
        }
        labels = {
            'mcq': 'اختيارات',
            'true_false': 'صح/خطأ',
            'short_answer': 'إجابة قصيرة',
            'essay': 'مقالي',
        }
        color = colors.get(obj.question_type, '#6b7280')
        label = labels.get(obj.question_type, obj.question_type)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    question_type_badge.short_description = 'نوع الأسئلة'
    
    def difficulty_badge(self, obj):
        colors = {
            'easy': '#10b981',
            'medium': '#f59e0b',
            'hard': '#ef4444',
        }
        labels = {
            'easy': 'سهل',
            'medium': 'متوسط',
            'hard': 'صعب',
        }
        color = colors.get(obj.difficulty, '#6b7280')
        label = labels.get(obj.difficulty, obj.difficulty)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    difficulty_badge.short_description = 'الصعوبة'
    
    def questions_count(self, obj):
        if obj.questions:
            try:
                import json
                questions = json.loads(obj.questions) if isinstance(obj.questions, str) else obj.questions
                count = len(questions) if isinstance(questions, list) else 0
                return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', count)
            except:
                return '-'
        return '-'
    questions_count.short_description = 'عدد الأسئلة'


@admin.register(AIConversation)
class AIConversationAdmin(admin.ModelAdmin):
    """إدارة المحادثات"""
    list_display = ['title', 'user', 'file', 'messages_count', 'is_active_badge', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'user__full_name', 'file__title']
    ordering = ['-updated_at']
    
    def messages_count(self, obj):
        count = obj.messages.count()
        return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', count)
    messages_count.short_description = 'عدد الرسائل'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px;">نشطة</span>'
            )
        return format_html(
            '<span style="background: #6b7280; color: white; padding: 3px 10px; '
            'border-radius: 12px;">مغلقة</span>'
        )
    is_active_badge.short_description = 'الحالة'


@admin.register(AIMessage)
class AIMessageAdmin(admin.ModelAdmin):
    """إدارة رسائل المحادثات"""
    list_display = ['conversation', 'role_badge', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['conversation__title', 'content']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def role_badge(self, obj):
        colors = {
            'user': '#2563eb',
            'assistant': '#10b981',
            'system': '#6b7280',
        }
        labels = {
            'user': 'المستخدم',
            'assistant': 'المساعد',
            'system': 'النظام',
        }
        color = colors.get(obj.role, '#6b7280')
        label = labels.get(obj.role, obj.role)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    role_badge.short_description = 'الدور'
    
    def content_preview(self, obj):
        if obj.content:
            preview = obj.content[:80]
            if len(obj.content) > 80:
                preview += '...'
            return preview
        return '-'
    content_preview.short_description = 'المحتوى'


@admin.register(AIRateLimit)
class AIRateLimitAdmin(admin.ModelAdmin):
    """إدارة حدود الاستخدام"""
    list_display = [
        'user', 'date', 'summary_count', 'question_count', 
        'chat_count', 'total_count', 'limit_status'
    ]
    list_filter = ['date']
    search_fields = ['user__full_name', 'user__academic_id']
    ordering = ['-date']
    readonly_fields = ['user', 'date', 'summary_count', 'question_count', 'chat_count']
    
    def total_count(self, obj):
        total = obj.summary_count + obj.question_count + obj.chat_count
        return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', total)
    total_count.short_description = 'الإجمالي'
    
    def limit_status(self, obj):
        total = obj.summary_count + obj.question_count + obj.chat_count
        # افتراض حد 50 طلب يومياً
        if total >= 50:
            return format_html(
                '<span style="background: #ef4444; color: white; padding: 3px 10px; '
                'border-radius: 12px;">تم الوصول للحد</span>'
            )
        elif total >= 40:
            return format_html(
                '<span style="background: #f59e0b; color: white; padding: 3px 10px; '
                'border-radius: 12px;">قريب من الحد</span>'
            )
        return format_html(
            '<span style="background: #10b981; color: white; padding: 3px 10px; '
            'border-radius: 12px;">متاح</span>'
        )
    limit_status.short_description = 'حالة الحد'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
