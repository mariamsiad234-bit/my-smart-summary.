import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعداد الـ API والموديل (نظام التحقق من الموديل)
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)

def load_safe_model():
    # بنجرب الفلاش الأول، لو منفعش بنحول للبرو عشان التطبيق ميفصلش
    try:
        m = genai.GenerativeModel('gemini-1.5-flash')
        return m
    except:
        return genai.GenerativeModel('gemini-pro')

model = load_safe_model()

# 2. واجهة المستخدم (Professional Glass UI)
st.set_page_config(page_title="المنصة الإمبراطورية AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    .main-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .quran-box { background: #fffcf0; border-right: 10px solid #10b981; padding: 25px; border-radius: 15px; font-size: 22px; color: #064e3b; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# 3. وظائف المعالجة الاحترافية (حل الـ TypeError)
def process_file_to_content(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return " ".join([page.get_text() for page in doc])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.type.startswith('image/'):
        return Image.open(uploaded_file)
    else:
        return uploaded_file.read().decode("utf-8", errors="ignore")

# --- الأقسام ---
tab1, tab2, tab3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات الذكي", "📖 الموسوعة القرآنية"])

# 1. قسم التلخيص
with tab1:
    st.markdown('<div class="main-card"><h2>🎯 التلخيص الذكي وتصميم القوالب</h2></div>', unsafe_allow_html=True)
    files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
    template = st.file_uploader("🖼️ قالب التنسيق (اختياري)", type=['jpg', 'png'])
    lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    
    if files and st.button("🚀 ولّد الملخص الفخم"):
        with st.spinner("⚡ جاري تحليل المحتوى وتنسيق القالب..."):
            final_contents = []
            for f in files:
                processed = process_file_to_content(f)
                final_contents.append(processed if isinstance(processed, Image.Image) else f"المحتوى المستخرج: {processed}")
            
            prompt = f"قم بتلخيص المحتوى بـ {lang} باحترافية تامة. استخدم جداول وأسئلة قياس مستوى. لو فيه صورة قالب، قلد أسلوبها في التنسيق."
            if template: final_contents.append(Image.open(template))
            
            res = model.generate_content([prompt] + final_contents)
            st.markdown(f'<div class="main-card">{res.text}</div>', unsafe_allow_html=True)

# 2. قسم الشات (جذاب وسريع)
with tab2:
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("تكلم معي، اطلب تلخيصاً، أو استفسر عن شيء..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            r = model.generate_content(p)
            st.markdown(r.text)
            st.session_state.messages.append({"role": "assistant", "content": r.text})

# 3. قسم القرآن (احترافي جداً)
with tab3:
    st.markdown('<div class="main-card"><h2>📖 الباحث القرآني المتقدم</h2></div>', unsafe_allow_html=True)
    q_input = st.text_input("أدخل الآية أو اسم السورة أو موضوع للبحث:")
    if q_input:
        with st.spinner("جاري استحضار التفسير الشامل..."):
            q_prompt = f"بصفتك خبير في علوم القرآن، فسر الآية التالية تفسيراً واسعاً ومجمعاً من (ابن كثير والطبري والجلالين) وأكملها لو كانت ناقصة: {q_input}"
            q_res = model.generate_content(q_prompt)
            st.markdown(f'<div class="quran-box">{q_res.text}</div>', unsafe_allow_html=True)
