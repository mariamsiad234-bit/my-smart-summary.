import streamlit as st
import google.generativeai as genai
import fitz
from docx import Document
from io import BytesIO
from PIL import Image

# 1. الإعدادات الأساسية
API_KEY = "AIzaSyDjbRuvdwVpJimDS6hpqH7hzoszP7Ud-rI"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. تصميم الواجهة (Advanced Professional UI)
st.set_page_config(page_title="المنصة الذكية المتكاملة", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; }
    .stApp { background: #f0f2f6; }
    .main-card { background: white; padding: 2rem; border-radius: 1.5rem; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border: 1px solid #e1e4e8; }
    .chat-msg { padding: 1rem; border-radius: 1rem; margin-bottom: 0.5rem; max-width: 80%; }
    .user-msg { background: #007bff; color: white; align-self: flex-start; }
    .ai-msg { background: #e9ecef; color: #333; align-self: flex-end; }
    .quran-section { background: #fffcf0; border-right: 8px solid #28a745; padding: 1.5rem; border-radius: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 3. وظائف المعالجة الذكية (حل مشكلة الـ Error)
def process_upload(uploaded_file):
    if uploaded_file.type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        return " ".join([page.get_text() for page in doc])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(uploaded_file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif uploaded_file.type.startswith('image/'):
        return Image.open(uploaded_file)
    return uploaded_file.read()

# --- القائمة الجانبية للتنسيق ---
with st.sidebar:
    st.title("🎨 لوحة التحكم")
    lang = st.radio("اللغة:", ["العربية", "English"])
    output_format = st.selectbox("تصدير الملخص كـ:", ["PDF احترافي", "Word منسق", "صورة جذابة"])
    st.info("نصيحة: لسرعة خيالية، ارفع ملفاتك وابدأ الشات فوراً!")

# --- التبويبات الرئيسية ---
tab1, tab2, tab3 = st.tabs(["📑 التلخيص الذكي", "💬 الشات المطور", "📖 واحة القرآن"])

# --- Tab 1: التلخيص ---
with tab1:
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.subheader("🎯 صانع الملخصات بجودة 4K")
    files = st.file_uploader("ارفع ملفاتك هنا", accept_multiple_files=True)
    template = st.file_uploader("🖼️ ارفع قالب ليتم تقليده", type=['jpg', 'png'])
    
    if files and st.button("🚀 ولّد الملخص الآن"):
        with st.spinner("⚡ جاري تحليل البيانات وبناء التنسيق..."):
            all_content = []
            for f in files:
                content = process_upload(f)
                all_content.append(content if isinstance(content, Image.Image) else f"المحتوى: {content}")
            
            prompt = f"لخص هذا المحتوى بـ {lang} باحترافية، شامل الجداول والأسئلة والكاريكاتير. قلد القالب المرفق إن وجد."
            if template: all_content.append(Image.open(template))
            
            res = model.generate_content([prompt] + all_content)
            st.markdown(f'<div class="main-card">{res.text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: الشات الاحترافي ---
with tab2:
    st.subheader("💬 دردشة ذكية وسريعة الفهم")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    chat_container = st.container()
    with chat_container:
        for m in st.session_state.messages:
            role_class = "user-msg" if m["role"] == "user" else "ai-msg"
            st.markdown(f'<div class="chat-msg {role_class}">{m["content"]}</div>', unsafe_allow_html=True)

    if p := st.chat_input("اسألني أي شيء أو اطلب تلخيصاً..."):
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        
        with st.chat_message("assistant"):
            full_prompt = f"أجب بذكاء وسرعة باللغة المختارة: {p}"
            r = model.generate_content(full_prompt)
            st.markdown(r.text)
            st.session_state.messages.append({"role": "assistant", "content": r.text})

# --- Tab 3: علوم القرآن ---
with tab3:
    st.markdown('<div class="main-card quran-section">', unsafe_allow_html=True)
    st.subheader("📖 الموسوعة القرآنية الشاملة")
    q_input = st.text_input("أدخل الآية، الجزء، أو موضوع البحث:")
    
    if q_input:
        with st.spinner("جاري استحضار التفسير الملم..."):
            q_prompt = f"""
            بصفتك خبير في علوم القرآن، فسر وأكمل ووضح أسباب نزول: {q_input}.
            يجب أن يشمل الرد:
            1. نص الآية الكريمة بالتشكيل.
            2. تفسير ملم يجمع بين (ابن كثير، الجلالين، والقرطبي).
            3. الدروس المستفادة بأسلوب رزين وسهل.
            """
            q_res = model.generate_content(q_prompt)
            st.markdown(f"<div>{q_res.text}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
