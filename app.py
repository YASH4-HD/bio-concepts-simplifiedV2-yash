import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- CUSTOM CSS FOR CLEANER LOOK ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .page-indicator { 
        text-align: center; 
        background-color: #f0f2f6; 
        padding: 10px; 
        border-radius: 10px; 
        font-weight: bold; 
    }
    .content-area { 
        font-size: 1.1rem; 
        line-height: 1.6; 
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ROBUST DATA LOADING ---
@st.cache_data
def load_knowledge_base():
    base_path = os.path.dirname(__file__)
    # Checks for both common filenames
    for file_name in ['knowledge.csv', 'knowledge_base.csv']:
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            try:
                # Try reading with common encodings
                df = pd.read_csv(full_path, encoding='utf-8')
                df.columns = df.columns.str.strip()
                return df
            except:
                df = pd.read_csv(full_path, encoding='latin1')
                df.columns = df.columns.str.strip()
                return df
    return None

knowledge_df = load_knowledge_base()

# --- APP LOGIC ---
if knowledge_df is not None:
    # Initialize Page Index
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    # Main Tabs
    tab0, tab1, tab2, tab3 = st.tabs(["📖 Interactive Reader", "🔬 DNA Lab Tools", "🤖 AI Assistant", "📊 Data Analysis"])

    # --- TAB 0: INTERACTIVE READER ---
    with tab0:
        # Navigation Header
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        if col_prev.button("⬅️ Previous Page"):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()

        with col_page:
            st.markdown(f"<div class='page-indicator'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</div>", unsafe_allow_html=True)

        if col_next.button("Next Page ➡️"):
            if st.session_state.page_index < len(knowledge_df) - 1:
                st.session_state.page_index += 1
                st.rerun()

        st.divider()

        # Content Layout: Text (2.5) and Image (1)
        # This prevents images from being too large while allowing zoom
        current_page = knowledge_df.iloc[st.session_state.page_index]
        col_text, col_img = st.columns([2.5, 1])

        with col_text:
            st.caption(f"Section {current_page.get('Section', 'N/A')}")
            st.header(current_page.get('Topic', 'Untitled Topic'))
            st.markdown("<div class='content-area'>", unsafe_allow_html=True)
            st.write(current_page.get('Explanation', 'No content available.'))
            st.markdown("</div>", unsafe_allow_html=True)

        with col_img:
            img_name = str(current_page.get('Image', ''))
            img_path = os.path.join(os.path.dirname(__file__), img_name)
            
            if img_name and os.path.exists(img_path):
                st.markdown("🔍 *Click image to zoom*")
                st.image(img_path, use_container_width=True)
            else:
                # Placeholder for sections without images
                st.info("💡 No diagram for this section. Focus on the text and lab tools.")

    # --- TAB 1: DNA LAB TOOLS ---
    with tab1:
        st.header("🔬 DNA Analysis Tools")
        st.info(f"Context: Analyzing sequences related to **{current_page['Topic']}**")
        dna_input = st.text_area("Sequence Input:", "ATGCATGCATGC", height=100)
        if st.button("Calculate GC %"):
            gc = (dna_input.upper().count('G') + dna_input.upper().count('C')) / len(dna_input) * 100
            st.metric("GC Content", f"{gc:.2f}%")

    # --- TAB 2: AI ASSISTANT ---
    with tab2:
        st.header("🤖 Research Assistant")
        st.write(f"Ask a question about: **{current_page['Topic']}**")
        st.text_input("How can I help you today?")

    # --- TAB 3: DATA ANALYSIS ---
    with tab3:
        st.header("📊 Lab Data")
        uploaded = st.file_uploader("Upload Experimental Results", type="csv")
        if uploaded:
            st.line_chart(pd.read_csv(uploaded))

else:
    # Error handling if CSV is missing
    st.error("❌ Could not load 'knowledge.csv'.")
    st.write("Files found in directory:", os.listdir(os.path.dirname(__file__)))
    st.info("Please ensure your CSV is named 'knowledge.csv' and is in the same folder as app.py")
