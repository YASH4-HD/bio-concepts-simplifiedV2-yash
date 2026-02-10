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
# SMART HINGLISH ENGINE
# =========================
def generate_smart_hinglish(text):
    t = text.lower()

    if "thermal cycling" in t and "taq" in t:
        return (
            "PCR mein Taq polymerase ka use hota hai, "
            "jisme thermal cycling ke through specific DNA targets amplify kiye jaate hain."
        )

    if "restriction enzyme" in t:
        return (
            "Restriction enzymes DNA ko specific palindromic sequences par cut karte hain, "
            "jo cloning ke liye bahut important hote hain."
        )

    if "enzyme" in t:
        return (
            "Enzyme ek biological catalyst hota hai "
            "jo reaction ko fast karta hai bina khud consume hue."
        )

    return (
        "Simple words mein, yeh biological process lab mein "
        "important molecules ko samajhne ke liye use hota hai."
    )

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
        img = str(row.get("Image", ""))
        if img and os.path.exists(img):
            with st.expander("🖼️ Show Diagram"):
                st.image(img, width=300)
                st.caption("Click image to zoom")
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
# TAB 4: SEARCH (TEXT + OCR)
# =========================
with tabs[3]:
    st.header("🔍 Smart Search")
    query = st.text_input("Search term").lower()

    if query:
        matches = []
        image_hits = []

        for i, r in knowledge_df.iterrows():
            topic = str(r.get("Topic", "")).lower()
            expl = str(r.get("Explanation", "")).lower()

            if query in topic or query in expl:
                matches.append(i)
            else:
                img = str(r.get("Image", ""))
                if query in get_text_from_image(img):
                    matches.append(i)
                    image_hits.append(i)

        if matches:
            st.success(f"Found {len(matches)} matches")
            for i in matches:
                r = knowledge_df.iloc[i]
                with st.expander(f"{r['Topic']} (Page {i+1})"):
                    if i in image_hits:
                        st.info("📍 Found inside diagram")
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
# TAB 6: HINGLISH HELPER
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi & Hinglish Helper")

    text = st.text_area(
        "Paste English sentence here:",
        height=100
    )

    if st.button("Translate & Explain"):
        if text.strip():
            with st.spinner("Processing..."):

                # Pure Hindi
                hindi = GoogleTranslator(
                    source="auto",
                    target="hi"
                ).translate(text)

                # Smart Hinglish
                hinglish = generate_smart_hinglish(text)

                c1, c2 = st.columns(2)
                with c1:
                    st.subheader("📝 Pure Hindi")
                    st.info(hindi)

                with c2:
                    st.subheader("🗣 Smart Hinglish (Chat Style)")
                    st.success(hinglish)

                # ---------- KEY BIOTECH TERMS (RESTORED) ----------
                st.divider()
                st.subheader("🔬 Key Biotech Terms")

                terms = {
                    "taq": "Taq Polymerase: Heat-stable enzyme used in PCR.",
                    "thermal cycling": "Thermal cycling: Repeated heating and cooling in PCR.",
                    "dna": "DNA: Genetic material of cells.",
                    "pcr": "PCR: Technique to amplify DNA."
                }

                for k, v in terms.items():
                    if k in text.lower():
                        st.info(v)

        else:
            st.warning("Please enter text.")
