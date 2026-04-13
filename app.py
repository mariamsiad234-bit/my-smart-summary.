import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعداد الـ API مع نظام "الإنقاذ الذاتي" للموديل
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)

def get_best_model():
    # بنجرب الموديلات المتاحة بالترتيب عشان نتخطى خطأ NotFound
    for m_name in ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']:
        try:
            tmp_model = genai.GenerativeModel(m_name)
            # تجربة وهمية للتأكد من الموديل
            tmp_model.generate_content("hi")
            return tmp_model
        except:
            continue
    return genai.GenerativeModel('gemini-pro')

model = get_best_model()

# 2. تصميم الواجهة الإمبراطورية (CSS الاحترافي)
st.set_page_config(page_title="المنصة الذكية Pro", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #f4f7f9; }
    /* كارت احترافي */
    .pro-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); border: 1px solid #e0e6ed;
        margin-bottom: 20px; transition: 0.3s;
    }
    .pro-card:hover { transform: translateY(-5px); }
    /* تنسيق القرآن */
    .quran-box {
        background: #fffdf5; border-right: 10px solid #10b981;
        padding: 25px; border-radius: 15px; font-size: 22px;
        color: #064e3b; box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# 3. محرك استخراج البيانات (منع الـ TypeError)
def get_clean_content(f):
    try:
        if f.type == "application/pdf":
            doc = fitz.open(stream=f.read(), filetype="pdf")
            return " ".join([p.get_text() for p in doc])
        elif f.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = Document(f)
            return "\n".join([p.text for p in doc.paragraphs])
        elif f.type.startswith('image/'):
            return Image.open(f)
        return f.read().decode("utf-8", errors="ignore")
    except: return "خطأ في قراءة الملف"

# --- التبويبات الرئيسية ---
t1, t2, t3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات الذكي", "📖 الموسوعة القرآنية"])

with t1:
    st.markdown('<div class="pro-card"><h2>🎯 التلخيص الفائق وتصميم القوالب</h2></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        u_files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
        lang = st.radio("اللغة:", ["العربية", "English"], horizontal=True)
    with c2:
        u_temp = st.file_uploader("🖼️ قالب التنسيق (اختياري)", type=['jpg', 'png'])
        out_format = st.selectbox("صيغة المخرج:", ["PDF احترافي", "Word منسق", "صورة جذابة"])

    if u_files and st.button("🚀 ولّد الملخص الإمبراطوري"):
        with st.spinner("⚡ جاري استخراج العظمة..."):
            all_data = []
            for f in u_files:
                data = get_clean_content(f)
                all_data.append(data if isinstance(data, Image.Image) else f"النص: {data}")
            
            prompt = f"قم بتلخيص المحتوى بـ {lang} باحترافية تامة. استخدم جداول وأسئلة ذكاء ونكتة. قلد القالب المرفق في التنسيق والألوان."
            if u_temp: all_data.append(Image.open(u_temp))
            
            res = model.generate_content([prompt] + all_data)
            st.markdown(f'<div class="pro-card" style="border-right: 5px solid blue;">{res.text}</div>', unsafe_allow_html=True)

with t2:
    st.subheader("💬 دردشة ذكية وسلسة")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("تحدث معي، اطلب تلخيصاً، أو اسأل عن أي شيء..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            r = model.generate_content(p)
            st.markdown(r.text)
            st.session_state.chat_history.append({"role": "assistant", "content": r.text})

with t3:
    st.markdown('<div class="pro-card"><h2>📖 الموسوعة القرآنية الشاملة</h2></div>', unsafe_allow_html=True)
    q_query = st.text_input("أدخل الآية أو الموضوع (تفسير، أسباب نزول، إكمال):")
    if q_query:
        with st.spinner("جاري البحث في أمهات التفاسير..."):
            q_prompt = f"بصفتك خبير في علوم القرآن، فسر الآية التالية تفسيراً مجمعاً (ابن كثير والطبري) بأسلوب رزين وفصيح وأكملها: {q_query}"
            q_res = model.generate_content(q_prompt)
            st.markdown(f'<div class="quran-box">{q_res.text}</div>', unsafe_allow_html=True)
