import streamlit as st

# Function to calculate Melting Temp (Basic Tm) for PCR
def calculate_tm(sequence):
    seq = sequence.upper()
    a = seq.count('A')
    t = seq.count('T')
    c = seq.count('C')
    g = seq.count('G')
    # Wallace Rule for short primers
    tm = 2 * (a + t) + 4 * (g + c)
    return tm

st.set_page_config(page_title="Wilson Walker Lab Assistant", layout="wide")

st.title("🔬 Molecular Biotechnology Interactive")
st.markdown("### Digital Companion to Wilson & Walker: Chapter 4")

tabs = st.tabs(["4.10 PCR Workspace", "4.12 Vector Selection", "4.6 Enzyme Database"])

# --- TAB 1: PCR WORKSPACE ---
with tabs[0]:
    st.header("PCR Optimization & Primer Check")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Primer Analysis")
        primer = st.text_input("Enter Primer Sequence (5' -> 3')", "ATGCGATCGTAGCTAG")
        if primer:
            tm = calculate_tm(primer)
            st.metric("Estimated Melting Temp (Tm)", f"{tm} °C")
            
            if 55 <= tm <= 65:
                st.success("Ideal Tm for standard PCR.")
            else:
                st.warning("Tm is outside the ideal range. Adjust length or GC content.")

    with col2:
        st.subheader("Troubleshooting (Table 4.2 logic)")
        problem = st.selectbox("Observed Result on Gel:", 
                               ["Select...", "No Bands", "Smearing", "Primer Dimers", "Non-specific bands"])
        
        if problem == "No Bands":
            st.info("**Wilson & Walker Suggestion:** Lower the annealing temperature ($T_a$), increase $Mg^{2+}$ concentration, or check template purity.")
        elif problem == "Smearing":
            st.info("**Wilson & Walker Suggestion:** Reduce the number of cycles or decrease the amount of template DNA.")

# --- TAB 2: VECTOR SELECTION ---
with tabs[1]:
    st.header("Cloning Vector Decision Matrix")
    st.write("Determine the best vehicle for your gene of interest.")
    
    insert_size = st.number_input("Insert Size (kb)", min_value=0.1, max_value=2000.0, value=1.0)
    application = st.selectbox("Primary Goal", 
                                ["General Cloning", "Protein Expression", "Genomic Library Construction", "Eukaryotic Study"])
    
    # Decision Logic based on Section 4.12
    st.divider()
    if insert_size < 10:
        if application == "Protein Expression":
            st.success("Recommended: **Expression Plasmid (e.g., pET series)**")
            st.write("Includes a strong promoter (like T7) and a Ribosome Binding Site.")
        else:
            st.success("Recommended: **Standard Cloning Plasmid (e.g., pUC19)**")
    elif 10 <= insert_size <= 20:
        st.success("Recommended: **Bacteriophage λ Vector**")
        st.write("Uses *in vitro* packaging for high transformation efficiency.")
    elif insert_size > 100:
        st.success("Recommended: **BAC (Bacterial Artificial Chromosome)**")
        st.write("Based on the F-plasmid; stable for very large inserts.")

# --- TAB 3: ENZYME DATABASE ---
with tabs[2]:
    st.header("Restriction Endonucleases (Section 4.6)")
    search = st.text_input("Search Enzyme (e.g., EcoRI, BamHI, HindIII)")
    
    # Mock Database
    enzymes = {
        "EcoRI": {"Site": "G^AATTC", "Type": "Sticky"},
        "SmaI": {"Site": "CCC^GGG", "Type": "Blunt"},
        "BamHI": {"Site": "G^GATCC", "Type": "Sticky"}
    }
    
    if search in enzymes:
        st.json(enzymes[search])
    else:
        st.write("Enter a valid Type II enzyme name.")
