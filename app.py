import streamlit as st
import pandas as pd
import os
import easyocr
from deep_translator import GoogleTranslator
import requests
import wikipedia

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
    for file in ["knowledge_base.csv", "knowledge.csv"]:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                df.columns = df.columns.str.strip()
                df = df.dropna(how='all')
                return df
            except Exception:
                continue
    return pd.DataFrame(columns=["Topic", "Section", "Explanation", "Image", "Ten_Points"])

knowledge_df = load_knowledge_base()

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
    "🌐 Global Bio-Search",
    "🇮🇳 Hindi Helper",
])

# =========================
# TAB 1: READER
# =========================
with tabs[0]:
    if knowledge_df.empty:
        st.warning("⚠️ Knowledge base is empty. Please check your CSV file.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        if col1.button("⬅ Previous"):
            st.session_state.page_index = max(0, st.session_state.page_index - 1)
            st.rerun()
        
        col2.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} / {len(knowledge_df)}</h3>", unsafe_allow_html=True)
        
        if col3.button("Next ➡"):
            st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
            st.rerun()

        st.divider()
        row = knowledge_df.iloc[st.session_state.page_index]
        left, right = st.columns([2, 1])
        
        with left:
            st.header(row.get("Topic", "Untitled"))
            st.write(row.get("Explanation", "No explanation available."))
            with st.expander("📘 Detailed Explanation"):
                st.write(row.get("Detailed_Explanation", "No extra details available."))
        
        with right:
            img = str(row.get("Image", ""))
            if img and os.path.exists(img):
                st.image(img, use_container_width=True)
            else:
                st.info("No diagram available.")

# =========================
# TAB 2: 10 POINTS
# =========================
with tabs[1]:
    st.header("🧠 10 Key Exam Points")
    if not knowledge_df.empty:
        row = knowledge_df.iloc[st.session_state.page_index]
        pts = row.get("Ten_Points", "")
        if pd.isna(pts) or str(pts).strip() == "":
            st.info("No points available for this topic.")
        else:
            for p in str(pts).split("\n"):
                if p.strip(): st.write(f"• {p.strip()}")
    else:
        st.info("Knowledge base is empty.")

# =========================
# TAB 3: DNA LAB
# =========================
with tabs[2]:
    st.header("🔬 DNA Analysis Tool")
    seq = st.text_area("Paste DNA sequence (A, T, G, C):", "ATGC").upper().strip()
    if st.button("Analyze Sequence"):
        if seq:
            try:
                gc = (seq.count("G") + seq.count("C")) / len(seq) * 100
                st.metric("GC Content", f"{gc:.2f}%")
                st.text(f"Length: {len(seq)} bp")
            except ZeroDivisionError:
                st.error("Invalid sequence.")

# =========================
# TAB 4: INTERNAL SEARCH
# =========================
with tabs[3]:
    st.header("🔍 Search Internal Textbook")
    query = st.text_input("Search for a term (Text or Diagram)...").lower()
    if query:
        found = False
        for i, r in knowledge_df.iterrows():
            txt_match = query in str(r['Topic']).lower() or query in str(r['Explanation']).lower()
            img_text = get_text_from_image(str(r.get('Image', '')))
            if txt_match or query in img_text:
                found = True
                with st.expander(f"📖 {r['Topic']} (Page {i+1})"):
                    st.write(r['Explanation'])
                    if query in img_text: st.success("Found in Diagram!")
                    if st.button(f"Go to Page {i+1}", key=f"src_{i}"):
                        st.session_state.page_index = i
                        st.rerun()
        if not found: st.warning("No matches found.")

# =========================
# TAB 5: GLOBAL BIO-SEARCH (With Wikipedia)
# =========================
import wikipedia  # Add this at the very top of your file

with tabs[4]:
    st.header("🌐 Global Bio-Intelligence")
    st.caption("Search Wikipedia and NCBI (National Center for Biotechnology Information)")
    
    # 1. Wikipedia Section
    st.subheader("📚 Quick Wikipedia Summary")
    wiki_query = st.text_input("Enter a topic to explain (e.g., DNA, CRISPR, Mitosis):")
    
    if wiki_query:
        with st.spinner("Fetching Wikipedia summary..."):
            try:
                # Get the summary (first 3 sentences)
                summary = wikipedia.summary(wiki_query, sentences=3)
                st.info(summary)
                
                # Link to full article
                page = wikipedia.page(wiki_query)
                st.markdown(f"🔗 [Read full Wikipedia article]({page.url})")
            except wikipedia.exceptions.DisambiguationError as e:
                st.warning(f"Too vague! Try one of these: {', '.join(e.options[:5])}")
            except Exception:
                st.error("Could not find a Wikipedia page for this term.")

    st.divider()

    # 2. NCBI Section
    st.subheader("🔬 Technical Research (NCBI)")
    s_type = st.selectbox("Database", ["pubmed", "gene", "protein"])
    s_query = st.text_input(f"Enter {s_type} keyword for technical data:")
    
    if st.button("Search NCBI"):
        if s_query:
            with st.spinner("Searching NCBI..."):
                try:
                    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                    res = requests.get(url, params={"db": s_type, "term": s_query, "retmode": "json", "retmax": 5}).json()
                    ids = res.get("esearchresult", {}).get("idlist", [])
                    if ids:
                        for rid in ids:
                            st.markdown(f"🧬 [NCBI Record {rid}](https://www.ncbi.nlm.nih.gov/{s_type}/{rid})")
                    else:
                        st.warning("No technical records found.")
                except:
                    st.error("NCBI Connection Error.")

# =========================
# TAB 6: HINDI HELPER
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi Helper")
    txt = st.text_area("Paste English text to translate to Hindi:")
    if st.button("Translate"):
        if txt.strip():
            translated = GoogleTranslator(source="auto", target="hi").translate(txt)
            st.info(translated)
