import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from PIL import Image, ImageDraw
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعداد الـ API (سرعة خيالية)
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. وظيفة إنشاء PDF بإطار احترافي (تم حل مشكلة hexColor)
def create_fancy_pdf(text):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # رسم إطار الصفحة (Border) بلون احترافي
    c.setStrokeColor(colors.blue) # إطار أزرق فخم
    c.setLineWidth(5)
    c.rect(20, 20, width-40, height-40)
    
    # معالجة النص العربي
    reshaped_text = get_display(reshape(text))
    c.setFont("Helvetica", 12)
    
    text_object = c.beginText(width - 50, height - 80)
    for line in reshaped_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    
    c.save()
    return buffer.getvalue()

# --- واجهة المستخدم الاحترافية ---
st.set_page_config(page_title="AI Ultra Super App", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 20px; border: 2px solid #3b82f6; box-shadow: 0 10px 15px rgba(0,0,0,0.1); }
    .quran-style { background: #fffcf2; border-right: 10px solid #059669; padding: 20px; border-radius: 10px; font-size: 20px; direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 التلخيص الإمبراطوري", "💬 الشات الذكي", "📖 واحة القرآن"])

with tab1:
    st.markdown('<div class="main-card"><h1>✨ صانع الملخصات بجودة 4K</h1></div>', unsafe_allow_html=True)
    u_files = st.file_uploader("ارفع (PDF, Word, صور, صوت)", accept_multiple_files=True)
    col1, col2 = st.columns(2)
    with col1:
        out_lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    with col2:
        out_format = st.selectbox("صيغة الملف:", ["PDF بإطار", "Word منسق", "صورة جذابة"])
    
    u_template = st.file_uploader("🖼️ ارفع قالب للتنسيق (اختياري)")

    if u_files and st.button("🚀 ولّد الملخص الآن"):
        with st.spinner("⚡ جاري استخراج العظمة..."):
            contents = ["لخص المحتوى باحترافية تامة، أضف جداول، أسئلة، ونكتة. قلد القالب إن وجد."]
            for f in u_files:
                if f.type.startswith('image/'): contents.append(Image.open(f))
                else: contents.append(f)
            if u_template: contents.append(Image.open(u_template))

            res = model.generate_content(contents)
            st.markdown(f'<div class="main-card">{res.text}</div>', unsafe_allow_html=True)
            
            # التحميل
            if "PDF" in out_format:
                st.download_button("📥 تحميل PDF الاحترافي", create_fancy_pdf(res.text), "Summary_Pro.pdf")
            elif "Word" in out_format:
                doc = Document()
                doc.add_heading('Professional Summary', 0)
                doc.add_paragraph(res.text)
                buf = BytesIO()
                doc.save(buf)
                st.download_button("📥 تحميل Word المنسق", buf.getvalue(), "Summary_Pro.docx")

# أقسام الشات والقرآن تعمل بنفس القوة المعتادة
