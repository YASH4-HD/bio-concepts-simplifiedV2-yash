import streamlit as st
import pandas as pd
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- DATA LOADING ---
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
                continue
    return None

knowledge_df = load_knowledge_base()

# --- APP LOGIC ---
if knowledge_df is not None:
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Interactive Reader", 
        "🔬 DNA Lab Tools", 
        "🔍 Search", 
        "📊 Data Analysis",
        "🇮🇳 Hinglish Helper"
    ])

    # --- TAB 0: READER ---
    with tab0:
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        if col_prev.button("⬅️ Previous"):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<center>Page {st.session_state.page_index + 1}</center>", unsafe_allow_html=True)
        if col_next.button("Next ➡️"):
            if st.session_state.page_index < len(knowledge_df) - 1:
                st.session_state.page_index += 1
                st.rerun()
        
        current_page = knowledge_df.iloc[st.session_state.page_index]
        st.header(current_page.get('Topic', 'Untitled'))
        st.write(current_page.get('Explanation', ''))

    # --- TAB 1: LAB ---
    with tab1:
        st.header("🔬 DNA Analysis")
        dna_input = st.text_area("Sequence:", "ATGC")
        if st.button("Analyze"):
            st.write(f"Length: {len(dna_input)}")

    # --- TAB 2: SEARCH ---
    with tab2:
        st.header("🔍 Search Textbook")
        q = st.text_input("Find keyword:")
        if q:
            res = knowledge_df[knowledge_df['Explanation'].str.contains(q, case=False, na=False)]
            st.write(res[['Section', 'Topic']])

    # --- TAB 3: DATA ---
    with tab3:
        st.header("📊 Data Analysis")
        st.info("Upload your lab results here.")

    # --- TAB 4: HINGLISH ---
    with tab4:
        st.header("🇮🇳 Hinglish Helper")
        text_to_exp = st.text_area("Paste complex sentence:")
        if st.button("Explain"):
            st.write("Iska basic matlab yeh hai ki...")
            st.write(text_to_exp)

else:
    st.error("CSV File Missing. Please upload knowledge.csv to GitHub.")
