import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from io import BytesIO
from PIL import Image

# 1. إعداد الـ API بأعلى احترافية
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)

# إعدادات الموديل (السرعة القصوى والذكاء)
generation_config = {
  "temperature": 0.7, # توازن بين الإبداع والدقة
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

# 2. واجهة مستخدم (UI) تليق بمشروعك
st.set_page_config(page_title="المنصة الشاملة AI", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f8fafc; }
    .main-card { background: white; padding: 25px; border-radius: 15px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1); }
    .quran-style { font-size: 20px; color: #064e3b; background: #ecfdf5; padding: 20px; border-radius: 10px; border-right: 8px solid #10b981; line-height: 1.8; }
    </style>
    """, unsafe_allow_html=True)

# 3. تنظيم الأقسام (Tabs)
tab1, tab2, tab3 = st.tabs(["💎 التلخيص والقوالب", "💬 الشات الذكي", "📖 الباحث القرآني"])

# --- القسم الأول: التلخيص الاحترافي ---
with tab1:
    st.subheader("🎯 ملخصات ذكية وتصميم قوالب")
    col_a, col_b = st.columns(2)
    with col_a:
        file = st.file_uploader("ارفع الملف (PDF, Word, Audio, Image)", type=['pdf', 'docx', 'jpg', 'png', 'mp3', 'wav'])
    with col_b:
        template = st.file_uploader("🖼️ ارفع القالب اللي عايزنا نقلده", type=['jpg', 'png'])
    
    lang = st.segmented_control("اللغة المطلوبة", ["العربية", "English"], default="العربية")

    if file and st.button("✨ توليد الملخص الاحترافي"):
        with st.spinner("⚡ الذكاء الاصطناعي شغال حالياً..."):
            prompt = f"قم بتلخيص المحتوى المرفق بأسلوب احترافي شامل بـ {lang}. استخدم جداول، أسئلة MCQs، وكاريكاتير مضحك. لو ريكورد اذكر مدته."
            content_to_send = [prompt, file]
            if template: content_to_send.append(Image.open(template))
            
            response = model.generate_content(content_to_send)
            st.markdown(f'<div class="main-card">{response.text}</div>', unsafe_allow_html=True)

# --- القسم الثاني: الشات (بذاكرة قوية) ---
with tab2:
    st.subheader("💬 دردشة ذكية (Gemini Pro)")
    if "chat_session" not in st.session_state:
        st.session_state.chat_session = model.start_chat(history=[])

    for message in st.session_state.chat_session.history:
        with st.chat_message("user" if message.role == "user" else "assistant"):
            st.markdown(message.parts[0].text)

    if user_query := st.chat_input("اسأل أي شيء..."):
        with st.chat_message("user"): st.markdown(user_query)
        response = st.session_state.chat_session.send_message(user_query)
        with st.chat_message("assistant"): st.markdown(response.text)

# --- القسم الثالث: القرآن الكريم (تفسير وإكمال) ---
with tab3:
    st.subheader("📖 المساعد القرآني المتكامل")
    mode = st.radio("الاختيار:", ["تفسير شامل", "إكمال الآية وتصحيحها"], horizontal=True)
    quran_input = st.text_area("أدخل الآية أو جزء منها:")
    
    if quran_input and st.button("🔍 بحث"):
        with st.spinner("جاري استخراج البيانات من كتب التفسير..."):
            q_prompt = f"بصفتك خبير في علوم القرآن، قم بـ {mode} للنص التالي: {quran_input}. اذكر اسم السورة ورقم الآية والتفسير المعتمد فقهياً ولغوياً."
            q_response = model.generate_content(q_prompt)
            st.markdown(f'<div class="quran-style">{q_response.text}</div>', unsafe_allow_html=True)
