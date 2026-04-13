import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import hexColor
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعداد الـ API (السرعة الخيالية مع Flash)
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. وظيفة رسم إطار وتنسيق PDF احترافي
def create_fancy_pdf(text, color_hex="#1e3a8a"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # رسم الإطار (Border)
    c.setStrokeColor(hexColor(color_hex))
    c.setLineWidth(5)
    c.rect(20, 20, width-40, height-40) # إطار فخم
    
    # كتابة النص (معالجة العربي)
    reshaped_text = get_display(reshape(text))
    c.setFont("Helvetica", 12) # ملاحظة: يفضل تحميل خط عربي ttf
    
    # توزيع النص
    text_object = c.beginText(width - 50, height - 70)
    for line in reshaped_text.split('\n'):
        text_object.textLine(line)
    c.drawText(text_object)
    
    c.save()
    return buffer.getvalue()

# 3. وظيفة تحويل الملخص لصورة (تصميم جذاب)
def text_to_image(text):
    img = Image.new('RGB', (800, 1200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    # رسم برواز للصورة
    d.rectangle([10, 10, 790, 1190], outline="#1e3a8a", width=10)
    d.text((50, 50), text[:1000], fill=(0, 0, 0)) # تبسيط للعرض
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()

# --- واجهة المستخدم ---
st.set_page_config(page_title="AI Ultra Pro", layout="wide")

# تصميم CSS فائق الجمال
st.markdown("""
    <style>
    .main { background: #f0f2f5; }
    .stTabs [data-baseweb="tab-list"] { background: white; border-radius: 15px; padding: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }
    .res-box { background: white; border: 2px solid #1e3a8a; border-radius: 15px; padding: 25px; color: #1e293b; }
    </style>
    """, unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚀 التلخيص الفائق", "💬 الشات المفتوح", "📖 كنوز القرآن"])

with tab1:
    st.subheader("🛠️ تخصيص الملخص (الجودة العالية)")
    col1, col2 = st.columns(2)
    with col1:
        u_files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور متعددة)", accept_multiple_files=True)
        out_lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    with col2:
        u_template = st.file_uploader("🖼️ ارفع قالب ليتم تقليده", type=['jpg', 'png'])
        out_type = st.selectbox("صيغة المخرجات:", ["PDF (إطار احترافي)", "Word (تنسيق عالي)", "صورة (تصميم جذاب)"])

    if u_files and st.button("✨ ابدأ المعالجة"):
        with st.spinner("⚡ جاري استخراج البيانات ومحاكاة القالب بسرعة خيالية..."):
            # تجميع المحتوى
            full_content = []
            for f in u_files:
                if f.type.startswith('image/'):
                    full_content.append(Image.open(f))
                else:
                    full_content.append(f)
            
            prompt = f"لخص المحتوى بـ {out_lang} باحترافية تامة. استخدم جداول، عناوين، أسئلة، ونكتة. قلد القالب المرفق في التنسيق والألوان."
            if u_template: full_content.append(Image.open(u_template))
            
            response = model.generate_content([prompt] + full_content)
            result_text = response.text
            
            st.markdown(f'<div class="res-box">{result_text}</div>', unsafe_allow_html=True)
            
            # خيارات التحميل
            if "PDF" in out_type:
                data = create_fancy_pdf(result_text)
                st.download_button("📥 تحميل PDF بالإطار", data, "Summary_Pro.pdf")
            elif "صورة" in out_type:
                data = text_to_image(result_text)
                st.download_button("📥 تحميل الملخص كصورة", data, "Summary_Pro.png")
            else:
                doc = Document()
                doc.add_heading('Professional Summary', 0)
                doc.add_paragraph(result_text)
                buf = BytesIO()
                doc.save(buf)
                st.download_button("📥 تحميل Word منسق", buf.getvalue(), "Summary.docx")

# التبويبات الأخرى (الشات والقرآن) بنفس القوة
