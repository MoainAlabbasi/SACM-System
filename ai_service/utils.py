"""
وحدة الاتصال بـ Google Gemini API
S-ACM - نظام إدارة المحتوى الأكاديمي الذكي

هذا الملف يحتوي على جميع دوال الاتصال بـ Gemini API
يستخدم موديل gemini-1.5-flash (الأسرع والأرخص)
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any

from django.conf import settings

# إعداد التسجيل
logger = logging.getLogger(__name__)

# متغير للتخزين المؤقت للـ client
_gemini_client = None


# ==================== إعداد Gemini API ====================

def get_api_key():
    """الحصول على مفتاح API"""
    api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY غير معيّن. "
            "يرجى إضافته في ملف .env أو settings.py"
        )
    return api_key


def get_gemini_client():
    """
    الحصول على عميل Gemini API
    يستخدم المكتبة الجديدة google-genai
    """
    global _gemini_client
    
    if _gemini_client is None:
        try:
            from google import genai
            api_key = get_api_key()
            _gemini_client = genai.Client(api_key=api_key)
        except ImportError:
            # Fallback للمكتبة القديمة
            import google.generativeai as genai
            api_key = get_api_key()
            genai.configure(api_key=api_key)
            _gemini_client = genai
    
    return _gemini_client


def generate_content(prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    توليد محتوى باستخدام Gemini API
    
    Args:
        prompt: النص المطلوب
        model_name: اسم النموذج
    
    Returns:
        str: النص المولد
    """
    try:
        client = get_gemini_client()
        
        # التحقق من نوع العميل
        if hasattr(client, 'models'):
            # المكتبة الجديدة google-genai
            from google.genai import types
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )
            return response.text
        else:
            # المكتبة القديمة google-generativeai
            model = client.GenerativeModel(
                model_name=model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                }
            )
            response = model.generate_content(prompt)
            return response.text
            
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise


# ==================== دوال التلخيص ====================

def generate_summary(text: str, summary_type: str = 'brief', language: str = 'ar') -> str:
    """
    توليد ملخص للنص باستخدام Gemini API
    
    Args:
        text: النص المراد تلخيصه
        summary_type: نوع الملخص ('brief', 'detailed', 'key_points')
        language: لغة المخرجات ('ar' للعربية، 'en' للإنجليزية)
    
    Returns:
        str: الملخص بصيغة Markdown
    
    Raises:
        Exception: في حالة فشل الاتصال بـ API
    """
    if not text or len(text.strip()) < 50:
        return "# خطأ\n\nالنص قصير جداً للتلخيص."
    
    # تحديد التعليمات حسب نوع الملخص
    prompts = {
        'brief': f"""
أنت مساعد أكاديمي متخصص في تلخيص المحتوى التعليمي.

المهمة: قم بإنشاء ملخص موجز للنص التالي.

التعليمات:
1. اكتب ملخصاً موجزاً في 3-5 فقرات
2. ركز على الأفكار الرئيسية فقط
3. استخدم لغة واضحة ومباشرة
4. اكتب بصيغة Markdown
5. ابدأ بعنوان "# ملخص موجز"

النص:
{text[:15000]}
""",
        'detailed': f"""
أنت مساعد أكاديمي متخصص في تلخيص المحتوى التعليمي.

المهمة: قم بإنشاء ملخص تفصيلي شامل للنص التالي.

التعليمات:
1. اكتب ملخصاً تفصيلياً يغطي جميع النقاط المهمة
2. قسّم الملخص إلى أقسام مع عناوين فرعية
3. اشرح المفاهيم الصعبة
4. أضف أمثلة إن وجدت
5. اكتب بصيغة Markdown مع تنسيق جيد
6. ابدأ بعنوان "# ملخص تفصيلي"

النص:
{text[:15000]}
""",
        'key_points': f"""
أنت مساعد أكاديمي متخصص في استخراج النقاط الرئيسية.

المهمة: استخرج النقاط الرئيسية من النص التالي.

التعليمات:
1. استخرج 10-15 نقطة رئيسية
2. رتبها حسب الأهمية
3. اكتب كل نقطة بشكل مختصر وواضح
4. استخدم قائمة نقطية (-)
5. اكتب بصيغة Markdown
6. ابدأ بعنوان "# النقاط الرئيسية"

النص:
{text[:15000]}
"""
    }
    
    prompt = prompts.get(summary_type, prompts['brief'])
    
    try:
        result = generate_content(prompt)
        
        if result:
            return result
        else:
            logger.error("Gemini API returned empty response")
            return "# خطأ\n\nلم نتمكن من توليد الملخص. يرجى المحاولة مرة أخرى."
            
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise Exception(f"خطأ في الاتصال بـ Gemini API: {str(e)}")


# ==================== دوال توليد الأسئلة ====================

def generate_questions(
    text: str, 
    difficulty: str = 'medium', 
    count: int = 5,
    question_type: str = 'multiple_choice'
) -> List[Dict[str, Any]]:
    """
    توليد أسئلة اختبارية من النص باستخدام Gemini API
    
    Args:
        text: النص المصدر
        difficulty: مستوى الصعوبة ('easy', 'medium', 'hard')
        count: عدد الأسئلة المطلوبة
        question_type: نوع الأسئلة ('multiple_choice', 'true_false', 'short_answer')
    
    Returns:
        list: قائمة الأسئلة بصيغة JSON
    
    Raises:
        Exception: في حالة فشل الاتصال بـ API
    """
    if not text or len(text.strip()) < 100:
        return []
    
    difficulty_desc = {
        'easy': 'سهلة ومباشرة، تختبر الفهم الأساسي',
        'medium': 'متوسطة الصعوبة، تختبر الفهم والتطبيق',
        'hard': 'صعبة، تختبر التحليل والتقييم'
    }
    
    prompt = f"""
أنت مساعد أكاديمي متخصص في إنشاء الاختبارات.

المهمة: قم بإنشاء {count} أسئلة اختيار من متعدد من النص التالي.

مستوى الصعوبة: {difficulty_desc.get(difficulty, difficulty_desc['medium'])}

التعليمات:
1. أنشئ {count} أسئلة متنوعة تغطي المحتوى
2. كل سؤال يجب أن يحتوي على 4 خيارات
3. خيار واحد فقط صحيح
4. الخيارات الخاطئة يجب أن تكون منطقية ومقنعة
5. أرجع النتيجة بصيغة JSON فقط (بدون أي نص إضافي)

صيغة JSON المطلوبة:
[
    {{
        "question": "نص السؤال",
        "options": ["الخيار أ", "الخيار ب", "الخيار ج", "الخيار د"],
        "correct_answer": "الخيار الصحيح",
        "explanation": "شرح مختصر للإجابة الصحيحة",
        "difficulty": "{difficulty}"
    }}
]

النص:
{text[:12000]}

أرجع JSON فقط:
"""
    
    try:
        result = generate_content(prompt)
        
        if result:
            # محاولة استخراج JSON من الرد
            json_text = result.strip()
            
            # إزالة علامات الكود إن وجدت
            if json_text.startswith('```json'):
                json_text = json_text[7:]
            if json_text.startswith('```'):
                json_text = json_text[3:]
            if json_text.endswith('```'):
                json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            questions = json.loads(json_text)
            
            # التحقق من صحة البنية
            if isinstance(questions, list):
                return questions[:count]
            else:
                logger.error("Invalid questions format from Gemini")
                return []
        else:
            logger.error("Gemini API returned empty response for questions")
            return []
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        raise Exception(f"خطأ في توليد الأسئلة: {str(e)}")


# ==================== دوال المحادثة (Chatbot) ====================

def generate_chat_response(
    question: str, 
    context: Optional[str] = None,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    توليد إجابة للمساعد الذكي باستخدام Gemini API
    
    Args:
        question: سؤال المستخدم
        context: سياق من الملف (اختياري)
        chat_history: سجل المحادثة السابقة (اختياري)
    
    Returns:
        str: الإجابة
    
    Raises:
        Exception: في حالة فشل الاتصال بـ API
    """
    if not question or len(question.strip()) < 2:
        return "يرجى إدخال سؤال واضح."
    
    # بناء السياق
    context_section = ""
    if context:
        context_section = f"""
السياق المتاح (من الملف المحدد):
---
{context[:10000]}
---
"""
    
    # بناء سجل المحادثة
    history_section = ""
    if chat_history:
        history_section = "\nالمحادثة السابقة:\n"
        for msg in chat_history[-5:]:  # آخر 5 رسائل فقط
            history_section += f"المستخدم: {msg.get('question', '')}\n"
            history_section += f"المساعد: {msg.get('answer', '')}\n\n"
    
    prompt = f"""
أنت مساعد أكاديمي ذكي لنظام S-ACM (نظام إدارة المحتوى الأكاديمي الذكي).

مهمتك:
- مساعدة الطلاب في فهم المحتوى الأكاديمي
- الإجابة على الأسئلة بشكل واضح ومفيد
- إذا كان هناك سياق متاح، استخدمه للإجابة
- إذا لم تعرف الإجابة، قل ذلك بصراحة

{context_section}

{history_section}

سؤال المستخدم الحالي: {question}

أجب بشكل مفيد ومختصر:
"""
    
    try:
        result = generate_content(prompt)
        
        if result:
            return result
        else:
            return "عذراً، لم أتمكن من توليد إجابة. يرجى إعادة صياغة سؤالك."
            
    except Exception as e:
        logger.error(f"Gemini Chat API error: {str(e)}")
        raise Exception(f"خطأ في المحادثة: {str(e)}")


# ==================== دوال مساعدة ====================

def check_api_connection() -> Dict[str, Any]:
    """
    التحقق من الاتصال بـ Gemini API
    
    Returns:
        dict: حالة الاتصال
    """
    try:
        result = generate_content("قل: مرحباً")
        
        return {
            'status': 'connected',
            'model': 'gemini-1.5-flash',
            'message': 'الاتصال ناجح'
        }
    except ValueError as e:
        return {
            'status': 'error',
            'model': None,
            'message': str(e)
        }
    except Exception as e:
        return {
            'status': 'error',
            'model': None,
            'message': f'خطأ في الاتصال: {str(e)}'
        }


def estimate_tokens(text: str) -> int:
    """
    تقدير عدد التوكنات في النص (تقريبي)
    
    Args:
        text: النص
    
    Returns:
        int: العدد التقريبي للتوكنات
    """
    # تقدير تقريبي: 1 توكن ≈ 4 أحرف للإنجليزية، 2 أحرف للعربية
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    english_chars = len(text) - arabic_chars
    
    return (arabic_chars // 2) + (english_chars // 4)
