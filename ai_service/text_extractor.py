"""
استخراج النصوص من الملفات
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي
"""

import os
from pathlib import Path


def extract_text_from_file(lecture_file):
    """استخراج النص من ملف المحاضرة"""
    
    if lecture_file.content_type == 'external_link':
        return None  # لا يمكن استخراج النص من الروابط الخارجية
    
    if not lecture_file.file:
        return None
    
    file_path = lecture_file.file.path
    extension = lecture_file.get_file_extension()
    
    try:
        if extension == 'pdf':
            return extract_from_pdf(file_path)
        elif extension in ['doc', 'docx']:
            return extract_from_docx(file_path)
        elif extension == 'txt':
            return extract_from_txt(file_path)
        elif extension == 'md':
            return extract_from_txt(file_path)
        else:
            return None
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def extract_from_pdf(file_path):
    """استخراج النص من PDF"""
    try:
        from PyPDF2 import PdfReader
        
        reader = PdfReader(file_path)
        text = ""
        
        for page in reader.pages:
            text += page.extract_text() or ""
        
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None


def extract_from_docx(file_path):
    """استخراج النص من DOCX"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        text = ""
        
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        print(f"DOCX extraction error: {e}")
        return None


def extract_from_txt(file_path):
    """استخراج النص من TXT"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='cp1256') as f:
                return f.read().strip()
        except:
            return None
    except Exception as e:
        print(f"TXT extraction error: {e}")
        return None
