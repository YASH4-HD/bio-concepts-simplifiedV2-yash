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
# SMART HINGLISH ENGINE (FORCE-FIXED)
# =========================
def generate_smart_hinglish(english_text, hindi_text):
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate
    import re

    # 1. Convert Hindi to Roman sounds
    text = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS).lower()

    # 2. Manual "Chat Style" Fixes
    fixes = {
        "shha": "sh", "aa": "a", "haim": "hain", "mam": "mein", 
        "upayoga": "use", "karake": "karke", "lie": "liye",
        "vishi": "specific", "badhane": "increase", "lakshyom": "targets",
        "ba.dhane": "increase"
    }
    for old, new in fixes.items():
        text = text.replace(old, new)

    # 3. THE FORCE-FIX: This replaces the broken words with original English
    # We look for the broken patterns and swap them out
    text = re.sub(r'die[a-z]*', 'DNA', text)
    text = re.sub(r'saika[a-z]*', 'cycling', text)
    text = re.sub(r'thar[a-z]*', 'thermal', text)
    text = re.sub(r'taka', 'Taq', text)
    text = re.sub(r'polima[a-z]*', 'polymerase', text)
    text = re.sub(r'vishi[a-z]*', 'specific', text)
    text = re.sub(r'laksh[a-z]*', 'targets', text)

    return text.strip().capitalize()
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
# TAB 6: HINGLISH HELPER (REBUILT FOR ACCURACY)
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi & Hinglish Helper")
    
    input_text = st.text_area("Paste English sentence here:", height=150)

    if st.button("Translate & Explain"):
        if input_text.strip():
            with st.spinner("Analyzing scientific context..."):
                # 1. Get Pure Hindi
                hindi_res = GoogleTranslator(source="auto", target="hi").translate(input_text)

                # 2. GENERATE SMART HINGLISH (The Real Way)
                # Instead of broken transliteration, we use the Hindi structure but keep 
                # technical English words intact.
                
                from indic_transliteration import sanscript
                from indic_transliteration.sanscript import transliterate

                # Convert Hindi to Roman sounds
                hinglish = transliterate(hindi_res, sanscript.DEVANAGARI, sanscript.ITRANS).lower()

                # Clean up the phonetic mess
                replacements = {
                    "shha": "sh", "aa": "a", "haim": "hain", "mam": "mein", "lie": "liye",
                    "karake": "karke", "die": "DNA", "saika": "cycling", "thar": "thermal",
                    "vishi": "specific", "ba.dhane": "increase", "laksh": "targets",
                    "autokleva": "autoclaved", "selsiyasa": "Celsius", "shishe": "glassware",
                    "samadhana": "solutions", "koshika": "cell", "vyavadhana": "disruption"
                }
                for old, new in replacements.items():
                    hinglish = hinglish.replace(old, new)

                # Force original English scientific terms back in
                # This fixes the "really bad results" by ensuring tech terms stay English
                sci_vocab = [
                    "dna", "dnase", "autoclaved", "glassware", "solutions", 
                    "cell disruption", "shear forces", "squashing", "purified", 
                    "celsius", "activity", "destroy", "performed"
                ]
                for word in sci_vocab:
                    if word in input_text.lower():
                        # Find the weird phonetic version and replace with original English
                        import re
                        pattern = r'\b' + word[:3] + r'[a-z]*\b'
                        hinglish = re.sub(pattern, word, hinglish)

                # 3. DISPLAY RESULTS
                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Pure Hindi")
                    st.info(hindi_res)
                
                with c2:
                    st.subheader("🗣 Smart Hinglish (Cleaned)")
                    st.success(hinglish)
                    
                    # THE COPY OPTION (Requested: Clear and functional)
                    st.write("📋 **Copy Hinglish:**")
                    st.code(hinglish, language="text")

                # 4. EXAM TIPS (Removed 'Did you know')
                st.divider()
                st.subheader("🔬 Exam Tips")
                tips = {
                    "dnase": "💡 **Exam Tip:** DNase is an enzyme that degrades DNA. Autoclaving is essential to remove it.",
                    "celsius": "💡 **Exam Tip:** 4°C is used to slow down enzymatic activity and prevent DNA degradation.",
                    "autoclave": "💡 **Exam Tip:** Autoclaving usually happens at 121°C at 15 psi pressure.",
                    "cell disruption": "💡 **Exam Tip:** Physical methods like shear forces are used to break the cell wall/membrane."
                }
                
                has_tip = False
                for k, v in tips.items():
                    if k in input_text.lower():
                        st.info(v)
                        has_tip = True
                if not has_tip:
                    st.write("Focus on the methodology and temperature requirements for this process.")
        else:
            st.warning("Please enter text.")

