import streamlit as st
import google.generativeai as genai
import pdfplumber
from docx import Document
from io import BytesIO
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from arabic_reshaper import reshape
from bidi.algorithm import get_display

# إعداد الـ API
API_KEY = "AIzaSyDso4OPFXij1guGTSX6gN2zwSaXDix-c1o"
genai.configure(api_key=API_KEY)

@st.cache_resource
def get_model():
    return genai.GenerativeModel('gemini-1.5-flash')

model = get_model()

# تنسيق الخط العربي
def fix_text(t):
    return get_display(reshape(t))

# واجهة المستخدم
st.set_page_config(page_title="المنصة الملكية AI", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #fdfdfd; }
    .pro-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #eee; margin-bottom: 20px; }
    .quran-box { background: #fffcf0; border-right: 10px solid #059669; padding: 25px; border-radius: 15px; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# القائمة الجانبية للتحكم
with st.sidebar:
    st.header("🎨 تخصيص الإطارات")
    b_color = st.color_picker("لون الإطار", "#1e3a8a")
    st.info("ارفع ملفاتك وابدأ التلخيص فوراً")

t1, t2, t3 = st.tabs(["📑 التلخيص والقوالب", "💬 الشات المطور", "📖 واحة القرآن"])

# --- التلخيص ---
with t1:
    st.markdown('<div class="pro-card"><h2>🎯 مركز التلخيص وتصميم الملفات</h2></div>', unsafe_allow_html=True)
    up_files = st.file_uploader("ارفع (صور، PDF، Word)", accept_multiple_files=True)
    custom_frame = st.file_uploader("🖼️ ارفع إطار خاص بك (اختياري)", type=['jpg', 'png'])
    
    if up_files:
        options = ["PDF احترافي", "Word منسق"]
        if len(up_files) <= 10: options.append("صور مصممة")
        out_type = st.radio("نوع الملف المطلوب:", options, horizontal=True)

        if st.button("🚀 ولّد الملخص الإمبراطوري"):
            with st.spinner("⚡ جاري استخراج العظمة..."):
                all_contents = []
                for f in up_files:
                    if f.type.startswith('image/'): all_contents.append(Image.open(f))
                    elif f.type == "application/pdf":
                        with pdfplumber.open(f) as pdf:
                            all_contents.append(" ".join([p.extract_text() for p in pdf.pages]))
                    else: all_contents.append(f.read().decode(errors='ignore'))
                
                if custom_frame: all_contents.append(Image.open(custom_frame))
                
                prompt = "لخص باحترافية، لغة عربية 100% رصينة، جداول، أسئلة، وكاريكاتير وصفي. قلد القالب لو وجد."
                res = model.generate_content([prompt] + all_contents).text
                st.markdown(f'<div class="pro-card" style="border-right: 10px solid {b_color};">{res}</div>', unsafe_allow_html=True)

# --- الشات (يدعم الصور والملفات) ---
with t2:
    st.subheader("💬 دردشة ذكية شاملة")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    # ارفع ملفات للشات
    chat_files = st.file_uploader("ارفع ملفات للشات (اختياري)", accept_multiple_files=True, key="chat")
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("تكلم معي أو اسأل عن الملفات المرفوعة..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            chat_payload = [p]
            if chat_files:
                for cf in chat_files:
                    if cf.type.startswith('image/'): chat_payload.append(Image.open(cf))
                    else: chat_payload.append(f"ملف مرفق: {cf.name}")
            
            r = model.generate_content(chat_payload).text
            st.markdown(r)
            st.session_state.messages.append({"role": "assistant", "content": r})

# --- القرآن ---
with t3:
    st.markdown('<div class="pro-card"><h2>📖 التفسير الملم والرزين</h2></div>', unsafe_allow_html=True)
    q = st.text_input("أدخل الآية أو اسم السورة:")
    if q:
        with st.spinner("جاري استحضار علوم القرآن..."):
            res = model.generate_content(f"فسر وأكمل ووضح أسباب نزول الآتي بأسلوب رزين ملم بكافة التفاسير: {q}").text
            st.markdown(f'<div class="quran-box">{res}</div>', unsafe_allow_html=True)
