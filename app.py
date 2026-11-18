
import streamlit as st
from pathlib import Path

# =========================================================
# IMPORT EXISTING RESEARCH MODULES
# =========================================================

from modules.dashboard import show_dashboard
from modules.data_analyzer import show_data_analyzer
from modules.gene_identification import show_gene_identification
from modules.variant_analysis import show_variant_analysis
from modules.rescue_recommendations import show_rescue_recommendations
from modules.crop_predictor import show_crop_predictor
from modules.research_reports import show_research_reports


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="GeneRescue AI | Research Workspace",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# APPLICATION PATHS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "style.css"


# =========================================================
# GLOBAL CSS
# =========================================================

if CSS_PATH.exists():
    css_content = CSS_PATH.read_text(encoding="utf-8")

    st.markdown(
        f"<style>{css_content}</style>",
        unsafe_allow_html=True
    )


# =========================================================
# HIDE STREAMLIT SIDEBAR
# =========================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebar"] {
        display: none !important;
    }

    [data-testid="collapsedControl"] {
        display: none !important;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    /* MAIN BRAND HEADER */

    .gr-brand-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 18px;
        padding: 22px 26px;
        background: #ffffff;
        border: 1px solid #e3ebe4;
        border-radius: 16px;
        margin-bottom: 22px;
    }

    .gr-brand-left {
        display: flex;
        align-items: center;
        gap: 15px;
    }

    .gr-brand-icon {
        width: 52px;
        height: 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #eaf3eb;
        border-radius: 13px;
        font-size: 27px;
    }

    .gr-brand-name {
        color: #174c35;
        font-size: 25px;
        font-weight: 750;
        letter-spacing: -0.7px;
    }

    .gr-brand-subtitle {
        color: #718276;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-top: 3px;
    }

    .gr-status {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 9px 14px;
        border-radius: 30px;
        background: #edf6ef;
        color: #276344;
        font-size: 12px;
        font-weight: 650;
    }

    .gr-status-dot {
        height: 8px;
        width: 8px;
        background: #329b62;
        border-radius: 50%;
    }

    /* NAVIGATION AREA */

    .gr-navigation-label {
        color: #738477;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 1.5px;
        margin: 8px 0 5px 3px;
    }

    /* PAGE INTRODUCTION */

    .gr-page-heading {
        padding: 19px 3px 14px 3px;
    }

    .gr-page-eyebrow {
        color: #718477;
        font-size: 10px;
        font-weight: 750;
        letter-spacing: 1.5px;
        margin-bottom: 7px;
    }

    .gr-page-title {
        color: #174c35;
        font-size: 29px;
        font-weight: 750;
        letter-spacing: -0.8px;
        line-height: 1.25;
    }

    .gr-page-description {
        color: #738176;
        font-size: 13px;
        margin-top: 7px;
    }

    /* FOOTER */

    .gr-footer {
        margin-top: 45px;
        padding: 20px 5px 8px 5px;
        border-top: 1px solid #e2eae3;
        text-align: center;
        color: #738176;
        font-size: 11px;
        line-height: 1.8;
    }

    .gr-footer-brand {
        color: #174c35;
        font-weight: 750;
        font-size: 14px;
    }

    /* REMOVE EXCESSIVE TOP NAVIGATION SPACING */

    div[data-testid="stRadio"] > label {
        display: none;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_history" not in st.session_state:
    st.session_state["analysis_history"] = []

if "rescue_report_data" not in st.session_state:
    st.session_state["rescue_report_data"] = None


# =========================================================
# NAVIGATION CONFIGURATION
# =========================================================

PAGES = [
    "Dashboard",
    "Genetic Data Analyzer",
    "Gene Identification",
    "Variant Analysis",
    "Rescue Recommendations",
    "Crop Improvement Predictor",
    "Research Reports"
]

PAGE_DESCRIPTIONS = {
    "Dashboard":
        "Your central overview of the GeneRescue AI research platform.",

    "Genetic Data Analyzer":
        "Upload genetic datasets and investigate sequence characteristics.",

    "Gene Identification":
        "Identify potential genes and open reading frames from nucleotide sequences.",

    "Variant Analysis":
        "Explore genetic variations and their structural classifications.",

    "Rescue Recommendations":
        "Investigate computational strategies for crop improvement.",

    "Crop Improvement Predictor":
        "Explore crop traits using machine-learning prediction models.",

    "Research Reports":
        "Generate and export structured research analysis reports."
}

PAGE_ICONS = {
    "Dashboard": "⌂",
    "Genetic Data Analyzer": "🧬",
    "Gene Identification": "🔬",
    "Variant Analysis": "🧪",
    "Rescue Recommendations": "🌱",
    "Crop Improvement Predictor": "📊",
    "Research Reports": "📑"
}


# =========================================================
# TOP BRAND HEADER
# =========================================================

st.markdown(
    """
    <div class="gr-brand-header">

        <div class="gr-brand-left">

            <div class="gr-brand-icon">
                🌱
            </div>

            <div>
                <div class="gr-brand-name">
                    GeneRescue AI
                </div>

                <div class="gr-brand-subtitle">
                    CLINICAL RESEARCH WORKSPACE
                </div>
            </div>

        </div>

        <div class="gr-status">
            <span class="gr-status-dot"></span>
            Research Platform
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HORIZONTAL NAVIGATION
# =========================================================

st.markdown(
    '<div class="gr-navigation-label">RESEARCH NAVIGATION</div>',
    unsafe_allow_html=True
)

page = st.radio(
    "Main Navigation",
    options=PAGES,
    index=0,
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation"
)


# =========================================================
# CURRENT PAGE HEADER
# =========================================================

page_icon = PAGE_ICONS[page]
page_description = PAGE_DESCRIPTIONS[page]

st.markdown(
    f"""
    <div class="gr-page-heading">

        <div class="gr-page-eyebrow">
            GENE RESCUE RESEARCH PLATFORM
        </div>

        <div class="gr-page-title">
            {page_icon} &nbsp; {page}
        </div>

        <div class="gr-page-description">
            {page_description}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# PAGE ROUTING
# =========================================================

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


# =========================================================
# APPLICATION FOOTER
# =========================================================

st.markdown(
    """
    <div class="gr-footer">

        <div class="gr-footer-brand">
            GeneRescue AI
        </div>

        Intelligent Genetic Rescue System for Crop Improvement

        <br>

        Computational research support.
        Findings require independent scientific and experimental validation.

        <br>

        Research Workspace · Version 2.0

    </div>
    """,
    unsafe_allow_html=True
)
