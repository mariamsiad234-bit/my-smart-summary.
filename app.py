import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from PIL import Image

# إعداد الـ API
genai.configure(api_key="AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI")

# تصميم الواجهة (UI/UX الاحترافي)
st.set_page_config(page_title="الإمبراطور الذكي AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #fdfdfd; }
    .main-card { background: white; padding: 25px; border-radius: 20px; border: 1px solid #e2e8f0; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
    .quran-box { background: #fffcf0; border-right: 10px solid #059669; padding: 25px; border-radius: 15px; font-size: 20px; line-height: 1.8; }
    .stChatFloatingInputContainer { background-color: rgba(255,255,255,0.0) !important; }
    </style>
    """, unsafe_allow_html=True)

# محرك ذكاء اصطناعي مضاد للأخطاء
def call_ai(prompt_content):
    try:
        # تجربة الموديل المستقر جداً لتجنب NotFound
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt_content)
        return response.text
    except Exception as e:
        return f"⚠️ عذراً يا بطل، السيرفر عليه ضغط حالياً. حاول مرة أخرى خلال ثوانٍ."

# القائمة الجانبية (Sidebar)
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100)
    st.title("التحكم الاحترافي")
    st.info("هذه المنصة مصممة لتكون مساعدك الشامل في التلخيص والعلوم.")

# التبويبات الرئيسية
t1, t2, t3 = st.tabs(["🚀 التلخيص والقوالب", "💬 الشات الذكي", "📖 واحة القرآن"])

# 1. قسم التلخيص
with t1:
    st.markdown('<div class="main-card"><h2>🎯 استخراج الملخصات ومحاكاة القوالب</h2></div>', unsafe_allow_html=True)
    files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
    template = st.file_uploader("🖼️ ارفع قالب التنسيق (اختياري)", type=['jpg', 'png'])
    if files and st.button("✨ ابدأ المعالجة الاحترافية"):
        with st.spinner("جاري قراءة البيانات وتنسيقها..."):
            extracted_text = ""
            for f in files:
                if f.type == "application/pdf":
                    doc = fitz.open(stream=f.read(), filetype="pdf")
                    extracted_text += " ".join([p.get_text() for p in doc])
                else: extracted_text += f" (File: {f.name}) "
            
            p = f"قم بتلخيص هذا المحتوى بأسلوب رزين واحترافي، مع جداول وأسئلة. قلد القالب المرفق في التنسيق: {extracted_text}"
            res = call_ai(p)
            st.markdown(f'<div class="main-card">{res}</div>', unsafe_allow_html=True)

# 2. قسم الشات (واجهة جذابة وسريعة)
with t2:
    st.subheader("💬 دردشة ذكية تفهمك من أول كلمة")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if prompt := st.chat_input("تحدث معي، اسأل عن مسألة أو اطلب خدمة..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            response = call_ai(prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

# 3. قسم القرآن (تفسير موسوعي ملم)
with t3:
    st.markdown('<div class="main-card"><h2>📖 الموسوعة القرآنية الشاملة</h2></div>', unsafe_allow_html=True)
    q_input = st.text_input("أدخل الآية، السورة، أو موضوع للبحث (مثلاً: تفسير سورة الكهف):")
    if q_input:
        with st.spinner("جاري استحضار علوم القرآن..."):
            q_p = f"بصفتك خبير في علوم القرآن، فسر وأكمل ووضح أسباب نزول الآتي بأسلوب رزين ملم بكافة التفاسير: {q_input}"
            res = call_ai(q_p)
            st.markdown(f'<div class="quran-box">{res}</div>', unsafe_allow_html=True)
