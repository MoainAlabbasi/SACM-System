# مرجع API والمسارات

## نظرة عامة

هذا المستند يوثق جميع المسارات (URLs) المتاحة في النظام.

## 1. مسارات المصادقة (accounts)

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/accounts/login/` | accounts:login | تسجيل الدخول | GET, POST |
| `/accounts/logout/` | accounts:logout | تسجيل الخروج | GET |
| `/accounts/activate/` | accounts:activate_step1 | تفعيل - الخطوة 1 | GET, POST |
| `/accounts/activate/email/` | accounts:activate_step2 | تفعيل - الخطوة 2 | GET, POST |
| `/accounts/activate/verify/` | accounts:activate_step3 | تفعيل - الخطوة 3 | GET, POST |
| `/accounts/activate/password/` | accounts:activate_step4 | تفعيل - الخطوة 4 | GET, POST |
| `/accounts/activate/resend-otp/` | accounts:resend_otp | إعادة إرسال OTP | GET |
| `/accounts/forgot-password/` | accounts:forgot_password | نسيت كلمة المرور | GET, POST |
| `/accounts/reset-password/<token>/` | accounts:reset_password | إعادة تعيين كلمة المرور | GET, POST |

## 2. المسارات الأساسية (core)

### 2.1 العامة

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/` | core:home | الصفحة الرئيسية | GET |
| `/dashboard/` | core:dashboard_redirect | توجيه للوحة التحكم | GET |

### 2.2 لوحة تحكم Admin

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/admin-panel/` | core:admin_dashboard | لوحة تحكم Admin | GET |
| `/admin-panel/users/` | core:admin_users | إدارة المستخدمين | GET |
| `/admin-panel/users/add/` | core:admin_add_user | إضافة مستخدم | GET, POST |
| `/admin-panel/users/<id>/edit/` | core:admin_edit_user | تعديل مستخدم | GET, POST |
| `/admin-panel/users/<id>/delete/` | core:admin_delete_user | حذف مستخدم | POST |
| `/admin-panel/courses/` | core:admin_courses | إدارة المقررات | GET |
| `/admin-panel/courses/add/` | core:admin_add_course | إضافة مقرر | GET, POST |
| `/admin-panel/courses/<id>/edit/` | core:admin_edit_course | تعديل مقرر | GET, POST |
| `/admin-panel/courses/<id>/delete/` | core:admin_delete_course | حذف مقرر | POST |
| `/admin-panel/semesters/` | core:admin_semesters | إدارة الفصول | GET |
| `/admin-panel/semesters/add/` | core:admin_add_semester | إضافة فصل | GET, POST |
| `/admin-panel/majors/` | core:admin_majors | إدارة التخصصات | GET |
| `/admin-panel/majors/add/` | core:admin_add_major | إضافة تخصص | GET, POST |
| `/admin-panel/levels/` | core:admin_levels | إدارة المستويات | GET |
| `/admin-panel/levels/add/` | core:admin_add_level | إضافة مستوى | GET, POST |
| `/admin-panel/promote/` | core:admin_promote_students | ترقية الطلاب | GET, POST |

### 2.3 لوحة تحكم المدرس

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/instructor/` | core:instructor_dashboard | لوحة تحكم المدرس | GET |
| `/instructor/courses/` | core:instructor_courses | مقررات المدرس | GET |
| `/instructor/courses/<id>/files/` | core:instructor_course_files | ملفات المقرر | GET |
| `/instructor/courses/<id>/upload/` | core:instructor_upload_file | رفع ملف | GET, POST |
| `/instructor/files/<id>/edit/` | core:instructor_edit_file | تعديل ملف | GET, POST |
| `/instructor/files/<id>/delete/` | core:instructor_delete_file | حذف ملف | POST |
| `/instructor/files/<id>/toggle/` | core:instructor_toggle_file | إخفاء/إظهار ملف | POST |
| `/instructor/courses/<id>/notify/` | core:instructor_send_notification | إرسال إشعار | GET, POST |

### 2.4 لوحة تحكم الطالب

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/student/` | core:student_dashboard | لوحة تحكم الطالب | GET |
| `/student/courses/` | core:student_courses | مقررات الطالب | GET |
| `/student/courses/<id>/files/` | core:student_course_files | ملفات المقرر | GET |
| `/student/notifications/` | core:student_notifications | الإشعارات | GET |
| `/student/notifications/<id>/` | core:student_notification_detail | تفاصيل الإشعار | GET |
| `/student/notifications/<id>/read/` | core:student_mark_read | تحديد كمقروء | POST |
| `/student/archive/` | core:student_archive | الأرشيف | GET |

### 2.5 الملفات

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/files/<id>/view/` | core:view_file | عرض الملف | GET |
| `/files/<id>/download/` | core:download_file | تحميل الملف | GET |

## 3. مسارات AI (ai_service)

| المسار | الاسم | الوصف | الطريقة |
|--------|-------|-------|---------|
| `/ai/summarize/<file_id>/` | ai:summarize | تلخيص ملف | GET, POST |
| `/ai/summary/<id>/` | ai:view_summary | عرض ملخص | GET |
| `/ai/my-summaries/` | ai:my_summaries | ملخصاتي | GET |
| `/ai/questions/<file_id>/` | ai:generate_questions | توليد أسئلة | GET, POST |
| `/ai/questions/view/<id>/` | ai:view_questions | عرض الأسئلة | GET |
| `/ai/my-questions/` | ai:my_questions | اختباراتي | GET |
| `/ai/chat/` | ai:chat | المساعد الذكي | GET, POST |
| `/ai/chat/<file_id>/` | ai:chat_with_file | محادثة مع ملف | GET, POST |

## 4. تفاصيل الطلبات

### 4.1 تسجيل الدخول

**POST** `/accounts/login/`

```json
// Request Body
{
    "academic_id": "123456",
    "password": "password123"
}

// Response (Redirect)
// Success: Redirect to dashboard
// Error: Render login page with errors
```

### 4.2 تفعيل الحساب - الخطوة 1

**POST** `/accounts/activate/`

```json
// Request Body
{
    "academic_id": "123456",
    "national_id": "1234567890"
}
```

### 4.3 تفعيل الحساب - الخطوة 2

**POST** `/accounts/activate/email/`

```json
// Request Body
{
    "email": "user@example.com"
}
```

### 4.4 تفعيل الحساب - الخطوة 3

**POST** `/accounts/activate/verify/`

```json
// Request Body
{
    "otp_code": "123456"
}
```

### 4.5 تفعيل الحساب - الخطوة 4

**POST** `/accounts/activate/password/`

```json
// Request Body
{
    "password": "newpassword123",
    "password_confirm": "newpassword123"
}
```

### 4.6 رفع ملف

**POST** `/instructor/courses/<id>/upload/`

```
// Request (multipart/form-data)
- title: string
- description: string (optional)
- file: File
- content_type: string (lecture, assignment, resource, exam)
```

### 4.7 تلخيص ملف

**POST** `/ai/summarize/<file_id>/`

```json
// Request Body
{
    "summary_type": "brief" | "detailed" | "key_points"
}

// Response (Redirect to summary view)
```

### 4.8 توليد أسئلة

**POST** `/ai/questions/<file_id>/`

```json
// Request Body
{
    "difficulty": "easy" | "medium" | "hard",
    "count": 5
}

// Response (Redirect to questions view)
```

### 4.9 المحادثة

**POST** `/ai/chat/`

```json
// Request Body
{
    "question": "ما هو موضوع المحاضرة؟",
    "file_id": 1  // optional
}

// Response (JSON)
{
    "answer": "الإجابة هنا..."
}
```

## 5. رموز الحالة

| الرمز | الوصف |
|-------|-------|
| 200 | نجاح |
| 302 | إعادة توجيه |
| 400 | طلب غير صالح |
| 401 | غير مصرح |
| 403 | ممنوع |
| 404 | غير موجود |
| 500 | خطأ في الخادم |

## 6. الرسائل

### 6.1 رسائل النجاح

```python
messages.success(request, 'تم بنجاح!')
```

### 6.2 رسائل الخطأ

```python
messages.error(request, 'حدث خطأ!')
```

### 6.3 عرض الرسائل في القالب

```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

## 7. HTMX Integration

### 7.1 تحديث جزئي

```html
<button hx-post="/api/action/"
        hx-target="#result"
        hx-swap="innerHTML">
    تنفيذ
</button>
<div id="result"></div>
```

### 7.2 تحميل محتوى

```html
<div hx-get="/api/content/"
     hx-trigger="load"
     hx-swap="innerHTML">
    جاري التحميل...
</div>
```
