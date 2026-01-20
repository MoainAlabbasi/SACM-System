"""
إدارة نماذج المستخدمين في لوحة Django Admin
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Role, Permission, RolePermission, Major, Level, UserActivity


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """إدارة الأدوار"""
    list_display = ['name', 'get_name_display', 'description', 'users_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']
    
    def users_count(self, obj):
        count = obj.users.count()
        return format_html('<span style="color: #2563eb; font-weight: bold;">{}</span>', count)
    users_count.short_description = 'عدد المستخدمين'


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """إدارة الصلاحيات"""
    list_display = ['name', 'codename', 'description']
    search_fields = ['name', 'codename', 'description']
    ordering = ['name']


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """إدارة صلاحيات الأدوار"""
    list_display = ['role', 'permission']
    list_filter = ['role', 'permission']
    search_fields = ['role__name', 'permission__name']


@admin.register(Major)
class MajorAdmin(admin.ModelAdmin):
    """إدارة التخصصات"""
    list_display = ['name', 'description', 'students_count', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']
    ordering = ['name']
    
    def students_count(self, obj):
        count = obj.students.count()
        return format_html('<span style="color: #10b981; font-weight: bold;">{}</span>', count)
    students_count.short_description = 'عدد الطلاب'


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """إدارة المستويات"""
    list_display = ['name', 'level_number', 'students_count']
    search_fields = ['name']
    ordering = ['level_number']
    
    def students_count(self, obj):
        count = obj.students.count()
        return format_html('<span style="color: #8b5cf6; font-weight: bold;">{}</span>', count)
    students_count.short_description = 'عدد الطلاب'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """إدارة المستخدمين"""
    list_display = [
        'academic_id', 'full_name', 'email', 'role', 
        'account_status_badge', 'major', 'level', 'created_at'
    ]
    list_filter = ['role', 'account_status', 'major', 'level', 'is_staff', 'is_superuser']
    search_fields = ['academic_id', 'full_name', 'email', 'id_card_number']
    ordering = ['-created_at']
    
    fieldsets = (
        ('المعلومات الأساسية', {
            'fields': ('academic_id', 'full_name', 'id_card_number', 'email', 'password')
        }),
        ('الدور والتخصص', {
            'fields': ('role', 'major', 'level', 'account_status')
        }),
        ('الصور', {
            'fields': ('profile_image', 'cover_image'),
            'classes': ('collapse',)
        }),
        ('التفضيلات', {
            'fields': ('preferred_language', 'preferred_theme'),
            'classes': ('collapse',)
        }),
        ('الصلاحيات', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('التواريخ', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('إنشاء مستخدم جديد', {
            'classes': ('wide',),
            'fields': (
                'academic_id', 'full_name', 'id_card_number', 'email',
                'password1', 'password2', 'role', 'major', 'level', 'account_status'
            ),
        }),
    )
    
    def account_status_badge(self, obj):
        colors = {
            'active': '#10b981',
            'inactive': '#f59e0b',
            'suspended': '#ef4444',
        }
        labels = {
            'active': 'مفعل',
            'inactive': 'غير مفعل',
            'suspended': 'موقوف',
        }
        color = colors.get(obj.account_status, '#6b7280')
        label = labels.get(obj.account_status, obj.account_status)
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 0.85em;">{}</span>',
            color, label
        )
    account_status_badge.short_description = 'حالة الحساب'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """إدارة سجل النشاط"""
    list_display = ['user', 'action', 'ip_address', 'created_at', 'details_preview']
    list_filter = ['action', 'created_at']
    search_fields = ['user__academic_id', 'user__full_name', 'ip_address', 'details']
    ordering = ['-created_at']
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'created_at']
    
    def details_preview(self, obj):
        if obj.details:
            preview = str(obj.details)[:50]
            if len(str(obj.details)) > 50:
                preview += '...'
            return preview
        return '-'
    details_preview.short_description = 'التفاصيل'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
