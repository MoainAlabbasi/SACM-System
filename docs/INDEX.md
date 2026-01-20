# فهرس التوثيق - S-ACM

## نظرة عامة

مرحباً بك في توثيق نظام S-ACM (نظام إدارة المحتوى الأكاديمي الذكي).

## هيكل التوثيق

```
docs/
├── INDEX.md                    # هذا الملف - فهرس التوثيق
├── SYSTEM_OVERVIEW.md          # نظرة عامة على النظام
│
├── Analysis/                   # التحليل
│   ├── DEEP_ANALYSIS.md        # التحليل العميق للمتطلبات
│   └── BUILD_BASIS.md          # أساس البناء والقرارات
│
├── Architecture/               # البنية التقنية
│   ├── TECH_STACK.md           # التقنيات المستخدمة
│   ├── DATABASE.md             # توثيق قاعدة البيانات
│   ├── FEATURES.md             # الميزات والوظائف
│   └── AUTH_FLOW.md            # تدفق المصادقة
│
├── Guides/                     # الأدلة
│   └── DEVELOPER_GUIDE.md      # دليل المطور الشامل
│
└── API/                        # مرجع API
    └── API_REFERENCE.md        # توثيق المسارات والـ API
```

## دليل القراءة السريعة

### للمدراء والمسؤولين
1. ابدأ بـ [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) - نظرة عامة
2. اقرأ [FEATURES.md](Architecture/FEATURES.md) - الميزات المتاحة

### للمطورين الجدد
1. ابدأ بـ [DEVELOPER_GUIDE.md](Guides/DEVELOPER_GUIDE.md) - دليل البدء
2. راجع [TECH_STACK.md](Architecture/TECH_STACK.md) - التقنيات
3. افهم [DATABASE.md](Architecture/DATABASE.md) - قاعدة البيانات

### لفهم القرارات التقنية
1. اقرأ [BUILD_BASIS.md](Analysis/BUILD_BASIS.md) - أساس البناء
2. راجع [DEEP_ANALYSIS.md](Analysis/DEEP_ANALYSIS.md) - التحليل العميق

### لتطوير الـ API
1. راجع [API_REFERENCE.md](API/API_REFERENCE.md) - مرجع API
2. افهم [AUTH_FLOW.md](Architecture/AUTH_FLOW.md) - تدفق المصادقة

## ملخص المحتويات

| الملف | الوصف |
|-------|-------|
| **SYSTEM_OVERVIEW.md** | مقدمة شاملة عن النظام وأهدافه ومستخدميه |
| **DEEP_ANALYSIS.md** | تحليل المتطلبات الوظيفية وغير الوظيفية |
| **BUILD_BASIS.md** | على أي أساس تم بناء النظام وقرارات التصميم |
| **TECH_STACK.md** | التقنيات المستخدمة وهيكل الملفات |
| **DATABASE.md** | توثيق جميع الجداول والعلاقات |
| **FEATURES.md** | قائمة كاملة بالميزات لكل دور |
| **AUTH_FLOW.md** | تدفق المصادقة والتفعيل بالتفصيل |
| **DEVELOPER_GUIDE.md** | دليل شامل للمطورين |
| **API_REFERENCE.md** | توثيق جميع المسارات والـ API |

## معلومات المشروع

| المعلومة | القيمة |
|----------|--------|
| **اسم المشروع** | S-ACM |
| **الإصدار** | 1.0.0 |
| **التقنيات** | Django 5.x, Bootstrap 5, HTMX, SQLite3 |
| **اللغة** | Python 3.11+ |
| **الترخيص** | MIT |

## روابط مفيدة

- **Django Documentation:** https://docs.djangoproject.com/
- **Bootstrap 5:** https://getbootstrap.com/docs/5.3/
- **HTMX:** https://htmx.org/docs/

## المساهمة

نرحب بمساهماتكم! يرجى:
1. قراءة التوثيق أولاً
2. فتح Issue لمناقشة التغييرات
3. إرسال Pull Request

## الدعم

للأسئلة والاستفسارات، يرجى فتح Issue في المستودع.
