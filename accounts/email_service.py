"""
خدمة البريد الإلكتروني للتحقق وإعادة تعيين كلمة المرور
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_otp_email(user, otp_code, email):
    """إرسال رمز التحقق OTP عبر البريد الإلكتروني"""
    subject = 'S-ACM - رمز التحقق من الحساب'
    
    message = f"""
مرحباً {user.full_name}،

رمز التحقق الخاص بك هو: {otp_code}

هذا الرمز صالح لمدة 10 دقائق.

إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.

مع تحيات،
فريق S-ACM
نظام إدارة المحتوى الأكاديمي الذكي
    """
    
    html_message = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f, #2563eb); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #2563eb; background: #e0e7ff; padding: 15px 30px; border-radius: 10px; display: inline-block; letter-spacing: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>S-ACM</h1>
                <p>نظام إدارة المحتوى الأكاديمي الذكي</p>
            </div>
            <div class="content">
                <h2>مرحباً {user.full_name}،</h2>
                <p>رمز التحقق الخاص بك هو:</p>
                <p style="text-align: center;">
                    <span class="otp-code">{otp_code}</span>
                </p>
                <p><strong>هذا الرمز صالح لمدة 10 دقائق.</strong></p>
                <p>إذا لم تطلب هذا الرمز، يرجى تجاهل هذه الرسالة.</p>
            </div>
            <div class="footer">
                <p>مع تحيات فريق S-ACM</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@sacm.edu',
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending OTP email: {e}")
        return False


def send_password_reset_email(user, reset_url):
    """إرسال رابط إعادة تعيين كلمة المرور"""
    subject = 'S-ACM - إعادة تعيين كلمة المرور'
    
    message = f"""
مرحباً {user.full_name}،

تم طلب إعادة تعيين كلمة المرور لحسابك.

اضغط على الرابط التالي لإعادة تعيين كلمة المرور:
{reset_url}

هذا الرابط صالح لمدة 24 ساعة.

إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذه الرسالة.

مع تحيات،
فريق S-ACM
    """
    
    html_message = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, sans-serif; direction: rtl; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f, #2563eb); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            .btn {{ display: inline-block; background: #2563eb; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; }}
            .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>S-ACM</h1>
                <p>نظام إدارة المحتوى الأكاديمي الذكي</p>
            </div>
            <div class="content">
                <h2>مرحباً {user.full_name}،</h2>
                <p>تم طلب إعادة تعيين كلمة المرور لحسابك.</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" class="btn">إعادة تعيين كلمة المرور</a>
                </p>
                <p><strong>هذا الرابط صالح لمدة 24 ساعة.</strong></p>
                <p>إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذه الرسالة.</p>
            </div>
            <div class="footer">
                <p>مع تحيات فريق S-ACM</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER or 'noreply@sacm.edu',
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending password reset email: {e}")
        return False
