import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from PIL import Image

# إعداد الـ API
genai.configure(api_key="AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI")

# تصميم الواجهة الاحترافية (Custom CSS)
st.set_page_config(page_title="المنصة الذكية المتكاملة", layout="wide", page_icon="💎")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background-color: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; max-width: 85%; }
    .quran-container { background: #fffcf0; border-right: 8px solid #059669; padding: 25px; border-radius: 15px; font-size: 20px; line-height: 1.8; color: #1e293b; }
    .stButton>button { background: linear-gradient(90deg, #2563eb, #3b82f6); color: white; border-radius: 12px; border: none; height: 50px; width: 100%; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# وظيفة جلب الموديل بأمان
def safe_generate(content):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"⚠️ السيرفر مشغول حالياً، جرب مرة ثانية بعد ثواني. (Error: {str(e)[:50]})"

# --- التبويبات ---
t1, t2, t3 = st.tabs(["📑 ملخصات احترافية", "💬 شات ذكي سريع", "📖 واحة القرآن الكريم"])

# 1. قسم التلخيص والقوالب
with t1:
    st.markdown('<div class="main-card"><h2>🎯 صناعة المحتوى والملخصات</h2></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        u_files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
        out_lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    with col2:
        u_temp = st.file_uploader("🖼️ ارفع قالب التنسيق المفضل", type=['jpg', 'png'])
        out_style = st.selectbox("نمط التنسيق:", ["رسمي جداً", "إبداعي ملون", "جداول وبيانات"])

    if u_files and st.button("🚀 ولّد الملخص الفاخر"):
        with st.spinner("⚡ جاري المعالجة..."):
            text_data = ""
            for f in u_files:
                if f.type == "application/pdf":
                    doc = fitz.open(stream=f.read(), filetype="pdf")
                    text_data += " ".join([p.get_text() for p in doc])
                else: text_data += f.name + " "
            
            p = f"قم بتلخيص الآتي بـ {out_lang} بتنسيق {out_style} مع جداول وأسئلة. المحتوى: {text_data}"
            res = safe_generate(p)
            st.markdown(f'<div class="main-card">{res}</div>', unsafe_allow_html=True)

# 2. قسم الشات (واجهة جذابة)
with t2:
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    st.markdown("### 💬 دردشة ذكية تفهمك بسرعة")
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("اسأل عن أي شيء..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            response = safe_generate(prompt)
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# 3. قسم القرآن (تفسير موسوعي رزين)
with t3:
    st.markdown('<div class="main-card"><h2>📖 المكتبة القرآنية الشاملة</h2></div>', unsafe_allow_html=True)
    q_query = st.text_input("أدخل الآية أو السورة أو موضوع للبحث:")
    if q_query:
        with st.spinner("جاري استحضار التفاسير الملمة..."):
            q_p = f"فسر الآية التالية تفسيراً ملمًا وشاملاً (ابن كثير، الطبري، القرطبي) بأسلوب رزين وفصيح: {q_query}"
            res = safe_generate(q_p)
            st.markdown(f'<div class="quran-container">{res}</div>', unsafe_allow_html=True)
