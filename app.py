import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# 1. إعداد الـ API والموديل
API_KEY = "AIzaSyDso4OPFXij1guGTSX6gN2zwSaXDix-c1o"
genai.configure(api_key=API_KEY)

@st.cache_resource
def load_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = load_model()

# 2. وظائف المعالجة الاحترافية
def fix_arabic(text):
    return get_display(reshape(text))

def create_pro_pdf(text, border_color):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    # إطار الصفحة
    c.setStrokeColor(colors.toColor(border_color))
    c.setLineWidth(10)
    c.rect(20, 20, width-40, height-40)
    # النص
    c.setFont("Helvetica", 12)
    t = c.beginText(width - 50, height - 80)
    for line in fix_arabic(text).split('\n'):
        t.textLine(line)
    c.drawText(t)
    c.save()
    return buf.getvalue()

# 3. واجهة المستخدم (Modern VIP Design)
st.set_page_config(page_title="المنصة الإمبراطورية Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .quran-style { background: #fffcf0; border-right: 10px solid #10b981; padding: 25px; border-radius: 15px; }
    </style>
    """, unsafe_allow_html=True)

# القائمة الجانبية للتحكم في الإطارات
with st.sidebar:
    st.header("🎨 استوديو التنسيق")
    b_color = st.color_picker("اختر لون الإطار الاحترافي", "#1e3a8a")
    st.divider()
    st.info("نظام التلخيص يدعم: الجداول، الكاريكاتير الوصفي، والأسئلة الذكية.")

t1, t2, t3 = st.tabs(["📑 التلخيص الذكي", "💬 الشات الأونلاين", "📖 واحة القرآن"])

# --- تبويب التلخيص ---
with t1:
    st.markdown('<div class="main-card"><h2>🎯 مركز التلخيص وتصميم الملفات</h2></div>', unsafe_allow_html=True)
    up_files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور متعددة)", accept_multiple_files=True)
    custom_border = st.file_uploader("🖼️ ارفع إطار خاص بك (اختياري)", type=['jpg', 'png'])
    
    if up_files:
        file_count = len(up_files)
        options = ["PDF احترافي", "Word منسق"]
        if file_count <= 10: options.append("ملف صور (تصميم جذاب)")
        
        out_format = st.selectbox("اختر صيغة استخراج الملخص:", options)
        
        if st.button("🚀 ولّد الملخص الآن"):
            with st.spinner("⚡ جاري تحليل المحتوى ومحاكاة القوالب..."):
                contents = ["لخص بأسلوب رزين، لغة عربية 100%، جداول، أسئلة، وكاريكاتير وصفي."]
                for f in up_files:
                    if f.type.startswith('image/'): contents.append(Image.open(f))
                    else: contents.append(f)
                if custom_border: contents.append(Image.open(custom_border))
                
                res = model.generate_content(contents).text
                st.markdown(f'<div class="main-card" style="border: 3px solid {b_color};">{res}</div>', unsafe_allow_html=True)
                
                # التصدير
                if out_format == "PDF احترافي":
                    st.download_button("📥 تحميل PDF", create_pro_pdf(res, b_color), "Summary.pdf")
                elif out_format == "Word منسق":
                    doc = Document()
                    doc.add_heading('Professional Summary', 0)
                    doc.add_paragraph(res)
                    b = BytesIO(); doc.save(b)
                    st.download_button("📥 تحميل Word", b.getvalue(), "Summary.docx")
                else:
                    st.warning("تم عرض الملخص كصورة في المعاينة أعلاه (ميزة الصور قيد التنسيق النهائي).")

# --- تبويب الشات ---
with t2:
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if p := st.chat_input("تكلم معي.. ارفع صورة واسأل عنها أو اطلب تلخيصاً"):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            r = model.generate_content(p).text
            st.markdown(r)
            st.session_state.msgs.append({"role": "assistant", "content": r})

# --- تبويب القرآن ---
with t3:
    st.markdown('<div class="main-card"><h2>📖 المكتبة القرآنية الشاملة</h2></div>', unsafe_allow_html=True)
    q = st.text_input("أدخل الآية أو الموضوع:")
    if q:
        with st.spinner("جاري استحضار التفاسير الملمة..."):
            res = model.generate_content(f"فسر وأكمل ووضح أسباب نزول الآتي بأسلوب رزين ملم بكافة التفاسير: {q}").text
            st.markdown(f'<div class="quran-style">{res}</div>', unsafe_allow_html=True)
