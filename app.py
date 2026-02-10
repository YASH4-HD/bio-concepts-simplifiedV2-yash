import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Bio-Logic Framework", layout="wide")

# =========================
# HEADER
# =========================
st.title("📖 Bio-Logic: The Core Principles")
st.markdown("""
*Simplifying the 'Big Three' for Systems Biology*  
**Lehninger (Biochem) | Watson (Genetics) | Wilson & Walker (Techniques)**
""")

# =========================
# SIDEBAR NAVIGATION
# =========================
with st.sidebar:
    st.header("📚 Select a Book")
    book = st.radio("Focus Area:", ["Lehninger: Enzyme Logic", "Watson: Gene Switches", "Wilson & Walker: Lab Logic"])
    st.divider()
    st.caption("Developed by Yashwant Nama")

# =========================
# MODULE 1: LEHNINGER (Enzymes)
# =========================
if book == "Lehninger: Enzyme Logic":
    st.subheader("🧬 Enzyme Kinetics Simplified")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.write("### The 'Why'")
        st.write("Lehninger spends chapters on this. The core idea: How fast can a machine work before it gets overwhelmed?")
        vmax = st.slider("Vmax (Max Speed)", 10, 100, 50)
        km = st.slider("Km (Affinity - lower is stronger)", 1, 50, 10)
        s = st.slider("[Substrate] Concentration", 0, 100, 20)

    with col2:
        s_plot = np.linspace(0, 100, 100)
        v_plot = (vmax * s_plot) / (km + s_plot)
        current_v = (vmax * s) / (km + s)
        
        fig, ax = plt.subplots()
        ax.plot(s_plot, v_plot, color='#1f77b4', lw=3)
        ax.axhline(y=vmax, color='r', linestyle='--', label='Saturation')
        ax.scatter([s], [current_v], color='black', zorder=5)
        ax.set_xlabel("[Substrate]")
        ax.set_ylabel("Velocity")
        st.pyplot(fig)
        st.success(f"Logic: The enzyme is currently at {int((current_v/vmax)*100)}% capacity.")

# =========================
# MODULE 2: WATSON (Genetics)
# =========================
elif book == "Watson: Gene Switches":
    st.subheader("🔌 The Genetic Logic Gate")
    st.write("Watson's 'Molecular Biology of the Gene' is about **Switches**. Let's simulate a Promoter.")
    
    c1, c2 = st.columns(2)
    with c1:
        repressor = st.toggle("Repressor Protein Present")
        inducer = st.toggle("Inducer (Lactose/IPTG) Present")
        
    with c2:
        # Simple Lac Operon Logic
        if repressor and not inducer:
            st.error("🚫 Gene OFF: Repressor is blocking the path.")
        elif repressor and inducer:
            st.warning("⚡ Gene ON (Leaky): Inducer removed the repressor.")
        elif not repressor:
            st.success("✅ Gene ON: Path is clear for Polymerase.")

# =========================
# MODULE 3: WILSON & WALKER (Lab)
# =========================
elif book == "Wilson & Walker: Lab Logic":
    st.subheader("🧪 The Technique Decision Tree")
    st.write("Wilson & Walker is about choosing the right tool. Tell the tool your goal:")
    
    goal = st.selectbox("What do you want to do?", [
        "Check Protein Size", 
        "Measure DNA Concentration", 
        "Identify an Unknown Metabolite",
        "See Protein 3D Structure"
    ])
    
    mapping = {
        "Check Protein Size": "Use **SDS-PAGE**. Logic: Detergent makes all proteins negative, so they move only by weight.",
        "Measure DNA Concentration": "Use **UV-Vis (260nm)**. Logic: Nitrogenous bases absorb UV light predictably.",
        "Identify an Unknown Metabolite": "Use **Mass Spectrometry**. Logic: Break it into pieces and measure the weight of the fragments.",
        "See Protein 3D Structure": "Use **X-Ray Crystallography or Cryo-EM**. Logic: Diffraction patterns reveal atom positions."
    }
    st.info(mapping[goal])

