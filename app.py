import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعداد الـ API مع نظام "التبديل التلقائي" للموديلات
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)

def get_working_model():
    # بنجرب الموديل الأحدث، لو فيه NotFound بنحول للمستقر فوراً
    for model_name in ['gemini-1.5-flash', 'gemini-pro']:
        try:
            m = genai.GenerativeModel(model_name)
            # تجربة سريعة للتأكد من الاتصال
            m.generate_content("ping")
            return m
        except Exception:
            continue
    return genai.GenerativeModel('gemini-pro')

model = get_working_model()

# 2. تصميم الواجهة الإمبراطورية (Glass UI)
st.set_page_config(page_title="المنصة الذكية Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); }
    .glass-card { background: rgba(255, 255, 255, 0.9); padding: 25px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #dee2e6; margin-bottom: 20px; }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; max-width: 80%; line-height: 1.6; }
    .user { background: #007bff; color: white; align-self: flex-start; }
    .bot { background: #ffffff; color: #333; border: 1px solid #ddd; align-self: flex-end; }
    .quran-style { background: #fffdf5; border-right: 10px solid #10b981; padding: 25px; border-radius: 15px; font-size: 22px; color: #064e3b; }
    </style>
    """, unsafe_allow_html=True)

# 3. وظيفة استخراج النص (لحل TypeError نهائياً)
def extract_content(file):
    if file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return " ".join([page.get_text() for page in doc])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.type.startswith('image/'):
        return Image.open(file)
    return file.read().decode("utf-8", errors="ignore")

# --- الأقسام الرئيسية ---
tab1, tab2, tab3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات الذكي", "📖 الموسوعة القرآنية"])

# القسم 1: التلخيص
with tab1:
    st.markdown('<div class="glass-card"><h2>🎯 التلخيص الاحترافي الفوري</h2></div>', unsafe_allow_html=True)
    files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
    template = st.file_uploader("🖼️ قالب التنسيق (اختياري)", type=['jpg', 'png'])
    lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    
    if files and st.button("🚀 ولّد الملخص الإمبراطوري"):
        with st.spinner("⚡ جاري تحليل البيانات..."):
            all_data = []
            for f in files:
                data = extract_content(f)
                all_data.append(data if isinstance(data, Image.Image) else f"نص: {data}")
            
            prompt = f"لخص هذا المحتوى بـ {lang} باحترافية تامة، مع جداول وأسئلة. لو وجدت صورة قالب، قلد أسلوبها."
            if template: all_data.append(Image.open(template))
            
            response = model.generate_content([prompt] + all_data)
            st.markdown(f'<div class="glass-card">{response.text}</div>', unsafe_allow_html=True)

# القسم 2: الشات (سريع وجذاب)
with tab2:
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("تكلم معي، اطلب تلخيصاً، أو اسأل عن أي شيء..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            r = model.generate_content(p)
            st.markdown(r.text)
            st.session_state.chat_history.append({"role": "assistant", "content": r.text})

# القسم 3: القرآن (تفسير ملم وبأسلوب رزين)
with tab3:
    st.markdown('<div class="glass-card"><h2>📖 واحة القرآن الكريم</h2></div>', unsafe_allow_html=True)
    q_query = st.text_input("أدخل الآية أو الموضوع للبحث:")
    if q_query:
        with st.spinner("جاري استحضار التفسير الشامل..."):
            q_prompt = f"بصفتك خبير في علوم القرآن، فسر الآية التالية تفسيراً واسعاً من (ابن كثير والطبري) وأكملها: {q_query}"
            q_res = model.generate_content(q_prompt)
            st.markdown(f'<div class="quran-style">{q_res.text}</div>', unsafe_allow_html=True)
