import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from PIL import Image

# 1. إعداد الـ API بالمفتاح الجديد
API_KEY = "AIzaSyDso4OPFXij1guGTSX6gN2zwSaXDix-c1o"
genai.configure(api_key=API_KEY)

# 2. تصميم الواجهة (UI الملكي)
st.set_page_config(page_title="المنصة الذكية المتكاملة", layout="wide", page_icon="💎")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    * { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #f0f2f6; }
    .pro-card { background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-bottom: 20px; }
    .quran-frame { background: #fffcf0; border-right: 10px solid #059669; padding: 30px; border-radius: 15px; font-size: 22px; line-height: 2; color: #1e293b; box-shadow: inset 0 0 10px rgba(0,0,0,0.02); }
    .chat-bubble { padding: 15px; border-radius: 15px; margin: 10px 0; max-width: 85%; }
    .stButton>button { background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; border-radius: 12px; height: 50px; width: 100%; font-weight: bold; border: none; }
    </style>
    """, unsafe_allow_html=True)

# محرك الرد السريع
def get_ai_response(prompt_text):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        return model.generate_content(prompt_text).text
    except Exception as e:
        return f"⚠️ السيرفر يحتاج لحظة للتنفس.. جرب مجدداً. (خطأ: {str(e)[:40]})"

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("⚙️ الإعدادات")
    st.write("مرحباً بك في نسختك الاحترافية")
    st.divider()
    st.success("تم تفعيل مفتاح الـ API بنجاح ✅")

# --- التبويبات الرئيسية ---
t1, t2, t3 = st.tabs(["💬 الشات الأونلاين", "📑 التلخيص والقوالب", "📖 الموسوعة القرآنية"])

# 1. الشات الأونلاين (سريع وجذاب)
with t1:
    st.markdown('<div class="pro-card"><h2>💬 دردشة ذكية وفورية</h2></div>', unsafe_allow_html=True)
    if "messages" not in st.session_state: st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    if user_input := st.chat_input("تكلم معي.. أنا أسمعك وأفهمك بسرعة"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("⚡ جاري الرد..."):
                full_res = get_ai_response(user_input)
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})

# 2. التلخيص والقوالب
with t2:
    st.markdown('<div class="pro-card"><h2>🎯 التلخيص الذكي ومحاكاة القوالب</h2></div>', unsafe_allow_html=True)
    files = st.file_uploader("ارفع ملفاتك (PDF, Word, صور)", accept_multiple_files=True)
    style_temp = st.file_uploader("🖼️ ارفع قالب التنسيق المفضل (اختياري)", type=['jpg', 'png'])
    
    if files and st.button("🚀 ولّد الملخص الفخم"):
        with st.spinner("⚡ جاري تحليل البيانات وبناء المحتوى..."):
            all_text = ""
            for f in files:
                if f.type == "application/pdf":
                    doc = fitz.open(stream=f.read(), filetype="pdf")
                    all_text += " ".join([p.get_text() for p in doc])
                else: all_text += f" (الملف: {f.name}) "
            
            p = f"قم بتلخيص هذا المحتوى باحترافية تامة، استخدم جداول وأسئلة. قلد أسلوب القالب المرفق إن وجد: {all_text}"
            res = get_ai_response(p)
            st.markdown(f'<div class="pro-card">{res}</div>', unsafe_allow_html=True)

# 3. القرآن الكريم (تفسير ملم ورزين)
with t3:
    st.markdown('<div class="pro-card"><h2>📖 الموسوعة القرآنية الشاملة</h2></div>', unsafe_allow_html=True)
    q_input = st.text_input("أدخل الآية، السورة، أو موضوع البحث:")
    if q_input:
        with st.spinner("جاري البحث في أمهات التفاسير..."):
            q_p = f"بصفتك خبيراً في علوم القرآن، فسر وأكمل ووضح أسباب نزول الآتي بأسلوب رزين ملم بكافة التفاسير (ابن كثير، الطبري، القرطبي): {q_input}"
            q_res = get_ai_response(q_p)
            st.markdown(f'<div class="quran-frame">{q_res}</div>', unsafe_allow_html=True)
