# S-ACM - نظام إدارة المحتوى الأكاديمي الذكي

نظام متكامل لإدارة المحتوى الأكاديمي مع ميزات الذكاء الاصطناعي المحلي.

## المتطلبات

- Python 3.11+
- Django 5.x
- SQLite3 (افتراضي) أو PostgreSQL 15+

## التثبيت

### 1. إنشاء بيئة افتراضية

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# أو
venv\Scripts\activate  # Windows
```

### 2. تثبيت الحزم

```bash
pip install -r requirements.txt
```

### 3. إعداد متغيرات البيئة

انسخ ملف `.env.example` إلى `.env` وعدّل القيم:

```bash
cp .env.example .env
```

**المتغيرات المطلوبة:**

```env
# المفتاح السري (أنشئ واحداً عشوائياً)
SECRET_KEY=your-secret-key-here

# وضع التطوير
DEBUG=True

# البريد الإلكتروني (Gmail)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

**للحصول على App Password من Gmail:**
1. اذهب إلى إعدادات حساب Google
2. الأمان > التحقق بخطوتين (فعّله إن لم يكن مفعلاً)
3. كلمات مرور التطبيقات > أنشئ كلمة مرور جديدة

### 4. تطبيق قاعدة البيانات

```bash
python manage.py migrate
```

### 5. إنشاء حساب Admin

```bash
python manage.py createsuperuser
```

### 6. تشغيل الخادم

```bash
python manage.py runserver
```

افتح المتصفح على: http://127.0.0.1:8000

## هيكل المشروع

```
sacm_django/
├── accounts/           # نظام المصادقة والمستخدمين
│   ├── models.py       # نماذج المستخدمين والأدوار
│   ├── views.py        # عروض تسجيل الدخول والتفعيل
│   ├── forms.py        # نماذج الإدخال
│   └── email_service.py # خدمة البريد الإلكتروني
│
├── core/               # النظام الأساسي
│   ├── models.py       # المقررات، الملفات، الإشعارات
│   ├── views.py        # لوحات التحكم وإدارة المحتوى
│   └── urls.py         # المسارات
│
├── ai_service/         # خدمات الذكاء الاصطناعي
│   ├── models.py       # الملخصات والأسئلة
│   ├── views.py        # عروض AI
│   ├── summarizer.py   # نموذج التلخيص المحلي
│   └── text_extractor.py # استخراج النصوص
│
├── templates/          # قوالب HTML
├── static/             # ملفات CSS/JS
└── media/              # الملفات المرفوعة
```

## الأدوار والصلاحيات

| الدور | الصلاحيات |
|-------|----------|
| **Admin** | إدارة كاملة: المستخدمين، المقررات، الفصول، التخصصات، ترقية الطلاب |
| **Instructor** | رفع الملفات، إرسال الإشعارات، إدارة مقرراته |
| **Student** | عرض المقررات، تحميل الملفات، استخدام AI، استقبال الإشعارات |

## ميزات نظام AI المحلي

### 1. التلخيص
- ملخص موجز
- ملخص تفصيلي
- النقاط الرئيسية

### 2. توليد الأسئلة
- أسئلة اختيار من متعدد
- مستويات صعوبة متعددة
- تقييم تلقائي

### 3. المساعد الذكي (Chatbot)
- الإجابة على الاستفسارات
- مساعدة في فهم المحتوى

### Rate Limiting
- 10 طلبات/ساعة/مستخدم لكل خدمة

## نظام الإشعارات

- إشعارات داخلية في النظام
- إشعار تلقائي عند رفع ملف جديد
- إشعارات من المدرسين للطلاب

## البريد الإلكتروني

يُستخدم فقط لـ:
- رمز OTP عند تفعيل الحساب
- رابط إعادة تعيين كلمة المرور

## الانتقال إلى PostgreSQL

1. ثبّت PostgreSQL
2. أنشئ قاعدة بيانات جديدة
3. عدّل `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'sacm_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. طبّق migrations:
```bash
python manage.py migrate
```

## التقنيات المستخدمة

- **Backend:** Django 5.x
- **Frontend:** Bootstrap 5, HTMX
- **Database:** SQLite3 / PostgreSQL
- **AI:** نموذج محلي (NLP بسيط)

## الترخيص

MIT License

## المساهمة

نرحب بمساهماتكم! يرجى فتح Issue أو Pull Request.
