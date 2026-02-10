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
# API SETUP (GEMINI)
# =========================
# Get your key from https://aistudio.google.com/
GEMINI_API_KEY = "AIzaSyCmYzYISM5CpuAsiJ4eEZ3pBBL9XmYXGB8" 

if GEMINI_API_KEY != "AIzaSyCmYzYISM5CpuAsiJ4eEZ3pBBL9XmYXGB8":
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("⚠️ Please insert your Gemini API Key in the code.")

# =========================
# OCR & DATA LOADING
# =========================
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

@st.cache_data
def load_knowledge_base():
    # Try to load existing database
    for file in ["knowledge_base.csv", "knowledge.csv"]:
        if os.path.exists(file):
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()
            return df
    # Fallback Data
    return pd.DataFrame({
        "Topic": ["DNA Replication", "PCR Technique"], 
        "Explanation": ["DNA replication is the process by which a double-stranded DNA molecule is copied to produce two identical DNA molecules.", "Polymerase Chain Reaction is a method used to make millions of copies of a specific DNA sample."], 
        "Ten_Points": ["Occurs in S-phase\nSemi-conservative\nRequires DNA Polymerase", "Denaturation at 94C\nAnnealing at 55C\nExtension at 72C"],
        "Image": ["", ""]
    })

knowledge_df = load_knowledge_base()

# =========================
# AI LOGIC
# =========================
def ask_gemini_hinglish(text):
    prompt = f"""
    You are an expert Bio-Technology Teacher. 
    Explain the following technical text in 'Hinglish' (Natural mix of Hindi and English) for an Indian college student.
    
    CRITICAL RULES:
    1. Keep all technical terms (DNA, PCR, Enzymes, Primers, etc.) in English.
    2. Use Roman script (English letters) for Hindi words (e.g., write 'kaise hota hai' instead of 'कैसे होता है').
    3. Make it sound like a friendly 'Chat' style explanation.
    4. Provide 3 short 'Exam Tips' in Hinglish at the end.

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
st.markdown("---")

tabs = st.tabs(["📖 AI Reader", "🧠 10 Points", "🔬 DNA Lab", "🇮🇳 AI Hinglish Helper", "📊 Data Management"])

# 1. AI READER
with tabs[0]:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅ Previous"):
            st.session_state.page_index = max(0, st.session_state.page_index - 1)
    with col2:
        st.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} / {len(knowledge_df)}</h3>", unsafe_allow_html=True)
    with col3:
        if st.button("Next ➡"):
            st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
    
    row = knowledge_df.iloc[st.session_state.page_index]
    
    left, right = st.columns([1, 1])
    with left:
        st.header(row['Topic'])
        st.write(row['Explanation'])
        if st.button("✨ Explain in Hinglish"):
            with st.spinner("Gemini is drafting your notes..."):
                explanation = ask_gemini_hinglish(row['Explanation'])
                st.info(explanation)

    with right:
        img_path = str(row.get('Image', ""))
        if img_path and os.path.exists(img_path):
            st.image(img_path, caption=row['Topic'], use_container_width=True)
        else:
            st.warning("No diagram found for this topic.")

# 2. 10 POINTS
with tabs[1]:
    st.header(f"Revison Points: {row['Topic']}")
    points = str(row['Ten_Points']).split('\n')
    for p in points:
        if p.strip():
            st.success(f"🔹 {p}")

# 3. DNA LAB
with tabs[2]:
    st.header("🔬 Sequence Tools")
    dna_input = st.text_area("Paste DNA Sequence:", "ATGCATGCATGC").upper()
    if st.button("Analyze Sequence"):
        gc_content = (dna_input.count('G') + dna_input.count('C')) / len(dna_input) * 100
        st.metric("GC Content", f"{gc_content:.2f}%")
        st.write(f"**Complimentary Strand:** {dna_input.replace('A','t').replace('T','a').replace('G','c').replace('C','g').upper()}")

# 4. AI HINGLISH HELPER (CUSTOM INPUT)
with tabs[3]:
    st.header("🇮🇳 Custom AI Hinglish Translator")
    st.write("Paste text from any source (PDF/Web) to get an instant Hinglish breakdown.")
    
    user_text = st.text_area("Enter English Text:", height=200, placeholder="Example: CRISPR-Cas9 is a unique technology that enables geneticists to edit parts of the genome...")
    
    if st.button("Convert with Gemini"):
        if user_text:
            with st.spinner("AI is processing..."):
                result = ask_gemini_hinglish(user_text)
                st.markdown("### 📝 AI Notes")
                st.write(result)
        else:
            st.warning("Please enter text.")

# 5. DATA MANAGEMENT
with tabs[4]:
    st.header("📊 Database Settings")
    st.dataframe(knowledge_df)
    
    uploaded_file = st.file_uploader("Update Database (CSV)", type="csv")
    if uploaded_file:
        new_df = pd.read_csv(uploaded_file)
        if st.button("Confirm & Save"):
            new_df.to_csv("knowledge_base.csv", index=False)
            st.success("Database Updated!")
