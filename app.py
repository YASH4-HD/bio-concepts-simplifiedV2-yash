import streamlit as st
import pandas as pd
import os

# --- UPDATED DATA LOADING LOGIC ---
@st.cache_data
def load_knowledge_base():
    # Get the directory where app.py is located
    base_path = os.path.dirname(__file__)
    
    # Try both possible filenames
    file_options = ['knowledge_base.csv', 'knowledge.csv']
    
    for file_name in file_options:
        full_path = os.path.join(base_path, file_name)
        if os.path.exists(full_path):
            try:
                # Use 'latin1' or 'utf-8' encoding to avoid common CSV errors
                df = pd.read_csv(full_path, encoding='utf-8')
                df.columns = df.columns.str.strip() # Clean column names
                return df
            except Exception as e:
                # If utf-8 fails, try latin1
                try:
                    df = pd.read_csv(full_path, encoding='latin1')
                    df.columns = df.columns.str.strip()
                    return df
                except:
                    st.error(f"Error reading {file_name}: {e}")
    
    return None

# --- THE REST OF THE CODE REMAINS THE SAME ---
knowledge_df = load_knowledge_base()

if knowledge_df is not None:
    # Initialize Page Index
    if 'page_index' not in st.session_state:
        st.session_state.page_index = 0

    tab0, tab1, tab2, tab3 = st.tabs(["📖 Interactive Reader", "🔬 DNA Lab Tools", "🤖 AI Assistant", "📊 Data Analysis"])

    with tab0:
    st.title("Wilson & Walker: Smart Textbook")
    
    # Navigation Row
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    if col_prev.button("⬅️ Previous Page"):
        if st.session_state.page_index > 0:
            st.session_state.page_index -= 1
            st.rerun()

    with col_page:
        st.markdown(f"<p style='text-align:center; font-weight:bold;'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</p>", unsafe_allow_html=True)

    if col_next.button("Next Page ➡️"):
        if st.session_state.page_index < len(knowledge_df) - 1:
            st.session_state.page_index += 1
            st.rerun()

    st.divider()

    # --- CONTENT AREA ---
    current_page = knowledge_df.iloc[st.session_state.page_index]
    
    # We use a 2:1 ratio (Text:Image) to keep the image smaller on the side
    col_text, col_img = st.columns([2, 1])

    with col_text:
        st.header(current_page.get('Topic', 'No Topic'))
        st.write(current_page.get('Explanation', 'No content available.'))
        
    with col_img:
        img_path = str(current_page.get('Image', ''))
        if img_path and os.path.exists(img_path):
            # 1. We wrap the image in a container
            # 2. use_container_width=True makes it fit the narrow column
            # 3. Streamlit automatically adds a "Zoom/Full Screen" button on hover
            st.image(img_path, caption="Click top-right to zoom", use_container_width=True)
        else:
            st.info("ℹ️ No diagram for this section.")

        
        with col_page:
            st.markdown(f"<h3 style='text-align:center;'>Page {st.session_state.page_index + 1} of {len(knowledge_df)}</h3>", unsafe_allow_html=True)
            
        if col_next.button("Next Page ➡️"):
            if st.session_state.page_index < len(knowledge_df) - 1:
                st.session_state.page_index += 1
                st.rerun()

        st.divider()
        
        # Display Current Page
        current_page = knowledge_df.iloc[st.session_state.page_index]
        col_text, col_img = st.columns([3, 2])
        
        with col_text:
            st.header(current_page.get('Topic', 'No Topic Found'))
            st.write(current_page.get('Explanation', 'No Explanation Found'))
            
        with col_img:
            img_file = str(current_page.get('Image', ''))
            if img_file and os.path.exists(os.path.join(os.path.dirname(__file__), img_file)):
                st.image(img_file, use_container_width=True)
            else:
                st.info("Diagram will appear here")
else:
    st.error("⚠️ CSV File not detected by the system.")
    st.write("Current Directory Files:", os.listdir(os.path.dirname(__file__))) # This helps us debug
