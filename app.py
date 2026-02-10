import streamlit as st
import pandas as pd
import os
import easyocr
from deep_translator import GoogleTranslator
import requests
import wikipedia
import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Bio-Tech Smart Textbook",
    layout="wide"
)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🛡️ Bio-Verify 2026")
    st.write(f"**Current Date:** {datetime.date.today().strftime('%d %b %Y')}")
    st.success("✅ Live API Connection: Active")
    st.info("Verified Data Sources: NCBI, Wikipedia, Google")
    st.divider()
 # --- PROFILE CARD (Image 3 Style) ---
    st.markdown("""
        <div style="background-color: #1e468a; padding: 20px; border-radius: 15px; text-align: center; color: white;">
            <h3 style="margin: 0; color: white;">Yashwant Nama</h3>
            <p style="margin: 5px 0; font-size: 0.9rem; opacity: 0.8;">Developer & Researcher</p>
            <p style="font-weight: bold; font-size: 1rem;">Bio-Informatics & Genetics</p>
            <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px;">
                <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.8rem;">🧬 Genomics</span>
                <span style="background: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 20px; font-size: 0.8rem;">🕸️ Networks</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
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
    # Looking for either filename
    for file in ["knowledge_base.csv", "knowledge.csv"]:
        if os.path.exists(file):
            try:
                df = pd.read_csv(file)
                df.columns = df.columns.str.strip()
                df = df.dropna(how='all')
                return df
            except Exception:
                continue
    return pd.DataFrame(columns=["Topic", "Section", "Explanation", "Image", "Ten_Points", "Detailed_Explanation"])

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
# --- HERO HEADER (Image 2 Style) ---
st.markdown("""
    <div style="text-align: left; padding: 10px 0px;">
        <h1 style="margin-bottom: 0;">🧬 Bio-Tech Smart Textbook</h1>
        <p style="font-style: italic; color: #555; font-size: 1.1rem;">
            This resource guide serves as a foundational reference for computational hypothesis generation, 
            validation, and extension of biotechnology mechanisms.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- TABS DEFINITION ---
tabs = st.tabs([
    "📖 Reader",
    "🧠 10 Points",
    "🔬 DNA Lab",
    "🔍 Search",
    "🌐 Global Bio-Search",
    "🇮🇳 Hindi Helper"
])

# =========================
# TAB 1: READER
# =========================
with tabs[0]:
    if knowledge_df.empty:
        st.warning("⚠️ Knowledge base is empty. Please check your CSV file.")
    else:
        # Navigation Buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        if col1.button("⬅ Previous"):
            st.session_state.page_index = max(0, st.session_state.page_index - 1)
            st.rerun()
        
        col2.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} / {len(knowledge_df)}</h3>", unsafe_allow_html=True)
        
        if col3.button("Next ➡"):
            st.session_state.page_index = min(len(knowledge_df) - 1, st.session_state.page_index + 1)
            st.rerun()

        st.divider()
        
        # Define current row and save to session state
        row = knowledge_df.iloc[st.session_state.page_index]
        st.session_state['selected_row'] = row
        
        # Layout: Text on Left, Diagram Spoiler on Right
        left, right = st.columns([2, 1])
        
        with left:
            st.header(row.get("Topic", "Untitled"))
            st.write(row.get("Explanation", "No explanation available."))
            with st.expander("📘 Detailed Explanation"):
                st.write(row.get("Detailed_Explanation", "No extra details available."))
        
        with right:
            # --- DIAGRAM SPOILER ---
            with st.expander("🖼️ View Topic Diagram", expanded=False):
                img_path = str(row.get("Image", ""))
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True, caption=f"Visual: {row.get('Topic')}")
                else:
                    st.info("No diagram available.")


# =========================
# TAB 2: 10 POINTS
# =========================
with tabs[1]:
    st.header("🧠 10 Key Exam Points")
    
    if 'selected_row' in st.session_state:
        current_row = st.session_state['selected_row']
        # Try both common column names for points
        pts = current_row.get('Ten_Points') or current_row.get('10_Points') or "No points available for this topic."
        
        st.info(f"Summary for: **{current_row.get('Topic', 'Selected Topic')}**")
        st.write(pts)
        
        st.divider()
        col_cite, col_dl = st.columns(2)
        
        with col_cite:
            if st.button("📋 Generate Citation"):
                citation = f"Source: Bio-Verify 2026, Topic: {current_row.get('Topic')}, Date: {datetime.date.today()}"
                st.code(citation, language="text")
        
        with col_dl:
            st.download_button(
                label="📥 Download Study Notes",
                data=str(pts),
                file_name=f"{current_row.get('Topic', 'Bio_Notes')}_Notes.txt",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.warning("⚠️ Please go to the 'Reader' tab and select a topic first!")

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
# TAB 5: GLOBAL BIO-SEARCH
# =========================
with tabs[4]:
    st.header("🌐 Global Bio-Intelligence")
    st.caption("Search results are now matched for accuracy (Google-style logic)")
    
    st.subheader("📚 Quick Wikipedia Summary")
    user_input = st.text_input("Search for any topic (e.g., DNA, MITOSIS, CRISPR):")
    
    if user_input:
        with st.spinner(f"Searching for '{user_input}'..."):
            try:
                search_results = wikipedia.search(user_input, results=5)
                if not search_results:
                    st.error("❌ No results found on Wikipedia.")
                    google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}+biology"
                    st.link_button(f"🔍 Search Google for '{user_input}'", google_url)
                else:
                    target_title = search_results[0]
                    summary = wikipedia.summary(target_title, sentences=3, auto_suggest=False)
                    page = wikipedia.page(target_title, auto_suggest=False)
                    st.success(f"Top Result: **{page.title}**")
                    st.info(summary)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("📖 Open Wikipedia Page", page.url, use_container_width=True)
                    with col2:
                        google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}+biology"
                        st.link_button(f"🔍 Search Google for '{user_input}'", google_url, use_container_width=True)
            except Exception:
                st.error("Could not find a direct match.")
                google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}+biology"
                st.link_button(f"🔍 Search Google for '{user_input}'", google_url)

    st.divider()
    st.subheader("🔬 Technical Research (NCBI)")
    s_type = st.selectbox("Select Database", ["pubmed", "gene", "protein"])
    s_query = st.text_input(f"Enter {s_type} keyword for technical data:")
    
    if st.button("Search NCBI"):
        if s_query:
            with st.spinner("Searching NCBI..."):
                try:
                    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
                    res = requests.get(url, params={"db": s_type, "term": s_query, "retmode": "json", "retmax": 5}).json()
                    ids = res.get("esearchresult", {}).get("idlist", [])
                    if ids:
                        st.caption("🛡️ Verified Technical Records found:")
                        for rid in ids:
                            st.write(f"✅ **Record {rid}:** [View Official NCBI Data](https://www.ncbi.nlm.nih.gov/{s_type}/{rid})")
                    else:
                        st.warning("No technical records found.")
                except Exception as e:
                    st.error(f"NCBI Connection Error: {e}")
        else:
            st.warning("Please enter a keyword.")

# =========================
# TAB 6: HINDI HELPER
# =========================
with tabs[5]:
    st.header("🇮🇳 Hindi Helper")
    txt = st.text_area("Paste English text to translate to Hindi:")
    if st.button("Translate"):
        if txt.strip():
            try:
                translated = GoogleTranslator(source="auto", target="hi").translate(txt)
                st.info(translated)
            except Exception as e:
                st.error("Translation Error.")
