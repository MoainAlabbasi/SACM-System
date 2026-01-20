"""
العروض الرئيسية ولوحات التحكم
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.utils import timezone

from accounts.models import User, Role, Major, Level
from .models import Course, Semester, LectureFile, Notification, NotificationRecipient, InstructorCourse


def home_view(request):
    """الصفحة الرئيسية"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    return render(request, 'core/home.html')


@login_required
def dashboard_redirect_view(request):
    """توجيه المستخدم للوحة التحكم المناسبة حسب دوره"""
    user = request.user
    
    if user.is_admin():
        return redirect('core:admin_dashboard')
    elif user.is_instructor():
        return redirect('core:instructor_dashboard')
    elif user.is_student():
        return redirect('core:student_dashboard')
    else:
        messages.error(request, 'لم يتم تحديد دور لحسابك. يرجى التواصل مع الإدارة.')
        return redirect('core:home')


# ==================== لوحة تحكم Admin ====================

@login_required
def admin_dashboard_view(request):
    """لوحة تحكم المسؤول"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول لهذه الصفحة.')
        return redirect('core:dashboard_redirect')
    
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role__name='student').count(),
        'total_instructors': User.objects.filter(role__name='instructor').count(),
        'total_courses': Course.objects.count(),
        'total_files': LectureFile.objects.filter(is_deleted=False).count(),
        'active_semester': Semester.objects.filter(is_current=True).first(),
        'recent_users': User.objects.order_by('-created_at')[:5],
        'recent_files': LectureFile.objects.filter(is_deleted=False).order_by('-upload_date')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
def admin_users_view(request):
    """إدارة المستخدمين"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    users = User.objects.select_related('role', 'major', 'level').order_by('-created_at')
    
    # فلترة
    role_filter = request.GET.get('role')
    status_filter = request.GET.get('status')
    search = request.GET.get('search')
    
    if role_filter:
        users = users.filter(role__name=role_filter)
    if status_filter:
        users = users.filter(account_status=status_filter)
    if search:
        users = users.filter(
            Q(full_name__icontains=search) |
            Q(academic_id__icontains=search) |
            Q(email__icontains=search)
        )
    
    paginator = Paginator(users, 20)
    page = request.GET.get('page')
    users = paginator.get_page(page)
    
    context = {
        'users': users,
        'roles': Role.objects.all(),
        'majors': Major.objects.all(),
        'levels': Level.objects.all(),
    }
    return render(request, 'admin_panel/users.html', context)


@login_required
def admin_add_user_view(request):
    """إضافة مستخدم جديد"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        academic_id = request.POST.get('academic_id')
        id_card_number = request.POST.get('id_card_number')
        full_name = request.POST.get('full_name')
        role_id = request.POST.get('role')
        major_id = request.POST.get('major')
        level_id = request.POST.get('level')
        
        try:
            user = User.objects.create(
                academic_id=academic_id,
                id_card_number=id_card_number,
                full_name=full_name,
                role_id=role_id if role_id else None,
                major_id=major_id if major_id else None,
                level_id=level_id if level_id else None,
                account_status='inactive'
            )
            messages.success(request, f'تم إضافة المستخدم {full_name} بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
        
        return redirect('core:admin_users')
    
    context = {
        'roles': Role.objects.all(),
        'majors': Major.objects.all(),
        'levels': Level.objects.all(),
    }
    return render(request, 'admin_panel/add_user.html', context)


@login_required
def admin_courses_view(request):
    """إدارة المقررات"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    courses = Course.objects.select_related('level', 'semester').prefetch_related('majors', 'instructors').order_by('-created_at')
    
    paginator = Paginator(courses, 20)
    page = request.GET.get('page')
    courses = paginator.get_page(page)
    
    context = {
        'courses': courses,
        'levels': Level.objects.all(),
        'semesters': Semester.objects.all(),
        'majors': Major.objects.all(),
        'instructors': User.objects.filter(role__name='instructor'),
    }
    return render(request, 'admin_panel/courses.html', context)


@login_required
def admin_add_course_view(request):
    """إضافة مقرر جديد"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        description = request.POST.get('description')
        level_id = request.POST.get('level')
        semester_id = request.POST.get('semester')
        major_ids = request.POST.getlist('majors')
        instructor_ids = request.POST.getlist('instructors')
        
        try:
            course = Course.objects.create(
                name=name,
                code=code,
                description=description,
                level_id=level_id,
                semester_id=semester_id,
            )
            
            # إضافة التخصصات
            for major_id in major_ids:
                course.majors.add(major_id)
            
            # إضافة المدرسين
            for instructor_id in instructor_ids:
                InstructorCourse.objects.create(course=course, instructor_id=instructor_id)
            
            messages.success(request, f'تم إضافة المقرر {name} بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
        
        return redirect('core:admin_courses')
    
    context = {
        'levels': Level.objects.all(),
        'semesters': Semester.objects.all(),
        'majors': Major.objects.all(),
        'instructors': User.objects.filter(role__name='instructor'),
    }
    return render(request, 'admin_panel/add_course.html', context)


@login_required
def admin_semesters_view(request):
    """إدارة الفصول الدراسية"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    semesters = Semester.objects.order_by('-academic_year', '-semester_number')
    
    context = {
        'semesters': semesters,
    }
    return render(request, 'admin_panel/semesters.html', context)


@login_required
def admin_majors_view(request):
    """إدارة التخصصات"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    majors = Major.objects.annotate(students_count=Count('students'))
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        try:
            Major.objects.create(name=name, description=description)
            messages.success(request, f'تم إضافة التخصص {name} بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {
        'majors': majors,
    }
    return render(request, 'admin_panel/majors.html', context)


@login_required
def admin_levels_view(request):
    """إدارة المستويات"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    levels = Level.objects.annotate(students_count=Count('students'))
    
    if request.method == 'POST':
        name = request.POST.get('name')
        level_number = request.POST.get('level_number')
        
        try:
            Level.objects.create(name=name, level_number=level_number)
            messages.success(request, f'تم إضافة المستوى {name} بنجاح.')
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {
        'levels': levels,
    }
    return render(request, 'admin_panel/levels.html', context)


@login_required
def admin_promote_students_view(request):
    """ترقية الطلاب للمستوى التالي"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    if request.method == 'POST':
        # ترقية جميع الطلاب للمستوى التالي
        students = User.objects.filter(role__name='student', level__isnull=False)
        promoted_count = 0
        
        for student in students:
            current_level = student.level
            next_level = Level.objects.filter(level_number=current_level.level_number + 1).first()
            
            if next_level:
                student.level = next_level
                student.save()
                promoted_count += 1
        
        messages.success(request, f'تم ترقية {promoted_count} طالب للمستوى التالي.')
        return redirect('core:admin_users')
    
    context = {
        'students_count': User.objects.filter(role__name='student', level__isnull=False).count(),
    }
    return render(request, 'admin_panel/promote_students.html', context)


# ==================== لوحة تحكم Instructor ====================

@login_required
def instructor_dashboard_view(request):
    """لوحة تحكم المدرس"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول لهذه الصفحة.')
        return redirect('core:dashboard_redirect')
    
    my_courses = Course.objects.filter(instructors=request.user)
    my_files = LectureFile.objects.filter(uploader=request.user, is_deleted=False)
    
    context = {
        'my_courses': my_courses,
        'my_files_count': my_files.count(),
        'recent_files': my_files.order_by('-upload_date')[:5],
        'total_downloads': sum(f.download_count for f in my_files),
        'total_views': sum(f.view_count for f in my_files),
    }
    return render(request, 'instructor/dashboard.html', context)


@login_required
def instructor_courses_view(request):
    """مقررات المدرس"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    courses = Course.objects.filter(instructors=request.user).select_related('level', 'semester')
    
    context = {
        'courses': courses,
    }
    return render(request, 'instructor/courses.html', context)


@login_required
def instructor_course_files_view(request, course_id):
    """ملفات مقرر معين"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    course = get_object_or_404(Course, id=course_id, instructors=request.user)
    files = LectureFile.objects.filter(course=course, is_deleted=False).order_by('-upload_date')
    
    context = {
        'course': course,
        'files': files,
    }
    return render(request, 'instructor/course_files.html', context)


@login_required
def instructor_upload_file_view(request, course_id):
    """رفع ملف جديد"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    course = get_object_or_404(Course, id=course_id, instructors=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        file_type = request.POST.get('file_type')
        content_type = request.POST.get('content_type', 'local_file')
        
        try:
            lecture_file = LectureFile(
                course=course,
                uploader=request.user,
                title=title,
                description=description,
                file_type=file_type,
                content_type=content_type,
            )
            
            if content_type == 'local_file' and request.FILES.get('file'):
                uploaded_file = request.FILES['file']
                lecture_file.file = uploaded_file
                lecture_file.file_size = uploaded_file.size
            elif content_type == 'external_link':
                lecture_file.external_url = request.POST.get('external_url')
            
            lecture_file.save()
            
            # إرسال إشعار للطلاب
            send_file_notification(course, lecture_file, request.user)
            
            messages.success(request, f'تم رفع الملف "{title}" بنجاح.')
            return redirect('core:instructor_course_files', course_id=course.id)
        except Exception as e:
            messages.error(request, f'حدث خطأ: {str(e)}')
    
    context = {
        'course': course,
    }
    return render(request, 'instructor/upload_file.html', context)


@login_required
def instructor_edit_file_view(request, file_id):
    """تعديل ملف"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, uploader=request.user)
    
    if request.method == 'POST':
        lecture_file.title = request.POST.get('title')
        lecture_file.description = request.POST.get('description')
        lecture_file.file_type = request.POST.get('file_type')
        lecture_file.is_visible = request.POST.get('is_visible') == 'on'
        lecture_file.save()
        
        messages.success(request, 'تم تحديث الملف بنجاح.')
        return redirect('core:instructor_course_files', course_id=lecture_file.course.id)
    
    context = {
        'file': lecture_file,
    }
    return render(request, 'instructor/edit_file.html', context)


@login_required
def instructor_delete_file_view(request, file_id):
    """حذف ملف (Soft Delete)"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    lecture_file = get_object_or_404(LectureFile, id=file_id, uploader=request.user)
    course_id = lecture_file.course.id
    
    lecture_file.soft_delete()
    messages.success(request, 'تم حذف الملف بنجاح.')
    
    return redirect('core:instructor_course_files', course_id=course_id)


@login_required
def instructor_send_notification_view(request, course_id):
    """إرسال إشعار للطلاب"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    course = get_object_or_404(Course, id=course_id, instructors=request.user)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        
        notification = Notification.objects.create(
            sender=request.user,
            title=title,
            body=body,
            notification_type='announcement',
            course=course,
        )
        
        # إضافة المستلمين (طلاب المقرر)
        students = User.objects.filter(
            role__name='student',
            major__in=course.majors.all(),
            level=course.level
        )
        
        for student in students:
            NotificationRecipient.objects.create(
                notification=notification,
                user=student
            )
        
        messages.success(request, f'تم إرسال الإشعار لـ {students.count()} طالب.')
        return redirect('core:instructor_courses')
    
    context = {
        'course': course,
    }
    return render(request, 'instructor/send_notification.html', context)


# ==================== لوحة تحكم Student ====================

@login_required
def student_dashboard_view(request):
    """لوحة تحكم الطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول لهذه الصفحة.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # المقررات الحالية
    current_courses = Course.objects.filter(
        majors=user.major,
        level=user.level,
        semester=current_semester
    ) if current_semester and user.major and user.level else []
    
    # الإشعارات غير المقروءة
    unread_notifications = NotificationRecipient.objects.filter(
        user=user,
        is_read=False
    ).select_related('notification').order_by('-notification__created_at')[:5]
    
    context = {
        'current_courses': current_courses,
        'unread_notifications': unread_notifications,
        'unread_count': unread_notifications.count(),
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def student_courses_view(request):
    """مقررات الطالب الحالية"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    current_semester = Semester.objects.filter(is_current=True).first()
    
    courses = Course.objects.filter(
        majors=user.major,
        level=user.level,
        semester=current_semester
    ).select_related('level', 'semester') if current_semester and user.major and user.level else []
    
    context = {
        'courses': courses,
        'semester': current_semester,
    }
    return render(request, 'student/courses.html', context)


@login_required
def student_course_files_view(request, course_id):
    """ملفات مقرر معين"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    course = get_object_or_404(Course, id=course_id)
    
    # التحقق من أن الطالب مسجل في هذا المقرر
    user = request.user
    if not (user.major in course.majors.all() and user.level == course.level):
        messages.error(request, 'ليس لديك صلاحية الوصول لهذا المقرر.')
        return redirect('core:student_courses')
    
    files = LectureFile.objects.filter(
        course=course,
        is_deleted=False,
        is_visible=True
    ).order_by('-upload_date')
    
    context = {
        'course': course,
        'files': files,
    }
    return render(request, 'student/course_files.html', context)


@login_required
def student_archive_view(request):
    """أرشيف المقررات السابقة"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    current_semester = Semester.objects.filter(is_current=True).first()
    
    # المقررات من الفصول السابقة أو المستويات السابقة
    archived_courses = Course.objects.filter(
        majors=user.major
    ).exclude(
        semester=current_semester,
        level=user.level
    ).select_related('level', 'semester') if user.major else []
    
    context = {
        'courses': archived_courses,
    }
    return render(request, 'student/archive.html', context)


@login_required
def student_notifications_view(request):
    """إشعارات الطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    notifications = NotificationRecipient.objects.filter(
        user=request.user
    ).select_related('notification', 'notification__sender').order_by('-notification__created_at')
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'student/notifications.html', context)


@login_required
def mark_notification_read_view(request, notification_id):
    """تحديد الإشعار كمقروء"""
    recipient = get_object_or_404(NotificationRecipient, id=notification_id, user=request.user)
    recipient.mark_as_read()
    
    if request.headers.get('HX-Request'):
        return HttpResponse('')
    return redirect('core:student_notifications')


# ==================== عروض مشتركة ====================

@login_required
def view_file_view(request, file_id):
    """عرض ملف"""
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # تسجيل المشاهدة
    lecture_file.increment_view()
    
    context = {
        'file': lecture_file,
    }
    return render(request, 'core/view_file.html', context)


@login_required
def download_file_view(request, file_id):
    """تحميل ملف"""
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    if lecture_file.content_type == 'external_link':
        return redirect(lecture_file.external_url)
    
    # تسجيل التحميل
    lecture_file.increment_download()
    
    response = FileResponse(lecture_file.file.open('rb'))
    response['Content-Disposition'] = f'attachment; filename="{lecture_file.title}.{lecture_file.get_file_extension()}"'
    return response


def send_file_notification(course, lecture_file, sender):
    """إرسال إشعار عند رفع ملف جديد"""
    notification = Notification.objects.create(
        sender=sender,
        title=f'ملف جديد: {lecture_file.title}',
        body=f'تم رفع ملف جديد في مقرر {course.name}',
        notification_type='file_upload',
        course=course,
    )
    
    # إضافة المستلمين
    students = User.objects.filter(
        role__name='student',
        major__in=course.majors.all(),
        level=course.level
    )
    
    for student in students:
        NotificationRecipient.objects.create(
            notification=notification,
            user=student
        )


# ==================== عروض الطالب الإضافية ====================

@login_required
def student_notification_detail_view(request, notification_id):
    """تفاصيل الإشعار"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    recipient = get_object_or_404(
        NotificationRecipient, 
        id=notification_id, 
        user=request.user
    )
    
    # تحديد كمقروء
    if not recipient.is_read:
        recipient.mark_as_read()
    
    context = {
        'notification': recipient.notification,
    }
    return render(request, 'student/notification_detail.html', context)


@login_required
def mark_all_notifications_read_view(request):
    """تحديد جميع الإشعارات كمقروءة"""
    if request.method == 'POST':
        NotificationRecipient.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())
        messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة.')
    
    return redirect('core:student_notifications')


@login_required
def student_summaries_view(request):
    """ملخصات الطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    from ai_service.models import Summary
    
    summaries = Summary.objects.filter(
        user=request.user
    ).select_related('lecture_file', 'lecture_file__course').order_by('-created_at')
    
    paginator = Paginator(summaries, 10)
    page = request.GET.get('page')
    summaries = paginator.get_page(page)
    
    context = {
        'summaries': summaries,
    }
    return render(request, 'student/summaries.html', context)


@login_required
def student_quizzes_view(request):
    """اختبارات الطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    from ai_service.models import Quiz
    
    quizzes = Quiz.objects.filter(
        user=request.user
    ).select_related('lecture_file', 'lecture_file__course').prefetch_related('questions').order_by('-created_at')
    
    context = {
        'quizzes': quizzes,
    }
    return render(request, 'student/quizzes.html', context)
