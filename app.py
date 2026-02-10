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
# SMART HINGLISH ENGINE
# =========================
def generate_smart_hinglish(english_text, hindi_text):
    # 1. Convert Hindi script to Roman script (Hinglish sounds)
    raw_roman = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()
    
    # 2. Fix common "broken" library sounds to WhatsApp style
    sound_fixes = {
        "shha": "sh", "aa": "a", "haim": "hain", "mam": "mein", 
        "upayoga": "use", "karke": "karke", "liye": "liye", 
        "vishi": "specific", "lakshyom": "targets", "badhane": "increase",
        "denae": "DNA", "sekalimga": "cycling", "tharmala": "thermal",
        "taka": "Taq", "polimeresa": "polymerase"
    }
    for old, new in sound_fixes.items():
        raw_roman = raw_roman.replace(old, new)

    # 3. Protect Scientific Terms (Force English spelling)
    sci_terms = ["dna", "taq", "polymerase", "pcr", "thermal", "cycling", "vector", "enzyme", "amplify"]
    for term in sci_terms:
        if term in english_text.lower():
            # Use regex to find the butchered version (e.g., 'dienae') and replace with 'DNA'
            pattern = r'\b' + term[:2] + r'[a-z]*\b'
            raw_roman = re.sub(pattern, term, raw_roman)

    return raw_roman.strip().capitalize()

# =========================
# MAIN APP
# =========================
if knowledge_df is None:
    st.error("❌ Knowledge base CSV not found. Please ensure 'knowledge.csv' is in the folder.")
    st.stop()

tabs = st.tabs([
    "📖 Reader",
    "🔬 DNA Lab",
    "🔍 Search",
    "📊 Data",
    "🇮🇳 Hinglish Helper"
])

# =========================
# TAB 1: READER
# =========================
with tabs[0]:
    col1, col2, col3 = st.columns([1, 2, 1])

    if col1.button("⬅ Previous"):
        if st.session_state.page_index > 0:
            st.session_state.page_index -= 1
            st.rerun()

    col2.markdown(
        f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</h3>",
        unsafe_allow_html=True
    )

    if col3.button("Next ➡"):
        if st.session_state.page_index < len(knowledge_df) - 1:
            st.session_state.page_index += 1
            st.rerun()

    st.divider()
    row = knowledge_df.iloc[st.session_state.page_index]

    left, right = st.columns([2, 1])
    with left:
        st.header(row.get("Topic", "Untitled"))
        st.write(row.get("Explanation", ""))

    with right:
        img_path = str(row.get("Image", ""))
        if img_path and os.path.exists(img_path):
            st.image(img_path, use_container_width=True)
        else:
            st.info("No diagram available for this page.")

# =========================
# TAB 2: DNA LAB
# =========================
with tabs[1]:
    st.header("🔬 DNA Analysis Tool")
    seq = st.text_area("Paste DNA sequence:", "ATGC").upper().strip()

    if st.button("Analyze"):
        if seq:
            gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
            st.metric("GC Content", f"{gc:.2f}%")
        else:
            st.warning("Please enter a sequence.")

# =========================
# TAB 3: SEARCH (TEXT + OCR)
# =========================
with tabs[2]:
    st.header("🔍 Smart Search")
    query = st.text_input("Search term (even inside images)").lower()

    if query:
        matches = []
        image_hits = []

        with st.spinner("Scanning pages..."):
            for i, row in knowledge_df.iterrows():
                topic = str(row.get("Topic", "")).lower()
                expl = str(row.get("Explanation", "")).lower()

                if query in topic or query in expl:
                    matches.append(i)
                else:
                    img = str(row.get("Image", ""))
                    if query in get_text_from_image(img):
                        matches.append(i)
                        image_hits.append(i)

        if matches:
            st.success(f"Found {len(matches)} matches")
            for i in matches:
                r = knowledge_df.iloc[i]
                with st.expander(f"📖 {r['Topic']} (Page {i+1})"):
                    if i in image_hits:
                        st.info("📍 Term found inside a diagram/image.")
                    st.write(r["Explanation"][:250] + "...")
                    if st.button(f"Go to page {i+1}", key=f"go_{i}"):
                        st.session_state.page_index = i
                        st.rerun()
        else:
            st.warning("No results found.")

# =========================
# TAB 4: DATA
# =========================
with tabs[3]:
    st.header("📊 CSV Viewer")
    uploaded_file = st.file_uploader("Upload Lab CSV", type="csv")
    if uploaded_file:
        st.dataframe(pd.read_csv(uploaded_file))
    else:
        st.write("Upload a CSV file to analyze lab data.")

# =========================
# TAB 5: HINGLISH HELPER
# =========================
with tabs[4]:
    st.header("🇮🇳 Hindi & Hinglish Helper")
    st.write("Understand complex Biotech in simple conversational language.")

    input_text = st.text_area(
        "Paste English sentence here:",
        placeholder="e.g., Thermal cycling to amplify specific DNA targets using Taq",
        height=100
    )

    if st.button("Translate & Explain"):
        if input_text.strip():
            with st.spinner("Analyzing..."):
                # 1. Pure Hindi
                hindi_res = GoogleTranslator(source="auto", target="hi").translate(input_text)

                # 2. Smart Hinglish
                hinglish_res = generate_smart_hinglish(input_text, hindi_res)

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Pure Hindi (Exam Style)")
                    st.markdown(f"""<div style="background-color:#f0f2f6; padding:15px; border-radius:10px; border-left:5px solid #ff4b4b;">
                                {hindi_res}</div>""", unsafe_allow_html=True)

                with c2:
                    st.subheader("🗣 Smart Hinglish (Chat Style)")
                    st.markdown(f"""<div style="background-color:#e1f5fe; padding:15px; border-radius:10px; border-left:5px solid #03a9f4; color:#01579b;">
                                {hinglish_res}</div>""", unsafe_allow_html=True)

                # 3. Key Term Dictionary
                st.divider()
                st.subheader("🔬 Key Biotech Terms")
                terms_map = {
                    "taq": "<b>Taq Polymerase:</b> Ek heat-stable enzyme jo PCR reaction mein DNA banane mein madad karta hai.",
                    "pcr": "<b>PCR:</b> Polymerase Chain Reaction - DNA ki copies badhane ki technique.",
                    "thermal cycling": "<b>Thermal Cycling:</b> Temperature ko upar-neeche karke DNA amplify karne ka process.",
                    "amplify": "<b>Amplify:</b> DNA ki quantity ko badhana (making many copies)."
                }
                
                t_cols = st.columns(2)
                found_term = False
                for idx, (k, v) in enumerate(terms_map.items()):
                    if k in input_text.lower():
                        with t_cols[idx % 2]:
                            st.info(v, icon="📍")
                        found_term = True
                if not found_term:
                    st.caption("No specific biotech definitions found for this sentence.")
        else:
            st.warning("Please enter text to translate.")
