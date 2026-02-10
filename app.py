import streamlit as st
from Bio.Seq import Seq
from Bio.Restriction import Analysis, AllEnzymes
from openai import OpenAI

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Wilson Walker Digital Lab",
    page_icon="🧬",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 5px; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: AI TUTOR ---
with st.sidebar:
    st.title("🤖 Wilson-Walker AI")
    st.info("Ask questions about Chapter 4: Recombinant DNA.")
    
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    user_question = st.text_input("Ask a concept:")
    
    if user_question:
        if not api_key:
            st.error("Please enter an API key to use the AI Tutor.")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("Consulting the textbook..."):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a PhD-level tutor based on Wilson & Walker's 'Principles and Techniques'. Explain concepts from Chapter 4 (Molecular Biology) clearly and accurately."},
                        {"role": "user", "content": user_question}
                    ]
                )
                st.write(response.choices[0].message.content)

# --- MAIN INTERFACE ---
st.title("🔬 Wilson & Walker: Interactive Molecular Lab")
st.caption("A PhD Project for Enhancing Biotechnology Education")

tab1, tab2, tab3 = st.tabs(["🧬 Sequence Analyzer", "📦 Vector Selector", "🧪 PCR Optimizer"])

# --- TAB 1: SEQUENCE ANALYZER (Section 4.6) ---
with tab1:
    st.header("Restriction Mapping & Sequence Analysis")
    st.write("Analyze DNA sequences using the tools described in **Section 4.6**.")
    
    raw_seq = st.text_area("Input DNA Sequence (FASTA or Raw):", 
                           "GAATTCGCTAGCTAGCTAGGGATCC", height=150)
    
    clean_seq = "".join(raw_seq.split()).upper()
    
    if st.button("Run Analysis"):
        if clean_seq:
            my_seq = Seq(clean_seq)
            # Restriction Analysis
            analysis = Analysis(AllEnzymes, my_seq)
            results = analysis.full()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Sequence Length", f"{len(my_seq)} bp")
            col2.metric("GC Content", f"{round((clean_seq.count('G')+clean_seq.count('C'))/len(clean_seq)*100, 2)}%")
            
            st.subheader("Detected Restriction Sites")
            found_any = False
            for enz, sites in results.items():
                if sites:
                    st.write(f"✅ **{enz}**: cuts at position(s) {sites}")
                    found_any = True
            if not found_any:
                st.info("No common restriction sites found.")
        else:
            st.error("Please enter a valid sequence.")

# --- TAB 2: VECTOR SELECTOR (Section 4.12) ---
with tab2:
    st.header("Smart Vector Selection Tool")
    st.write("Select the best vector based on the criteria in **Table 4.4**.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        size = st.number_input("Insert Size (kb)", 0.1, 2000.0, 1.0)
        host = st.selectbox("Host System", ["Prokaryotic (E. coli)", "Eukaryotic (Yeast/Mammalian)"])
    
    with col_b:
        goal = st.radio("Primary Goal", ["Cloning/Storage", "Protein Expression", "Large Library"])

    st.divider()
    
    # Logic Engine
    if size < 10:
        if goal == "Protein Expression":
            st.success("Target: **Expression Plasmid** (e.g., pET vectors)")
            st.markdown("- **Key Features:** T7 Promoter, RBS, Selectable Marker.")
        else:
            st.success("Target: **Standard Plasmid** (e.g., pUC19)")
            st.markdown("- **Key Features:** High copy number, Blue/White screening.")
    elif 10 <= size <= 23:
        st.success("Target: **Bacteriophage λ**")
        st.markdown("- **Key Features:** *In vitro* packaging, high efficiency.")
    elif 100 <= size <= 300:
        st.success("Target: **BAC (Bacterial Artificial Chromosome)**")
        st.markdown("- **Key Features:** Based on F-factor, stable for large genomes.")
    else:
        st.info("Based on size, consider a Cosmid or YAC (Yeast Artificial Chromosome).")

# --- TAB 3: PCR OPTIMIZER (Section 4.10) ---
with tab3:
    st.header("PCR Troubleshooting & Design")
    
    with st.expander("Step 1: Calculate Annealing Temp"):
        primer = st.text_input("Enter Primer (20-30 bp):", "ATGCGATCGTAGCTAGCTAG")
        if primer:
            # Wallace Rule
            tm = 2*(primer.count('A')+primer.count('T')) + 4*(primer.count('G')+primer.count('C'))
            st.write(f"**Melting Temperature (Tm):** {tm}°C")
            st.write(f"**Suggested Annealing Temp (Ta):** {tm - 5}°C")

    with st.expander("Step 2: Troubleshooting (Section 4.10.4)"):
        issue = st.selectbox("What do you see on the gel?", 
                             ["No Bands", "Smearing", "Non-specific bands (Multiple bands)", "Primer Dimers"])
        
        if issue == "No Bands":
            st.warning("**Action:** Decrease Annealing Temp, increase MgCl2, or check template concentration.")
        elif issue == "Smearing":
            st.warning("**Action:** Reduce number of cycles or template amount. Ensure DNA is not degraded.")
        elif issue == "Non-specific bands":
            st.warning("**Action:** Increase Annealing Temp or use 'Hot Start' PCR.")

st.divider()
st.center = st.write("© 2023 - PhD Project: Interactive Molecular Education")
