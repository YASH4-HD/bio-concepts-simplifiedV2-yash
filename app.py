import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator
import easyocr
import cv2
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- INITIALIZE OCR (Cache it so it only loads once) ---
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])

reader = load_ocr()

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
            except: continue
    return None

knowledge_df = load_knowledge_base()

# --- SESSION STATE ---
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# --- APP LOGIC ---
if knowledge_df is not None:
    tabs = st.tabs(["📖 Reader", "🔬 DNA Lab", "🔍 Smart Search", "📊 Data", "🇮🇳 Hinglish"])

    # --- TAB 0: READER ---
    with tabs[0]:
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
            img_path = str(current_page.get('Image', ''))
            if img_path and os.path.exists(img_path):
                st.image(img_path, use_container_width=True)

    # --- TAB 2: SMART SEARCH (WITH IMAGE OCR) ---
    with tabs[2]:
        st.header("🔍 AI Search (Text + Images)")
        query = st.text_input("Search for any word (even inside diagrams):")
        
        if query:
            with st.spinner("AI is scanning text and images..."):
                # 1. Search in CSV Text
                text_matches = knowledge_df[
                    knowledge_df['Topic'].str.contains(query, case=False, na=False) | 
                    knowledge_df['Explanation'].str.contains(query, case=False, na=False)
                ].index.tolist()

                # 2. Search in Images using OCR
                image_matches = []
                # To save time, we only scan images mentioned in the CSV
                for idx, row in knowledge_df.iterrows():
                    img_file = str(row.get('Image', ''))
                    if img_file and os.path.exists(img_file):
                        # Perform OCR on the image
                        results = reader.readtext(img_file, detail=0)
                        # Check if query exists in the list of words found in image
                        if any(query.lower() in word.lower() for word in results):
                            if idx not in text_matches:
                                image_matches.append(idx)

                # Combine results
                all_indices = list(set(text_matches + image_matches))

                if all_indices:
                    st.success(f"Found {len(all_indices)} matches!")
                    for i in all_indices:
                        row = knowledge_df.iloc[i]
                        with st.expander(f"📖 {row['Topic']} (Page {i+1})"):
                            if i in image_matches:
                                st.info("📍 Found this word inside the diagram/image on this page!")
                            st.write(row['Explanation'][:200] + "...")
                            if st.button(f"Go to Page {i+1}", key=f"search_{i}"):
                                st.session_state.page_index = i
                                st.rerun()
                else:
                    st.warning("No matches found in text or diagrams.")

    # --- TAB 4: HINGLISH ---
    with tabs[4]:
        st.header("🇮🇳 Hinglish Helper")
        to_translate = st.text_area("Paste complex bio-sentence:")
        if st.button("Translate"):
            if to_translate:
                res = GoogleTranslator(source='auto', target='hi').translate(to_translate)
                st.success(res)

else:
    st.error("CSV File not found.")
