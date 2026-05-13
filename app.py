import streamlit as st
import os
from PIL import Image
from groq import Groq
import base64
import io
import fitz
import subprocess

# connect to AI
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ============================================
# PAGE CONFIG AND CUSTOM CSS
# ============================================
st.set_page_config(page_title="RecallIt", page_icon="🔍", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #F5F5F5; }
    
    [data-testid="stSidebar"] {
        background-color: #424242 !important;
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    .hero {
        background: linear-gradient(135deg, #2D2D2D, #555555);
        padding: 50px 30px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
    }
    
    .hero-title {
        color: white;
        font-size: 42px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .hero-subtitle {
        color: #C0C0C0;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .feature-icon { font-size: 35px; margin-bottom: 10px; }
    .feature-title { color: #2D2D2D; font-size: 16px; font-weight: bold; margin-bottom: 5px; }
    .feature-desc { color: #9E9E9E; font-size: 13px; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stButton > button {
        background-color: #2D2D2D;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 25px;
        font-size: 15px;
        width: 100%;
    }
    
    .stButton > button:hover {
        background-color: #555555;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown("""
<div style="background-color:#2D2D2D; padding:15px 30px; border-radius:10px; margin-bottom:30px;">
    <p style="font-size:42px; color:white; font-weight:900; letter-spacing:3px; margin:0;">
        🔍 <span style="color:#C0C0C0;">Recall</span><span style="color:white;">It</span>
    </p>
    <p style="color:#9E9E9E; font-size:14px; margin:0;">AI powered search for your personal files</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# HERO SECTION
# ============================================
st.markdown("""
<div class="hero">
    <p class="hero-title">Find Anything. Instantly.</p>
    <p class="hero-subtitle">Search your photos, screenshots and PDFs using plain English</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# FEATURE CARDS
# ============================================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📸</div>
        <p class="feature-title">Photo Search</p>
        <p class="feature-desc">AI understands colors, people, emotions and objects in your photos</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📱</div>
        <p class="feature-title">Screenshot Search</p>
        <p class="feature-desc">Reads all text inside your screenshots instantly</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <p class="feature-title">PDF Search</p>
        <p class="feature-desc">Searches inside your PDF documents and finds exact content</p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ============================================
# SIDEBAR
# ============================================
st.markdown("## 📁 Your Folders")
col_f1, col_f2, col_f3 = st.columns([2, 2, 1])

with col_f1:
    photos_folder = st.text_input(
        "Photos & Screenshots Folder",
        value=r"C:\Users\91844\OneDrive\Desktop\test_photos"
    )

with col_f2:
    pdf_folder = st.text_input(
        "PDF Folder",
        value=r"C:\Users\91844\OneDrive\Desktop\PDF"
    )

with col_f3:
    st.markdown("<br>", unsafe_allow_html=True)
    scan_button = st.button("🚀 Scan Everything!", type="primary")

# ============================================
# SCANNING LOGIC
# ============================================
if scan_button:
    all_data = {}

    with st.spinner("📸 Scanning photos and screenshots..."):
        if os.path.exists(photos_folder):
            images = os.listdir(photos_folder)
            for image_name in images:
                image_path = os.path.join(photos_folder, image_name)
                try:
                    img = Image.open(image_path)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG")
                    image_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

                    response = client.chat.completions.create(
                        model="meta-llama/llama-4-scout-17b-16e-instruct",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/jpeg;base64,{image_data}"
                                        }
                                    },
                                    {
                                        "type": "text",
                                        "text": "Describe this image in detail. Include: 1) Colors, people, objects, food, everything you see. 2) Detect emotions of people — happy, sad, excited, calm, angry etc. 3) Give happiness score 0-100. 4) Detect mood/vibe. 5) If any date or year visible mention it!"
                                    }
                                ]
                            }
                        ]
                    )

                    all_data[image_name] = {
                        "type": "photo",
                        "description": response.choices[0].message.content,
                        "path": image_path
                    }
                    st.sidebar.success(f"✅ {image_name}")

                except Exception as e:
                    st.sidebar.warning(f"⚠️ Skipped {image_name}")

    with st.spinner("📄 Scanning PDF files..."):
        if os.path.exists(pdf_folder):
            pdf_files = os.listdir(pdf_folder)
            for pdf_name in pdf_files:
                if not pdf_name.endswith(".pdf"):
                    continue
                pdf_path = os.path.join(pdf_folder, pdf_name)
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()

                all_data[pdf_name] = {
                    "type": "pdf",
                    "description": text[:1000],
                    "path": pdf_path
                }
                st.sidebar.success(f"✅ {pdf_name}")

    st.session_state.all_data = all_data
    st.session_state.search_done = False
    st.success(f"🎉 Scanned {len(all_data)} files! Now search below!")

# ============================================
# SEARCH BAR
# ============================================
st.markdown("## 🔎 Search Anything")

col_search, col_btn = st.columns([4, 1])

with col_search:
    search = st.text_input(
    "Search",
    placeholder="Try: happiest photos, burger, mca notes, swiggy order, red dress...",
    label_visibility="collapsed"
)
    

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("Search!", type="primary")

if search_button and search:
    if "all_data" not in st.session_state:
        st.warning("⚠️ Please scan your folders first!")
    else:
        all_data = st.session_state.all_data

        with st.spinner("🤖 AI is searching..."):
            all_descriptions = "\n".join([
                f"{name} ({data['type']}): {data['description'][:300]}"
                for name, data in all_data.items()
            ])

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content": f"Here are all files:\n{all_descriptions}\n\nUser searching for: '{search}'\n\nFind files that STRONGLY match only. Give each file a match score out of 100. Only show files with score above 60. If nothing matches say 'No strong matches found'. Format: filename - score% - reason"
                    }
                ]
            )

        st.session_state.result = response.choices[0].message.content
        st.session_state.search_done = True

# ============================================
# SHOW RESULTS — stays even after button click
# ============================================
if "search_done" in st.session_state and st.session_state.search_done:
    result = st.session_state.result
    all_data = st.session_state.all_data

    st.markdown("## ✅ Results")
    cols = st.columns(3)
    col_index = 0

    for name, data in all_data.items():
        if name.lower() in result.lower():
            with cols[col_index % 3]:
                if data["type"] == "photo":
                    img = Image.open(data["path"])
                    st.image(img, caption=name, use_column_width=True)
                    if st.button(f"📂 Open Photo", key=f"photo_{col_index}"):
                        os.system(f'start "" "{data["path"]}"')
                else:
                    st.info(f"📄 {name}")
                    st.write(data["description"][:200] + "...")
                    if st.button(f"📂 Open PDF", key=f"pdf_{col_index}"):
                        os.system(f'start "" "{data["path"]}"')
            col_index += 1

    if col_index == 0:
        st.warning("No strong matches found! Try different words! 😄")

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
<p style="text-align:center; color:#9E9E9E; font-size:13px;">
    RecallIt — Built with ❤️ using Python, Groq AI and Streamlit
</p>
""", unsafe_allow_html=True)
