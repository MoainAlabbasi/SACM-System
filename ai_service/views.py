"""
عروض خدمات الذكاء الاصطناعي - Google Gemini API
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي

يستخدم:
- Google Gemini API للتلخيص وتوليد الأسئلة والمحادثة
- HTMX للتحديثات الجزئية بدون إعادة تحميل الصفحة
- UserActivity لتسجيل جميع الأنشطة
"""

import time
import json
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.template.loader import render_to_string

from core.models import LectureFile
from accounts.models import UserActivity
from .models import AISummary, AIQuestion, AIChat, AIRateLimit
from .text_extractor import extract_text_from_file
from .utils import generate_summary, generate_questions, generate_chat_response, check_api_connection

# إعداد التسجيل
logger = logging.getLogger(__name__)


# ==================== عروض التلخيص ====================

@login_required
def ai_summary_view(request, file_id):
    """
    صفحة توليد الملخص - تعرض النموذج
    """
    if not request.user.is_student():
        messages.error(request, 'هذه الميزة متاحة للطلاب فقط.')
        return redirect('core:dashboard_redirect')
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'summary')
    
    # التحقق من وجود ملخصات سابقة
    existing_summaries = AISummary.objects.filter(
        file=lecture_file, 
        user=request.user
    ).order_by('-generated_at')[:5]
    
    # التحقق من اتصال API
    api_status = check_api_connection()
    
    context = {
        'file': lecture_file,
        'existing_summaries': existing_summaries,
        'remaining_requests': remaining,
        'can_use': can_use,
        'api_status': api_status,
    }
    return render(request, 'ai_service/generate_summary.html', context)


@login_required
@require_POST
def ai_summary_generate_view(request, file_id):
    """
    توليد الملخص - يُستدعى عبر HTMX
    يُرجع HTML جزئي للنتيجة
    """
    if not request.user.is_student():
        return HttpResponse(
            '<div class="alert alert-danger">غير مصرح لك بهذه العملية.</div>',
            status=403
        )
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'summary')
    if not can_use:
        return HttpResponse(
            '<div class="alert alert-warning">'
            '<i class="bi bi-exclamation-triangle me-2"></i>'
            'لقد تجاوزت الحد المسموح (10 طلبات/ساعة). يرجى المحاولة لاحقاً.'
            '</div>',
            status=429
        )
    
    summary_type = request.POST.get('summary_type', 'brief')
    start_time = time.time()
    
    try:
        # استخراج النص من الملف
        text = extract_text_from_file(lecture_file)
        
        if not text or len(text.strip()) < 50:
            return HttpResponse(
                '<div class="alert alert-danger">'
                '<i class="bi bi-x-circle me-2"></i>'
                'لم نتمكن من استخراج نص كافٍ من هذا الملف.'
                '</div>',
                status=400
            )
        
        # توليد الملخص عبر Gemini API
        summary_text = generate_summary(text, summary_type)
        
        processing_time = time.time() - start_time
        
        # حفظ الملخص في قاعدة البيانات
        summary = AISummary.objects.create(
            file=lecture_file,
            user=request.user,
            summary_type=summary_type,
            summary_text=summary_text,  # محفوظ بصيغة Markdown
            word_count=len(summary_text.split()),
            processing_time=processing_time
        )
        
        # تسجيل الطلب في Rate Limit
        AIRateLimit.record_request(request.user, 'summary')
        
        # تسجيل النشاط في User_Activity
        UserActivity.log(
            user=request.user,
            action=UserActivity.AI_SUMMARY,
            request=request,
            details={
                'file_id': file_id,
                'file_name': lecture_file.title,
                'summary_type': summary_type,
                'summary_id': summary.id,
                'word_count': summary.word_count,
                'processing_time': round(processing_time, 2)
            }
        )
        
        logger.info(f"Summary generated for user {request.user.academic_id}, file {file_id}")
        
        # إرجاع HTML جزئي للنتيجة
        html = render_to_string('ai_service/partials/summary_result.html', {
            'summary': summary,
            'remaining': remaining - 1,
        }, request=request)
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.error(f"Summary generation error: {str(e)}")
        return HttpResponse(
            f'<div class="alert alert-danger">'
            f'<i class="bi bi-x-circle me-2"></i>'
            f'حدث خطأ: {str(e)}'
            f'</div>',
            status=500
        )


@login_required
def view_summary_view(request, summary_id):
    """عرض ملخص محفوظ"""
    summary = get_object_or_404(AISummary, id=summary_id, user=request.user)
    
    context = {
        'summary': summary,
    }
    return render(request, 'ai_service/view_summary.html', context)


# ==================== عروض الأسئلة ====================

@login_required
def ai_questions_view(request, file_id):
    """
    صفحة توليد الأسئلة - تعرض النموذج
    """
    if not request.user.is_student():
        messages.error(request, 'هذه الميزة متاحة للطلاب فقط.')
        return redirect('core:dashboard_redirect')
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'questions')
    
    # التحقق من وجود أسئلة سابقة
    existing_questions = AIQuestion.objects.filter(
        file=lecture_file, 
        user=request.user
    ).order_by('-generated_at')[:5]
    
    # التحقق من اتصال API
    api_status = check_api_connection()
    
    context = {
        'file': lecture_file,
        'existing_questions': existing_questions,
        'remaining_requests': remaining,
        'can_use': can_use,
        'api_status': api_status,
    }
    return render(request, 'ai_service/generate_questions.html', context)


@login_required
@require_POST
def ai_questions_generate_view(request, file_id):
    """
    توليد الأسئلة - يُستدعى عبر HTMX
    يُرجع HTML جزئي للنتيجة
    """
    if not request.user.is_student():
        return HttpResponse(
            '<div class="alert alert-danger">غير مصرح لك بهذه العملية.</div>',
            status=403
        )
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'questions')
    if not can_use:
        return HttpResponse(
            '<div class="alert alert-warning">'
            '<i class="bi bi-exclamation-triangle me-2"></i>'
            'لقد تجاوزت الحد المسموح (10 طلبات/ساعة). يرجى المحاولة لاحقاً.'
            '</div>',
            status=429
        )
    
    difficulty = request.POST.get('difficulty', 'medium')
    questions_count = int(request.POST.get('questions_count', 5))
    questions_count = min(max(questions_count, 3), 15)  # بين 3 و 15
    
    start_time = time.time()
    
    try:
        # استخراج النص من الملف
        text = extract_text_from_file(lecture_file)
        
        if not text or len(text.strip()) < 100:
            return HttpResponse(
                '<div class="alert alert-danger">'
                '<i class="bi bi-x-circle me-2"></i>'
                'لم نتمكن من استخراج نص كافٍ من هذا الملف.'
                '</div>',
                status=400
            )
        
        # توليد الأسئلة عبر Gemini API
        questions_json = generate_questions(text, difficulty, questions_count)
        
        if not questions_json:
            return HttpResponse(
                '<div class="alert alert-warning">'
                '<i class="bi bi-exclamation-triangle me-2"></i>'
                'لم نتمكن من توليد أسئلة من هذا المحتوى. جرب ملفاً آخر.'
                '</div>',
                status=400
            )
        
        processing_time = time.time() - start_time
        
        # حفظ الأسئلة في قاعدة البيانات
        ai_questions = AIQuestion.objects.create(
            file=lecture_file,
            user=request.user,
            difficulty=difficulty,
            questions_json=questions_json,
            questions_count=len(questions_json),
            processing_time=processing_time
        )
        
        # تسجيل الطلب في Rate Limit
        AIRateLimit.record_request(request.user, 'questions')
        
        # تسجيل النشاط في User_Activity
        UserActivity.log(
            user=request.user,
            action=UserActivity.AI_QUESTIONS,
            request=request,
            details={
                'file_id': file_id,
                'file_name': lecture_file.title,
                'difficulty': difficulty,
                'questions_id': ai_questions.id,
                'questions_count': len(questions_json),
                'processing_time': round(processing_time, 2)
            }
        )
        
        logger.info(f"Questions generated for user {request.user.academic_id}, file {file_id}")
        
        # إرجاع HTML جزئي للنتيجة
        html = render_to_string('ai_service/partials/questions_result.html', {
            'ai_questions': ai_questions,
            'remaining': remaining - 1,
        }, request=request)
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.error(f"Questions generation error: {str(e)}")
        return HttpResponse(
            f'<div class="alert alert-danger">'
            f'<i class="bi bi-x-circle me-2"></i>'
            f'حدث خطأ: {str(e)}'
            f'</div>',
            status=500
        )


@login_required
def view_questions_view(request, questions_id):
    """عرض أسئلة محفوظة"""
    ai_questions = get_object_or_404(AIQuestion, id=questions_id, user=request.user)
    
    context = {
        'ai_questions': ai_questions,
    }
    return render(request, 'ai_service/view_questions.html', context)


# ==================== عروض المحادثة (Chatbot) ====================

@login_required
def ai_chat_view(request):
    """
    صفحة المساعد الذكي (Chatbot)
    """
    if not request.user.is_student():
        messages.error(request, 'هذه الميزة متاحة للطلاب فقط.')
        return redirect('core:dashboard_redirect')
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'chat')
    
    # المحادثات السابقة
    chat_history = AIChat.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    # ملفات المستخدم للسياق
    from core.models import Course
    user_courses = Course.objects.filter(
        majors=request.user.major,
        level=request.user.level,
        semester__is_current=True
    )
    user_files = LectureFile.objects.filter(
        course__in=user_courses,
        is_deleted=False
    ).order_by('-upload_date')[:20]
    
    context = {
        'chat_history': chat_history,
        'remaining_requests': remaining,
        'can_use': can_use,
        'user_files': user_files,
    }
    return render(request, 'ai_service/chat.html', context)


@login_required
@require_POST
def ai_chat_send_view(request):
    """
    إرسال رسالة للمساعد الذكي - يُستدعى عبر HTMX
    يُرجع HTML جزئي للرسالة الجديدة
    """
    if not request.user.is_student():
        return HttpResponse(
            '<div class="alert alert-danger">غير مصرح لك بهذه العملية.</div>',
            status=403
        )
    
    # التحقق من حد الاستخدام
    can_use, remaining = AIRateLimit.check_rate_limit(request.user, 'chat')
    if not can_use:
        return HttpResponse(
            '<div class="chat-message bot-message">'
            '<div class="message-content text-warning">'
            '<i class="bi bi-exclamation-triangle me-2"></i>'
            'لقد تجاوزت الحد المسموح (10 طلبات/ساعة). يرجى المحاولة لاحقاً.'
            '</div>'
            '</div>',
            status=429
        )
    
    question = request.POST.get('question', '').strip()
    file_id = request.POST.get('file_id')
    
    if not question:
        return HttpResponse(
            '<div class="chat-message bot-message">'
            '<div class="message-content text-muted">'
            'يرجى إدخال سؤال.'
            '</div>'
            '</div>',
            status=400
        )
    
    try:
        # الحصول على سياق الملف إن وجد
        context_text = None
        lecture_file = None
        
        if file_id:
            lecture_file = LectureFile.objects.filter(id=file_id, is_deleted=False).first()
            if lecture_file:
                context_text = extract_text_from_file(lecture_file)
        
        # الحصول على سجل المحادثة الأخير
        recent_chats = AIChat.objects.filter(user=request.user).order_by('-created_at')[:5]
        chat_history = [{'question': c.question, 'answer': c.answer} for c in recent_chats]
        
        # توليد الإجابة عبر Gemini API
        answer = generate_chat_response(question, context_text, chat_history)
        
        # حفظ المحادثة
        chat = AIChat.objects.create(
            user=request.user,
            file=lecture_file,
            question=question,
            answer=answer
        )
        
        # تسجيل الطلب في Rate Limit
        AIRateLimit.record_request(request.user, 'chat')
        
        # تسجيل النشاط في User_Activity
        UserActivity.log(
            user=request.user,
            action=UserActivity.AI_CHAT,
            request=request,
            details={
                'chat_id': chat.id,
                'file_id': file_id,
                'question_length': len(question),
                'answer_length': len(answer)
            }
        )
        
        # إرجاع HTML جزئي للرسالة
        html = render_to_string('ai_service/partials/chat_message.html', {
            'chat': chat,
            'remaining': remaining - 1,
        }, request=request)
        
        return HttpResponse(html)
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return HttpResponse(
            f'<div class="chat-message bot-message">'
            f'<div class="message-content text-danger">'
            f'<i class="bi bi-x-circle me-2"></i>'
            f'حدث خطأ: {str(e)}'
            f'</div>'
            f'</div>',
            status=500
        )


# ==================== عروض إضافية ====================

@login_required
def my_summaries_view(request):
    """ملخصاتي"""
    summaries = AISummary.objects.filter(
        user=request.user
    ).select_related('file').order_by('-generated_at')
    
    context = {
        'summaries': summaries,
    }
    return render(request, 'ai_service/my_summaries.html', context)


@login_required
def my_questions_view(request):
    """أسئلتي"""
    questions = AIQuestion.objects.filter(
        user=request.user
    ).select_related('file').order_by('-generated_at')
    
    context = {
        'questions': questions,
    }
    return render(request, 'ai_service/my_questions.html', context)


@login_required
def export_summary_view(request, summary_id, format):
    """تصدير الملخص بصيغة Markdown أو Text"""
    summary = get_object_or_404(AISummary, id=summary_id, user=request.user)
    
    if format == 'md':
        response = HttpResponse(summary.summary_text, content_type='text/markdown; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="summary_{summary.id}.md"'
        return response
    
    elif format == 'txt':
        # تحويل Markdown إلى نص عادي (بسيط)
        import re
        text = summary.summary_text
        text = re.sub(r'#+ ', '', text)  # إزالة العناوين
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # إزالة Bold
        text = re.sub(r'\*(.+?)\*', r'\1', text)  # إزالة Italic
        
        response = HttpResponse(text, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="summary_{summary.id}.txt"'
        return response
    
    messages.error(request, 'صيغة غير مدعومة.')
    return redirect('ai_service:view_summary', summary_id=summary_id)


@login_required
@require_GET
def api_status_view(request):
    """
    التحقق من حالة API - يُستدعى عبر HTMX
    """
    status = check_api_connection()
    
    if status['status'] == 'connected':
        html = '''
        <span class="badge bg-success">
            <i class="bi bi-check-circle me-1"></i>
            متصل
        </span>
        '''
    else:
        html = f'''
        <span class="badge bg-danger" title="{status['message']}">
            <i class="bi bi-x-circle me-1"></i>
            غير متصل
        </span>
        '''
    
    return HttpResponse(html)


@login_required
def delete_summary_view(request, summary_id):
    """حذف ملخص"""
    summary = get_object_or_404(AISummary, id=summary_id, user=request.user)
    summary.delete()
    messages.success(request, 'تم حذف الملخص.')
    return redirect('ai_service:my_summaries')


@login_required
def delete_questions_view(request, questions_id):
    """حذف أسئلة"""
    questions = get_object_or_404(AIQuestion, id=questions_id, user=request.user)
    questions.delete()
    messages.success(request, 'تم حذف الأسئلة.')
    return redirect('ai_service:my_questions')
