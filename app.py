import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعداد الـ API
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)

# 2. وظيفة ذكية لجلب الموديل المتاح (حل مشكلة NotFound)
def load_model():
    # بنجرب كل المسميات الممكنة عشان نهرب من الـ NotFound
    models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-1.5-flash']
    for m_name in models_to_try:
        try:
            m = genai.GenerativeModel(m_name)
            # تجربة وهمية للتأكد
            m.generate_content("test")
            return m, m_name
        except:
            continue
    return None, None

model, active_model_name = load_model()

# 3. واجهة المستخدم الاحترافية
st.set_page_config(page_title="AI Ultra Pro", layout="wide")

# لو الموديل مش متاح، بنعرض تنبيه شيك بدل الشاشة الحمراء
if not model:
    st.error("⚠️ عذراً يا بطل، الموديل مش متاح في منطقتك حالياً أو مفتاح الـ API محتاج تفعيل. جرب تعمل Reboot للتطبيق.")
    st.stop()

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #fdfdfd; }
    .main-box { background: white; padding: 20px; border-radius: 15px; border: 2px solid #3b82f6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

# --- التبويبات الرئيسية ---
t1, t2, t3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات الذكي", "📖 واحة القرآن"])

with t1:
    st.markdown('<div class="main-box"><h2>🎯 ملخصات ذكية بتصميم القوالب</h2></div>', unsafe_allow_html=True)
    f = st.file_uploader("ارفع ملفاتك", accept_multiple_files=True)
    temp = st.file_uploader("🖼️ قالب التنسيق", type=['jpg', 'png'])
    if f and st.button("🚀 ولّد الملخص"):
        with st.spinner("⚡ شغالين يا بطل..."):
            contents = ["لخص بأسلوب احترافي جداً بجدول وأسئلة ونكتة. قلد القالب إن وجد."]
            for file in f:
                if file.type.startswith('image/'): contents.append(Image.open(file))
                elif file.type == "application/pdf":
                    doc = fitz.open(stream=file.read(), filetype="pdf")
                    contents.append(" ".join([p.get_text() for p in doc]))
                else: contents.append(file.read().decode())
            if temp: contents.append(Image.open(temp))
            
            res = model.generate_content(contents)
            st.markdown(f'<div class="main-card">{res.text}</div>', unsafe_allow_html=True)

with t2:
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if p := st.chat_input("تحدث معي..."):
        st.session_state.msgs.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        r = model.generate_content(p)
        st.session_state.msgs.append({"role": "assistant", "content": r.text})
        with st.chat_message("assistant"): st.markdown(r.text)

with t3:
    st.markdown('<div class="main-box"><h2>📖 الموسوعة القرآنية</h2></div>', unsafe_allow_html=True)
    q = st.text_input("أدخل الآية أو الموضوع:")
    if q:
        with st.spinner("جاري استحضار التفسير..."):
            res = model.generate_content(f"فسر وأكمل ووضح أسباب نزول بأسلوب رزين ملم بكافة التفاسير: {q}")
            st.markdown(f'<div style="background:#fffcf0; padding:20px; border-radius:10px;">{res.text}</div>', unsafe_allow_html=True)
