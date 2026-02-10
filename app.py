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

# --- CUSTOM STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: AI TUTOR & INFO ---
with st.sidebar:
    st.title("🤖 Wilson-Walker AI")
    st.markdown("---")
    st.info("This AI is trained to explain concepts from **Chapter 4: Recombinant DNA Technology**.")
    
    # User provides API key or you can use st.secrets for deployment
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    user_question = st.text_input("Ask a concept (e.g., 'What is a polylinker?'):")
    
    if user_question:
        if not api_key:
            st.warning("Please enter an API key to activate the AI Tutor.")
        else:
            try:
                client = OpenAI(api_key=api_key)
                with st.spinner("Consulting Chapter 4..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a PhD-level tutor based on Wilson & Walker's 'Principles and Techniques'. Use the logic of Chapter 4 to answer questions accurately."},
                            {"role": "user", "content": user_question}
                        ]
                    )
                    st.success("**AI Response:**")
                    st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.caption("PhD Project: Interactive Textbook Digital Twin")

# --- MAIN INTERFACE ---
st.title("🔬 Wilson & Walker: Interactive Molecular Lab")
st.markdown("### *A Digital Companion to Recombinant DNA Techniques*")

tab1, tab2, tab3 = st.tabs(["🧬 Sequence Analyzer", "📦 Vector Selector", "🧪 PCR Optimizer"])

# --- TAB 1: SEQUENCE ANALYZER (Section 4.6) ---
with tab1:
    st.header("Restriction Mapping & Analysis (Section 4.6)")
    st.write("Analyze DNA sequences and find cutting sites for Type II Endonucleases.")
    
    raw_seq = st.text_area("Paste DNA Sequence:", "GAATTCGCTAGCTAGCTAGGGATCC", height=100)
    clean_seq = "".join(raw_seq.split()).upper()
    
    if st.button("Analyze Sequence"):
        if clean_seq:
            my_seq = Seq(clean_seq)
            analysis = Analysis(AllEnzymes, my_seq)
            results = analysis.full()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Length", f"{len(my_seq)} bp")
            c2.metric("GC Content", f"{round((clean_seq.count('G')+clean_seq.count('C'))/len(clean_seq)*100, 1)}%")
            c3.metric("Purity Check", "Ready")
            
            st.subheader("Detected Cut Sites")
            found = False
            for enz, sites in results.items():
                if sites:
                    with st.expander(f"Enzyme: {enz}"):
                        st.write(f"**Cut Positions:** {sites}")
                        st.write(f"**Type:** Type II Restriction Endonuclease (Ref: Section 4.6.1)")
                        # Simple visual map for this enzyme
                        st.code(f"Sequence: {clean_seq}\nCut at:  {' ' * (sites[0]-1)}^")
                    found = True
            if not found:
                st.info("No common restriction sites found in this sequence.")
        else:
            st.error("Please enter a sequence.")

# --- TAB 2: VECTOR SELECTOR (Section 4.12) ---
with tab2:
    st.header("Vector Selection Decision Matrix")
    st.write("Choose the appropriate cloning vehicle based on **Table 4.4**.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        size = st.number_input("DNA Insert Size (kb)", 0.1, 2000.0, 1.0)
        host = st.selectbox("Target Host", ["Bacteria (E. coli)", "Yeast (S. cerevisiae)", "Mammalian Cells"])
    
    with col_b:
        goal = st.radio("Experimental Goal", ["General Cloning", "Protein Expression", "Genomic Library"])

    st.divider()
    
    st.subheader("Recommended Vector System:")
    if size < 10:
        if goal == "Protein Expression":
            st.success("**Expression Plasmid (e.g., pET-28a)**")
            st.info("Ref: Section 4.12.1 - Features a strong T7 promoter and His-tag for purification.")
        else:
            st.success("**Standard Cloning Plasmid (e.g., pUC19)**")
            st.info("Ref: Section 4.12.1 - High copy number, ideal for blue/white screening.")
    elif 10 <= size <= 23:
        st.success("**Bacteriophage λ (Lambda) Vector**")
        st.info("Ref: Section 4.12.2 - Uses 'In Vitro Packaging' to infect E. coli with high efficiency.")
    elif 100 <= size <= 300:
        st.success("**BAC (Bacterial Artificial Chromosome)**")
        st.info("Ref: Section 4.12.4 - Based on the F-plasmid. Crucial for large scale genome mapping.")
    else:
        st.warning("**YAC (Yeast Artificial Chromosome)**")
        st.info("Ref: Section 4.12.5 - Used for inserts up to 2000kb. Mimics a eukaryotic chromosome.")

# --- TAB 3: PCR OPTIMIZER (Section 4.10) ---
with tab3:
    st.header("PCR Design & Troubleshooting (Section 4.10)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Primer Design")
        p_seq = st.text_input("Enter Primer Sequence (5'->3'):", "CCGATAGCTAGCTAGCTAGC")
        if p_seq:
            # Wallace Rule Calculation
            tm = 2*(p_seq.upper().count('A')+p_seq.upper().count('T')) + 4*(p_seq.upper().count('G')+p_seq.upper().count('C'))
            st.metric("Melting Temp (Tm)", f"{tm} °C")
            st.write(f"**Recommended Annealing Temp:** {tm - 5} °C")
            st.caption("Calculation based on Section 4.10.2 basic parameters.")

    with col2:
        st.subheader("Troubleshooting Gel Results")
        issue = st.selectbox("Identify the problem:", 
                             ["No Bands", "Multiple Non-specific Bands", "Smearing", "Primer Dimers"])
        
        if issue == "No Bands":
            st.error("**Wilson & Walker Solution (Table 4.2):**")
            st.markdown("- Decrease Annealing Temperature ($T_a$)\n- Increase $Mg^{2+}$ concentration\n- Check template DNA integrity")
        elif issue == "Multiple Non-specific Bands":
            st.warning("**Wilson & Walker Solution (Table 4.2):**")
            st.markdown("- Increase Annealing Temperature ($T_a$)\n- Use 'Hot Start' PCR\n- Reduce Primer concentration")
        elif issue == "Smearing":
            st.warning("**Wilson & Walker Solution (Table 4.2):**")
            st.markdown("- Reduce number of cycles\n- Decrease template DNA amount\n- Check for contamination")

st.markdown("---")
st.caption("Developed as an interactive educational tool for PhD research in Biotechnology Education.")
