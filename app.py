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
    for file_name in ['knowledge.csv', 'knowledge_base.csv']:
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            try:
                df = pd.read_csv(full_path, encoding='utf-8')
                df.columns = df.columns.str.strip()
                return df
            except:
                try:
                    df = pd.read_csv(full_path, encoding='latin1')
                    df.columns = df.columns.str.strip()
                    return df
                except:
                    continue
    return None

knowledge_df = load_knowledge_base()

# --- APP LOGIC ---
if knowledge_df is not None:
    # Initialize Page Index
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    # Main Tabs
    tab0, tab1, tab2, tab3 = st.tabs(["📖 Interactive Reader", "🔬 DNA Lab Tools", "🔍 Search Knowledge", "📊 Data Analysis"])

    # --- TAB 0: INTERACTIVE READER ---
    with tab0:
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
                st.markdown("🔍 *Click image top-right to zoom*")
                st.image(img_path, use_container_width=True)
            else:
                st.info("💡 No diagram for this section.")

    # --- TAB 1: DNA LAB TOOLS ---
    with tab1:
        st.header("🔬 DNA Analysis Tools")
        st.info(f"Context: Analyzing sequences related to **{current_page['Topic']}**")
        dna_input = st.text_area("Sequence Input:", "ATGCATGCATGC", height=100)
        if st.button("Calculate GC %"):
            dna_clean = dna_input.strip().upper()
            if len(dna_clean) > 0:
                gc = (dna_clean.count('G') + dna_clean.count('C')) / len(dna_clean) * 100
                st.metric("GC Content", f"{gc:.2f}%")
            else:
                st.error("Please enter a valid sequence.")

    # --- TAB 2: KNOWLEDGE SEARCH (Local Search) ---
    with tab2:
        st.header("🔍 Wilson & Walker Search")
        query = st.text_input("Search for keywords (e.g., 'DNA', 'PCR', 'Enzyme'):")
        
        if query:
            results = knowledge_df[
                knowledge_df['Topic'].str.contains(query, case=False, na=False) | 
                knowledge_df['Explanation'].str.contains(query, case=False, na=False)
            ]
            
            if not results.empty:
                st.success(f"Found {len(results)} results:")
                for i, row in results.iterrows():
                    with st.expander(f"📖 {row['Topic']} (Section {row['Section']})"):
                        st.write(row['Explanation'])
                        if st.button(f"Go to Page {i+1}", key=f"search_{i}"):
                            st.session_state.page_index = i
                            st.rerun()
            else:
                st.warning(f"No results found for '{query}'.")

    # --- TAB 3: DATA ANALYSIS ---
    with tab3:
        st.header("📊 Lab Data Analysis")
        uploaded = st.file_uploader("Upload CSV Results", type="csv")
        if uploaded:
            lab_data = pd.read_csv(uploaded)
            st.dataframe(lab_data)
            st.line_chart(lab_data.select_dtypes(include=['number']))

else:
    st.error("❌ Could not load 'knowledge.csv'. Check file name and location.")
    st.write("Current folder contains:", os.listdir(os.path.dirname(__file__)))
