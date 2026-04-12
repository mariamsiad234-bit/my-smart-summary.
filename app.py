import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

# 1. إعداد الصفحة وتغيير الثيم للعربي
st.set_page_config(page_title="الملخص الذكي", page_icon="📝", layout="centered")

# 2. إعداد مفتاح Gemini الجديد
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. وظيفة استخراج النص من الملفات
def extract_text(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(uploaded_file)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return None

# 4. واجهة المستخدم (تصميم أنيق)
st.markdown("""
    <style>
    .main { text-align: right; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #4CAF50; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📝 مساعد التلخيص الذكي")
st.write("ارفع ملفك (PDF أو Word) وسأقوم بتلخيصه لك فوراً باستخدام الذكاء الاصطناعي.")

file = st.file_uploader("اختر الملف من جهازك", type=['pdf', 'docx', 'txt'])

if file:
    with st.spinner("جاري معالجة الملف وتوليد الملخص..."):
        text_content = extract_text(file)
        
        if text_content and len(text_content.strip()) > 10:
            prompt = f"قم بتلخيص النص التالي بأسلوب احترافي ونقاط واضحة ومنظمة باللغة العربية:\n\n{text_content}"
            
            try:
                response = model.generate_content(prompt)
                
                st.success("تم التلخيص بنجاح!")
                st.subheader("الملخص الناتجة:")
                st.write(response.text)
                
                # إنشاء ملف Word للتحميل
                output_doc = Document()
                output_doc.add_heading('ملخص الملف الخاص بك', 0)
                output_doc.add_paragraph(response.text)
                
                target_stream = BytesIO()
                output_doc.save(target_stream)
                
                st.download_button(
                    label="📥 تحميل الملخص كملف Word",
                    data=target_stream.getvalue(),
                    file_name="smart_summary.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error("عذراً، حدث خطأ مع الذكاء الاصطناعي. تأكد من صلاحية المفتاح.")
        else:
            st.warning("الملف يبدو فارغاً أو غير مدعوم بشكل صحيح.")

st.info("نصيحة: إذا واجهت خطأ 'removeChild'، فقط قم بتحديث الصفحة (Refresh).")
