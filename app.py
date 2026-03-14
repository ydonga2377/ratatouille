import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import json
import urllib.parse
from dotenv import load_dotenv

# Load the API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# --- PAGE CONFIG ---
st.set_page_config(page_title="Ratatouille", page_icon="🍳", layout="wide")

# --- THEME-FRIENDLY CSS ---
st.markdown("""
<style>
    /* Force the uploaded image to a fixed, clean size without stretching */
    [data-testid="stImage"] img {
        object-fit: cover;
        height: 300px !important;
        width: 100% !important;
        border-radius: 8px;
    }
    /* Make the recipe card images look uniform */
    .recipe-img {
        border-radius: 8px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("🍳 Ratatouille: Your AI Sous-Chef")

col1, col2 = st.columns([3, 6], gap="small") 

# --- LEFT COLUMN: INPUTS & IMAGE ---
with col1:
    with st.container(border=True):
        st.markdown("### 🛒 Pantry")
        
        dietary_preference = st.selectbox(
            "Dietary preferences?",
            ["None", "Vegetarian", "Vegan", "Gluten-Free", "Keto", "Dairy-Free", "High Protein"]
        )

        uploaded_file = st.file_uploader("Snap a pic of your fridge...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Ingredients", use_container_width=True)

        generate_button = st.button("What's for dinner? 🍽️", type="primary", use_container_width=True)

# --- RIGHT COLUMN: OUTPUTS ---
with col2:
    with st.container(border=True):
        st.markdown("### 👨‍🍳 The Menu")
        
        if generate_button and uploaded_file is not None:
            with st.spinner("Analyzing ingredients and brainstorming recipes..."):
                
                diet_instruction = ""
                if dietary_preference != "None":
                    diet_instruction = f"IMPORTANT: All recipes MUST be strictly {dietary_preference}."

                # --- NEW PROMPT: Forcing JSON Output ---
                prompt = f"""
                Look carefully at this photo. 
                1. Identify the main ingredients.
                2. Suggest exactly 3 creative recipes using these ingredients. 
                {diet_instruction}
                3. You MUST respond ONLY in valid JSON format using this exact structure:
                {{
                    "ingredients": ["emoji Ingredient 1", "emoji Ingredient 2"],
                    "recipes": [
                        {{
                            "title": "Catchy Title",
                            "description": "Short appetizing description",
                            "steps": ["Step 1", "Step 2"]
                        }}
                    ]
                }}
                Do not include any markdown formatting like ```json. Just return the raw JSON object.
                """
                
                try:
                    response = model.generate_content([prompt, image])
                    
                    # Clean up the response in case the AI added markdown blocks
                    raw_text = response.text.strip()
                    if raw_text.startswith("```json"):
                        raw_text = raw_text[7:]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                        
                    # Parse the JSON string into a Python dictionary
                    recipe_data = json.loads(raw_text)
                    
                    # --- 1. DISPLAY INGREDIENTS ---
                    st.markdown("#### 🥦 Detected Ingredients")
                    # Display ingredients in a neat comma-separated list
                    st.write(", ".join(recipe_data["ingredients"]))
                    st.divider()
                    
                    # --- 2. DISPLAY RECIPE CARDS IN COLUMNS ---
                    st.markdown("#### ✨ Suggested Recipes")
                    
                    # Create 3 columns dynamically based on the recipes
                    recipe_cols = st.columns(len(recipe_data["recipes"]))
                    
                    for idx, recipe in enumerate(recipe_data["recipes"]):
                        with recipe_cols[idx]:
                            # 1. Clean the title to prevent URL errors (swap & for and)
                            safe_title = recipe['title'].replace("&", "and").replace("/", " ")
                            
                            # 2. Generate the dynamic image URL
                            search_query = urllib.parse.quote(f"delicious {safe_title} food photography appetizing")
                            
                             
                            st.markdown(f"**{recipe['title']}**")
                            
                            # The Expander creates the "Click box to open recipe" effect
                            with st.expander("Show Recipe"):
                                st.write(f"*{recipe['description']}*")
                                st.markdown("---")
                                for step_num, step in enumerate(recipe['steps'], 1):
                                    st.write(f"**{step_num}.** {step}")
                                    
                except json.JSONDecodeError:
                    st.error("Oops! The AI got a little too creative and didn't format the recipes correctly. Try clicking the button again!")
                except Exception as e:
                    st.error(f"Oops! Something went wrong: {e}")
                    
        elif not uploaded_file:
            st.info("👈 Upload your fridge photo on the left and hit the button to see your menu!")
        else:
            st.info("👈 Ingredients loaded! Hit the button to cook up some ideas.")