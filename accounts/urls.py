"""
مسارات المصادقة
S-ACM
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # تسجيل الدخول والخروج
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # تفعيل الحساب
    path('activate/', views.activate_step1_view, name='activate_step1'),
    path('activate/email/', views.activate_step2_view, name='activate_step2'),
    path('activate/verify/', views.activate_step3_view, name='activate_step3'),
    path('activate/password/', views.activate_step4_view, name='activate_step4'),
    path('activate/resend-otp/', views.resend_otp_view, name='resend_otp'),
    
    # نسيت كلمة المرور
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password_view, name='reset_password'),
]
