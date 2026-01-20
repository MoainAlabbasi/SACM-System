#!/usr/bin/env python
"""
سكريبت إنشاء البيانات الأولية للنظام
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي

الاستخدام:
    python manage.py shell < setup_initial_data.py
    أو
    python setup_initial_data.py (بعد إعداد Django)
"""

import os
import sys
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sacm_project.settings')
django.setup()

from accounts.models import Role, Major, Level
from core.models import Semester
from datetime import date


def create_roles():
    """إنشاء الأدوار الأساسية"""
    print("📋 إنشاء الأدوار...")
    
    roles_data = [
        {'name': 'admin', 'description': 'مسؤول النظام - صلاحيات كاملة'},
        {'name': 'instructor', 'description': 'مدرس - إدارة المقررات والملفات'},
        {'name': 'student', 'description': 'طالب - عرض المحتوى والتفاعل'},
    ]
    
    for role_data in roles_data:
        role, created = Role.objects.get_or_create(
            name=role_data['name'],
            defaults={'description': role_data['description']}
        )
        status = "✅ تم إنشاؤه" if created else "⏭️ موجود مسبقاً"
        print(f"   {status}: {role.get_name_display()}")
    
    print()


def create_levels():
    """إنشاء المستويات الدراسية"""
    print("📊 إنشاء المستويات الدراسية...")
    
    levels_data = [
        {'name': 'المستوى الأول', 'level_number': 1},
        {'name': 'المستوى الثاني', 'level_number': 2},
        {'name': 'المستوى الثالث', 'level_number': 3},
        {'name': 'المستوى الرابع', 'level_number': 4},
        {'name': 'المستوى الخامس', 'level_number': 5},
        {'name': 'المستوى السادس', 'level_number': 6},
        {'name': 'المستوى السابع', 'level_number': 7},
        {'name': 'المستوى الثامن', 'level_number': 8},
    ]
    
    for level_data in levels_data:
        level, created = Level.objects.get_or_create(
            level_number=level_data['level_number'],
            defaults={'name': level_data['name']}
        )
        status = "✅ تم إنشاؤه" if created else "⏭️ موجود مسبقاً"
        print(f"   {status}: {level.name}")
    
    print()


def create_majors():
    """إنشاء التخصصات"""
    print("🎓 إنشاء التخصصات...")
    
    majors_data = [
        {'name': 'علوم الحاسب', 'description': 'تخصص علوم الحاسب الآلي'},
        {'name': 'نظم المعلومات', 'description': 'تخصص نظم المعلومات'},
        {'name': 'هندسة البرمجيات', 'description': 'تخصص هندسة البرمجيات'},
        {'name': 'الذكاء الاصطناعي', 'description': 'تخصص الذكاء الاصطناعي'},
        {'name': 'الأمن السيبراني', 'description': 'تخصص الأمن السيبراني'},
    ]
    
    for major_data in majors_data:
        major, created = Major.objects.get_or_create(
            name=major_data['name'],
            defaults={'description': major_data['description']}
        )
        status = "✅ تم إنشاؤه" if created else "⏭️ موجود مسبقاً"
        print(f"   {status}: {major.name}")
    
    print()


def create_semesters():
    """إنشاء الفصول الدراسية"""
    print("📅 إنشاء الفصول الدراسية...")
    
    current_year = date.today().year
    
    semesters_data = [
        {
            'name': 'الفصل الأول',
            'academic_year': f'{current_year}-{current_year + 1}',
            'start_date': date(current_year, 9, 1),
            'end_date': date(current_year + 1, 1, 15),
            'is_current': True,
        },
        {
            'name': 'الفصل الثاني',
            'academic_year': f'{current_year}-{current_year + 1}',
            'start_date': date(current_year + 1, 2, 1),
            'end_date': date(current_year + 1, 6, 15),
            'is_current': False,
        },
    ]
    
    for semester_data in semesters_data:
        semester, created = Semester.objects.get_or_create(
            name=semester_data['name'],
            academic_year=semester_data['academic_year'],
            defaults={
                'start_date': semester_data['start_date'],
                'end_date': semester_data['end_date'],
                'is_current': semester_data['is_current'],
            }
        )
        status = "✅ تم إنشاؤه" if created else "⏭️ موجود مسبقاً"
        print(f"   {status}: {semester.name} ({semester.academic_year})")
    
    print()


def main():
    """تنفيذ إنشاء البيانات الأولية"""
    print("=" * 50)
    print("🚀 S-ACM - إعداد البيانات الأولية")
    print("=" * 50)
    print()
    
    create_roles()
    create_levels()
    create_majors()
    create_semesters()
    
    print("=" * 50)
    print("✅ تم إنشاء البيانات الأولية بنجاح!")
    print("=" * 50)
    print()
    print("📌 الخطوات التالية:")
    print("   1. قم بإنشاء مستخدم superuser:")
    print("      python manage.py createsuperuser")
    print()
    print("   2. قم بتشغيل الخادم:")
    print("      python manage.py runserver")
    print()
    print("   3. افتح المتصفح على:")
    print("      http://127.0.0.1:8000/")
    print()


if __name__ == '__main__':
    main()
