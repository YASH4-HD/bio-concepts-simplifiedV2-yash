import streamlit as st
import pandas as pd
import os
from deep_translator import GoogleTranslator
import easyocr
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Bio-Tech Smart Textbook", layout="wide")

# --- INITIALIZE OCR ---
@st.cache_resource
def load_ocr():
    # Loading English reader
    return easyocr.Reader(['en'])

reader = load_ocr()

# --- OPTIMIZED OCR CACHING ---
@st.cache_data
def get_text_from_image(img_path):
    """Reads image once and stores text in cache to prevent lag."""
    if img_path and os.path.exists(img_path):
        try:
            results = reader.readtext(img_path, detail=0)
            return " ".join(results).lower()
        except Exception:
            return ""
    return ""

# --- DATA LOADING ---
@st.cache_data
def load_knowledge_base():
    base_path = os.path.dirname(__file__)
    # Checking for both possible filenames
    for file_name in ['knowledge.csv', 'knowledge_base.csv']:
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            try:
                df = pd.read_csv(full_path, encoding='utf-8')
                df.columns = df.columns.str.strip()
                return df
            except Exception:
                continue
    return None

knowledge_df = load_knowledge_base()

# --- INITIALIZE SESSION STATES ---
if 'page_index' not in st.session_state:
    st.session_state.page_index = 0

# --- APP LOGIC ---
if knowledge_df is not None:
    
    tab_list = ["📖 Reader", "🔬 DNA Lab", "🔍 Search", "📊 Data Analysis", "🇮🇳 Hinglish Helper"]
    tabs = st.tabs(tab_list)

    # --- TAB 0: READER ---
    with tabs[0]:
        col_prev, col_page, col_next = st.columns([1, 2, 1])
        if col_prev.button("⬅️ Previous"):
            if st.session_state.page_index > 0:
                st.session_state.page_index -= 1
                st.rerun()
        with col_page:
            st.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</h3>", unsafe_allow_html=True)
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
            else:
                st.info("No diagram for this section.")

    # --- TAB 1: DNA LAB ---
    with tabs[1]:
        st.header("🔬 DNA Analysis")
        seq = st.text_area("Paste DNA Sequence:", "ATGC").upper().strip()
        if st.button("Analyze Sequence"):
            if seq:
                gc = (seq.count('G') + seq.count('C')) / len(seq) * 100
                st.metric("GC Content", f"{gc:.2f}%")

    # --- TAB 2: SMART SEARCH (TEXT + OCR) ---
    with tabs[2]:
        st.header("🔍 AI Search (Text + Images)")
        query = st.text_input("Search for any word (e.g. 'Ligase', 'Vector'):").lower().strip()
        
        if query:
            with st.spinner("Searching through text and diagrams..."):
                all_indices = []
                image_matches = []

                for idx, row in knowledge_df.iterrows():
                    # 1. Search in CSV Text
                    topic = str(row.get('Topic', '')).lower()
                    expl = str(row.get('Explanation', '')).lower()
                    
                    if query in topic or query in expl:
                        all_indices.append(idx)
                    else:
                        # 2. Search in Image Text (Cached OCR)
                        img_file = str(row.get('Image', ''))
                        img_text = get_text_from_image(img_file)
                        if query in img_text:
                            all_indices.append(idx)
                            image_matches.append(idx)

                all_indices = sorted(list(set(all_indices)))

                if all_indices:
                    st.success(f"Found {len(all_indices)} matches!")
                    for i in all_indices:
                        row = knowledge_df.iloc[i]
                        with st.expander(f"📖 {row['Topic']} (Page {i+1})"):
                            if i in image_matches:
                                st.info("📍 Word found inside a diagram/table on this page.")
                            st.write(row['Explanation'][:200] + "...")
                            
                            # Unique key for each button to prevent errors
                            if st.button(f"Go to Page {i+1}", key=f"jump_search_{i}"):
                                st.session_state.page_index = i
                                st.rerun()
                else:
                    st.warning("No matches found.")

    # --- TAB 3: DATA ANALYSIS ---
    with tabs[3]:
        st.header("📊 Lab Data")
        up = st.file_uploader("Upload CSV", type="csv")
        if up:
            st.dataframe(pd.read_csv(up))

    # --- TAB 4: HINDI & HINGLISH HELPER ---
    with tabs[4]:
        st.header("🇮🇳 Language Support Center")
        st.write("Convert complex Biotech English into Pure Hindi and Romanized Hinglish.")
        
        to_translate = st.text_area("Paste English text here:", height=100)
        
        if st.button("Translate & Explain"):
            if to_translate:
                with st.spinner("Processing..."):
                    # 1. Get Pure Hindi (Devanagari)
                    hindi_text = GoogleTranslator(source='auto', target='hi').translate(to_translate)
                    
                    # 2. Convert Devanagari to Roman Script (Hinglish)
                    # Using ITRANS for transliteration
                    hinglish_roman = transliterate(hindi_text, sanscript.DEVANAGARI, sanscript.ITRANS)
                    
                    # Clean up the Romanization to make it look like WhatsApp chat
                    hinglish_roman = (hinglish_roman.lower()
                                      .replace('shha', 'sh')
                                      .replace('aa', 'a')
                                      .replace('. ', ' ')
                                      .replace('..', '.')
                                      .replace('  ', ' '))

                    # Display Results
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("📝 Pure Hindi (शुद्ध हिंदी)")
                        st.markdown(f"<div style='background-color:#f0f2f6; padding:15px; border-radius:10px;'>{hindi_text}</div>", unsafe_allow_html=True)
                    
                    with col2:
                        st.subheader("🗣️ Smart Hinglish (Roman Script)")
                        st.markdown(f"<div style='background-color:#e1f5fe; padding:15px; border-radius:10px; color:#01579b;'>{hinglish_roman}</div>", unsafe_allow_html=True)

                    # 3. Scientific Vocabulary Definitions
                    st.divider()
                    st.subheader("🔬 Key Biotech Terms in this context:")
                    term_definitions = {
                        "enzyme": "**Enzyme:** Biological catalysts jo reactions ko fast karte hain.",
                        "dna": "**DNA:** Deoxyribonucleic acid, jo genetic information carry karta hai.",
                        "restriction": "**Restriction Enzymes:** DNA ko specific location pe cut karne wali 'molecular scissors'.",
                        "palindromic": "**Palindromic:** Woh sequence jo aage aur peeche se same read ho (e.g., MADAM).",
                        "ligase": "**Ligase:** DNA fragments ko jodne wala 'molecular glue'."
                    }
                    
                    found_any = False
                    for term, definition in term_definitions.items():
                        if term in to_translate.lower():
                            st.info(definition)
                            found_any = True
                    if not found_any:
                        st.caption("No specific biotech terms detected for breakdown.")
            else:
                st.warning("Please enter text first.")

else:
    st.error("Knowledge base (CSV) not found. Please check your file path.")
