import streamlit as st
from Bio.Seq import Seq
from Bio.Restriction import Analysis, AllEnzymes
import io

# --- PAGE CONFIG ---
st.set_page_config(page_title="Wilson Walker Digital Lab", page_icon="🧬", layout="wide")

# --- KNOWLEDGE DATABASE (Free) ---
KNOWLEDGE_BASE = {
    "Restriction Enzymes": "Section 4.6: Type II enzymes cut at specific palindromic sites.",
    "PCR Principles": "Section 4.10: Thermal cycling to amplify specific DNA targets.",
    "Plasmids": "Section 4.12.1: Circular DNA for cloning inserts <10kb.",
    "BACs": "Section 4.12.4: For large genomic fragments (100-300kb)."
}

# --- SIDEBAR ---
with st.sidebar:
    st.title("📚 Concept Navigator")
    topic = st.selectbox("Quick Theory:", list(KNOWLEDGE_BASE.keys()))
    st.info(KNOWLEDGE_BASE[topic])
    st.divider()
    st.caption("PhD Project: Interactive Lab Assistant")

# --- MAIN INTERFACE ---
st.title("🔬 Wilson & Walker: Interactive Molecular Lab")

tab1, tab2, tab3 = st.tabs(["🧬 Sequence Analyzer", "📦 Vector Selector", "🧪 PCR Optimizer"])

# --- TAB 1: SEQUENCE ANALYZER (With File Upload) ---
with tab1:
    st.header("Restriction Mapping (Section 4.6)")
    
    # FILE UPLOAD OPTION
    uploaded_file = st.file_uploader("Upload a DNA sequence file (.txt or .fasta)", type=["txt", "fasta"])
    
    # TEXT AREA OPTION (as fallback)
    manual_seq = st.text_area("OR Paste DNA Sequence here:", height=100)
    
    final_seq = ""
    
    # Logic to handle uploaded file
    if uploaded_file is not None:
        stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
        file_content = stringio.read()
        # If it's a FASTA file, remove the header line starting with '>'
        lines = file_content.splitlines()
        if lines[0].startswith(">"):
            final_seq = "".join(lines[1:])
        else:
            final_seq = "".join(lines)
        st.success(f"File uploaded successfully: {uploaded_file.name}")
    elif manual_seq:
        final_seq = manual_seq

    clean_seq = "".join(final_seq.split()).upper()
    
    if st.button("Run Full Analysis"):
        if clean_seq:
            try:
                my_seq = Seq(clean_seq)
                analysis = Analysis(AllEnzymes, my_seq)
                results = analysis.full()
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Length", f"{len(my_seq)} bp")
                c2.metric("GC Content", f"{round((clean_seq.count('G')+clean_seq.count('C'))/len(clean_seq)*100, 1)}%")
                
                st.subheader("Detected Restriction Sites")
                found = False
                for enz, sites in results.items():
                    if sites:
                        with st.expander(f"Enzyme: {enz}"):
                            st.write(f"**Cut Positions:** {sites}")
                            st.code(f"Seq: {clean_seq[:50]}...\nCut: {' ' * (sites[0]-1)}^")
                        found = True
                if not found:
                    st.info("No common restriction sites found.")
            except Exception as e:
                st.error(f"Error processing sequence: {e}")
        else:
            st.warning("Please upload a file or paste a sequence first.")

# --- TAB 2: VECTOR SELECTOR ---
with tab2:
    st.header("Vector Selection (Table 4.4)")
    size = st.number_input("Enter your Insert Size (kb):", 0.1, 2000.0, 1.0)
    
    if size < 10:
        st.success("**Standard Plasmid** (Ref: 4.12.1)")
        st.write("Best for: Subcloning, sequencing, and small protein expression.")
    elif 10 <= size <= 23:
        st.success("**Bacteriophage λ** (Ref: 4.12.2)")
        st.write("Best for: cDNA libraries and genomic mapping.")
    elif 100 <= size <= 300:
        st.success("**BAC (Bacterial Artificial Chromosome)** (Ref: 4.12.4)")
        st.write("Best for: Large scale physical mapping of genomes.")
    else:
        st.warning("**YAC (Yeast Artificial Chromosome)** (Ref: 4.12.5)")
        st.write("Best for: Human Genome Project-scale fragments.")

# --- TAB 3: PCR OPTIMIZER ---
with tab3:
    st.header("PCR Troubleshooting (Section 4.10)")
    issue = st.selectbox("What is your Gel result?", ["No Bands", "Smearing", "Non-specific bands"])
    
    solutions = {
        "No Bands": "Lower the Annealing Temperature, check primer design, or increase MgCl2 concentration.",
        "Smearing": "Reduce the number of cycles or decrease the amount of template DNA.",
        "Non-specific bands": "Increase the Annealing Temperature or use a 'Hot Start' DNA polymerase."
    }
    st.error(f"**Wilson & Walker Solution:** {solutions[issue]}")
