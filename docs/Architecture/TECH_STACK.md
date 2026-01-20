# البنية التقنية - Tech Stack

## نظرة عامة

تم بناء نظام S-ACM باستخدام مجموعة تقنيات حديثة ومستقرة تضمن الأداء العالي والأمان وسهولة الصيانة.

## التقنيات المستخدمة

### Backend

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| **Python** | 3.11+ | لغة البرمجة الأساسية |
| **Django** | 5.x | إطار العمل الرئيسي |
| **Django ORM** | - | التعامل مع قاعدة البيانات |

### Frontend

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| **Bootstrap** | 5.3 | إطار CSS |
| **Bootstrap Icons** | 1.11 | الأيقونات |
| **HTMX** | 1.9 | التفاعلية بدون JS معقد |
| **Django Templates** | - | محرك القوالب |

### Database

| التقنية | الإصدار | الغرض |
|---------|---------|-------|
| **SQLite3** | 3.x | قاعدة بيانات التطوير |
| **PostgreSQL** | 15+ | قاعدة بيانات الإنتاج (اختياري) |

### AI/NLP

| التقنية | الغرض |
|---------|-------|
| **Python NLP** | معالجة اللغة الطبيعية |
| **PyPDF2** | استخراج نص من PDF |
| **python-docx** | استخراج نص من Word |
| **python-pptx** | استخراج نص من PowerPoint |

### Security

| التقنية | الغرض |
|---------|-------|
| **Django Auth** | نظام المصادقة |
| **CSRF Protection** | حماية من هجمات CSRF |
| **Password Hashing** | تشفير كلمات المرور (PBKDF2) |
| **Session Management** | إدارة الجلسات |

## هيكل الملفات

```
sacm_django/
│
├── sacm_project/              # إعدادات المشروع
│   ├── __init__.py
│   ├── settings.py            # الإعدادات الرئيسية
│   ├── urls.py                # المسارات الرئيسية
│   ├── wsgi.py                # WSGI للإنتاج
│   └── asgi.py                # ASGI (اختياري)
│
├── accounts/                   # تطبيق المصادقة
│   ├── models.py              # User, Role, VerificationCode
│   ├── views.py               # Login, Activate, Reset Password
│   ├── forms.py               # نماذج الإدخال
│   ├── urls.py                # مسارات المصادقة
│   └── email_service.py       # خدمة البريد
│
├── core/                       # التطبيق الأساسي
│   ├── models.py              # Course, LectureFile, Notification
│   ├── views.py               # لوحات التحكم
│   └── urls.py                # المسارات
│
├── ai_service/                 # خدمات AI
│   ├── models.py              # AISummary, AIQuestion
│   ├── views.py               # عروض AI
│   ├── summarizer.py          # نموذج التلخيص
│   ├── text_extractor.py      # استخراج النصوص
│   └── urls.py                # المسارات
│
├── templates/                  # قوالب HTML
│   ├── base.html              # القالب الأساسي
│   ├── dashboard_base.html    # قالب لوحة التحكم
│   ├── accounts/              # قوالب المصادقة
│   ├── admin_panel/           # قوالب Admin
│   ├── instructor/            # قوالب المدرس
│   ├── student/               # قوالب الطالب
│   └── ai_service/            # قوالب AI
│
├── static/                     # الملفات الثابتة
│   ├── css/style.css          # التنسيقات
│   ├── js/                    # JavaScript
│   └── images/                # الصور
│
├── media/                      # الملفات المرفوعة
│   ├── uploads/               # ملفات المحاضرات
│   └── summaries/             # الملخصات
│
├── docs/                       # التوثيق
│
├── manage.py                   # أداة Django
├── requirements.txt            # الحزم المطلوبة
├── .env                        # متغيرات البيئة
└── README.md                   # دليل البدء
```

## طبقات التطبيق

### 1. طبقة العرض (Presentation Layer)

```
┌─────────────────────────────────────────────────────────────┐
│                    Templates + Static Files                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Bootstrap 5 │  │    HTMX      │  │   Custom CSS │       │
│  │     RTL      │  │              │  │              │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 2. طبقة التطبيق (Application Layer)

```
┌─────────────────────────────────────────────────────────────┐
│                      Django Views                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │   accounts   │  │     core     │  │  ai_service  │       │
│  │    views     │  │    views     │  │    views     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Forms     │  │  Decorators  │  │   Mixins     │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 3. طبقة المنطق (Business Logic Layer)

```
┌─────────────────────────────────────────────────────────────┐
│                    Business Services                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Email     │  │  Summarizer  │  │    Text      │       │
│  │   Service    │  │   Service    │  │  Extractor   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 4. طبقة البيانات (Data Layer)

```
┌─────────────────────────────────────────────────────────────┐
│                      Django ORM                              │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │    Models    │  │   Managers   │  │  QuerySets   │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              SQLite3 / PostgreSQL                    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## الحزم المطلوبة

```txt
# requirements.txt

# Django Framework
Django>=5.0,<6.0

# Database
psycopg2-binary>=2.9.9      # PostgreSQL

# Environment Variables
python-dotenv>=1.0.0

# File Processing
PyPDF2>=3.0.0               # PDF
python-docx>=1.1.0          # Word
openpyxl>=3.1.0             # Excel
python-pptx>=0.6.23         # PowerPoint

# Markdown
markdown>=3.5.0

# Image Processing
Pillow>=10.0.0
```

## إعدادات الأمان

```python
# settings.py

# CSRF Protection
CSRF_COOKIE_SECURE = True  # في الإنتاج
CSRF_COOKIE_HTTPONLY = True

# Session Security
SESSION_COOKIE_SECURE = True  # في الإنتاج
SESSION_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## الأداء

### التحسينات المطبقة

1. **Database Queries**:
   - استخدام `select_related()` و `prefetch_related()`
   - تجنب N+1 queries

2. **Caching** (للإنتاج):
   - Django cache framework
   - Template fragment caching

3. **Static Files**:
   - WhiteNoise للخدمة
   - Compression

4. **Pagination**:
   - تقسيم النتائج الكبيرة

## التوسع المستقبلي

| الميزة | الصعوبة | الأولوية |
|--------|---------|----------|
| REST API | متوسطة | عالية |
| تطبيق موبايل | عالية | متوسطة |
| WebSocket للإشعارات | متوسطة | متوسطة |
| تكامل LMS | عالية | منخفضة |
| Multi-tenancy | عالية | منخفضة |
