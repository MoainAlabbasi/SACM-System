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

from accounts.models import User, Role, Major, Level, UserActivity
from .models import Course, Semester, LectureFile, Notification, NotificationRecipient, InstructorCourse
from .forms import validate_file_content, validate_file_size


# ==================== دوال مساعدة ====================

def send_file_notification(course, lecture_file, sender):
    """
    إرسال إشعار للطلاب عند رفع ملف جديد
    يستخدم bulk_create لتحسين الأداء
    """
    notification = Notification.objects.create(
        sender=sender,
        title=f'ملف جديد: {lecture_file.title}',
        body=f'تم رفع ملف جديد "{lecture_file.title}" في مقرر {course.name}',
        notification_type='new_file',
        course=course,
    )
    
    # جلب الطلاب المستهدفين
    students = User.objects.filter(
        role__name='student',
        major__in=course.majors.all(),
        level=course.level
    ).values_list('id', flat=True)
    
    # استخدام bulk_create لتحسين الأداء
    recipients = [
        NotificationRecipient(notification=notification, user_id=student_id)
        for student_id in students
    ]
    
    # إنشاء جميع السجلات دفعة واحدة (batch_size للتعامل مع أعداد كبيرة)
    NotificationRecipient.objects.bulk_create(recipients, batch_size=500)
    
    return notification


def home_view(request):
    """الصفحة الرئيسية"""
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')
    return render(request, 'core/home.html')


@login_required
def dashboard_redirect_view(request):
    """توجيه المستخدم للوحة التحكم المناسبة حسب دوره"""
    user = request.user
    
    # التحقق من الدور أولاً
    if user.is_admin() or user.is_superuser:
        return redirect('core:admin_dashboard')
    elif user.is_instructor():
        return redirect('core:instructor_dashboard')
    elif user.is_student():
        return redirect('core:student_dashboard')
    else:
        # إذا لم يكن للمستخدم دور، عرض صفحة خطأ بدلاً من إعادة التوجيه
        from django.contrib.auth import logout
        messages.error(request, 'لم يتم تحديد دور لحسابك. يرجى التواصل مع الإدارة.')
        logout(request)
        return redirect('accounts:login')


# ==================== لوحة تحكم Admin ====================

@login_required
def admin_dashboard_view(request):
    """لوحة تحكم المسؤول"""
    if not request.user.is_admin():
        messages.error(request, 'ليس لديك صلاحية الوصول لهذه الصفحة.')
        return redirect('core:dashboard_redirect')
    
    # إحصائيات سريعة
    from accounts.models import UserActivity
    
    context = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role__name='student').count(),
        'total_instructors': User.objects.filter(role__name='instructor').count(),
        'total_courses': Course.objects.count(),
        'total_files': LectureFile.objects.filter(is_deleted=False).count(),
        'active_semester': Semester.objects.filter(is_current=True).first(),
        'recent_users': User.objects.order_by('-created_at')[:5],
        'recent_files': LectureFile.objects.filter(is_deleted=False).order_by('-upload_date')[:5],
        'recent_activities': UserActivity.objects.select_related('user').order_by('-timestamp')[:10],
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
            
            # إضافة التخصصات (bulk)
            course.majors.add(*major_ids)
            
            # إضافة المدرسين (bulk_create)
            instructor_courses = [
                InstructorCourse(course=course, instructor_id=int(instructor_id))
                for instructor_id in instructor_ids
            ]
            InstructorCourse.objects.bulk_create(instructor_courses)
            
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
        # الحصول على أعلى مستوى (للخريجين)
        max_level = Level.objects.order_by('-level_number').first()
        
        # جلب الطلاب مع مستوياتهم
        students = User.objects.filter(
            role__name='student', 
            level__isnull=False
        ).select_related('level')
        
        # تجميع التحديثات حسب المستوى الجديد
        updates_by_level = {}
        graduated_ids = []
        
        for student in students:
            current_level = student.level
            
            # استبعاد الخريجين (أعلى مستوى)
            if max_level and current_level.level_number >= max_level.level_number:
                graduated_ids.append(student.id)
                continue
            
            next_level = Level.objects.filter(
                level_number=current_level.level_number + 1
            ).first()
            
            if next_level:
                if next_level.id not in updates_by_level:
                    updates_by_level[next_level.id] = []
                updates_by_level[next_level.id].append(student.id)
        
        # تنفيذ التحديثات بشكل مجمع (Bulk Update)
        promoted_count = 0
        for level_id, student_ids in updates_by_level.items():
            count = User.objects.filter(id__in=student_ids).update(level_id=level_id)
            promoted_count += count
        
        messages.success(request, f'تم ترقية {promoted_count} طالب للمستوى التالي. ({len(graduated_ids)} طالب في المستوى الأخير)')
    
    levels = Level.objects.annotate(students_count=Count('students')).order_by('level_number')
    
    context = {
        'levels': levels,
    }
    return render(request, 'admin_panel/promote_students.html', context)


# ==================== لوحة تحكم Instructor ====================

@login_required
def instructor_dashboard_view(request):
    """لوحة تحكم المدرس"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول لهذه الصفحة.')
        return redirect('core:dashboard_redirect')
    
    courses = Course.objects.filter(instructors=request.user)
    
    context = {
        'courses_count': courses.count(),
        'files_count': LectureFile.objects.filter(uploader=request.user, is_deleted=False).count(),
        'recent_files': LectureFile.objects.filter(uploader=request.user, is_deleted=False).order_by('-upload_date')[:5],
        'courses': courses[:5],
    }
    return render(request, 'instructor/dashboard.html', context)


@login_required
def instructor_courses_view(request):
    """مقررات المدرس"""
    if not request.user.is_instructor():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    courses = Course.objects.filter(
        instructors=request.user
    ).select_related('level', 'semester').prefetch_related('majors').annotate(
        files_count=Count('files', filter=Q(files__is_deleted=False))
    )
    
    context = {
        'courses': courses,
    }
    return render(request, 'instructor/courses.html', context)


@login_required
def instructor_course_files_view(request, course_id):
    """ملفات المقرر"""
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
                
                # التحقق من نوع الملف ومحتواه (الأمان)
                try:
                    validate_file_content(uploaded_file)
                    validate_file_size(uploaded_file, max_size_mb=50)
                except Exception as validation_error:
                    messages.error(request, str(validation_error))
                    return redirect('core:instructor_upload_file', course_id=course.id)
                
                lecture_file.file = uploaded_file
                lecture_file.file_size = uploaded_file.size
            elif content_type == 'external_link':
                lecture_file.external_url = request.POST.get('external_url')
            
            lecture_file.save()
            
            # تسجيل النشاط في UserActivity
            UserActivity.log(
                user=request.user,
                action=UserActivity.FILE_UPLOAD,
                request=request,
                details={
                    'file_id': lecture_file.id,
                    'file_name': lecture_file.title,
                    'course_id': course.id,
                    'course_name': course.name,
                    'content_type': content_type,
                    'file_size': lecture_file.file_size
                }
            )
            
            # إرسال إشعار للطلاب (باستخدام bulk_create)
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
        
        # جلب الطلاب المستهدفين
        students = User.objects.filter(
            role__name='student',
            major__in=course.majors.all(),
            level=course.level
        ).values_list('id', flat=True)
        
        # استخدام bulk_create لتحسين الأداء
        recipients = [
            NotificationRecipient(notification=notification, user_id=student_id)
            for student_id in students
        ]
        NotificationRecipient.objects.bulk_create(recipients, batch_size=500)
        
        messages.success(request, f'تم إرسال الإشعار لـ {len(students)} طالب.')
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
    
    # المقررات الحالية (الفصل الحالي فقط)
    current_semester = Semester.objects.filter(is_current=True).first()
    
    courses = Course.objects.filter(
        majors=user.major,
        level=user.level,
        semester=current_semester
    ).select_related('level', 'semester') if user.major and user.level and current_semester else Course.objects.none()
    
    # الإشعارات غير المقروءة
    unread_notifications = NotificationRecipient.objects.filter(
        user=user,
        is_read=False
    ).count()
    
    # آخر الملفات
    recent_files = LectureFile.objects.filter(
        course__in=courses,
        is_deleted=False,
        is_visible=True
    ).order_by('-upload_date')[:5]
    
    context = {
        'courses_count': courses.count(),
        'unread_notifications': unread_notifications,
        'recent_files': recent_files,
        'current_semester': current_semester,
    }
    return render(request, 'student/dashboard.html', context)


@login_required
def student_courses_view(request):
    """مقررات الطالب (الفصل الحالي)"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    
    # المقررات الحالية فقط (is_current=True)
    current_semester = Semester.objects.filter(is_current=True).first()
    
    courses = Course.objects.filter(
        majors=user.major,
        level=user.level,
        semester=current_semester
    ).select_related('level', 'semester').prefetch_related('instructors').annotate(
        files_count=Count('files', filter=Q(files__is_deleted=False, files__is_visible=True))
    ) if user.major and user.level and current_semester else Course.objects.none()
    
    context = {
        'courses': courses,
        'current_semester': current_semester,
    }
    return render(request, 'student/courses.html', context)


@login_required
def student_archive_view(request):
    """أرشيف المقررات السابقة"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    
    # المقررات من الفصول السابقة (is_current=False)
    archived_courses = Course.objects.filter(
        majors=user.major,
        semester__is_current=False
    ).select_related('level', 'semester').prefetch_related('instructors').annotate(
        files_count=Count('files', filter=Q(files__is_deleted=False, files__is_visible=True))
    ).order_by('-semester__academic_year', '-semester__semester_number') if user.major else Course.objects.none()
    
    context = {
        'courses': archived_courses,
    }
    return render(request, 'student/archive.html', context)


@login_required
def student_course_files_view(request, course_id):
    """ملفات المقرر للطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    user = request.user
    course = get_object_or_404(
        Course, 
        id=course_id, 
        majors=user.major
    )
    
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
def view_file_view(request, file_id):
    """عرض ملف"""
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من الصلاحية
    user = request.user
    if user.is_student():
        if user.major not in lecture_file.course.majors.all():
            messages.error(request, 'ليس لديك صلاحية الوصول لهذا الملف.')
            return redirect('core:student_courses')
    
    # زيادة عداد المشاهدات
    lecture_file.views_count += 1
    lecture_file.save(update_fields=['views_count'])
    
    context = {
        'file': lecture_file,
    }
    return render(request, 'core/view_file.html', context)


@login_required
def download_file_view(request, file_id):
    """تحميل ملف"""
    lecture_file = get_object_or_404(LectureFile, id=file_id, is_deleted=False)
    
    # التحقق من الصلاحية
    user = request.user
    if user.is_student():
        if user.major not in lecture_file.course.majors.all():
            messages.error(request, 'ليس لديك صلاحية تحميل هذا الملف.')
            return redirect('core:student_courses')
    
    # زيادة عداد التحميلات
    lecture_file.downloads_count += 1
    lecture_file.save(update_fields=['downloads_count'])
    
    # تسجيل النشاط في UserActivity (للتقارير)
    UserActivity.log(
        user=request.user,
        action=UserActivity.FILE_DOWNLOAD,
        request=request,
        details={
            'file_id': lecture_file.id,
            'file_name': lecture_file.title,
            'course_id': lecture_file.course.id,
            'course_name': lecture_file.course.name,
            'content_type': lecture_file.content_type,
            'file_size': lecture_file.file_size
        }
    )
    
    if lecture_file.content_type == 'external_link':
        return redirect(lecture_file.external_url)
    
    if lecture_file.file:
        return FileResponse(
            lecture_file.file.open('rb'),
            as_attachment=True,
            filename=lecture_file.file.name.split('/')[-1]
        )
    
    messages.error(request, 'الملف غير متوفر.')
    return redirect('core:view_file', file_id=file_id)


@login_required
def student_notifications_view(request):
    """إشعارات الطالب"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    notifications = NotificationRecipient.objects.filter(
        user=request.user
    ).select_related('notification', 'notification__sender', 'notification__course').order_by('-notification__created_at')
    
    paginator = Paginator(notifications, 20)
    page = request.GET.get('page')
    notifications = paginator.get_page(page)
    
    context = {
        'notifications': notifications,
    }
    return render(request, 'student/notifications.html', context)


@login_required
def student_notification_detail_view(request, notification_id):
    """تفاصيل الإشعار"""
    if not request.user.is_student():
        messages.error(request, 'ليس لديك صلاحية الوصول.')
        return redirect('core:dashboard_redirect')
    
    recipient = get_object_or_404(
        NotificationRecipient,
        notification_id=notification_id,
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
def mark_notification_read_view(request, notification_id):
    """تحديد إشعار واحد كمقروء"""
    if request.method == 'POST':
        try:
            recipient = NotificationRecipient.objects.get(
                notification_id=notification_id,
                user=request.user
            )
            if not recipient.is_read:
                recipient.is_read = True
                recipient.read_at = timezone.now()
                recipient.save()
        except NotificationRecipient.DoesNotExist:
            pass
    
    # إرجاع JSON إذا كان الطلب HTMX
    if request.headers.get('HX-Request'):
        from django.http import HttpResponse
        return HttpResponse('')
    
    return redirect('core:student_notifications')


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


# ==================== تبديل اللغة والوضع ====================

def toggle_theme_view(request):
    """تبديل الوضع الليلي/الفاتح"""
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    
    # حفظ في الجلسة
    request.session['theme'] = new_theme
    
    # حفظ في تفضيلات المستخدم إذا كان مسجل الدخول
    if request.user.is_authenticated:
        request.user.preferred_theme = new_theme
        request.user.save(update_fields=['preferred_theme'])
    
    # إرجاع JSON إذا كان الطلب HTMX
    if request.headers.get('HX-Request'):
        return JsonResponse({'theme': new_theme})
    
    # إعادة التوجيه للصفحة السابقة
    return redirect(request.META.get('HTTP_REFERER', 'core:home'))




def get_user_preferences_view(request):
    """الحصول على تفضيلات المستخدم (للـ AJAX)"""
    theme = request.session.get('theme', 'light')
    language = request.session.get('django_language', 'ar')
    
    if request.user.is_authenticated:
        theme = request.user.preferred_theme or theme
        language = request.user.preferred_language or language
    
    return JsonResponse({
        'theme': theme,
        'language': language,
    })
