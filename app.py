
import streamlit as st
from pathlib import Path

from modules.dashboard import show_dashboard
from modules.data_analyzer import show_data_analyzer
from modules.gene_identification import show_gene_identification
from modules.variant_analysis import show_variant_analysis
from modules.rescue_recommendations import show_rescue_recommendations
from modules.crop_predictor import show_crop_predictor
from modules.research_reports import show_research_reports


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- CUSTOM STYLING ----------------

css_path = Path("assets/style.css")

if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )

st.markdown("""
<style>

.stApp {
    background-color: #F5F8F4;
}

[data-testid="stSidebar"] {
    background-color: #123C2D;
}

[data-testid="stSidebar"] * {
    color: white;
}

[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid #DCE8DD;
}

h1, h2, h3 {
    color: #174C35;
}

</style>
""", unsafe_allow_html=True)


# ---------------- SESSION STATE ----------------

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown("# 🌱 GeneRescue AI")

    st.caption(
        "Intelligent Genetic Rescue System"
    )

    st.divider()

    page = st.radio(
        "MAIN NAVIGATION",
        [
            "Dashboard",
            "Genetic Data Analyzer",
            "Gene Identification",
            "Variant Analysis",
            "Rescue Recommendations",
            "Crop Improvement Predictor",
            "Research Reports"
        ],
        index=0
    )

    st.divider()

    st.markdown("### Research Areas")

    st.caption("🌾 Drought Tolerance")
    st.caption("🧂 Salinity Tolerance")
    st.caption("🦠 Disease Resistance")
    st.caption("🌱 Yield Improvement")

    st.divider()

    st.caption("GeneRescue AI | Version 1.0")


# ---------------- PAGE ROUTING ----------------

if page == "Dashboard":

    show_dashboard()

elif page == "Genetic Data Analyzer":

    show_data_analyzer()

elif page == "Gene Identification":

    show_gene_identification()

elif page == "Variant Analysis":

    show_variant_analysis()

elif page == "Rescue Recommendations":

    show_rescue_recommendations()

elif page == "Crop Improvement Predictor":

    show_crop_predictor()

elif page == "Research Reports":

    show_research_reports()


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#718477;font-size:12px;">
        GeneRescue AI | Intelligent Genetic Rescue System
        for Crop Improvement<br>
        Computational research support. Experimental validation required.
    </div>
    """,
    unsafe_allow_html=True
)
