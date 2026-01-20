"""
مسارات خدمات AI
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.urls import path
from . import views

app_name = 'ai_service'

urlpatterns = [
    # ==================== التلخيص ====================
    # صفحة توليد الملخص (GET)
    path('summary/<int:file_id>/', views.ai_summary_view, name='generate_summary'),
    # توليد الملخص عبر HTMX (POST)
    path('summary/<int:file_id>/generate/', views.ai_summary_generate_view, name='summary_generate'),
    # عرض ملخص محفوظ
    path('summary/view/<int:summary_id>/', views.view_summary_view, name='view_summary'),
    # تصدير الملخص
    path('summary/export/<int:summary_id>/<str:format>/', views.export_summary_view, name='export_summary'),
    # حذف ملخص
    path('summary/delete/<int:summary_id>/', views.delete_summary_view, name='delete_summary'),
    # ملخصاتي
    path('my-summaries/', views.my_summaries_view, name='my_summaries'),
    
    # ==================== الأسئلة ====================
    # صفحة توليد الأسئلة (GET)
    path('questions/<int:file_id>/', views.ai_questions_view, name='generate_questions'),
    # توليد الأسئلة عبر HTMX (POST)
    path('questions/<int:file_id>/generate/', views.ai_questions_generate_view, name='questions_generate'),
    # عرض أسئلة محفوظة
    path('questions/view/<int:questions_id>/', views.view_questions_view, name='view_questions'),
    # حذف أسئلة
    path('questions/delete/<int:questions_id>/', views.delete_questions_view, name='delete_questions'),
    # أسئلتي
    path('my-questions/', views.my_questions_view, name='my_questions'),
    
    # ==================== المساعد الذكي ====================
    # صفحة المحادثة
    path('chat/', views.ai_chat_view, name='chat'),
    # إرسال رسالة عبر HTMX (POST)
    path('chat/send/', views.ai_chat_send_view, name='chat_send'),
    
    # ==================== API ====================
    # التحقق من حالة API
    path('api/status/', views.api_status_view, name='api_status'),
]
