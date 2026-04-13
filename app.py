import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعدادات الـ API والموديل
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. تصميم الواجهة الاحترافي (Advanced CSS)
st.set_page_config(page_title="المساعد الذكي Pro", page_icon="🪄", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Cairo', sans-serif; }
    .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
    
    /* تأثير الزجاج للبوكسات */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        margin-bottom: 20px;
    }
    
    /* أزرار جذابة */
    .stButton>button {
        background: linear-gradient(45deg, #00dbde 0%, #fc00ff 100%);
        color: white; border: none; border-radius: 12px;
        transition: 0.3s; transform: scale(1);
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    
    /* تنسيق القرآن */
    .quran-text {
        background: #fffdf5; border-right: 10px solid #10b981;
        padding: 20px; border-radius: 15px; font-size: 22px;
        color: #064e3b; box-shadow: inset 0 0 10px rgba(0,0,0,0.02);
    }
    </style>
    """, unsafe_allow_html=True)

# --- محرك معالجة النصوص ---
def get_text(file):
    if file.type == "application/pdf":
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return " ".join([p.get_text() for p in doc])
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    return ""

# --- الأقسام الرئيسية ---
tab1, tab2, tab3 = st.tabs(["✨ الملخص السحري", "💬 الشات المطور", "📖 واحة القرآن"])

with tab1:
    st.markdown('<div class="glass-card"><h1>🪄 التلخيص الاحترافي بالقوالب</h1></div>', unsafe_allow_html=True)
    c1, c2 = st.columns([2,1])
    with c1:
        u_file = st.file_uploader("ارفع (PDF, Word, صوت)", type=['pdf', 'docx', 'mp3', 'wav', 'm4a'], key="main_u")
    with c2:
        u_temp = st.file_uploader("🖼️ قالب التنسيق", type=['jpg', 'png'], key="temp_u")
    
    style = st.select_slider("اختر نمط التنسيق:", ["بسيط", "أكاديمي مكثف", "إبداعي ملون", "خرائط ذهنية نصية"])
    
    if u_file and st.button("🚀 ولّد العظمة"):
        with st.spinner("⚡ جاري استخراج الأفكار وتنسيقها..."):
            text_content = get_text(u_file) if u_file.type in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"] else ""
            
            prompt = f"""
            بصفتك خبير تنسيق ومحتوى، لخص الآتي بنمط {style}:
            - استخدم ألوان (بالوصف النصي) وتنسيق جداول احترافي.
            - أضف أيقونات توضيحية لكل فكرة.
            - صمم 5 أسئلة ذكاء في النهاية.
            - أضف 'نكتة' أو كاريكاتير وصفي يخص الموضوع.
            """
            inputs = [prompt, u_file] if not text_content else [prompt + text_content]
            if u_temp: inputs.append(Image.open(u_temp))
            
            res = model.generate_content(inputs)
            st.markdown(f'<div class="glass-card">{res.text}</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<h3>💬 دردش وتحكم في ملفاتك</h3>', unsafe_allow_html=True)
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if p := st.chat_input("تحدث معي أو اطلب تلخيص جزء معين..."):
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        # الشات هنا يقدر يوصل لكل ملفاتك
        r = model.generate_content(p)
        st.session_state.chat_history.append({"role": "assistant", "content": r.text})
        with st.chat_message("assistant"): st.markdown(r.text)

with tab3:
    st.markdown('<div class="glass-card"><h2>📖 الباحث القرآني الفوري</h2></div>', unsafe_allow_html=True)
    q_query = st.text_input("اكتب الآية أو الموضوع (مثلاً: آيات الصبر، تفسير سورة الملك):")
    if q_query:
        with st.spinner("جاري استحضار التفسير..."):
            q_res = model.generate_content(f"قدم تفسير دقيق وشامل وإكمال للآية: {q_query}. اعتمد مراجع التفسير الموثوقة بأسلوب فصيح.")
            st.markdown(f'<div class="quran-text">{q_res.text}</div>', unsafe_allow_html=True)
