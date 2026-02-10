import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator
import easyocr

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
# SMART HINGLISH ENGINE (ULTIMATE FIX)
# =========================
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import re

def generate_smart_hinglish(english_text, hindi_text):
    # 1. Convert Hindi to Roman sounds
    raw_roman = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()

    # 2. Fix Chat Sounds
    sound_fixes = {
        "shha": "sh", "aa": "a", "haim": "hain", "mam": "mein", 
        "upayoga": "use", "karake": "karke", "lie": "liye",
        "vishi": "specific", "badhane": "increase", "lakshyom": "targets"
    }
    for old, new in sound_fixes.items():
        raw_roman = raw_roman.replace(old, new)

    # 3. THE HARD-SWAP (Fixes 'dienae' and 'saikalimga')
    # We look at the original English words and force them back
    important_terms = ["dna", "taq", "thermal", "cycling", "amplify", "specific", "targets", "pcr", "enzyme"]
    
    for term in important_terms:
        if term in english_text.lower():
            # This regex finds any butchered word starting with the same 2 letters and replaces it
            # e.g., it finds 'dienae' and replaces with 'DNA'
            pattern = r'\b' + term[:2] + r'[a-z]*\b'
            raw_roman = re.sub(pattern, term.upper() if term == "dna" else term, raw_roman)

    return raw_roman.strip().capitalize()
# =========================
# MAIN APP
# =========================
if knowledge_df is None:
    st.error("❌ Knowledge base CSV not found.")
    st.stop()

tabs = st.tabs([
    "📖 Reader",
    "🧠 10 Points",
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

        with st.expander("📘 Read Detailed Explanation"):
            st.write(
                row.get(
                    "Detailed_Explanation",
                    "No additional explanation available."
                )
            )

    with right:
        # --- FIXED INDENTATION HERE ---
        img = str(row.get("Image", ""))
        if img and os.path.exists(img):
            with st.expander("🖼️ Show Diagram", expanded=True):
                # FIXED: use_container_width for high resolution
                st.image(img, use_container_width=True)
                st.caption("🔍 Click the arrows on the image to view Fullscreen (HD)")
        else:
            st.info("No diagram available.")

# =========================
# TAB 2: 10 POINTS
# =========================
with tabs[1]:
    st.header("🧠 10 Key Exam Points")
    points = row.get("Ten_Points", "")
    if isinstance(points, str) and points.strip():
        for p in points.split("\n"):
            if p.strip():
                st.write("•", p.strip())
    else:
        st.info("10-point summary not available for this topic.")

# =========================
# TAB 3: DNA LAB
# =========================
with tabs[2]:
    st.header("🔬 DNA Analysis Tool")
    seq = st.text_area("Paste DNA sequence:", "ATGC").upper().strip()
    if st.button("Analyze"):
        if seq:
            gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
            st.metric("GC Content", f"{gc:.2f}%")

# =========================
# TAB 4: SEARCH
# =========================
with tabs[3]:
    st.header("🔍 Smart Search")
    query = st.text_input("Search term").lower()
    if query:
        matches = []
        for i, r in knowledge_df.iterrows():
            if query in str(r.get("Topic", "")).lower() or query in str(r.get("Explanation", "")).lower():
                matches.append(i)
        if matches:
            for i in matches:
                r = knowledge_df.iloc[i]
                with st.expander(f"{r['Topic']} (Page {i+1})"):
                    st.write(r["Explanation"])
                    if st.button(f"Go to Page {i+1}", key=f"go_{i}"):
                        st.session_state.page_index = i
                        st.rerun()
        else:
            st.warning("No results found.")

# =========================
# TAB 5: DATA
# =========================
with tabs[4]:
    st.header("📊 CSV Viewer")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        st.dataframe(pd.read_csv(file))

# =========================
# TAB 6: HINGLISH HELPER (FIXED + COPY BUTTON)
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi & Hinglish Helper")
    
    input_text = st.text_area("Paste English sentence here:", height=100)

    if st.button("Translate & Explain"):
        if input_text.strip():
            with st.spinner("Processing..."):
                # 1. Get Pure Hindi
                hindi_res = GoogleTranslator(source="auto", target="hi").translate(input_text)

                # 2. Get Clean Hinglish
                hinglish_res = generate_smart_hinglish(input_text, hindi_res)

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Pure Hindi")
                    st.info(hindi_res)
                with c2:
                    st.subheader("🗣 Smart Hinglish (Clean)")
                    st.success(hinglish_res)
                    
                    # --- THE COPY BUTTON ---
                    # Using st.code gives a built-in copy button on the top right
                    st.code(hinglish_res, language="text")
                    st.caption("Click the icon in the top-right of the box above to copy.")

                # 3. Term Suggestion & Exam Tips
                st.divider()
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.subheader("🔍 Did you mean?")
                    # Check for common typos
                    dictionary = ["enzyme", "purification", "isolation", "polymerase", "cycling"]
                    words_in_input = input_text.lower().split()
                    found_typo = False
                    for word in words_in_input:
                        clean_w = word.strip(".,()")
                        for correct in dictionary:
                            if len(clean_w) > 3 and clean_w[:3] == correct[:3] and clean_w != correct:
                                st.warning(f"Found '{clean_w}', did you mean **{correct}**?")
                                found_typo = True
                    if not found_typo:
                        st.write("All scientific terms look correct!")

                with col_b:
                    st.subheader("🔬 Exam Tips")
                    tips = {
                        "pcr": "💡 Mention the 3 steps: Denaturation, Annealing, Extension.",
                        "taq": "💡 Mention it is isolated from Thermus aquaticus.",
                        "dna": "💡 Mention it is negatively charged and moves toward Anode.",
                        "cycling": "💡 Mention that thermal cycling is automated using a Thermocycler."
                    }
                    has_tip = False
                    for k, v in tips.items():
                        if k in input_text.lower():
                            st.info(v)
                            has_tip = True
                    if not has_tip:
                        st.write("Write clearly and use diagrams for better marks!")
        else:
            st.warning("Please enter text.")
