import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { border-radius: 10px; height: 3em; font-weight: bold; }
    .page-info { text-align: center; font-size: 1.2rem; font-weight: bold; color: #007bff; }
    .content-box { 
        padding: 25px; 
        background: white; 
        border-radius: 15px; 
        border: 1px solid #e0e0e0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATA LOADING LOGIC ---
@st.cache_data
def load_knowledge_base():
    file_name = 'knowledge_base.csv'
    if os.path.exists(file_name):
        try:
            df = pd.read_csv(file_name)
            # Clean column names (removes hidden spaces)
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
            return None
    return None

# Load the data
knowledge_df = load_knowledge_base()

# --- APP LOGIC ---
if knowledge_df is not None:
    # Initialize Page Index in Session State
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    # Tabs for the PhD App
    tab0, tab1, tab2, tab3 = st.tabs(["📖 Interactive Reader", "🔬 DNA Lab Tools", "🤖 AI Assistant", "📊 Data Analysis"])

    # --- TAB 0: INTERACTIVE READER (OPTION 1) ---
    with tab0:
        st.title("Wilson & Walker: Smart Textbook")
        
        # Reader Navigation Bar
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        
        if col_prev.button("⬅️ Previous Page"):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()

        with col_page:
            st.markdown(f"<p class='page-info'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</p>", unsafe_allow_html=True)

        if col_next.button("Next Page ➡️"):
            if st.session_state.page_index < len(knowledge_df) - 1:
                st.session_state.page_index += 1
                st.rerun()

        st.divider()

        # Display Content
        current_page = knowledge_df.iloc[st.session_state.page_index]
        
        col_text, col_img = st.columns([3, 2])

        with col_text:
            st.markdown(f"### Section {current_page.get('Section', 'N/A')}")
            st.header(current_page.get('Topic', 'Untitled Topic'))
            
            st.markdown("<div class='content-box'>", unsafe_allow_html=True)
            st.write(current_page.get('Explanation', 'No explanation available.'))
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.info(f"💡 **PhD Tip:** Use the 'DNA Lab Tools' tab to experiment with sequences related to {current_page.get('Topic')}.")

        with col_img:
            img_path = str(current_page.get('Image', ''))
            if img_path and os.path.exists(img_path):
                st.image(img_path, caption=f"Figure: {current_page.get('Topic')}", use_container_width=True)
            else:
                st.warning("📸 Image placeholder: Add image path to CSV to display diagrams here.")

    # --- TAB 1: DNA LAB TOOLS ---
    with tab1:
        st.header("🔬 DNA Sequence Analysis")
        seq = st.text_area("Paste DNA Sequence here:", "ATGCATGCATGC", height=150)
        if st.button("Analyze Sequence"):
            gc_content = (seq.upper().count('G') + seq.upper().count('C')) / len(seq) * 100
            st.success(f"GC Content of {current_page['Topic']}: {gc_content:.2f}%")

    # --- TAB 2: AI ASSISTANT ---
    with tab2:
        st.header("🤖 Research Assistant")
        st.write(f"Currently focused on: **{current_page['Topic']}**")
        user_q = st.text_input("Ask a question about this section:")
        if user_q:
            st.write("Generating answer based on Wilson & Walker principles...")

    # --- TAB 3: DATA ANALYSIS ---
    with tab3:
        st.header("📊 Experimental Data")
        uploaded = st.file_uploader("Upload CSV Lab Results", type="csv")
        if uploaded:
            df_lab = pd.read_csv(uploaded)
            st.line_chart(df_lab)

else:
    # --- ERROR STATE: If CSV is missing ---
    st.error("⚠️ 'knowledge_base.csv' not found!")
    st.info("Please ensure your CSV file is in the same folder as this script.")
    st.markdown("""
    **Your CSV should look like this:**
    | Section | Topic | Explanation | Image |
    | :--- | :--- | :--- | :--- |
    | 1.1 | DNA Structure | Full text here... | dna.jpg |
    """)
