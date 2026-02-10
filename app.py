import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator
import easyocr
import re
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bio-Tech Smart Textbook",
    layout="wide"
)

# =========================
# OCR INITIALIZATION
# =========================
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

@st.cache_data
def get_text_from_image(img_path):
    if img_path and os.path.exists(img_path):
        try:
            text = reader.readtext(img_path, detail=0)
            return " ".join(text).lower()
        except Exception:
            return ""
    return ""

# =========================
# LOAD KNOWLEDGE BASE
# =========================
@st.cache_data
def load_knowledge_base():
    for file in ["knowledge.csv", "knowledge_base.csv"]:
        if os.path.exists(file):
            df = pd.read_csv(file)
            df.columns = df.columns.str.strip()
            return df
    return None

knowledge_df = load_knowledge_base()

# =========================
# SESSION STATE
# =========================
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

# =========================
# DYNAMIC HINGLISH ENGINE (FIXED)
# =========================
def generate_dynamic_hinglish(hindi_text, original_english):
    # 1. Convert Hindi to Roman sounds
    text = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()

    # 2. Manual "Chat Style" Fixes
    fixes = {
        "shha": "sh", "aa": "a", "haim": "hain", "mam": "mein", 
        "upayoga": "use", "karake": "karke", "lie": "liye",
        "vishi": "specific", "badhane": "increase", "laksh": "targets",
        "ba.dhane": "increase", "koshika": "cell", "vyavadhana": "disruption"
    }
    for old, new in fixes.items():
        text = text.replace(old, new)

    # 3. Scientific Term Protection (Regex)
    # This prevents 'dna' becoming 'die' or 'cycling' becoming 'saikalimga'
    text = re.sub(r'die[a-z]*', 'DNA', text)
    text = re.sub(r'saika[a-z]*', 'cycling', text)
    text = re.sub(r'thar[a-z]*', 'thermal', text)
    text = re.sub(r'taka', 'Taq', text)
    text = re.sub(r'polima[a-z]*', 'polymerase', text)
    
    return text.strip().capitalize()

# =========================
# DYNAMIC EXAM TIPS (KEYWORD BASED)
# =========================
def get_dynamic_tips(text):
    all_tips = {
        "dnase": "DNase DNA ko degrade karta hai, isliye EDTA use hota hai use inhibit karne ke liye.",
        "rnase": "RNase heat-stable hota hai, isliye extraction ke waqt iska dhayan rakhna zaroori hai.",
        "pcr": "PCR exponential amplification dikhata hai. 30 cycles mein 1 billion copies ban sakti hain.",
        "taq": "Taq polymerase Thermus aquaticus se milta hai aur high temperature par stable rehta hai.",
        "autoclave": "Autoclaving 121°C par 15 psi pressure ke saath ki jaati hai sterilization ke liye.",
        "ethanol": "Ethanol precipitation se DNA solution se solid form mein bahar nikalta hai.",
        "4": "4°C temperature enzymatic activity ko slow rakhta hai taaki sample degrade na ho."
    }
    
    found = [tip for key, tip in all_tips.items() if key in text.lower()]
    return found if found else ["Focus on the methodology and technical terms for better marks."]

# =========================
# MAIN APP
# =========================
if knowledge_df is None:
    st.error("❌ Knowledge base CSV not found.")
    st.stop()

tabs = st.tabs(["📖 Reader", "🧠 10 Points", "🔬 DNA Lab", "🔍 Search", "📊 Data", "🇮🇳 Hinglish Helper"])

# READER, 10 POINTS, DNA LAB, SEARCH, DATA (Keeping your working code)
with tabs[0]:
    col1, col2, col3 = st.columns([1, 2, 1])
    if col1.button("⬅ Previous"):
        st.session_state.page_index = max(0, st.session_state.page_index - 1)
        st.rerun()
    col2.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</h3>", unsafe_allow_html=True)
    if col3.button("Next ➡"):
        st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
        st.rerun()
    st.divider()
    row = knowledge_df.iloc[st.session_state.page_index]
    left, right = st.columns([2, 1])
    with left:
        st.header(row.get("Topic", "Untitled"))
        st.write(row.get("Explanation", ""))
    with right:
        img = str(row.get("Image", ""))
        if img and os.path.exists(img):
            st.image(img, use_container_width=True)

with tabs[1]:
    st.header("🧠 10 Key Exam Points")
    points = row.get("Ten_Points", "")
    if isinstance(points, str) and points.strip():
        for p in points.split("\n"): st.write("•", p.strip())

with tabs[2]:
    st.header("🔬 DNA Analysis Tool")
    seq = st.text_area("Paste DNA sequence:", "ATGC").upper()
    if st.button("Analyze"):
        st.metric("GC Content", f"{(seq.count('G') + seq.count('C')) / len(seq) * 100:.2f}%")

with tabs[3]:
    st.header("🔍 Smart Search")
    query = st.text_input("Search term").lower()
    if query:
        for i, r in knowledge_df.iterrows():
            if query in str(r.get("Topic", "")).lower():
                with st.expander(r["Topic"]):
                    st.write(r["Explanation"])
                    if st.button("Go", key=f"search_{i}"):
                        st.session_state.page_index = i
                        st.rerun()

with tabs[4]:
    file = st.file_uploader("Upload CSV", type="csv")
    if file: st.dataframe(pd.read_csv(file))

# =========================
# TAB 6: HINGLISH HELPER (DYNAMIC FIX)
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi & Hinglish Helper")
    text_input = st.text_area("Paste English text here:", height=150)

    if st.button("Translate & Explain"):
        if text_input.strip():
            with st.spinner("Processing..."):
                # 1. Hindi Translation
                hindi_out = GoogleTranslator(source="auto", target="hi").translate(text_input)
                
                # 2. DYNAMIC Hinglish (Translates exactly what the user pasted)
                hinglish_out = generate_dynamic_hinglish(hindi_out, text_input)
                
                # 3. DYNAMIC Exam Tips
                exam_tips = get_dynamic_tips(text_input)

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Pure Hindi")
                    st.info(hindi_out)

                with c2:
                    st.subheader("🗣 Smart Hinglish")
                    st.success(hinglish_out)
                    # COPY BUTTON (Built-in to st.code)
                    st.markdown("**Copy Hinglish:**")
                    st.code(hinglish_out, language="text")

                st.divider()
                st.subheader("🧠 Relevant Exam Tips")
                for tip in exam_tips:
                    st.info("• " + tip)
        else:
            st.warning("Please enter text first.")
