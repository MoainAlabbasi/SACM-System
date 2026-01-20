"""
نماذج Django للتحقق من البيانات
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import magic  # python-magic للتحقق من نوع الملف الحقيقي

from .models import LectureFile, Course


# ==================== المحققات (Validators) ====================

def validate_file_content(file):
    """
    التحقق من محتوى الملف (وليس الامتداد فقط)
    يستخدم python-magic لفحص Magic Bytes
    """
    # أنواع MIME المسموحة
    ALLOWED_MIME_TYPES = {
        # PDF
        'application/pdf': ['.pdf'],
        # Microsoft Word
        'application/msword': ['.doc'],
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
        # Microsoft PowerPoint
        'application/vnd.ms-powerpoint': ['.ppt'],
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': ['.pptx'],
        # Microsoft Excel
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        # نصوص
        'text/plain': ['.txt'],
        # صور
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/gif': ['.gif'],
        # فيديو
        'video/mp4': ['.mp4'],
        'video/webm': ['.webm'],
        # صوت
        'audio/mpeg': ['.mp3'],
        'audio/wav': ['.wav'],
        # ملفات مضغوطة
        'application/zip': ['.zip'],
        'application/x-rar-compressed': ['.rar'],
    }
    
    # قراءة أول 2048 بايت للتحقق من نوع الملف
    file.seek(0)
    file_header = file.read(2048)
    file.seek(0)  # إعادة المؤشر للبداية
    
    # استخدام python-magic للتحقق من نوع الملف الحقيقي
    try:
        mime_type = magic.from_buffer(file_header, mime=True)
    except Exception:
        # إذا فشل magic، نستخدم طريقة بديلة
        mime_type = None
    
    # التحقق من نوع MIME
    if mime_type and mime_type not in ALLOWED_MIME_TYPES:
        raise ValidationError(
            f'نوع الملف غير مسموح به. النوع المكتشف: {mime_type}',
            code='invalid_mime_type'
        )
    
    # التحقق من تطابق الامتداد مع نوع MIME
    file_ext = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
    
    if mime_type and file_ext:
        allowed_extensions = ALLOWED_MIME_TYPES.get(mime_type, [])
        if file_ext not in allowed_extensions:
            raise ValidationError(
                f'امتداد الملف ({file_ext}) لا يتطابق مع محتواه الفعلي ({mime_type})',
                code='extension_mismatch'
            )
    
    return True


def validate_file_size(file, max_size_mb=50):
    """
    التحقق من حجم الملف
    الحد الأقصى الافتراضي: 50 ميجابايت
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file.size > max_size_bytes:
        raise ValidationError(
            f'حجم الملف ({file.size / (1024*1024):.1f} MB) يتجاوز الحد المسموح ({max_size_mb} MB)',
            code='file_too_large'
        )
    
    return True


def validate_pdf_content(file):
    """
    التحقق المتقدم من ملفات PDF
    يتحقق من أن الملف PDF حقيقي وليس ملف مخفي
    """
    file.seek(0)
    header = file.read(8)
    file.seek(0)
    
    # PDF Magic Bytes: %PDF-
    if not header.startswith(b'%PDF-'):
        raise ValidationError(
            'الملف ليس PDF صالح. تأكد من رفع ملف PDF حقيقي.',
            code='invalid_pdf'
        )
    
    return True


def validate_docx_content(file):
    """
    التحقق المتقدم من ملفات DOCX
    DOCX هو في الأساس ملف ZIP
    """
    file.seek(0)
    header = file.read(4)
    file.seek(0)
    
    # ZIP Magic Bytes: PK (0x50 0x4B)
    if header[:2] != b'PK':
        raise ValidationError(
            'الملف ليس DOCX صالح. تأكد من رفع ملف Word حقيقي.',
            code='invalid_docx'
        )
    
    return True


# ==================== النماذج (Forms) ====================

class LectureFileUploadForm(forms.ModelForm):
    """
    نموذج رفع ملف محاضرة
    مع تحقق متقدم من نوع الملف ومحتواه
    """
    
    # الامتدادات المسموحة
    ALLOWED_EXTENSIONS = ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'jpg', 'jpeg', 'png', 'mp4', 'mp3']
    
    file = forms.FileField(
        required=False,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_EXTENSIONS)
        ],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': ','.join([f'.{ext}' for ext in ALLOWED_EXTENSIONS])
        }),
        help_text='الملفات المسموحة: PDF, Word, PowerPoint, Excel, نصوص, صور, فيديو, صوت'
    )
    
    external_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'https://www.youtube.com/watch?v=...'
        }),
        help_text='رابط YouTube أو أي رابط خارجي'
    )
    
    content_type = forms.ChoiceField(
        choices=[
            ('local_file', 'ملف محلي'),
            ('external_link', 'رابط خارجي'),
        ],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        initial='local_file'
    )
    
    class Meta:
        model = LectureFile
        fields = ['title', 'description', 'file_type', 'content_type', 'file', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'عنوان الملف'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف اختياري للملف'
            }),
            'file_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def clean_file(self):
        """التحقق المتقدم من الملف"""
        file = self.cleaned_data.get('file')
        
        if not file:
            return file
        
        # 1. التحقق من الحجم (50 MB كحد أقصى)
        validate_file_size(file, max_size_mb=50)
        
        # 2. التحقق من المحتوى الحقيقي
        validate_file_content(file)
        
        # 3. تحقق إضافي لـ PDF
        if file.name.lower().endswith('.pdf'):
            validate_pdf_content(file)
        
        # 4. تحقق إضافي لـ DOCX
        if file.name.lower().endswith('.docx'):
            validate_docx_content(file)
        
        return file
    
    def clean_external_url(self):
        """التحقق من الرابط الخارجي"""
        url = self.cleaned_data.get('external_url')
        
        if not url:
            return url
        
        # التحقق من روابط YouTube
        youtube_patterns = [
            'youtube.com/watch',
            'youtu.be/',
            'youtube.com/embed/'
        ]
        
        is_youtube = any(pattern in url for pattern in youtube_patterns)
        
        # يمكن إضافة تحقق إضافي هنا
        
        return url
    
    def clean(self):
        """التحقق من البيانات المجمعة"""
        cleaned_data = super().clean()
        content_type = cleaned_data.get('content_type')
        file = cleaned_data.get('file')
        external_url = cleaned_data.get('external_url')
        
        if content_type == 'local_file' and not file:
            raise ValidationError('يجب رفع ملف عند اختيار "ملف محلي"')
        
        if content_type == 'external_link' and not external_url:
            raise ValidationError('يجب إدخال رابط عند اختيار "رابط خارجي"')
        
        return cleaned_data


class CourseForm(forms.ModelForm):
    """نموذج إضافة/تعديل مقرر"""
    
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'level', 'semester']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'اسم المقرر'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'رمز المقرر (مثل: CS101)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'وصف المقرر'
            }),
            'level': forms.Select(attrs={
                'class': 'form-select'
            }),
            'semester': forms.Select(attrs={
                'class': 'form-select'
            }),
        }


class NotificationForm(forms.Form):
    """نموذج إرسال إشعار"""
    
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'عنوان الإشعار'
        })
    )
    
    body = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'محتوى الإشعار'
        })
    )
    
    notification_type = forms.ChoiceField(
        choices=[
            ('announcement', 'إعلان'),
            ('reminder', 'تذكير'),
            ('alert', 'تنبيه'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='announcement'
    )
