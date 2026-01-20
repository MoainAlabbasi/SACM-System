"""
إدارة نماذج النظام الأساسية في لوحة Django Admin
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Semester, Course, InstructorCourse, LectureFile, 
    Notification, NotificationRecipient
)


@admin.register(Semester)
class SemesterAdmin(admin.ModelAdmin):
    """إدارة الفصول الدراسية"""
    list_display = ['name', 'academic_year', 'is_current_badge', 'start_date', 'end_date']
    list_filter = ['is_current', 'academic_year']
    search_fields = ['name', 'academic_year']
    ordering = ['-academic_year', '-start_date']
    
    def is_current_badge(self, obj):
        if obj.is_current:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px;">✓ الحالي</span>'
            )
        return format_html(
            '<span style="background: #6b7280; color: white; padding: 3px 10px; '
            'border-radius: 12px;">-</span>'
        )
    is_current_badge.short_description = 'الفصل الحالي'


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """إدارة المقررات"""
    list_display = [
        'code', 'name', 'level', 'semester', 
        'files_count', 'is_active_badge', 'created_at'
    ]
    list_filter = ['level', 'semester', 'is_active', 'majors']
    search_fields = ['code', 'name', 'description']
    filter_horizontal = ['majors']
    ordering = ['code']
    
    def files_count(self, obj):
        count = obj.files.filter(is_deleted=False).count()
        return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', count)
    files_count.short_description = 'عدد الملفات'
    
    def is_active_badge(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px;">نشط</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 3px 10px; '
            'border-radius: 12px;">غير نشط</span>'
        )
    is_active_badge.short_description = 'الحالة'


@admin.register(InstructorCourse)
class InstructorCourseAdmin(admin.ModelAdmin):
    """إدارة تعيينات المدرسين"""
    list_display = ['instructor', 'course', 'semester', 'assigned_at']
    list_filter = ['semester', 'assigned_at']
    search_fields = ['instructor__full_name', 'instructor__academic_id', 'course__name', 'course__code']
    ordering = ['-assigned_at']
    autocomplete_fields = ['instructor', 'course']


@admin.register(LectureFile)
class LectureFileAdmin(admin.ModelAdmin):
    """إدارة الملفات"""
    list_display = [
        'title', 'course', 'file_type_badge', 'uploaded_by',
        'file_size_display', 'download_count', 'is_deleted_badge', 'upload_date'
    ]
    list_filter = ['file_type', 'is_deleted', 'course', 'upload_date']
    search_fields = ['title', 'description', 'course__name', 'uploaded_by__full_name']
    ordering = ['-upload_date']
    readonly_fields = ['download_count', 'upload_date', 'file_size', 'content_type']
    
    def file_type_badge(self, obj):
        colors = {
            'pdf': '#ef4444',
            'docx': '#2563eb',
            'pptx': '#f59e0b',
            'xlsx': '#10b981',
            'image': '#8b5cf6',
            'other': '#6b7280',
        }
        color = colors.get(obj.file_type, '#6b7280')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; text-transform: uppercase; font-size: 0.8em;">{}</span>',
            color, obj.file_type
        )
    file_type_badge.short_description = 'نوع الملف'
    
    def file_size_display(self, obj):
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return '-'
    file_size_display.short_description = 'الحجم'
    
    def is_deleted_badge(self, obj):
        if obj.is_deleted:
            return format_html(
                '<span style="background: #ef4444; color: white; padding: 3px 10px; '
                'border-radius: 12px;">محذوف</span>'
            )
        return format_html(
            '<span style="background: #10b981; color: white; padding: 3px 10px; '
            'border-radius: 12px;">متاح</span>'
        )
    is_deleted_badge.short_description = 'الحالة'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات"""
    list_display = ['title', 'sender', 'notification_type_badge', 'course', 'recipients_count', 'created_at']
    list_filter = ['notification_type', 'created_at', 'course']
    search_fields = ['title', 'body', 'sender__full_name']
    ordering = ['-created_at']
    
    def notification_type_badge(self, obj):
        colors = {
            'general': '#6b7280',
            'new_file': '#2563eb',
            'assignment': '#f59e0b',
            'exam': '#ef4444',
            'announcement': '#8b5cf6',
        }
        labels = {
            'general': 'عام',
            'new_file': 'ملف جديد',
            'assignment': 'واجب',
            'exam': 'اختبار',
            'announcement': 'إعلان',
        }
        color = colors.get(obj.notification_type, '#6b7280')
        label = labels.get(obj.notification_type, obj.notification_type)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px;">{}</span>',
            color, label
        )
    notification_type_badge.short_description = 'النوع'
    
    def recipients_count(self, obj):
        count = obj.recipients.count()
        return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', count)
    recipients_count.short_description = 'عدد المستلمين'


@admin.register(NotificationRecipient)
class NotificationRecipientAdmin(admin.ModelAdmin):
    """إدارة مستلمي الإشعارات"""
    list_display = ['notification', 'user', 'is_read_badge', 'read_at']
    list_filter = ['is_read', 'read_at']
    search_fields = ['notification__title', 'user__full_name', 'user__academic_id']
    ordering = ['-notification__created_at']
    
    def is_read_badge(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 10px; '
                'border-radius: 12px;">✓ مقروء</span>'
            )
        return format_html(
            '<span style="background: #f59e0b; color: white; padding: 3px 10px; '
            'border-radius: 12px;">غير مقروء</span>'
        )
    is_read_badge.short_description = 'حالة القراءة'
