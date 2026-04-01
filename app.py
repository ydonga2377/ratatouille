import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import urllib.parse
import base64
from dotenv import load_dotenv

# Load the API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ratatouille", page_icon="🍳", layout="wide")

# --- HELPER: CONVERT LOCAL IMAGES TO BASE64 ---
def get_base64(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
    except:
        return None
    return None

rat_base64 = get_base64("rat.gif")
walk_base64 = get_base64("walk.gif")

# --- UI STYLING ---
st.markdown(f"""
<style>
    /* 1. Pastel Background */
    .stApp {{
        background-color: #fbf9f6; 
    }}
    
    /* 2. Floating Background Emojis */
    @keyframes float {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(10deg); }}
        100% {{ transform: translateY(0px) rotate(0deg); }}
    }}

    /* 3. Walking Animation for Footer */
    @keyframes walkAcross {{
        0% {{ left: -10%; }} 
        100% {{ left: 110%; }}
    }}

    .bg-emoji {{
        position: fixed; font-size: 4rem; opacity: 0.07; z-index: 0;
        pointer-events: none; animation: float 6s ease-in-out infinite;
    }}
    .e1 {{ top: 10%; left: 10%; animation-delay: 0s; }}
    .e2 {{ top: 70%; left: 5%; animation-delay: 1s; }}
    .e3 {{ top: 20%; right: 10%; animation-delay: 2s; }}
    .e4 {{ top: 75%; right: 8%; animation-delay: 3s; }}
    .e5 {{ top: 40%; left: 50%; animation-delay: 1.5s; }}

    /* 4. Strict 2rem Border Radius */
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stImage"] img,
    .stButton > button,
    div[data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"],
    div[data-testid="stExpander"],
    div[data-testid="stExpander"] details summary {{
        border-radius: 2rem !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid #e8e1d5 !important;
        background-color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        min-height: 400px; padding: 1.5rem !important;
        z-index: 1; position: relative;
    }}
    
    /* 5. Fixed Footer Logic */
    .block-container {{
        padding-bottom: 120px !important; 
    }}
    
    .fixed-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #fbf9f6; text-align: center;
        padding: 15px 0; color: #a39e97; font-size: 14px;
        z-index: 999999; border-top: 1px solid #e8e1d5;
    }}

    /* YOUR ADDED CODE: The Walking GIF pseudo-element */
    .fixed-footer:before {{
        height: 7em;
        width: 7em;
        position: absolute;
        content: "";
        background: url(data:image/gif;base64,{walk_base64 if walk_base64 else ""});
        top: -7em;
        left: -10%;
        background-size: cover;
        background-repeat: no-repeat;
        animation: walkAcross 25s linear infinite;
    }}

    /* Text colors */
    h1, h2, h3, p, span, label {{ color: #4A4641 !important; }}
    header {{ visibility: hidden; }}
</style>

<div class="bg-emoji e1">🥑</div>
<div class="bg-emoji e2">🥕</div>
<div class="bg-emoji e3">🥐</div>
<div class="bg-emoji e4">🍅</div>
<div class="bg-emoji e5">🍳</div>
""", unsafe_allow_html=True)


# --- CENTERED APP INFO SECTION ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px; z-index: 2; position: relative;">
    <h1 style="font-size: 3.5rem; margin-bottom: 0;">🍳 Ratatouille</h1>
    <h3 style="font-weight: 400; color: #87827b !important; margin-top: 5px;">Your AI-Powered Sous-Chef</h3>
</div>
""", unsafe_allow_html=True)


# --- MAIN LAYOUT ---
col1, col2 = st.columns([3, 6], gap="medium") 

with col1:
    with st.container(border=True):
        st.markdown("### 🛒 Pantry")
        dietary_preference = st.selectbox(
            "Dietary preferences?",
            ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Dairy-Free", "High Protein"]
        )
        uploaded_file = st.file_uploader("Upload a photo...", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(Image.open(uploaded_file), use_container_width=True)
        generate_button = st.button("What's for dinner? ✨", type="primary", use_container_width=True)

with col2:
    with st.container(border=True):
        # --- THE FLOATING RAT GIF (STAYS IN COL2) ---
        if rat_base64:
            st.markdown(f'''
                <div style="
                    position: absolute;
                    top: -16rem;
                    right: 4rem;
                    height: 15rem;
                    z-index: 10;
                    pointer-events: none;
                    background: url(data:image/gif;base64,{rat_base64});
                    background-repeat: no-repeat;
                    width: 13rem;
                    background-position: center;
                    background-size: cover;
                "></div>
            ''', unsafe_allow_html=True)
        else:
            st.warning("Missing rat.gif")
            
        st.markdown("### 👨‍🍳 The Menu")
        
        if generate_button and uploaded_file:
            with st.spinner("Whisking up some ideas..."):
                # Insert your specific AI response logic here
                st.write("Recipes would appear here!")
        else:
            st.info("👈 Upload your fridge photo to start!")

# --- THE FIXED FOOTER ---
st.markdown("""
<div class="fixed-footer">
    <p>© 2026 Ratatouille v1.0 | Cooked with ❤️ by <a href="#" style="color: #A3B18A; text-decoration: none;">Yutika Donga</a></p>
</div>
""", unsafe_allow_html=True)
