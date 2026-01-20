#!/usr/bin/env python
"""
سكريبت إنشاء البيانات التجريبية للنظام
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي

الاستخدام:
    python create_demo_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacm_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Role, Major, Level
from core.models import Semester, Course, InstructorCourse, Notification, NotificationRecipient

User = get_user_model()


def create_roles():
    """إنشاء الأدوار الأساسية"""
    print("\n📋 إنشاء الأدوار...")
    roles = [
        ('admin', 'مسؤول النظام - صلاحيات كاملة'),
        ('instructor', 'مدرس - إدارة المقررات والملفات'),
        ('student', 'طالب - عرض المحتوى والتفاعل'),
    ]
    created_roles = {}
    for name, description in roles:
        role, created = Role.objects.get_or_create(
            name=name, defaults={'description': description}
        )
        created_roles[name] = role
        status = "✅" if created else "⏭️"
        print(f"   {status} {role.get_name_display()}")
    return created_roles


def create_levels():
    """إنشاء المستويات الدراسية"""
    print("\n📊 إنشاء المستويات...")
    created_levels = {}
    for i in range(1, 9):
        level, created = Level.objects.get_or_create(
            level_number=i, defaults={'name': f'المستوى {i}'}
        )
        created_levels[i] = level
        status = "✅" if created else "⏭️"
        print(f"   {status} المستوى {i}")
    return created_levels


def create_majors():
    """إنشاء التخصصات"""
    print("\n🎓 إنشاء التخصصات...")
    majors_data = [
        ('علوم الحاسب', 'تخصص علوم الحاسب الآلي'),
        ('نظم المعلومات', 'تخصص نظم المعلومات'),
        ('هندسة البرمجيات', 'تخصص هندسة البرمجيات'),
        ('الذكاء الاصطناعي', 'تخصص الذكاء الاصطناعي'),
        ('الأمن السيبراني', 'تخصص الأمن السيبراني'),
    ]
    created_majors = {}
    for name, description in majors_data:
        major, created = Major.objects.get_or_create(
            name=name, defaults={'description': description}
        )
        created_majors[name] = major
        status = "✅" if created else "⏭️"
        print(f"   {status} {name}")
    return created_majors


def create_semesters():
    """إنشاء الفصول الدراسية"""
    print("\n📅 إنشاء الفصول الدراسية...")
    current_year = date.today().year
    semesters_data = [
        ('الفصل الأول', f'{current_year}-{current_year + 1}', 
         date(current_year, 9, 1), date(current_year + 1, 1, 15), True),
        ('الفصل الثاني', f'{current_year}-{current_year + 1}', 
         date(current_year + 1, 2, 1), date(current_year + 1, 6, 15), False),
    ]
    created_semesters = {}
    for name, academic_year, start_date, end_date, is_current in semesters_data:
        semester, created = Semester.objects.get_or_create(
            name=name, academic_year=academic_year,
            defaults={'start_date': start_date, 'end_date': end_date, 'is_current': is_current}
        )
        created_semesters[name] = semester
        status = "✅" if created else "⏭️"
        current_badge = " 🟢" if semester.is_current else ""
        print(f"   {status} {name} ({academic_year}){current_badge}")
    return created_semesters


def create_users(roles, majors, levels):
    """إنشاء المستخدمين التجريبيين"""
    print("\n👥 إنشاء المستخدمين...")
    created_users = {'admins': [], 'instructors': [], 'students': []}
    
    # المسؤولون
    print("\n   👔 المسؤولون:")
    admins = [
        ('ADMIN001', 'أحمد محمد الإداري', '1100000001', 'admin1@sacm.edu.sa'),
        ('ADMIN002', 'سارة علي المديرة', '1100000002', 'admin2@sacm.edu.sa'),
    ]
    for academic_id, full_name, id_card, email in admins:
        user, created = User.objects.get_or_create(
            academic_id=academic_id,
            defaults={
                'full_name': full_name, 'id_card_number': id_card, 'email': email,
                'role': roles['admin'], 'account_status': 'active', 'is_staff': True,
            }
        )
        if created:
            user.set_password('Admin@123')
            user.save()
        created_users['admins'].append(user)
        status = "✅" if created else "⏭️"
        print(f"      {status} {full_name} ({academic_id})")
    
    # المدرسون
    print("\n   👨‍🏫 المدرسون:")
    instructors = [
        ('INST001', 'د. محمد أحمد العلي', '1200000001', 'instructor1@sacm.edu.sa'),
        ('INST002', 'د. فاطمة سعيد الزهراني', '1200000002', 'instructor2@sacm.edu.sa'),
        ('INST003', 'د. خالد عبدالله القحطاني', '1200000003', 'instructor3@sacm.edu.sa'),
        ('INST004', 'د. نورة محمد الشمري', '1200000004', 'instructor4@sacm.edu.sa'),
    ]
    for academic_id, full_name, id_card, email in instructors:
        user, created = User.objects.get_or_create(
            academic_id=academic_id,
            defaults={
                'full_name': full_name, 'id_card_number': id_card, 'email': email,
                'role': roles['instructor'], 'account_status': 'active',
            }
        )
        if created:
            user.set_password('Instructor@123')
            user.save()
        created_users['instructors'].append(user)
        status = "✅" if created else "⏭️"
        print(f"      {status} {full_name} ({academic_id})")
    
    # الطلاب
    print("\n   👨‍🎓 الطلاب:")
    students = [
        ('STU001', 'عبدالرحمن محمد السعيد', '1300000001', 'student1@sacm.edu.sa', 'علوم الحاسب', 3),
        ('STU002', 'ريم أحمد الحربي', '1300000002', 'student2@sacm.edu.sa', 'نظم المعلومات', 2),
        ('STU003', 'فهد سعود العتيبي', '1300000003', 'student3@sacm.edu.sa', 'هندسة البرمجيات', 4),
        ('STU004', 'لمى خالد الدوسري', '1300000004', 'student4@sacm.edu.sa', 'الذكاء الاصطناعي', 1),
        ('STU005', 'سلطان عبدالله المالكي', '1300000005', 'student5@sacm.edu.sa', 'الأمن السيبراني', 5),
        ('STU006', 'هند محمد الغامدي', '1300000006', 'student6@sacm.edu.sa', 'علوم الحاسب', 6),
        ('STU007', 'ياسر أحمد الشهري', '1300000007', 'student7@sacm.edu.sa', 'نظم المعلومات', 3),
        ('STU008', 'منى سعيد القرني', '1300000008', 'student8@sacm.edu.sa', 'هندسة البرمجيات', 2),
    ]
    for academic_id, full_name, id_card, email, major_name, level_num in students:
        user, created = User.objects.get_or_create(
            academic_id=academic_id,
            defaults={
                'full_name': full_name, 'id_card_number': id_card, 'email': email,
                'role': roles['student'], 'major': majors.get(major_name),
                'level': levels.get(level_num), 'account_status': 'active',
            }
        )
        if created:
            user.set_password('Student@123')
            user.save()
        created_users['students'].append(user)
        status = "✅" if created else "⏭️"
        print(f"      {status} {full_name} ({academic_id})")
    
    return created_users


def create_courses(majors, levels, semesters):
    """إنشاء المقررات"""
    print("\n📚 إنشاء المقررات...")
    current_semester = Semester.objects.filter(is_current=True).first()
    if not current_semester:
        current_semester = list(semesters.values())[0]
    
    courses_data = [
        ('CS101', 'مقدمة في البرمجة', 'أساسيات البرمجة باستخدام Python', 1, ['علوم الحاسب', 'هندسة البرمجيات']),
        ('CS201', 'هياكل البيانات', 'دراسة هياكل البيانات والخوارزميات', 2, ['علوم الحاسب', 'هندسة البرمجيات']),
        ('CS301', 'قواعد البيانات', 'تصميم وإدارة قواعد البيانات', 3, ['علوم الحاسب', 'نظم المعلومات']),
        ('CS401', 'هندسة البرمجيات', 'مبادئ تطوير البرمجيات', 4, ['هندسة البرمجيات']),
        ('AI101', 'مقدمة في الذكاء الاصطناعي', 'أساسيات الذكاء الاصطناعي', 3, ['الذكاء الاصطناعي', 'علوم الحاسب']),
        ('AI201', 'تعلم الآلة', 'خوارزميات تعلم الآلة', 4, ['الذكاء الاصطناعي']),
        ('SEC101', 'أساسيات الأمن السيبراني', 'مبادئ أمن المعلومات', 3, ['الأمن السيبراني']),
        ('SEC201', 'اختبار الاختراق', 'تقنيات اختبار الاختراق الأخلاقي', 5, ['الأمن السيبراني']),
        ('IS101', 'تحليل النظم', 'تحليل وتصميم نظم المعلومات', 2, ['نظم المعلومات']),
        ('IS201', 'إدارة المشاريع', 'إدارة مشاريع تقنية المعلومات', 4, ['نظم المعلومات', 'هندسة البرمجيات']),
    ]
    
    created_courses = []
    for code, name, description, level_num, major_names in courses_data:
        course, created = Course.objects.get_or_create(
            code=code,
            defaults={
                'name': name, 'description': description,
                'level': levels.get(level_num), 'semester': current_semester, 'is_active': True,
            }
        )
        for major_name in major_names:
            if major_name in majors:
                course.majors.add(majors[major_name])
        created_courses.append(course)
        status = "✅" if created else "⏭️"
        print(f"   {status} {code}: {name}")
    
    return created_courses


def assign_instructors(instructors, courses, semesters):
    """تعيين المدرسين للمقررات"""
    print("\n👨‍🏫 تعيين المدرسين...")
    current_semester = Semester.objects.filter(is_current=True).first()
    for i, course in enumerate(courses):
        instructor = instructors[i % len(instructors)]
        assignment, created = InstructorCourse.objects.get_or_create(
            instructor=instructor, course=course, semester=current_semester
        )
        status = "✅" if created else "⏭️"
        print(f"   {status} {instructor.full_name} ← {course.code}")


def print_summary(users):
    """طباعة ملخص البيانات"""
    print("\n" + "=" * 60)
    print("📊 ملخص البيانات التجريبية")
    print("=" * 60)
    print("\n🔐 بيانات الدخول:")
    print("-" * 40)
    print("\n👔 المسؤولون: ADMIN001, ADMIN002")
    print("   كلمة المرور: Admin@123")
    print("\n👨‍🏫 المدرسون: INST001, INST002, INST003, INST004")
    print("   كلمة المرور: Instructor@123")
    print("\n👨‍🎓 الطلاب: STU001 - STU008")
    print("   كلمة المرور: Student@123")
    print("\n" + "=" * 60)
    print("✅ تم إنشاء البيانات التجريبية بنجاح!")
    print("=" * 60)


def main():
    print("\n" + "=" * 60)
    print("🚀 S-ACM - إنشاء البيانات التجريبية")
    print("=" * 60)
    
    roles = create_roles()
    levels = create_levels()
    majors = create_majors()
    semesters = create_semesters()
    users = create_users(roles, majors, levels)
    courses = create_courses(majors, levels, semesters)
    assign_instructors(users['instructors'], courses, semesters)
    print_summary(users)


if __name__ == '__main__':
    main()
