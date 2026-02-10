import streamlit as st
import pandas as pd
import os
import easyocr
from deep_translator import GoogleTranslator

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
# LOAD KNOWLEDGE BASE (Updated)
# =========================
@st.cache_data
def load_knowledge_base():
    for file in ["knowledge.csv", "knowledge_base.csv"]:
        if os.path.exists(file):
            df = pd.read_csv(file)
            # Remove any completely empty rows
            df = df.dropna(how='all')
            df.columns = df.columns.str.strip()
            return df
    return None

# ... (keep other parts of code) ...

# =========================
# SESSION STATE
# =========================
if "page_index" not in st.session_state:
    st.session_state.page_index = 0

# =========================
# TABS
# =========================
tabs = st.tabs([
    "📖 Reader",
    "🧠 10 Points",
    "🔬 DNA Lab",
    "🔍 Search",
    "📊 Data",
    "🇮🇳 Hindi Helper",
    
])

# =========================
# TAB 1: READER
# =========================
with tabs[0]:
    col1, col2, col3 = st.columns([1, 2, 1])

    if col1.button("⬅ Previous"):
        st.session_state.page_index = max(0, st.session_state.page_index - 1)
        st.rerun()

    col2.markdown(
        f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} / {len(knowledge_df)}</h3>",
        unsafe_allow_html=True
    )

    if col3.button("Next ➡"):
        st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
        st.rerun()

    st.divider()
    row = knowledge_df.iloc[st.session_state.page_index]

    left, right = st.columns([2, 1])

    with left:
        st.header(row.get("Topic", "Untitled"))
        st.write(row.get("Explanation", ""))

        with st.expander("📘 Detailed Explanation"):
            st.write(row.get("Detailed_Explanation", "No additional explanation available."))

    with right:
        img = str(row.get("Image", ""))
        if img and os.path.exists(img):
            with st.expander("🖼️ Show Diagram"):
                st.image(img, use_container_width=True)
        else:
            st.info("No diagram available.")

# =========================
# TAB 2: 10 POINTS (Updated)
# =========================
with tabs[1]:
    st.header("🧠 10 Key Exam Points")
    
    # 1. Get the data
    points_data = row.get("Ten_Points", "")
    
    # 2. Check if it's actually a string and not "NaN" (empty)
    if pd.isna(points_data) or str(points_data).strip() == "":
        st.info("10-point summary not available for this specific row.")
        st.write("Debug: Check if your CSV Row has data in the Ten_Points column.")
    else:
        # 3. Clean and split the points
        # This handles newlines (\n) which occur when you press Alt+Enter in Excel
        lines = str(points_data).split('\n')
        for line in lines:
            if line.strip():
                st.write(f"• {line.strip()}")

    if st.button("🔄 Force Refresh CSV"):
        st.cache_data.clear()
        st.rerun()

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
# TAB 4: SEARCH (TEXT + OCR)
# =========================
with tabs[3]:
    st.header("🔍 Smart Search (Text + Diagrams)")
    query = st.text_input("Search term").lower().strip()

    if query:
        found_any = False

        for i, r in knowledge_df.iterrows():
            topic = str(r.get("Topic", "")).lower()
            expl = str(r.get("Explanation", "")).lower()
            img = str(r.get("Image", ""))

            found_in = []

            if query in topic or query in expl:
                found_in.append("Text")

            if query in get_text_from_image(img):
                found_in.append("Diagram")

            if found_in:
                found_any = True
                with st.expander(f"📖 {r['Topic']} (Page {i+1})"):
                    st.write(r.get("Explanation", ""))
                    if "Diagram" in found_in:
                        st.info("📸 Term found inside diagram")
                    if st.button(f"Go to Page {i+1}", key=f"go_{i}"):
                        st.session_state.page_index = i
                        st.rerun()

        if not found_any:
            st.warning("No matches found in text or diagrams.")

# =========================
# TAB 5: DATA
# =========================
with tabs[4]:
    st.header("📊 CSV Viewer")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        st.dataframe(pd.read_csv(file))

# =========================
# TAB 6: HINDI HELPER
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi Explanation Helper")

    text = st.text_area("Paste English text here:", height=150)

    if st.button("Translate to Hindi"):
        if not text.strip():
            st.warning("Please enter text.")
        else:
            hindi = GoogleTranslator(source="auto", target="hi").translate(text)
            st.subheader("📝 Pure Hindi Explanation")
            st.info(hindi)

