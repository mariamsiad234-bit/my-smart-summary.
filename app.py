import streamlit as st
import google.generativeai as genai
import os
import fitz  # PyMuPDF
from docx import Document
from xhtml2pdf import pisa
from io import BytesIO

# --- 1. إعدادات الصفحة والواجهة (الألوان المريحة) ---
st.set_page_config(page_title="أداة التلخيص الفرفوشة", page_icon="📂", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #FAFAFA; }
    .stButton>button { 
        background-color: #4A90E2; 
        color: white; 
        border-radius: 12px; 
        width: 100%;
        height: 3em;
        font-weight: bold;
    }
    h1 { color: #2C3E50; text-align: center; }
    </style>
    """, unsafe_allow_type=True)

# --- 2. إعداد Gemini (حط مفتاحك هنا) ---
# نصيحة: للأمان، يفضل وضع المفتاح في Streamlit Secrets لاحقاً
API_KEY = "AIzaSyAlGMaza9pgQ_0m2D61vKGOC239VSS4VOI" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. وظائف المعالجة ---

def extract_text_from_file(uploaded_file):
    """سحب النص من الملفات المرفوعة"""
    file_details = uploaded_file.name
    ext = os.path.splitext(file_details)[1].lower()
    text = ""
    
    if ext == ".pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    elif ext == ".docx":
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = str(uploaded_file.read(), "utf-8")
    return text

def generate_pdf(html_content):
    """تحويل الـ HTML لملف PDF في الذاكرة"""
    result = BytesIO()
    pisa.CreatePDF(BytesIO(html_content.encode("utf-8")), dest=result, encoding='utf-8')
    return result.getvalue()

# --- 4. واجهة المستخدم ---

st.title("📂 أداة التلخيص الاحترافية")
st.subheader("لخص ملفاتك بذكاء وشياكة.. وفرفش في الآخر 😉")

uploaded_file = st.file_uploader("ارمي ملفك هنا (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
language = st.radio("عايز الملخص بأي لغة؟", ["العربية", "English"], horizontal=True)

if uploaded_file is not None:
    if st.button("ابدأ العظمة ✨"):
        with st.spinner("جاري قراءة الملف وتجهيز الخلاصة..."):
            try:
                # استخراج النص
                raw_text = extract_text_from_file(uploaded_file)
                
                # طلب التلخيص من Gemini
                prompt = f"""
                أنت مساعد محترف. قم بتلخيص النص التالي بأسلوب احترافي ومبسط جداً:
                1. استخدم لغة {language}.
                2. لخص الأفكار الرئيسية في نقاط واضحة.
                3. إذا وجد بيانات تصلح لجدول، ضعها في جدول HTML ملون بألوان Pastel هادئة.
                4. في النهاية، اكتب جملة مضحكة جداً (Meme description) تناسب المحتوى لفك الملل.
                
                تنسيق المخرجات: HTML فقط (بدون علامات ```html).
                """
                
                response = model.generate_content([prompt, raw_text[:10000]])
                ai_content = response.text
                
                # تصميم قالب الـ PDF النهائي
                full_html = f"""
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Helvetica', sans-serif; direction: {"rtl" if language=="العربية" else "ltr"}; background-color: #FAFAFA; padding: 20px; }}
                        h1 {{ color: #4A90E2; text-align: center; }}
                        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; background: white; }}
                        th {{ background-color: #A3DFF7; padding: 10px; border: 1px solid #D6EAF8; }}
                        td {{ padding: 8px; border: 1px solid #EAECEF; text-align: center; }}
                        .meme-section {{ margin-top: 30px; border: 2px dashed #A3DFF7; padding: 15px; text-align: center; background: #EBF5FB; }}
                    </style>
                </head>
                <body>
                    <h1>ملخص الملف: {uploaded_file.name}</h1>
                    <div>{ai_content}</div>
                    <div class="meme-section">
                        <p>💡 فقرة الفرفشة: المحتوى اللي فوق ده بيقولك "فكها شوية المذاكرة مش كل حاجة" 😂</p>
                        <img src="[https://i.imgflip.com/4/39t1o.jpg](https://i.imgflip.com/4/39t1o.jpg)" width="250">
                    </div>
                </body>
                </html>
                """
                
                # عرض النتيجة في الموقع
                st.markdown("---")
                st.markdown(ai_content, unsafe_allow_type=True)
                
                # زرار التحميل
                pdf_bytes = generate_pdf(full_html)
                st.download_button(
                    label="📥 تحميل الملخص PDF الاحترافي",
                    data=pdf_bytes,
                    file_name=f"Summary_{uploaded_file.name}.pdf",
                    mime="application/pdf"
                )
                st.balloons() # احتفال بسيط بالنجاح
                
            except Exception as e:
                st.error(f"حصلت مشكلة يا صاحبي: {e}")

st.markdown("---")
st.caption("صنع بكل حب عشان يريح عينك ويفرفش قلبك.")
