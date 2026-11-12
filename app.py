
import streamlit as st
from pathlib import Path

from modules.dashboard import show_dashboard
from modules.data_analyzer import show_data_analyzer
from modules.gene_identification import show_gene_identification
from modules.variant_analysis import show_variant_analysis
from modules.rescue_recommendations import show_rescue_recommendations
from modules.crop_predictor import show_crop_predictor
from modules.research_reports import show_research_reports


# ---------------- APPLICATION CONFIGURATION ----------------

st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------- LOAD CSS ----------------

css_path = Path(__file__).parent / "assets" / "style.css"

if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as file:
        st.markdown(
            f"<style>{file.read()}</style>",
            unsafe_allow_html=True
        )


# ---------------- SESSION STATE ----------------

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "crop_model_results" not in st.session_state:
    st.session_state.crop_model_results = None


# ---------------- SIDEBAR ----------------

with st.sidebar:

    st.markdown(
        """
        <h1 style="color:#FFFFFF;">🌱 GeneRescue AI</h1>
        <p style="color:#D4E8D9;">
        Intelligent Genetic Rescue System
        </p>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    selected_page = st.radio(
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
        key="main_navigation"
    )

    st.divider()

    st.markdown(
        """
        **Platform Information**

        Version: 1.0

        Status: Active

        Technology: Python + Bioinformatics
        """
    )

    st.caption("GeneRescue AI | Crop Genetics Research")


# ---------------- PAGE ROUTING ----------------

try:

    if selected_page == "Dashboard":
        show_dashboard()

    elif selected_page == "Genetic Data Analyzer":
        show_data_analyzer()

    elif selected_page == "Gene Identification":
        show_gene_identification()

    elif selected_page == "Variant Analysis":
        show_variant_analysis()

    elif selected_page == "Rescue Recommendations":
        show_rescue_recommendations()

    elif selected_page == "Crop Improvement Predictor":
        show_crop_predictor()

    elif selected_page == "Research Reports":
        show_research_reports()

except Exception as error:

    st.error("An unexpected application error occurred.")

    with st.expander("Technical error details"):
        st.exception(error)


# ---------------- FOOTER ----------------

st.divider()

st.markdown(
    """
    <div style="text-align:center;color:#718477;font-size:12px;">
    GeneRescue AI | Intelligent Genetic Rescue System for Crop Improvement
    <br>
    Computational research support. Experimental validation required.
    </div>
    """,
    unsafe_allow_html=True
)

