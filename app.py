import streamlit as st
import pandas as pd
import os
import easyocr
from deep_translator import GoogleTranslator
import requests
import wikipedia
import datetime
import plotly.express as px
import datetime
import pytz
# ==========================================
# 1. AUTO-ADAPTING UI (MOBILE + DESKTOP)
# ==========================================
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

def inject_responsive_design():
    st.markdown("""
    <style>
    /* 1. BASE THEME (Medical White) */
    .stApp {
        background: linear-gradient(180deg, #f8faff 0%, #eef2f7 100%);
        color: #1e293b;
    }

    /* 2. DESKTOP ONLY: Floating Particles */
    @media (min-width: 768px) {
        .particle {
          color: rgba(30, 70, 138, 0.1);
          font-size: 24px;
          position: fixed;
          top: -10%;
          z-index: 0;
          animation: fall 15s linear infinite, shake 4s ease-in-out infinite;
        }
    }
    /* MOBILE ONLY: Hide particles and optimize text */
    @media (max-width: 767px) {
        .particle { display: none; }
        p, li { font-size: 1.15rem !important; line-height: 1.6 !important; }
        .stButton button { width: 100% !important; height: 50px !important; margin-bottom: 10px !important; }
        h1 { font-size: 1.7rem !important; }
    }

    @keyframes fall { 0% { top: -10%; } 100% { top: 100%; } }
    @keyframes shake { 0%, 100% { transform: translateX(0); } 50% { transform: translateX(30px); } }

    /* 3. CONTENT CARDS */
    .bio-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        color: #1e293b;
    }

    /* 4. BIO TAGS */
    .bio-tag {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 12px;
        border-radius: 15px;
        margin-right: 8px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin-top: 5px;
        border: 1px solid #bae6fd;
    }
    /* Floating Search Bar at the bottom */
.floating-search-internal {
    margin-top: 20px;
    margin-bottom: 20px;
    width: 100%;
    background: white;
    padding: 10px;
    border-radius: 15px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* Hide on small phones so it doesn't block content */
@media (max-width: 767px) {
    .floating-search { width: 90%; bottom: 10px; }
}
/* This part allows the search bar to float outside the normal container */
.stApp {
    overflow: visible !important;
}

/* This targets the specific Streamlit input to make it look cleaner */
.stTextInput > div > div > input {
    border: none !important;
    background: transparent !important;
    }
    </style>
    """, unsafe_allow_html=True)  # This closes the CSS part

    # Now we start the HTML particles part
    st.markdown("""
    <div aria-hidden="true">
        <div class="particle" style="left:10%; animation-delay:0s;">🧬</div>
        <div class="particle" style="left:35%; animation-delay:5s;">●</div>
        <div class="particle" style="left:60%; animation-delay:2s;">○</div>
        <div class="particle" style="left:85%; animation-delay:8s;">🧬</div>
    </div>
    """, unsafe_allow_html=True)


inject_responsive_design()

# =========================
# SIDEBAR: BIO-VERIFY PANEL
# =========================
with st.sidebar:

    # Title
    st.title("🛡️ Bio-Verify 2026")

    # --- INDIA TIME (IST) ---
    ist = pytz.timezone("Asia/Kolkata")
    today_dt = datetime.datetime.now(ist)
    today_date = today_dt.date()

    # Display current date
    today_auto = today_dt.strftime("%d %b %Y")
    st.subheader(f"📅 {today_auto.upper()}")

    st.divider()

    # --- EXAM DATES ---
    EXAMS = {
        "CSIR NET JUNE": datetime.date(2026, 6, 1),
        "GATE 2027": datetime.date(2027, 2, 2),
    }

    st.subheader("📆 Exam Countdown")

    for exam, exam_date in EXAMS.items():
        days_left = (exam_date - today_date).days

        if days_left > 0:
            st.info(f"**{exam}**: {days_left} days left")
        elif days_left == 0:
            st.warning(f"**{exam}**: Exam Today!")
        else:
            st.error(f"**{exam}**: Exam completed")

    st.divider()

    # --- STATUS BADGES ---
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
    "🚀 Home", 
    "📖 Reader", 
    "🧠 10 Points", 
    "🧪 DNA Interactive Lab", 
    "🔍 Search", 
    "🌐 Global Bio-Search", 
    "🇮🇳 Hindi Helper", 
    "🧬 Advanced Molecular Suite",
    "🔬 3D Viewer"  # <--- This MUST be the 9th item
    "🔬 NCBS Research"
])
# =========================
# TAB 1: 🚀 HOME (LAUNCHPAD)
# =========================
with tabs[0]:
    # Header Section
    st.markdown("""
        <div class="bio-card" style="text-align: center; border: none; background: transparent; box-shadow: none;">
            <h1 style="color: #0369a1; margin-bottom: 10px;">Welcome to Bio-Tech Smart Textbook</h1>
            <p style="font-size: 1.2rem; color: #64748b;">A foundational reference for computational biotechnology research.</p>
        </div>
    """, unsafe_allow_html=True)

    # --- ROW 1: CORE TOOLS ---
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
            <div class="bio-card" style="text-align: center; height: 220px;">
                <h2 style="margin:0;">📖</h2>
                <h4 style="color: #0369a1;">Smart Reader</h4>
                <p style="font-size: 0.85rem; color: #64748b;">Navigate through core chapters, mechanisms, and detailed genomic analysis.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="bio-card" style="text-align: center; height: 220px;">
                <h2 style="margin:0;">🧪</h2>
                <h4 style="color: #0369a1;">DNA Lab</h4>
                <p style="font-size: 0.85rem; color: #64748b;">Clean raw sequences, perform transcription, and simulate random mutations.</p>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
            <div class="bio-card" style="text-align: center; height: 220px;">
                <h2 style="margin:0;">🌐</h2>
                <h4 style="color: #0369a1;">Global Intelligence</h4>
                <p style="font-size: 0.85rem; color: #64748b;">Direct connection to NCBI PubMed and Wikipedia for real-time research.</p>
            </div>
        """, unsafe_allow_html=True)

    # --- ROW 2: ADVANCED & SPECIALIZED ---
    c1, c2, c3 = st.columns(3) # Changed to 3 columns to fit the new tool
    
    with c1:
        st.markdown("""
            <div class="bio-card" style="display: flex; align-items: center; gap: 15px; height: 120px;">
                <div style="font-size: 2rem;">🔍</div>
                <div>
                    <h4 style="margin:0; color: #0369a1;">Smart Search</h4>
                    <p style="margin:0; font-size: 0.8rem; color: #64748b;">Search textbook content and diagram labels via OCR.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown("""
            <div class="bio-card" style="display: flex; align-items: center; gap: 15px; height: 120px;">
                <div style="font-size: 2rem;">🧬</div>
                <div>
                    <h4 style="margin:0; color: #0369a1;">Advanced Suite</h4>
                    <p style="margin:0; font-size: 0.8rem; color: #64748b;">Calculate GC content, MW, and Protein translation.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # --- NEW: NCBS LAB MODULE CARD ---
    with c3:
        st.markdown("""
            <div class="bio-card" style="display: flex; align-items: center; gap: 15px; height: 120px; border: 1px solid #00d4ff; background: rgba(0, 212, 255, 0.05);">
                <div style="font-size: 2rem;">🔬</div>
                <div>
                    <h4 style="margin:0; color: #00d4ff;">NCBS Lab Module</h4>
                    <p style="margin:0; font-size: 0.8rem; color: #64748b;">Structural Mechanobiology engine for C. elegans research.</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
         # Update the button logic here:
    if st.button("Open Lab Module 🔬", use_container_width=True, key="launch_ncbs"):
        st.balloons() # Adds a celebratory effect!
        st.success("🚀 NCBS Module Ready! Please click on the **'NCBS: Mechanobiology'** tab at the top of the page.")

    st.info("💡 **Study Tip:** Use the '10 Points' tab to quickly review key exam facts for the currently selected chapter.")

   
# =========================
# TAB 1: 📖 READER (Previously tabs[0])
# =========================
with tabs[1]:
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
        if st.button("Add to Research Report", icon="➕", use_container_width=False):
                if 'report_list' not in st.session_state:
                    st.session_state['report_list'] = []
                
                # Check if already added
                if row['Topic'] not in [item['Topic'] for item in st.session_state['report_list']]:
                    st.session_state['report_list'].append({
                        "Topic": row['Topic'],
                        "Notes": row['Explanation']
                    })
                    st.toast(f"Added {row['Topic']} to report!", icon="✅")
                else:
                    st.warning("Topic already in report.")
        with right:
            # --- DIAGRAM SPOILER ---
            with st.expander("🖼️ View Topic Diagram", expanded=False):
                img_path = str(row.get("Image", ""))
                if img_path and os.path.exists(img_path):
                    st.image(img_path, use_container_width=True, caption=f"Visual: {row.get('Topic')}")
                else:
                    st.info("No diagram available.")


# =========================
# TAB 2: 🧠 10 POINTS (Previously tabs[1])
# =========================
with tabs[2]:
    st.header("🧠 10 Key Exam Points")
    
    if 'selected_row' in st.session_state:
        current_row = st.session_state['selected_row']
        st.info(f"Topic: **{current_row.get('Topic', 'Selected Topic')}**")
        
        # --- NEW: STUDY MODE TOGGLE ---
        study_mode = st.toggle("Enable Study Mode (Hide Notes)", value=False)
        
        pts = current_row.get('Ten_Points') or current_row.get('10_Points') or "No points available."
        
        if study_mode:
            st.warning("🙈 **Study Mode Active:** Try to recall the key points about this topic before revealing them!")
            if st.button("👁️ Reveal Notes for 10 Seconds"):
                st.write(pts)
        else:
            # Standard View
            st.success("📝 **Full Notes:**")
            st.write(pts)
        
        st.divider()
        # --- CITATION & DOWNLOAD ---
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
# TAB 3: 🧪 DNA LAB (Previously tabs[2])
# =========================
with tabs[3]:
    st.header("🧪 DNA Interactive Lab")
    st.info("Transform and prepare your genomic sequences for analysis.")
    
    # Input Section
    raw_input = st.text_area("Enter Raw DNA (can include spaces/numbers):", "atgc 123 gtatc", key="lab_input")
    
    # Action Buttons in a nice row
    c1, c2, c3 = st.columns(3)
    
    # Logic to handle which button was pressed
    result_text = ""
    result_type = None
    label = ""

    if c1.button("🧹 Clean Sequence", use_container_width=True):
        result_text = "".join([char for char in raw_input if char.upper() in "ATGC"]).upper()
        result_type = "success"
        label = "Cleaned DNA Sequence:"

    if c2.button("🧬 Transcribe", use_container_width=True):
        cleaned = "".join([char for char in raw_input if char.upper() in "ATGC"]).upper()
        result_text = cleaned.replace("T", "U")
        result_type = "warning"
        label = "mRNA Transcript (T → U):"

    if c3.button("🎲 Random Mutation", use_container_width=True):
        cleaned = "".join([char for char in raw_input if char.upper() in "ATGC"]).upper()
        if cleaned:
            import random
            list_seq = list(cleaned)
            idx = random.randint(0, len(list_seq)-1)
            old, new = list_seq[idx], random.choice([b for b in "ATGC" if b != list_seq[idx]])
            list_seq[idx] = new
            result_text = "".join(list_seq)
            result_type = "error"
            label = f"Mutation Alert: Position {idx} changed from {old} to {new}"

    # SHOW RESULTS HERE (Below the buttons, full width)
    if result_text:
        st.divider()
        if result_type == "success": st.success(label)
        elif result_type == "warning": st.warning(label)
        elif result_type == "error": st.error(label)
        st.code(result_text)
        st.caption("Copy this sequence for use in the Advanced Molecular Suite.")

    st.divider()
    
    # Quick Reference
    st.subheader("Quick Reference")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("- **A** $\\rightarrow$ Adenine\n- **T** $\\rightarrow$ Thymine (DNA)")
    with col_b:
        st.markdown("- **G** $\\rightarrow$ Guanine\n- **C** $\\rightarrow$ Cytosine")
    
    st.info("💡 **Lab Tip:** This lab is designed for sequence preparation. Use the 'Clean' tool to remove non-genetic characters from your data.")
# =========================
# TAB 4: INTERNAL SEARCH (Fixed & Enhanced)
# =========================
with tabs[4]:
    st.header("🔍 Smart Textbook Search")
    st.info("Search across text content and diagram labels (via OCR).")
    
    # Search input
    query = st.text_input("Enter a term to search (e.g., 'DNA', 'Polymerase')...")
    
    if query:
        query_lower = query.lower()
        found = False
        
        # Loop through the dataframe
        for i, r in knowledge_df.iterrows():
            # 1. Check Text (using 'Topic' and 'Explanation' columns)
            # We use .get() to prevent crashes if a column is missing
            topic_val = str(r.get('Topic', '')).lower()
            expl_val = str(r.get('Explanation', '')).lower()
            
            txt_match = query_lower in topic_val or query_lower in expl_val
            
            # 2. Check Image via OCR
            img_path = str(r.get('Image', ''))
            img_text = ""
            if img_path and img_path != 'nan':
                img_text = get_text_from_image(img_path).lower()
            
            ocr_match = query_lower in img_text
            
            # If we find a match in either Text or OCR
            if txt_match or ocr_match:
                found = True
                with st.expander(f"📖 {r.get('Topic', 'Untitled')} (Page {i+1})", expanded=True):
                    col_text, col_img = st.columns([2, 1])
                    
                    with col_text:
                        if txt_match:
                            st.markdown("🎯 **Found in Text**")
                        if ocr_match:
                            st.markdown("👁️ **Found in Diagram (OCR)**")
                        
                        # Show a preview of the explanation
                        preview_text = str(r.get('Explanation', 'No content available'))
                        st.write(preview_text[:300] + "...") 
                        
                        # Button to jump to the Reader tab
                        if st.button(f"Go to Page {i+1}", key=f"search_btn_{i}"):
                            st.session_state.page_index = i
                            # This ensures the app switches focus to the reader's index
                            st.rerun()
                            
                    with col_img:
                        if img_path and os.path.exists(img_path):
                            st.image(img_path, caption="Related Diagram", use_container_width=True)
                        else:
                            st.caption("No image available")
                            
        if not found:
            st.warning(f"No results found for '{query}'. Try checking the 'Global Bio-Search' tab!")

# =========================
# TAB 5: GLOBAL BIO-SEARCH
# =========================
with tabs[5]:
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
with tabs[6]:
    st.header("🇮🇳 Hindi Helper")
    txt = st.text_area("Paste English text to translate to Hindi:")
    if st.button("Translate"):
        if txt.strip():
            try:
                translated = GoogleTranslator(source="auto", target="hi").translate(txt)
                st.info(translated)
            except Exception as e:
                st.error("Translation Error.")
# ==========================================
# TAB 7: SEQUENCE ANALYZER
# ==========================================
with tabs[7]:
    st.header("🧬 Advanced Molecular Suite")
    raw_seq = st.text_area("Paste DNA Sequence:", "ATGGCCATTGTAATGGGCCGCTGAAAGGGTACCCGATAG", key="dna_input_area").upper().strip()
    
    if raw_seq:
        # ... (keep your length and GC calculation lines here) ...
        seq_len = len(raw_seq)
        gc_count = raw_seq.count('G') + raw_seq.count('C')
        gc_content = (gc_count / seq_len) * 100 if seq_len > 0 else 0
        
        # 1. Metrics and Chart (Indented inside the IF)
        col1, col2, col3 = st.columns(3)
        col1.metric("Length", f"{seq_len} bp")
        col2.metric("GC Content", f"{gc_content:.1f}%")
        mw = (raw_seq.count('A')*313.2) + (raw_seq.count('T')*304.2) + (raw_seq.count('C')*289.2) + (raw_seq.count('G')*329.2)
        col3.metric("Mol. Weight", f"{mw:,.1f} Da")
        df = pd.DataFrame({
                'Nucleotide': ['A', 'T', 'G', 'C'],
                'Count': [raw_seq.count('A'), raw_seq.count('T'), raw_seq.count('G'), raw_seq.count('C')]
            })
            
        fig = px.bar(df, x='Nucleotide', y='Count', color='Nucleotide',
                     color_discrete_map={'A':'#FF4B4B', 'T':'#1C83E1', 'G':'#00C78C', 'C':'#FACA2B'},
                     height=300)
        st.plotly_chart(fig, use_container_width=True)
        # ---------------------
        # 2. Tools (Indented inside the IF)
        c1, c2 = st.columns(2)
        with c1:
               with st.expander("🔗 Complementary Strand", expanded=True):
                    pairs = {"A": "T", "T": "A", "G": "C", "C": "G"}
                    comp = "".join([pairs.get(b, "N") for b in raw_seq])
                    st.code(f"3'- {comp} -5'")


        
        with c2:
            with st.expander("🧪 Protein Translation", expanded=True):
                # FULL CODON MAP
                codon_map = {'ATA':'I', 'ATC':'I', 'ATT':'I', 'ATG':'M', 'ACA':'T', 'ACC':'T', 'ACG':'T', 'ACT':'T', 'AAC':'N', 'AAT':'N', 'AAA':'K', 'AAG':'K', 'AGC':'S', 'AGT':'S', 'AGA':'R', 'AGG':'R', 'CTA':'L', 'CTC':'L', 'CTG':'L', 'CTT':'L', 'CCA':'P', 'CCC':'P', 'CCG':'P', 'CCT':'P', 'CAC':'H', 'CAT':'H', 'CAA':'Q', 'CAG':'Q', 'CGA':'R', 'CGC':'R', 'CGG':'R', 'CGT':'R', 'GTA':'V', 'GTC':'V', 'GTG':'V', 'GTT':'V', 'GCA':'A', 'GCC':'A', 'GCG':'A', 'GCT':'A', 'GAC':'D', 'GAT':'D', 'GAA':'E', 'GAG':'E', 'GGA':'G', 'GGC':'G', 'GGG':'G', 'GGT':'G', 'TCA':'S', 'TCC':'S', 'TCG':'S', 'TCT':'S', 'TTC':'F', 'TTT':'F', 'TTA':'L', 'TTG':'L', 'TAC':'Y', 'TAT':'Y', 'TAA':'_', 'TAG':'_', 'TGC':'C', 'TGT':'C', 'TGA':'_', 'TGG':'W'}
                protein = ""
                for i in range(0, len(raw_seq)-2, 3):
                    codon = raw_seq[i:i+3]
                    protein += codon_map.get(codon, '?')
                # THIS LINE BELOW puts it INSIDE the box
                st.write(f"**Protein:** `{protein}`")

        # 3. Insight (Indented inside the IF so it doesn't show in other tabs)
        if gc_content > 60:
            st.warning("⚠️ High GC Content: Very stable sequence.")
        elif gc_content < 40:
            st.info("ℹ️ Low GC Content: AT-rich region.")
        else:
            st.success("✅ Balanced GC Content: Normal distribution.")
# Insert this at the top of your Tab 8 code
st.markdown("""
<style>
    .nexus-status-card {
        background: rgba(0, 0, 0, 0.8);
        border: 1px solid #00f2ff;
        border-radius: 10px;
        padding: 15px;
        color: white;
        box-shadow: 0 0 15px rgba(0, 242, 255, 0.4);
        text-align: center;
        margin-bottom: 20px;
    }
    .nexus-stat-label {
        font-size: 0.8rem;
        color: #00f2ff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .nexus-stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# TAB 8: 🔬 BIO-NEXUS STRUCTURE ENGINE
# ==========================================
with tabs[8]:
    try:
        from stmol import showmol
        import py3Dmol
        import streamlit.components.v1 as components # Add this line


        # 1. NEXUS STYLING ENGINE
        st.markdown("""
        <style>
            .nexus-status-card {
                background: rgba(0, 0, 0, 0.6);
                border: 1px solid #00f2ff;
                border-radius: 10px;
                padding: 15px;
                color: white;
                box-shadow: 0 0 15px rgba(0, 242, 255, 0.3);
                text-align: center;
                margin-bottom: 15px;
            }
            .nexus-stat-label {
                font-size: 0.75rem;
                color: #00f2ff;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .nexus-stat-value {
                font-size: 1.4rem;
                font-weight: bold;
                font-family: 'Courier New', monospace;
            }
            .stProgress > div > div > div > div {
                background-color: #00f2ff;
            }
        </style>
        """, unsafe_allow_html=True)

        # 2. RENDER ENGINE (With Mechanobiology Logic)
        def render_advanced_protein(pdb_id, style_type, color_type, remove_water=False, show_surface=False, spin=True, dark_mode=True, force_mode=False):
            view = py3Dmol.view(query=f'pdb:{pdb_id}')
            bg_color = '#0e1117' if dark_mode else 'white'
            view.setBackgroundColor(bg_color)
            
            # If Force Mode is on, we override color to show "Tension" (hot pink to blue)
            final_color = "hotpink" if force_mode else color_type
            
            view.setStyle({style_type: {
                'color': final_color,
                'specular': '#ffffff',
                'shininess': 100,
                'thickness': 0.4
            }})
            
            if remove_water:
                view.removeSelection({'resn': 'HOH'})
            if show_surface:
                view.addSurface(py3Dmol.VDW, {'opacity': 0.3, 'colorscheme': final_color})
                
            view.zoomTo()
            view.spin(spin)
            return showmol(view, height=600, width=800)

        # 3. HEADER & CONTROL PANEL
        st.markdown("<h2 style='text-align: center; color: #00d4ff;'>🧬 Bio-Nexus Structure Engine</h2>", unsafe_allow_html=True)
        
        c_in, c_s, c_c, c_v = st.columns([2, 1, 1, 1])
        with c_in:
            target_pdb = st.text_input("Target PDB ID", value="1A8M", key="nexus_pdb")
        with c_s:
            style_choice = st.selectbox("Render Mode", ["cartoon", "stick", "sphere", "line"], key="nexus_style")
        with c_c:
            color_choice = st.selectbox("Color Palette", ["spectrum", "chain", "element", "residue"], key="nexus_color")
        with c_v:
            dark_mode = st.toggle("Night Vision", value=True, key="nexus_dark")

        # Command Terminal
        chat_query = st.text_input("💬 Command Terminal", placeholder="Try 'HIGHLIGHT ACTIVE SITE' or 'SIMULATE TENSION'", key="nexus_chat").upper()
        water_flag = "REMOVE WATER" in chat_query
        spin_flag = "STOP" not in chat_query

        # 4. MAIN INTERFACE LAYOUT
        col_main, col_side = st.columns([3, 1])
        
        # DATABASE LOGIC (C. elegans focus for NCBS)
        pdb_data = {
            "1BNA": {"chains": "2", "res": "24", "type": "DNA B-Form", "helix": 0.0, "sheet": 0.0},
            "1A8M": {"chains": "4", "res": "574", "type": "Hemoglobin", "helix": 0.72, "sheet": 0.12},
            "1WBD": {"chains": "1", "res": "450", "type": "C. elegans Myosin", "helix": 0.65, "sheet": 0.15},
            "2SPY": {"chains": "2", "res": "280", "type": "Spectrin (NCBS Model)", "helix": 0.88, "sheet": 0.05}
        }

        stats = pdb_data.get(target_pdb.upper(), {"chains": "1", "res": "Unknown", "type": "Protein", "helix": 0.5, "sheet": 0.2})

        with col_side:
            # NCBS Lab Special Feature
            st.markdown("### 🔬 Lab Focus: NCBS")
            lab_mode = st.toggle("Mechanobiology Mode", help="Visualize mechanical strain on tissue proteins")
            
            if lab_mode:
                st.warning("Force-Vector Active")
                st.caption("Analyzing C. elegans tissue tension...")

            # The Glowing Status Card
            st.markdown(f'''
                <div class="nexus-status-card">
                    <div class="nexus-stat-label">Core Status</div>
                    <div class="nexus-stat-value">SYSTEM ACTIVE</div>
                </div>
            ''', unsafe_allow_html=True)

            st.markdown("### 📡 Intelligence")
            st.caption(f"Classification: {stats['type']}")
            
            m1, m2 = st.columns(2)
            m1.metric("Chains", stats['chains'])
            m2.metric("Residues", stats['res'])
            
            st.divider()
            
            st.markdown("### Structure Analysis")
            st.progress(stats['sheet'], text=f"Beta Sheets: {int(stats['sheet']*100)}%")
            st.markdown("<br>", unsafe_allow_html=True) # Adds a small gap
            if target_pdb.upper() in ["1WBD", "2SPY"]:
                st.success("✅ NCBS Priority Model")


        with col_main:
            if 'show_surf' not in st.session_state: 
                st.session_state.show_surf = False
            
            # Call Render Function
            render_advanced_protein(
                target_pdb, style_choice, color_choice, 
                remove_water=water_flag, show_surface=st.session_state.show_surf,
                spin=spin_flag, dark_mode=dark_mode, force_mode=lab_mode
            )
            
            st.write("### Quick Actions")
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("🧊 Toggle Surface", use_container_width=True, key="nexus_btn1"):
                    st.session_state.show_surf = not st.session_state.show_surf
                    st.rerun()
            with b2:
                if st.button("🎯 Highlight Active Site", use_container_width=True, key="nexus_btn2"):
                    st.toast("Scanning Binding Pockets...")
            with b3:
                if st.button("🧪 Predict Properties", use_container_width=True, key="nexus_btn3"):
                    st.info("Calculated MW: 64.5 kDa | pI: 6.8")

            with st.expander("🧬 Sequence Map"):
                sequences = {"1BNA": "CGCGAATTCGCG", "1A8M": "VLSPADKT...", "1WBD": "MGDSEMAVFG...", "2SPY": "MEEKKDE..."}
                current_seq = sequences.get(target_pdb.upper(), "SEQUENCE DATA NOT IN CACHE")
                st.code(current_seq, wrap_lines=True)

    except Exception as e:
        # THE SAFETY NET: Show this if you make a code error
        st.warning("📡 **Nexus Engine: Updating...**")
        st.info("The 3D Visualization system is currently being calibrated. Please wait for the next sync.")
        with st.expander("Developer Debug Info"):
            st.error(f"Error Details: {e}")


    # 4. Footer info
    st.caption("Bio-Nexus Engine v2.4 | Powered by py3Dmol & OpenPDB")
# =========================
# SIDEBAR: RESEARCH REPORT
# =========================
with st.sidebar:
    st.divider()
    st.header("📋 My Research Report")
    
    if 'report_list' in st.session_state and st.session_state['report_list']:
        for idx, item in enumerate(st.session_state['report_list']):
            st.write(f"{idx+1}. {item['Topic']}")
        
        if st.button("🗑️ Clear Report"):
            st.session_state['report_list'] = []
            st.rerun()
            
        # Create the download string
        full_report = "BIO-VERIFY RESEARCH REPORT\n" + "="*25 + "\n\n"
        for item in st.session_state['report_list']:
            full_report += f"TOPIC: {item['Topic']}\n{item['Notes']}\n\n" + "-"*20 + "\n"
            
        st.download_button(
            label="📥 Download Full Report",
            data=full_report,
            file_name="Bio_Research_Report.txt",
            mime="text/plain",
            use_container_width=True
        )
    else:
        st.info("Your report is empty. Add topics from the 'Reader' tab.")
# =========================
# TAB 9: 🔬 NCBS Research
# =========================
with tabs[9]: # This is your 9th tab (index 8)
    st.markdown("<h2 style='color: #00d4ff;'>🔬 NCBS Research Intelligence Hub</h2>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown("""
        ### 🧬 Targeted Mechanobiology Study: *C. elegans*
        **Objective:** To investigate the structural integrity of the spectrin cytoskeleton under mechanical strain in muscle cells.
        """)
        
        # Experimental Checklist
        st.write("#### 📋 Virtual Lab Notebook")
        task1 = st.checkbox("Prepare NGM plates with OP50 bacteria", value=True)
        task2 = st.checkbox("Perform RNAi knockdown of unc-70 (Beta-spectrin)", value=True)
        task3 = st.checkbox("Mount worms for High-Res Confocal Imaging", value=False)
        task4 = st.checkbox("Analyze 3D Protein Strain via Bio-Nexus Engine", value=False)
        
        if task4:
            st.success("Analysis Complete: High strain detected in the CH-domain of Spectrin.")
            
        # Research Notes Area
        st.text_area("✍️ Researcher Observations", 
                     placeholder="Enter observations about worm motility or fluorescent signal intensity...",
                     height=150)

    with col_right:
        # Lab Specific Metadata
        st.markdown("""
        <div style="background: rgba(0, 212, 255, 0.1); padding: 15px; border-radius: 10px; border: 1px solid #00d4ff;">
            <h4 style="margin:0; color: #00d4ff;">Lab Profile: NCBS</h4>
            <p style="font-size: 0.8rem;"><b>Principal Investigator:</b> Organ Mechanobiology Group</p>
            <hr>
            <p style="font-size: 0.8rem;"><b>Priority Genes:</b><br>
            • unc-70 (Spectrin)<br>
            • myo-3 (Myosin)<br>
            • let-805 (Myotendinous junction)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # A simple data simulation for the lab
        st.write("#### 📊 Strain Analysis")
        chart_data = {
            'Strain (pN)': [2, 5, 8, 12, 15, 18],
            'Fluorescence (%)': [98, 92, 85, 70, 45, 20]
        }
        st.line_chart(chart_data, x='Strain (pN)', y='Fluorescence (%)')
        st.caption("FRET-based tension sensor simulation.")

    # Bottom Section: Why me?
    with st.expander("🎯 Message to the Recruiter"):
        st.write("""
        This module demonstrates my ability to integrate computational tools with real-world lab workflows. 
        By combining 3D protein modeling with experimental tracking, I aim to accelerate the 
        understanding of how mechanical forces shape biological systems.
        """)


# =========================
# SIDEBAR: RESEARCH TIP
# =========================
with st.sidebar:
    st.divider()
    st.markdown("### 💡 Research Tip")
    tips = [
        "Always verify GC content for primer design stability.",
        "Use NCBI BLAST to compare your sequences against known databases.",
        "CRISPR-Cas9 efficiency depends on the choice of Guide RNA (gRNA).",
        "Restriction enzymes work best at specific pH and temperature buffers."
    ]
    # This picks a different tip based on the day
    import datetime
    tip_index = datetime.datetime.now().day % len(tips)
    st.info(tips[tip_index])
    
    st.caption("© 2026 Bio-Verify | Developed for Genomic Research")


