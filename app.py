import streamlit as st
import pandas as pd
import os
# ... (keep other imports)

# --- AUTO-LOAD KNOWLEDGE BASE ---
@st.cache_data # This makes the app load the file once and remember it
def load_data():
    file_path = "knowledge.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

# Load the data automatically
knowledge_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("📚 Book Navigator")
    
    if knowledge_df is not None:
        st.success("✅ Textbook Data Loaded")
        selected_topic = st.selectbox("Select a Topic:", knowledge_df["Topic"].unique())
        topic_info = knowledge_df[knowledge_df["Topic"] == selected_topic].iloc[0]
        
        st.divider()
        st.markdown(f"### Section {topic_info['Section']}")
        # Show image preview if exists
        if "Image" in topic_info and pd.notna(topic_info['Image']):
            if os.path.exists(str(topic_info['Image'])):
                st.image(str(topic_info['Image']))
    else:
        st.error("❌ knowledge.csv not found!")
        st.write("Ensure 'knowledge.csv' is uploaded to your GitHub repository.")

# --- MAIN DASHBOARD (Tab 0) ---
with tab0:
    if knowledge_df is not None:
        st.header(selected_topic)
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader(f"Section {topic_info['Section']}")
            st.write(topic_info['Explanation'])
        with col2:
            if "Image" in topic_info and pd.notna(topic_info['Image']):
                if os.path.exists(str(topic_info['Image'])):
                    st.image(str(topic_info['Image']), use_container_width=True)
    else:
        st.header("Welcome")
        st.write("System is currently offline. Please contact the administrator.")
