# دليل المطور الشامل

## مقدمة

هذا الدليل يوفر كل ما تحتاجه لفهم وتطوير نظام S-ACM.

## 1. إعداد بيئة التطوير

### 1.1 المتطلبات الأساسية

```bash
# التحقق من Python
python --version  # يجب أن يكون 3.11+

# التحقق من pip
pip --version
```

### 1.2 استنساخ المشروع

```bash
# فك الضغط
unzip sacm_django.zip
cd sacm_django
```

### 1.3 إنشاء البيئة الافتراضية

```bash
# إنشاء
python -m venv venv

# تفعيل (Linux/Mac)
source venv/bin/activate

# تفعيل (Windows)
venv\Scripts\activate
```

### 1.4 تثبيت الحزم

```bash
pip install -r requirements.txt
```

### 1.5 إعداد متغيرات البيئة

```bash
# نسخ الملف
cp .env.example .env

# تعديل القيم
nano .env
```

**المتغيرات المطلوبة:**

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 1.6 تهيئة قاعدة البيانات

```bash
# إنشاء migrations
python manage.py makemigrations

# تطبيق migrations
python manage.py migrate

# إنشاء superuser
python manage.py createsuperuser
```

### 1.7 تشغيل الخادم

```bash
python manage.py runserver
```

افتح: http://127.0.0.1:8000

## 2. هيكل الكود

### 2.1 التطبيقات

```
sacm_django/
├── accounts/       # المصادقة والمستخدمين
├── core/           # النظام الأساسي
├── ai_service/     # خدمات AI
└── sacm_project/   # إعدادات Django
```

### 2.2 ملفات التطبيق

```
app_name/
├── __init__.py
├── admin.py        # تسجيل في Admin
├── apps.py         # إعدادات التطبيق
├── forms.py        # نماذج الإدخال
├── models.py       # نماذج قاعدة البيانات
├── urls.py         # المسارات
├── views.py        # العروض
└── migrations/     # migrations
```

## 3. النماذج (Models)

### 3.1 إنشاء نموذج جديد

```python
# models.py
from django.db import models

class MyModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='الاسم')
    description = models.TextField(blank=True, verbose_name='الوصف')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'نموذج'
        verbose_name_plural = 'نماذج'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
```

### 3.2 العلاقات

```python
# One-to-Many
class Course(models.Model):
    semester = models.ForeignKey(
        Semester, 
        on_delete=models.CASCADE,
        related_name='courses'
    )

# Many-to-Many
class Course(models.Model):
    instructors = models.ManyToManyField(
        User,
        related_name='taught_courses'
    )

# One-to-One
class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
```

### 3.3 تطبيق التغييرات

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. العروض (Views)

### 4.1 Function-Based Views

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def my_view(request):
    if request.method == 'POST':
        # معالجة البيانات
        messages.success(request, 'تم بنجاح!')
        return redirect('app:view_name')
    
    context = {
        'items': MyModel.objects.all()
    }
    return render(request, 'app/template.html', context)
```

### 4.2 Decorators للصلاحيات

```python
# decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role.name != 'admin':
            messages.error(request, 'غير مصرح لك بالوصول')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def instructor_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role.name not in ['admin', 'instructor']:
            messages.error(request, 'غير مصرح لك بالوصول')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper

def student_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.role.name != 'student':
            messages.error(request, 'هذه الصفحة للطلاب فقط')
            return redirect('core:home')
        return view_func(request, *args, **kwargs)
    return wrapper
```

### 4.3 استخدام Decorators

```python
from .decorators import admin_required, instructor_required

@admin_required
def admin_dashboard(request):
    return render(request, 'admin_panel/dashboard.html')

@instructor_required
def instructor_dashboard(request):
    return render(request, 'instructor/dashboard.html')
```

## 5. النماذج (Forms)

### 5.1 إنشاء Form

```python
from django import forms
from .models import MyModel

class MyModelForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'أدخل الاسم'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise forms.ValidationError('الاسم قصير جداً')
        return name
```

### 5.2 استخدام Form في View

```python
def create_item(request):
    if request.method == 'POST':
        form = MyModelForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, 'تم الإنشاء بنجاح!')
            return redirect('app:list')
    else:
        form = MyModelForm()
    
    return render(request, 'app/create.html', {'form': form})
```

## 6. القوالب (Templates)

### 6.1 هيكل القوالب

```
templates/
├── base.html              # القالب الأساسي
├── dashboard_base.html    # قالب لوحة التحكم
├── accounts/
│   ├── login.html
│   └── ...
├── admin_panel/
│   ├── dashboard.html
│   └── ...
└── ...
```

### 6.2 الوراثة

```html
<!-- base.html -->
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <title>{% block title %}S-ACM{% endblock %}</title>
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block extra_js %}{% endblock %}
</body>
</html>

<!-- child.html -->
{% extends 'base.html' %}

{% block title %}الصفحة - S-ACM{% endblock %}

{% block content %}
<h1>المحتوى هنا</h1>
{% endblock %}
```

### 6.3 Template Tags

```html
<!-- الحلقات -->
{% for item in items %}
    <p>{{ item.name }}</p>
{% empty %}
    <p>لا توجد عناصر</p>
{% endfor %}

<!-- الشروط -->
{% if user.is_authenticated %}
    <p>مرحباً {{ user.full_name }}</p>
{% else %}
    <a href="{% url 'accounts:login' %}">تسجيل الدخول</a>
{% endif %}

<!-- الروابط -->
<a href="{% url 'app:view_name' pk=item.id %}">رابط</a>

<!-- الملفات الثابتة -->
{% load static %}
<link href="{% static 'css/style.css' %}" rel="stylesheet">
```

## 7. المسارات (URLs)

### 7.1 إعداد المسارات

```python
# app/urls.py
from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('list/', views.list_view, name='list'),
    path('create/', views.create, name='create'),
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]
```

### 7.2 تضمين في المشروع

```python
# sacm_project/urls.py
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('core.urls')),
    path('ai/', include('ai_service.urls')),
]
```

## 8. خدمات AI

### 8.1 استخراج النص

```python
# ai_service/text_extractor.py
from PyPDF2 import PdfReader
from docx import Document

def extract_text(file_path, file_type):
    if file_type == 'pdf':
        return extract_pdf(file_path)
    elif file_type in ['docx', 'doc']:
        return extract_docx(file_path)
    # ...
```

### 8.2 التلخيص

```python
# ai_service/summarizer.py
class LocalSummarizer:
    def summarize(self, text, summary_type='brief'):
        sentences = self._split_sentences(text)
        scores = self._score_sentences(sentences)
        top_sentences = self._get_top_sentences(sentences, scores)
        return ' '.join(top_sentences)
```

### 8.3 Rate Limiting

```python
# التحقق من الحد
def check_rate_limit(user, service_type):
    limit, created = AIRateLimit.objects.get_or_create(
        user=user,
        service_type=service_type,
        defaults={'request_count': 0, 'window_start': timezone.now()}
    )
    
    # إعادة تعيين النافذة
    if timezone.now() - limit.window_start > timedelta(hours=1):
        limit.request_count = 0
        limit.window_start = timezone.now()
        limit.save()
    
    # التحقق من الحد
    if limit.request_count >= 10:
        return False
    
    limit.request_count += 1
    limit.save()
    return True
```

## 9. الاختبارات

### 9.1 إنشاء اختبار

```python
# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from .models import MyModel

class MyModelTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.item = MyModel.objects.create(name='Test')
    
    def test_list_view(self):
        response = self.client.get(reverse('app:list'))
        self.assertEqual(response.status_code, 200)
    
    def test_create(self):
        data = {'name': 'New Item'}
        response = self.client.post(reverse('app:create'), data)
        self.assertEqual(MyModel.objects.count(), 2)
```

### 9.2 تشغيل الاختبارات

```bash
# كل الاختبارات
python manage.py test

# تطبيق معين
python manage.py test accounts

# اختبار معين
python manage.py test accounts.tests.LoginTestCase
```

## 10. النشر (Deployment)

### 10.1 إعدادات الإنتاج

```python
# settings.py
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 10.2 جمع الملفات الثابتة

```bash
python manage.py collectstatic
```

### 10.3 Gunicorn

```bash
pip install gunicorn
gunicorn sacm_project.wsgi:application --bind 0.0.0.0:8000
```

## 11. أفضل الممارسات

### 11.1 الأمان
- لا تخزن كلمات المرور بشكل صريح
- استخدم HTTPS في الإنتاج
- تحقق من صلاحيات المستخدم دائماً

### 11.2 الأداء
- استخدم `select_related()` و `prefetch_related()`
- فعّل التخزين المؤقت
- استخدم pagination للقوائم الطويلة

### 11.3 الكود
- اتبع PEP 8
- اكتب تعليقات واضحة
- استخدم أسماء معبرة
