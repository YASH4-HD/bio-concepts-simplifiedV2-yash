import streamlit as st
import pandas as pd
import os
from googletrans import Translator

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- INITIALIZE TRANSLATOR ---
translator = Translator()

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

    # TABS
    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "📖 Reader", 
        "🔬 DNA Lab", 
        "🔍 Search", 
        "📊 Data Analysis",
        "🇮🇳 Hinglish Helper"
    ])

    # --- TAB 0: INTERACTIVE READER ---
    with tab0:
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        if col_prev.button("⬅️ Previous"):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1}</h3>", unsafe_allow_html=True)
        if col_next.button("Next ➡️"):
            if st.session_state.page_index < len(knowledge_df) - 1:
                st.session_state.page_index += 1
                st.rerun()
        
        st.divider()
        current_page = knowledge_df.iloc[st.session_state.page_index]
        t1, t2 = st.columns([2, 1])
        with t1:
            st.header(current_page.get('Topic', 'Untitled'))
            st.write(current_page.get('Explanation', ''))
        with t2:
            img = str(current_page.get('Image', ''))
            if img and os.path.exists(img):
                st.image(img, use_container_width=True)

    # --- TAB 1: DNA LAB ---
    with tab1:
        st.header("🔬 DNA Analysis")
        seq = st.text_area("Paste DNA Sequence:", "ATGC").upper().strip()
        if st.button("Analyze Sequence"):
            if seq:
                gc = (seq.count('G') + seq.count('C')) / len(seq) * 100
                st.metric("GC Content", f"{gc:.2f}%")
                st.write(f"Sequence Length: {len(seq)} bp")

    # --- TAB 2: SEARCH ENGINE ---
    with tab2:
        st.header("🔍 Search Textbook")
        query = st.text_input("Enter keyword (e.g. PCR):")
        if query:
            results = knowledge_df[knowledge_df['Explanation'].str.contains(query, case=False, na=False)]
            for i, row in results.iterrows():
                with st.expander(f"{row['Topic']} (Page {i+1})"):
                    st.write(row['Explanation'])
                    if st.button("Jump to this Page", key=f"jump_{i}"):
                        st.session_state.page_index = i
                        st.rerun()

    # --- TAB 3: DATA ANALYSIS ---
    with tab3:
        st.header("📊 Lab Data")
        up = st.file_uploader("Upload CSV", type="csv")
        if up:
            st.dataframe(pd.read_csv(up))

    # --- TAB 4: FREE HINGLISH HELPER ---
    with tab4:
        st.header("🇮🇳 Hinglish Concept Explainer")
        st.write("English text ko Hindi/Hinglish mein samajhne ke liye niche paste karein.")
        
        to_translate = st.text_area("Paste English sentence here:", height=150)
        
        if st.button("Translate to Hindi/Hinglish"):
            if to_translate:
                with st.spinner("Translating..."):
                    try:
                        # Translate to Hindi
                        translated = translator.translate(to_translate, src='en', dest='hi')
                        
                        st.subheader("Hindi Translation:")
                        st.success(translated.text)
                        
                        st.subheader("Hinglish Explanation Style:")
                        st.info(f"Iska simple matlab hai: {translated.text} \n\n (Note: This is a direct translation. For complex bio-terms, keep the English names same.)")
                    except Exception as e:
                        st.error("Translation error. Please try again in a moment.")
            else:
                st.warning("Please enter text first.")

else:
    st.error("CSV File not found. Please ensure 'knowledge.csv' is in your GitHub folder.")
