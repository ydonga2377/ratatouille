import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import urllib.parse
import base64
from dotenv import load_dotenv

# --- INITIALIZATION ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
# Using the standard flash model for speed and reliability
model = genai.GenerativeModel('gemini-1.5-flash-latest')

st.set_page_config(page_title="Ratatouille", page_icon="🍳", layout="wide")

# --- HELPER: BASE64 FOR LOCAL ASSETS ---
def get_base64(file_path):
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return None

rat_base64 = get_base64("rat.gif")
walk_base64 = get_base64("walk.gif")

# --- CSS & ANIMATIONS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #fbf9f6; }}
    
    @keyframes float {{
        0% {{ transform: translateY(0px) rotate(0deg); }}
        50% {{ transform: translateY(-20px) rotate(10deg); }}
        100% {{ transform: translateY(0px) rotate(0deg); }}
    }}

    @keyframes walkAcross {{
        0% {{ left: -10%; }} 
        100% {{ left: 110%; }}
    }}

    .bg-emoji {{
        position: fixed; font-size: 4rem; opacity: 0.07; z-index: 0;
        pointer-events: none; animation: float 6s ease-in-out infinite;
    }}
    .e1 {{ top: 10%; left: 10%; }} .e2 {{ top: 70%; left: 5%; }}
    .e3 {{ top: 20%; right: 10%; }} .e4 {{ top: 75%; right: 8%; }}

    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stImage"] img,
    .stButton > button, div[data-baseweb="select"] > div,
    [data-testid="stFileUploaderDropzone"], div[data-testid="stExpander"] {{
        border-radius: 2rem !important;
    }}

    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 2px solid #e8e1d5 !important;
        background-color: #ffffff;
        box-shadow: 0 10px 30px rgba(0,0,0,0.03) !important;
        padding: 1.5rem !important;
        z-index: 1; position: relative;
    }}
    
    .block-container {{ padding-bottom: 150px !important; }}
    
    .fixed-footer {{
        position: fixed; bottom: 0; left: 0; width: 100%;
        background-color: #fbf9f6; text-align: center;
        padding: 15px 0; color: #a39e97; font-size: 14px;
        z-index: 999999; border-top: 1px solid #e8e1d5;
    }}

    .fixed-footer:before {{
        height: 7em; width: 7em; position: absolute; content: "";
        background: url(data:image/gif;base64,{walk_base64 if walk_base64 else ""});
        top: -7em; left: -10%; background-size: contain;
        background-repeat: no-repeat; animation: walkAcross 15s linear infinite;
    }}

    h1, h2, h3, p, span, label {{ color: #4A4641 !important; }}
    header {{ visibility: hidden; }}
</style>
<div class="bg-emoji e1">🥑</div><div class="bg-emoji e2">🥕</div>
<div class="bg-emoji e3">🥐</div><div class="bg-emoji e4">🍅</div>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown('<div style="text-align: center; margin-bottom: 40px;"><h1>🍳 Ratatouille</h1><h3>Your AI Sous-Chef</h3></div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 6], gap="medium")

with col1:
    with st.container(border=True):
        st.markdown("### 🛒 Pantry")
        diet = st.selectbox("Dietary preferences?", ["None", "Vegetarian", "Vegan", "Keto", "Gluten-Free"])
        uploaded_file = st.file_uploader("Upload ingredients...", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            st.image(uploaded_file)
        generate_button = st.button("What's for dinner? ✨", type="primary", use_container_width=True)

with col2:
    with st.container(border=True):
        # Floating Rat GIF
        if rat_base64:
            st.markdown(f'<div style="position: absolute; top: -16rem; right: 4rem; height: 15rem; width: 13rem; background: url(data:image/gif;base64,{rat_base64}); background-size: cover; z-index: 10; pointer-events: none;"></div>', unsafe_allow_html=True)
            
        st.markdown("### 👨‍🍳 The Menu")
        
        if generate_button and uploaded_file is not None:
            image = Image.open(uploaded_file)
            with st.spinner("Analyzing ingredients..."):
                prompt = f"""Identify ingredients in this image and suggest 3 {diet} recipes. 
                Return ONLY a JSON object: {{"ingredients": [], "recipes": [{{"title": "", "description": "", "steps": []}}]}}"""
                
                try:
                    response = model.generate_content([prompt, image])
                    # Cleaning the markdown from the response
                    clean_json = response.text.replace("```json", "").replace("```", "").strip()
                    recipe_data = json.loads(clean_json)

                    st.write(f"**Detected:** {', '.join(recipe_data['ingredients'])}")
                    st.divider()

                    for recipe in recipe_data['recipes']:
                        with st.expander(f"✨ {recipe['title']}"):
                            st.write(recipe['description'])
                            for i, step in enumerate(recipe['steps'], 1):
                                st.write(f"{i}. {step}")
                except Exception as e:
                    st.error(f"Error: {e}")
        else:
            st.info("👈 Upload your photo and click the button!")

# --- FOOTER ---
st.markdown('<div class="fixed-footer"><p>© 2026 Ratatouille v1.0 | by <a href="#">Yutika Donga</a></p></div>', unsafe_allow_html=True)
