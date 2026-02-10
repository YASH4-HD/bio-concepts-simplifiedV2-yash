import streamlit as st
import pandas as pd
import os
import easyocr
import google.generativeai as genai
from deep_translator import GoogleTranslator

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bio-Tech Smart AI Textbook",
    layout="wide"
)

# =========================
# GEMINI CONFIG (FREE + SAFE)
# =========================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

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
# TOPIC DETECTION
# =========================
def detect_topic(text):
    t = text.lower()
    if any(k in t for k in ["phenol", "ethanol", "dnase", "rnase", "extraction"]):
        return "DNA extraction"
    if any(k in t for k in ["pcr", "taq", "thermal cycling"]):
        return "PCR"
    if any(k in t for k in ["restriction enzyme", "endonuclease"]):
        return "Restriction enzymes"
    if any(k in t for k in ["huntington", "ptc518", "votoplam"]):
        return "Neurogenetics"
    if any(k in t for k in ["immunotherapy", "cd40", "antibody"]):
        return "Immunology"
    return "General biology"

# =========================
# RULE-BASED HINGLISH
# =========================
def rule_based_hinglish(topic):
    data = {
        "DNA extraction": [
            "Cell se DNA nikalne ke baad proteins remove kiye jaate hain.",
            "RNase RNA ko degrade karta hai, DNase ko inactivate karna zaroori hota hai.",
            "Phenol–chloroform extraction proteins ko separate karta hai.",
            "Ethanol precipitation se DNA solution se bahar aata hai.",
            "EDTA DNase activity ko inhibit karta hai."
        ],
        "PCR": [
            "PCR DNA amplification ki technique hai.",
            "Taq polymerase heat-stable hota hai.",
            "Thermal cycling mein denaturation, annealing aur extension steps hote hain."
        ],
        "Restriction enzymes": [
            "Restriction enzymes DNA ko palindromic sequences par cut karte hain.",
            "Ye molecular cloning ke liye important hote hain.",
            "Sticky ends ligation ko easy banaate hain."
        ],
        "Neurogenetics": [
            "Huntington’s disease ek genetic neurodegenerative disorder hai.",
            "PTC518 (Votoplam) ek splicing modifier hai.",
            "Ye mutant huntingtin expression ko reduce karta hai."
        ],
        "Immunology": [
            "Immunotherapy immune system ko activate karti hai.",
            "CD40 immune activation mein important role play karta hai.",
            "Antibody-based therapies targeted hoti hain."
        ],
        "General biology": [
            "Yeh biology ka important concept hai.",
            "Exam ke liye definition aur mechanism samajhna kaafi hota hai."
        ]
    }
    return "\n".join("• " + x for x in data[topic])

# =========================
# GEMINI HINGLISH (SAFE)
# =========================
def gemini_hinglish(text, topic):
    prompt = f"""
You are a senior Indian biology teacher.

Explain in SIMPLE HINGLISH.
Rules:
- Bullet points (max 6)
- Exam oriented
- Scientific terms in English
- No hallucinations

Topic: {topic}
Text: {text}
"""
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 250
            }
        )
        return response.text.strip()
    except Exception:
        return None

# =========================
# MAIN APP
# =========================
if knowledge_df is None:
    st.error("❌ Knowledge base CSV not found.")
    st.stop()

tabs = st.tabs([
    "📖 AI Reader",
    "🧠 10 Points",
    "🔬 DNA Lab",
    "🔍 Search",
    "📊 Data Management",
    "🇮🇳 AI Hinglish Helper"
])

# =========================
# TAB 1: AI READER
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

    row = knowledge_df.iloc[st.session_state.page_index]

    left, right = st.columns([2, 1])
    with left:
        st.header(row.get("Topic", "Untitled"))
        st.write(row.get("Explanation", ""))
        with st.expander("📘 Detailed Explanation"):
            st.write(row.get("Detailed_Explanation", "Not available"))

        if st.button("✨ AI Hinglish Explanation"):
            topic = detect_topic(row.get("Topic", ""))
            ai_text = gemini_hinglish(row.get("Explanation", ""), topic)
            if ai_text:
                st.code(ai_text, language="text")
                st.caption("🤖 AI-assisted explanation")
            else:
                st.code(rule_based_hinglish(topic), language="text")
                st.caption("📘 Rule-based fallback")

    with right:
        img = str(row.get("Image", ""))
        if img and os.path.exists(img):
            with st.expander("🖼️ Show Diagram"):
                st.image(img, use_container_width=True)

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
        st.info("No exam points available.")

# =========================
# TAB 3: DNA LAB
# =========================
with tabs[2]:
    st.header("🔬 DNA Analysis Tool")
    seq = st.text_area("Paste DNA sequence:", "ATGC").upper()
    if st.button("Analyze"):
        st.metric("GC Content", f"{(seq.count('G') + seq.count('C')) / len(seq) * 100:.2f}%")

# =========================
# TAB 4: SEARCH
# =========================
with tabs[3]:
    st.header("🔍 Smart Search")
    query = st.text_input("Search term").lower()
    for i, r in knowledge_df.iterrows():
        if query and query in str(r.get("Topic", "")).lower():
            with st.expander(r["Topic"]):
                st.write(r["Explanation"])
                if st.button("Go", key=i):
                    st.session_state.page_index = i
                    st.rerun()

# =========================
# TAB 5: DATA MANAGEMENT
# =========================
with tabs[4]:
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        st.dataframe(pd.read_csv(file))

# =========================
# TAB 6: AI HINGLISH HELPER
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi & Hinglish Helper")

    text = st.text_area("Paste English text here:", height=150)
    use_ai = st.checkbox("🤖 Use Gemini AI (optional)", value=False)

    if st.button("Translate & Explain"):
        hindi = GoogleTranslator(source="auto", target="hi").translate(text)
        topic = detect_topic(text)

        if use_ai:
            hinglish = gemini_hinglish(text, topic)
            if hinglish is None:
                hinglish = rule_based_hinglish(topic)
                st.warning("AI unavailable. Showing rule-based explanation.")
        else:
            hinglish = rule_based_hinglish(topic)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📝 Pure Hindi")
            st.info(hindi)
        with c2:
            st.subheader("🗣 Smart Hinglish")
            st.code(hinglish, language="text")
