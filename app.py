import streamlit as st
import pandas as pd
from Bio.Seq import Seq
from Bio.Restriction import Analysis, AllEnzymes
import io
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wilson Walker Digital Lab",
    page_icon="🧬",
    layout="wide"
)

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #fcfcfc; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #f0f2f6; 
        border-radius: 5px; 
    }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: DYNAMIC BOOK NAVIGATOR ---
with st.sidebar:
    st.title("📚 Book Navigator")
    st.write("Upload your textbook data (CSV) and images to the project folder.")
    
    uploaded_knowledge = st.file_uploader("Upload knowledge.csv", type="csv")
    
    knowledge_loaded = False
    if uploaded_knowledge is not None:
        try:
            # Load CSV
            knowledge_df = pd.read_csv(uploaded_knowledge)
            knowledge_loaded = True
            
            # Topic Selection
            st.success("✅ Knowledge Base Active")
            selected_topic = st.selectbox("Jump to Topic:", knowledge_df["Topic"].unique())
            
            # Get data for selected topic
            topic_info = knowledge_df[knowledge_df["Topic"] == selected_topic].iloc[0]
            
            st.divider()
            st.markdown(f"### Section {topic_info['Section']}")
            
            # Show Image in Sidebar (Small Preview)
            if "Image" in topic_info and pd.notna(topic_info['Image']):
                img_path = topic_info['Image']
                if os.path.exists(img_path):
                    st.image(img_path, caption="Figure Preview")
                else:
                    st.caption(f"(Image '{img_path}' not found in folder)")
                    
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Check your CSV for commas inside text. Use double quotes!")
    else:
        st.warning("👈 Please upload 'knowledge.csv' to begin.")

# --- MAIN INTERFACE ---
st.title("🔬 Wilson & Walker: Interactive Molecular Lab")

# Create 4 Tabs
tab0, tab1, tab2, tab3 = st.tabs(["🏠 Home Dashboard", "🧬 Sequence Analyzer", "📦 Vector Selector", "🧪 PCR Optimizer"])

# --- TAB 0: HOME DASHBOARD (Where Diagrams and Text show up) ---
with tab0:
    if knowledge_loaded:
        st.header(selected_topic)
        
        # Create two columns: Left for Text, Right for Diagram
        col_text, col_diag = st.columns([1, 1])
        
        with col_text:
            st.subheader(f"Textbook Context: Section {topic_info['Section']}")
            st.write(topic_info['Explanation'])
            st.info("💡 Tip: You can change the topic in the sidebar to update this view.")
            
        with col_diag:
            if "Image" in topic_info and pd.notna(topic_info['Image']):
                img_path = topic_info['Image']
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True, caption=f"Diagram: {selected_topic}")
                else:
                    st.warning(f"Diagram file '{img_path}' is missing from the project folder.")
                    st.write("To fix this, ensure the image file is in the same folder as app.py")
            else:
                st.info("No diagram associated with this topic.")
    else:
        st.header("Welcome to the Digital Lab")
        st.markdown("""
        This application is an interactive companion to **Recombinant DNA Technology** chapters.
        
        **To get started:**
        1. Prepare a `knowledge.csv` file with columns: `Topic, Section, Explanation, Image`.
        2. Upload it using the sidebar.
        3. Navigate through the tabs to use molecular tools.
        """)
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/DNA_Double_Helix.png/400px-DNA_Double_Helix.png")

# --- TAB 1: SEQUENCE ANALYZER ---
with tab1:
    st.header("Restriction Mapping Tool")
    dna_file = st.file_uploader("Upload DNA Sequence (.txt or .fasta)", type=["txt", "fasta"])
    
    if dna_file:
        content = dna_file.getvalue().decode("utf-8")
        lines = content.splitlines()
        # Clean FASTA or TXT
        raw_seq = "".join(lines[1:]) if lines[0].startswith(">") else "".join(lines)
        clean_seq = "".join(raw_seq.split()).upper()
        
        if st.button("Analyze Sequence"):
            my_seq = Seq(clean_seq)
            analysis = Analysis(AllEnzymes, my_seq)
            results = analysis.full()
            
            st.metric("Sequence Length", f"{len(my_seq)} bp")
            
            cols = st.columns(2)
            for i, (enz, sites) in enumerate(results.items()):
                if sites:
                    with cols[i % 2].expander(f"Enzyme: {enz}"):
                        st.write(f"Cut positions: {sites}")
                        st.code(f"Cut at: {sites[0]}")

# --- TAB 2: VECTOR SELECTOR ---
with tab2:
    st.header("Vector Selection (Table 4.4)")
    kb_size = st.number_input("Enter DNA Insert Size (kb):", 0.1, 2000.0, 1.0)
    
    if kb_size < 10:
        st.success("**Plasmid** (e.g., pUC19) - Ref: Section 4.12.1")
    elif 10 <= kb_size <= 23:
        st.success("**Bacteriophage λ** - Ref: Section 4.12.2")
    elif 100 <= kb_size <= 300:
        st.success("**BAC** (Bacterial Artificial Chromosome) - Ref: Section 4.12.4")
    else:
        st.warning("**YAC** (Yeast Artificial Chromosome) - Ref: Section 4.12.5")

# --- TAB 3: PCR OPTIMIZER ---
with tab3:
    st.header("PCR Troubleshooting")
    problem = st.selectbox("Identify Gel Issue:", ["No Bands", "Smearing", "Non-specific Bands"])
    
    advice = {
        "No Bands": "Lower Annealing Temperature, check primers, increase MgCl2.",
        "Smearing": "Reduce cycle number, check template purity.",
        "Non-specific Bands": "Increase Annealing Temperature, use Hot Start Taq."
    }
    st.error(f"Wilson & Walker Solution: {advice[problem]}")

st.divider()
st.caption("PhD Project | Biotechnology Education Digital Twin")
