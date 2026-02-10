import streamlit as st
import pandas as pd
import os
import google.generativeai as genai
import easyocr
import re

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bio-Tech Smart AI Textbook",
    page_icon="🧬",
    layout="wide"
)

# =========================
# API SETUP (SECURE)
# =========================
# This will look for GEMINI_API_KEY in your Streamlit Secrets or environment
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("🔑 API Key not found! Please add 'GEMINI_API_KEY' to Streamlit Secrets.")
    st.stop() # Stops the app if no key is found

# =========================
# DATA LOADING (FIXED FOR KEYERRORS)
# =========================
@st.cache_data
def load_knowledge_base():
    file_path = "knowledge_base.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip() # Remove hidden spaces
        return df
    
    return pd.DataFrame({
        "Topic": ["Welcome"], 
        "Explanation": ["Please upload a CSV file in the Data Management tab."], 
        "Ten_Points": ["No data found."],
        "Image": [""]
    })

knowledge_df = load_knowledge_base()

def get_col_data(row, possible_names, default="Not Available"):
    for name in possible_names:
        if name in row:
            return str(row[name])
    return default

# =========================
# AI LOGIC
# =========================
def ask_gemini_hinglish(text):
    prompt = f"""
    Explain this Bio-Tech text in 'Hinglish' (Hindi + English mix in Roman script).
    - Keep technical terms (DNA, PCR, CRISPR, etc) in English.
    - Use a friendly, conversational tone (Chat style).
    - Write the Hindi parts in English letters (Roman script).
    Text: {text}
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

# =========================
# SESSION STATE
# =========================
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

# =========================
# MAIN UI
# =========================
st.title("🧬 Bio-Tech Smart AI Textbook")

tabs = st.tabs(["📖 AI Reader", "🧠 10 Points", "🔬 DNA Lab", "🇮🇳 AI Hinglish Helper", "📊 Data Management"])

# Current Row Data
row = knowledge_df.iloc[st.session_state.page_index]

# 1. AI READER
with tabs[0]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅ Previous"):
            st.session_state.page_index = max(0, st.session_state.page_index - 1)
            st.rerun()
    with col2:
        st.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} / {len(knowledge_df)}</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡"):
            st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
            st.rerun()
    
    st.divider()
    
    left, right = st.columns([1, 1])
    with left:
        topic = get_col_data(row, ["Topic", "topic", "Title"])
        expl = get_col_data(row, ["Explanation", "explanation", "Content", "Description"])
        
        st.header(topic)
        st.write(expl)
        
        if st.button("✨ AI Hinglish Explanation"):
            with st.spinner("Gemini is thinking..."):
                st.info(ask_gemini_hinglish(expl))

    with right:
        img_path = get_col_data(row, ["Image", "image", "Picture"], "")
        if img_path and os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.info("No diagram found for this topic.")

# 2. 10 POINTS
with tabs[1]:
    topic = get_col_data(row, ["Topic", "topic"])
    st.header(f"Key Points: {topic}")
    
    points_text = get_col_data(row, ["Ten_Points", "Points", "ten_points", "Key Points"])
    
    if points_text != "Not Available":
        points_list = points_text.split('\n')
        for p in points_list:
            if p.strip():
                st.success(f"🔹 {p.strip()}")
    else:
        st.warning("No revision points column found in CSV.")

# 3. DNA LAB
with tabs[2]:
    st.header("🔬 DNA Analyzer")
    dna = st.text_input("Enter Sequence:", "ATGCATGC").upper()
    if dna:
        gc = (dna.count('G') + dna.count('C')) / len(dna) * 100
        st.metric("GC Content", f"{gc:.2f}%")

# 4. AI HINGLISH HELPER
with tabs[3]:
    st.header("🇮🇳 Custom AI Translator")
    st.write("Paste any English text to get a Hinglish explanation.")
    user_text = st.text_area("Paste English Text here:", height=200)
    if st.button("Translate with AI"):
        if user_text:
            st.write(ask_gemini_hinglish(user_text))
        else:
            st.warning("Please paste text first.")

# 5. DATA MANAGEMENT
with tabs[4]:
    st.header("📊 Database Management")
    st.write("Columns detected:", list(knowledge_df.columns))
    
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        df.to_csv("knowledge_base.csv", index=False)
        st.success("File uploaded! Please refresh the page.")
    
    st.dataframe(knowledge_df)
