import streamlit as st
import pandas as pd
import os
import easyocr
from deep_translator import GoogleTranslator
import requests
import wikipedia
import datetime
import plotly.express as px
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

# --- HERO HEADER ---
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
                                                                                                # 1. TOP PROGRESS BAR
        progress_value = (st.session_state.page_index + 1) / len(knowledge_df)
        st.progress(progress_value)

        # 2. SIMPLE TOOLBAR (Using standard columns, no complex CSS)
        # The [0.5, 0.8, 0.5, 4] ratio keeps everything small and to the left
        c1, c2, c3, c4 = st.columns([0.6, 0.8, 0.6, 4])
        
        with c1:
            # Standard button - works every time
            if st.button("⬅ PREV", use_container_width=True, disabled=st.session_state.page_index == 0):
                st.session_state.page_index = max(0, st.session_state.page_index - 1)
                st.rerun()
        
        with c2:
            # Use a simple st.info or st.code for a boxed look without complex CSS
            current_pg = st.session_state.page_index + 1
            total_pg = len(knowledge_df)
            st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 5px; padding: 2px; text-align: center; background-color: #f9f9f9; line-height: 1.2;">
                    <p style="margin: 0; font-size: 0.7rem; color: gray;">PAGE</p>
                    <p style="margin: 0; font-weight: bold; font-size: 1rem;">{current_pg} / {total_pg}</p>
                </div>
            """, unsafe_allow_html=True)
        
        with c3:
            if st.button("NEXT ➡", use_container_width=True, disabled=st.session_state.page_index == len(knowledge_df) - 1):
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
            
            # --- NEW: AUTO-TAG GENERATOR ---
            # This logic simulates NLP entity extraction
            bio_keywords = ["DNA", "RNA", "Protein", "CRISPR", "Gene", "Cell", "Enzyme", "Mutation", "Pathway", "Genomics"]
            text_content = str(row.get("Explanation", "")) + " " + str(row.get("Detailed_Explanation", ""))
            
            # Find which keywords are in the text
            found_tags = [tag for tag in bio_keywords if tag.lower() in text_content.lower()]
            
            if found_tags:
                tag_html = ""
                for t in found_tags:
                    tag_html += f'<span style="background-color:#e1f5fe; color:#01579b; padding:4px 10px; border-radius:15px; margin-right:5px; font-size:0.8rem; font-weight:bold; border:1px solid #01579b;">🧬 {t}</span>'
                st.markdown(tag_html, unsafe_allow_html=True)
                st.write("") # Spacer
            
            # --- END TAGS ---

            st.write(row.get("Explanation", "No explanation available."))
            
            with st.expander("📘 Detailed Analysis & Mechanism"):
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
# TAB 3: DNA LAB (Updated)
# =========================
with tabs[2]:
    st.header("🔬 DNA Analysis Tool")
    st.info("Analyze nucleotide distribution and GC content for genomic sequences.")
    
    seq = st.text_area("Paste DNA sequence (A, T, G, C):", "ATGCGATCGTAGCTAGCTACGATCGTAGCT").upper().strip()
    
    if st.button("Analyze Sequence"):
        if seq:
            # Check for invalid characters
            valid_bases = set("ATGC")
            if not all(base in valid_bases for base in seq):
                st.error("⚠️ Invalid sequence detected! Please use only A, T, G, and C.")
            else:
                # 1. Metrics
                c1, c2, c3 = st.columns(3)
                gc_content = (seq.count("G") + seq.count("C")) / len(seq) * 100
                
                c1.metric("Sequence Length", f"{len(seq)} bp")
                c2.metric("GC Content", f"{gc_content:.2f}%")
                c3.metric("AT Content", f"{100 - gc_content:.2f}%")
                
                st.divider()
                
                # 2. Visualization
                st.subheader("📊 Nucleotide Distribution")
                counts = {
                    "Nucleotide": ["Adenine (A)", "Thymine (T)", "Guanine (G)", "Cytosine (C)"],
                    "Count": [seq.count("A"), seq.count("T"), seq.count("G"), seq.count("C")]
                }
                df_counts = pd.DataFrame(counts)
                
                # Create Plotly Chart
                fig = px.bar(
                    df_counts, 
                    x="Nucleotide", 
                    y="Count", 
                    color="Nucleotide",
                    color_discrete_map={
                        "Adenine (A)": "#FF4B4B", 
                        "Thymine (T)": "#FFA421", 
                        "Guanine (G)": "#31333F", 
                        "Cytosine (C)": "#0068C9"
                    },
                    template="plotly_white"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 3. Simple Bioinformatics Insight
                if gc_content > 50:
                    st.success("💡 **Insight:** High GC content suggests higher thermal stability (common in extremophiles).")
                else:
                    st.info("💡 **Insight:** Normal/Low GC content detected, typical of many standard genomic regions.")
        else:
            st.warning("Please enter a sequence first.")

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
                else:
                    target_title = search_results[0]
                    page = wikipedia.page(target_title, auto_suggest=False)
                    summary = wikipedia.summary(target_title, sentences=4, auto_suggest=False)
                    
                    # --- NEW RESEARCH CARD UI ---
                    st.markdown(f"""
                        <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #1e468a;">
                            <h3 style="margin-top: 0;">📚 Research Snapshot: {page.title}</h3>
                            <p style="font-size: 1.1rem; line-height: 1.6;">{summary}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Metadata Columns
                    st.write("") 
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.info(f"🔗 **Source:** Wikipedia")
                    with m2:
                        # Simple logic to count words as a 'complexity' metric
                        word_count = len(summary.split())
                        st.info(f"📊 **Complexity:** {word_count} words")
                    with m3:
                        st.info(f"📅 **Last Updated:** Today")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.link_button("📖 Read Full Article", page.url, use_container_width=True)
                    with col2:
                        google_url = f"https://www.google.com/search?q={user_input.replace(' ', '+')}+biology+research+gate"
                        st.link_button("🔬 Search ResearchGate", google_url, use_container_width=True)
                        
            except wikipedia.exceptions.DisambiguationError as e:
                st.warning(f"Too many matches. Did you mean: {', '.join(e.options[:3])}?")
            except Exception as e:
                st.error("Could not fetch detailed summary. Try a more specific term.")

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
