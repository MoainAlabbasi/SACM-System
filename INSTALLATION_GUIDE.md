# 📚 دليل تثبيت وتشغيل نظام S-ACM

## نظام إدارة المحتوى الأكاديمي الذكي

---

## 📦 المتطلبات الأساسية

| البرنامج | الإصدار المطلوب |
|----------|-----------------|
| Python | 3.10 أو أحدث |
| Git | أي إصدار |

---

## 🪟 التثبيت على Windows

### الخطوة 1: تحميل المشروع

```powershell
cd C:\Projects
git clone https://github.com/MoainAlabbasi/SACM-System.git
cd SACM-System
```

### الخطوة 2: إنشاء البيئة الافتراضية

```powershell
python -m venv venv
.\venv\Scripts\activate
```

### الخطوة 3: تثبيت المتطلبات

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### ⚠️ حل مشكلة python-magic على Windows

```powershell
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

---

## 🐧 التثبيت على Linux/Mac

```bash
git clone https://github.com/MoainAlabbasi/SACM-System.git
cd SACM-System
python3 -m venv venv
source venv/bin/activate

# Linux فقط
sudo apt-get install libmagic1

# Mac فقط
brew install libmagic

pip install -r requirements.txt
```

---

## 🗄️ إعداد قاعدة البيانات

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌱 إعداد البيانات

### الخيار 1: البيانات الأساسية فقط
```bash
python setup_initial_data.py
```

### الخيار 2: البيانات التجريبية الكاملة (موصى به)
```bash
python create_demo_data.py
```

### إنشاء مستخدم superuser
```bash
python manage.py createsuperuser
```

---

## 🚀 تشغيل النظام

```bash
python manage.py runserver
```

**افتح المتصفح على:** http://127.0.0.1:8000/

---

## 🔐 بيانات الدخول التجريبية

### بعد تشغيل `create_demo_data.py`:

| الدور | الرقم الأكاديمي | كلمة المرور |
|-------|-----------------|-------------|
| **مسؤول** | ADMIN001 | Admin@123 |
| **مسؤول** | ADMIN002 | Admin@123 |
| **مدرس** | INST001 | Instructor@123 |
| **مدرس** | INST002 | Instructor@123 |
| **مدرس** | INST003 | Instructor@123 |
| **مدرس** | INST004 | Instructor@123 |
| **طالب** | STU001 | Student@123 |
| **طالب** | STU002 | Student@123 |
| **طالب** | STU003 | Student@123 |
| **طالب** | STU004 | Student@123 |
| **طالب** | STU005 | Student@123 |
| **طالب** | STU006 | Student@123 |
| **طالب** | STU007 | Student@123 |
| **طالب** | STU008 | Student@123 |

---

## 🤖 إعداد الذكاء الاصطناعي

1. احصل على مفتاح من [Google AI Studio](https://makersuite.google.com/app/apikey)
2. أنشئ ملف `.env` في المجلد الرئيسي:

```env
GEMINI_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your_secret_key_here
```

---

## 🔧 استكشاف الأخطاء

### مشكلة: خطأ libmagic على Windows
```powershell
pip uninstall python-magic python-magic-bin
pip install python-magic-bin
```

### مشكلة: حلقة إعادة توجيه لا نهائية
**السبب:** المستخدم ليس له دور محدد.
**الحل:**
```bash
python setup_initial_data.py
```

### مشكلة: الملفات الثابتة لا تظهر
```bash
python manage.py collectstatic
```

### مشكلة: خطأ في الهجرات
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🌐 النشر على الإنتاج

### 1. إعداد المتغيرات البيئية
```bash
export DEBUG=False
export SECRET_KEY='your-production-secret-key'
export ALLOWED_HOSTS='yourdomain.com'
```

### 2. جمع الملفات الثابتة
```bash
python manage.py collectstatic --noinput
```

### 3. تشغيل Gunicorn
```bash
pip install gunicorn
gunicorn sacm_project.wsgi:application --bind 0.0.0.0:8000
```

---

## 📞 الدعم

- **GitHub Issues:** https://github.com/MoainAlabbasi/SACM-System/issues

---

**تم إنشاء هذا الدليل بواسطة فريق S-ACM** 🚀
