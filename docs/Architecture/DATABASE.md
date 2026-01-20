# توثيق قاعدة البيانات

## نظرة عامة

يستخدم النظام 18 جدولاً موزعة على 3 تطبيقات Django:
- **accounts**: 6 جداول
- **core**: 8 جداول
- **ai_service**: 4 جداول

## مخطط العلاقات (ERD)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              accounts                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐     ┌──────────┐     ┌──────────────────┐                 │
│  │   Role   │◄────│   User   │────►│ VerificationCode │                 │
│  └──────────┘     └────┬─────┘     └──────────────────┘                 │
│                        │                                                 │
│                        │           ┌──────────────────┐                 │
│                        └──────────►│PasswordResetToken│                 │
│                        │           └──────────────────┘                 │
│                        │                                                 │
│                        │           ┌──────────────────┐                 │
│                        └──────────►│   UserActivity   │                 │
│                                    └──────────────────┘                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                                core                                      │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────┐     ┌──────────┐     ┌──────────┐                         │
│  │ Semester │     │   Major  │     │  Level   │                         │
│  └────┬─────┘     └────┬─────┘     └────┬─────┘                         │
│       │                │                │                                │
│       └────────────────┼────────────────┘                                │
│                        │                                                 │
│                        ▼                                                 │
│                  ┌──────────┐                                           │
│                  │  Course  │                                           │
│                  └────┬─────┘                                           │
│                       │                                                  │
│                       ▼                                                  │
│               ┌─────────────┐                                           │
│               │ LectureFile │                                           │
│               └─────────────┘                                           │
│                                                                          │
│  ┌──────────────┐     ┌─────────────────────┐                           │
│  │ Notification │────►│NotificationRecipient│                           │
│  └──────────────┘     └─────────────────────┘                           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                             ai_service                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌───────────┐  ┌────────────┐  ┌────────┐  ┌─────────────┐            │
│  │ AISummary │  │ AIQuestion │  │ AIChat │  │ AIRateLimit │            │
│  └───────────┘  └────────────┘  └────────┘  └─────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## تفاصيل الجداول

### 1. accounts.Role

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| name | CharField(50) | اسم الدور (admin, instructor, student) |
| description | TextField | وصف الدور |
| created_at | DateTimeField | تاريخ الإنشاء |

### 2. accounts.User

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| academic_id | CharField(20) | الرقم الأكاديمي (فريد) |
| national_id | CharField(20) | رقم الهوية |
| full_name | CharField(100) | الاسم الكامل |
| email | EmailField | البريد الإلكتروني |
| password | CharField | كلمة المرور (مشفرة) |
| role | ForeignKey(Role) | الدور |
| major | ForeignKey(Major) | التخصص (للطلاب) |
| level | ForeignKey(Level) | المستوى (للطلاب) |
| account_status | CharField | الحالة (pending, active, suspended) |
| created_at | DateTimeField | تاريخ الإنشاء |
| last_login | DateTimeField | آخر تسجيل دخول |

### 3. accounts.VerificationCode

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| user | ForeignKey(User) | المستخدم |
| code | CharField(6) | رمز التحقق |
| email | EmailField | البريد المرسل إليه |
| is_used | BooleanField | هل تم استخدامه |
| created_at | DateTimeField | تاريخ الإنشاء |
| expires_at | DateTimeField | تاريخ الانتهاء |

### 4. accounts.PasswordResetToken

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| user | ForeignKey(User) | المستخدم |
| token | CharField(64) | رمز إعادة التعيين |
| is_used | BooleanField | هل تم استخدامه |
| created_at | DateTimeField | تاريخ الإنشاء |
| expires_at | DateTimeField | تاريخ الانتهاء |

### 5. accounts.UserActivity

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| user | ForeignKey(User) | المستخدم |
| action | CharField | نوع النشاط |
| ip_address | GenericIPAddressField | عنوان IP |
| created_at | DateTimeField | تاريخ النشاط |

### 6. core.Semester

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| name | CharField(100) | اسم الفصل |
| academic_year | CharField(20) | السنة الأكاديمية |
| start_date | DateField | تاريخ البداية |
| end_date | DateField | تاريخ النهاية |
| is_current | BooleanField | هل هو الفصل الحالي |

### 7. core.Major

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| name | CharField(100) | اسم التخصص |
| code | CharField(20) | رمز التخصص |
| description | TextField | الوصف |
| is_active | BooleanField | نشط |

### 8. core.Level

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| name | CharField(50) | اسم المستوى |
| order | IntegerField | الترتيب |

### 9. core.Course

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| code | CharField(20) | رمز المقرر |
| name | CharField(200) | اسم المقرر |
| description | TextField | الوصف |
| credit_hours | IntegerField | الساعات المعتمدة |
| semester | ForeignKey(Semester) | الفصل |
| level | ForeignKey(Level) | المستوى |
| majors | ManyToMany(Major) | التخصصات |
| instructors | ManyToMany(User) | المدرسين |
| is_active | BooleanField | نشط |

### 10. core.LectureFile

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| course | ForeignKey(Course) | المقرر |
| uploader | ForeignKey(User) | الرافع |
| title | CharField(200) | العنوان |
| description | TextField | الوصف |
| file | FileField | الملف |
| file_type | CharField | نوع الملف |
| file_size | BigIntegerField | حجم الملف |
| content_type | CharField | نوع المحتوى |
| external_url | URLField | رابط خارجي |
| view_count | IntegerField | عدد المشاهدات |
| download_count | IntegerField | عدد التحميلات |
| is_visible | BooleanField | مرئي |
| is_deleted | BooleanField | محذوف (Soft Delete) |
| upload_date | DateTimeField | تاريخ الرفع |

### 11. core.Notification

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| sender | ForeignKey(User) | المرسل |
| title | CharField(200) | العنوان |
| body | TextField | المحتوى |
| notification_type | CharField | النوع |
| course | ForeignKey(Course) | المقرر (اختياري) |
| created_at | DateTimeField | تاريخ الإنشاء |

### 12. core.NotificationRecipient

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| notification | ForeignKey(Notification) | الإشعار |
| user | ForeignKey(User) | المستلم |
| is_read | BooleanField | مقروء |
| read_at | DateTimeField | تاريخ القراءة |

### 13. ai_service.AISummary

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| file | ForeignKey(LectureFile) | الملف |
| user | ForeignKey(User) | المستخدم |
| summary_type | CharField | نوع الملخص |
| summary_text | TextField | نص الملخص |
| word_count | IntegerField | عدد الكلمات |
| processing_time | FloatField | وقت المعالجة |
| generated_at | DateTimeField | تاريخ التوليد |

### 14. ai_service.AIQuestion

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| file | ForeignKey(LectureFile) | الملف |
| user | ForeignKey(User) | المستخدم |
| difficulty | CharField | مستوى الصعوبة |
| questions_json | JSONField | الأسئلة |
| questions_count | IntegerField | عدد الأسئلة |
| processing_time | FloatField | وقت المعالجة |
| generated_at | DateTimeField | تاريخ التوليد |

### 15. ai_service.AIChat

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| user | ForeignKey(User) | المستخدم |
| file | ForeignKey(LectureFile) | الملف (اختياري) |
| question | TextField | السؤال |
| answer | TextField | الإجابة |
| created_at | DateTimeField | تاريخ الإنشاء |

### 16. ai_service.AIRateLimit

| الحقل | النوع | الوصف |
|-------|-------|-------|
| id | AutoField | المعرف الأساسي |
| user | ForeignKey(User) | المستخدم |
| service_type | CharField | نوع الخدمة |
| request_count | IntegerField | عدد الطلبات |
| window_start | DateTimeField | بداية النافذة الزمنية |

## الفهارس

```sql
-- فهارس مهمة للأداء
CREATE INDEX idx_user_academic_id ON accounts_user(academic_id);
CREATE INDEX idx_user_role ON accounts_user(role_id);
CREATE INDEX idx_course_semester ON core_course(semester_id);
CREATE INDEX idx_lecturefile_course ON core_lecturefile(course_id);
CREATE INDEX idx_notification_recipient_user ON core_notificationrecipient(user_id);
CREATE INDEX idx_ai_ratelimit_user_service ON ai_service_airatelimit(user_id, service_type);
```

## Migrations

```bash
# إنشاء migrations جديدة
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# عرض migrations
python manage.py showmigrations

# التراجع عن migration
python manage.py migrate app_name migration_name
```

## النسخ الاحتياطي

### SQLite
```bash
# نسخ احتياطي
cp db.sqlite3 db.sqlite3.backup

# استعادة
cp db.sqlite3.backup db.sqlite3
```

### PostgreSQL
```bash
# نسخ احتياطي
pg_dump -U username dbname > backup.sql

# استعادة
psql -U username dbname < backup.sql
```
