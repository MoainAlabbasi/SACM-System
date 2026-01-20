"""
مسارات النظام الرئيسية
S-ACM
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # الصفحة الرئيسية
    path('', views.home_view, name='home'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),
    
    # ==================== Admin ====================
    path('admin-panel/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/users/', views.admin_users_view, name='admin_users'),
    path('admin-panel/users/add/', views.admin_add_user_view, name='admin_add_user'),
    path('admin-panel/courses/', views.admin_courses_view, name='admin_courses'),
    path('admin-panel/courses/add/', views.admin_add_course_view, name='admin_add_course'),
    path('admin-panel/semesters/', views.admin_semesters_view, name='admin_semesters'),
    path('admin-panel/majors/', views.admin_majors_view, name='admin_majors'),
    path('admin-panel/levels/', views.admin_levels_view, name='admin_levels'),
    path('admin-panel/promote-students/', views.admin_promote_students_view, name='admin_promote_students'),
    
    # ==================== Instructor ====================
    path('instructor/', views.instructor_dashboard_view, name='instructor_dashboard'),
    path('instructor/courses/', views.instructor_courses_view, name='instructor_courses'),
    path('instructor/courses/<int:course_id>/files/', views.instructor_course_files_view, name='instructor_course_files'),
    path('instructor/courses/<int:course_id>/upload/', views.instructor_upload_file_view, name='instructor_upload_file'),
    path('instructor/files/<int:file_id>/edit/', views.instructor_edit_file_view, name='instructor_edit_file'),
    path('instructor/files/<int:file_id>/delete/', views.instructor_delete_file_view, name='instructor_delete_file'),
    path('instructor/courses/<int:course_id>/notify/', views.instructor_send_notification_view, name='instructor_send_notification'),
    
    # ==================== Student ====================
    path('student/', views.student_dashboard_view, name='student_dashboard'),
    path('student/courses/', views.student_courses_view, name='student_courses'),
    path('student/courses/<int:course_id>/files/', views.student_course_files_view, name='student_course_files'),
    path('student/archive/', views.student_archive_view, name='student_archive'),
    path('student/notifications/', views.student_notifications_view, name='student_notifications'),
    path('student/notifications/<int:notification_id>/read/', views.mark_notification_read_view, name='mark_notification_read'),
    path('student/notifications/<int:notification_id>/', views.student_notification_detail_view, name='student_notification_detail'),
    path('student/notifications/mark-all-read/', views.mark_all_notifications_read_view, name='mark_all_read'),
    path('student/summaries/', views.student_summaries_view, name='student_summaries'),
    path('student/quizzes/', views.student_quizzes_view, name='student_quizzes'),
    
    # ==================== مشترك ====================
    path('files/<int:file_id>/view/', views.view_file_view, name='view_file'),
    path('files/<int:file_id>/download/', views.download_file_view, name='download_file'),
]
