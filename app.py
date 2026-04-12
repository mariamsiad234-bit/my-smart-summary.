import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO

# 1. إعداد الصفحة
st.set_page_config(page_title="الملخص الذكي", page_icon="📝")

# 2. إعداد مفتاح Gemini (مفتاحك شغال تمام)
API_KEY = "AIzaSyAlGMaza9pgQ_0m2D61vKGOC239VSS4VOI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 3. وظيفة استخراج النص
def extract_text(uploaded_file):
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

# 4. واجهة المستخدم
st.title("📝 مساعد التلخيص الذكي")
st.write("ارفع ملفك (PDF أو Word) وهلخصه لك في ثواني!")

file = st.file_uploader("اختر الملف", type=['pdf', 'docx', 'txt'])

if file:
    with st.spinner("جاري قراءة الملف وتلخيصه..."):
        text_content = extract_text(file)
        prompt = f"قم بتلخيص النص التالي بأسلوب احترافي ونقاط واضحة باللغة العربية:\n\n{text_content}"
        
        response = model.generate_content(prompt)
        st.subheader("الملخص:")
        st.write(response.text)
        
        # تحويل الملخص لملف Word للتحميل
        output_doc = Document()
        output_doc.add_heading('ملخص الملف', 0)
        output_doc.add_paragraph(response.text)
        target_stream = BytesIO()
        output_doc.save(target_stream)
        
        st.download_button(
            label="تحميل الملخص (Word)",
            data=target_stream.getvalue(),
            file_name="summary.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
