"""
Context Processors للنظام
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.conf import settings


def theme_context(request):
    """
    Context processor للوضع الليلي/الفاتح واللغة
    
    يضيف المتغيرات التالية للقوالب:
    - current_theme: الوضع الحالي ('dark' أو 'light')
    - current_language: اللغة الحالية ('ar' أو 'en')
    - is_rtl: هل اللغة RTL
    - available_languages: اللغات المتاحة
    """
    # الحصول على الوضع من الجلسة أو تفضيلات المستخدم
    if request.user.is_authenticated:
        current_theme = getattr(request.user, 'preferred_theme', None) or request.session.get('theme', 'light')
        current_language = getattr(request.user, 'preferred_language', None) or request.LANGUAGE_CODE
    else:
        current_theme = request.session.get('theme', 'light')
        current_language = request.LANGUAGE_CODE
    
    # التحقق من RTL (العربية RTL)
    is_rtl = True  # العربية فقط
    
    return {
        'current_theme': current_theme,
        'current_language': current_language,
        'is_rtl': is_rtl,
        'available_languages': settings.LANGUAGES,
    }
