
import streamlit as st
from pathlib import Path

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
    initial_sidebar_state="expanded"
)


# =========================================================
# LOAD GLOBAL STYLES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
CSS_PATH = BASE_DIR / "assets" / "style.css"

if CSS_PATH.exists():
    css_content = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css_content}</style>",
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
# APPLICATION NAVIGATION
# =========================================================

PAGES = {
    "Research Overview": {
        "icon": "⌂",
        "description": "Platform overview and research workflow"
    },
    "Data Workspace": {
        "icon": "▤",
        "description": "Upload and inspect genetic datasets"
    },
    "Gene Discovery": {
        "icon": "⌬",
        "description": "Identify potential genes and ORFs"
    },
    "Variant Explorer": {
        "icon": "⌘",
        "description": "Explore genetic variations"
    },
    "Rescue Intelligence": {
        "icon": "✳",
        "description": "Explore crop improvement strategies"
    },
    "Crop Prediction": {
        "icon": "◫",
        "description": "Predict crop traits using machine learning"
    },
    "Research Reports": {
        "icon": "▧",
        "description": "Generate and export research reports"
    }
}

PAGE_DESCRIPTIONS = {
    "Research Overview":
        "A central overview of the GeneRescue AI research platform.",

    "Data Workspace":
        "Upload genetic datasets and inspect sequence characteristics.",

    "Gene Discovery":
        "Identify candidate open reading frames from nucleotide sequences.",

    "Variant Explorer":
        "Examine genetic variants and their structural classifications.",

    "Rescue Intelligence":
        "Explore computational strategies for crop improvement.",

    "Crop Prediction":
        "Analyse crop trait datasets using machine-learning models.",

    "Research Reports":
        "Compile analysis findings into downloadable research reports."
}


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand-panel">
            <div class="brand-icon">🌱</div>
            <div class="brand-name">GeneRescue AI</div>
            <div class="brand-subtitle">CLINICAL RESEARCH WORKSPACE</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section-label">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Research Navigation",
        list(PAGES.keys()),
        index=0,
        label_visibility="collapsed",
        key="main_navigation"
    )

    st.markdown("---")

    st.markdown(
        '<div class="sidebar-section-label">RESEARCH AREAS</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="research-area-list">
            <div>🌾 &nbsp; Drought tolerance</div>
            <div>🧂 &nbsp; Salinity tolerance</div>
            <div>🦠 &nbsp; Disease resistance</div>
            <div>🌿 &nbsp; Yield improvement</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        """
        <div class="sidebar-footer">
            <strong>GeneRescue AI</strong><br>
            Research workspace · Version 2.0
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# MAIN WORKSPACE HEADER
# =========================================================

st.markdown(
    """
    <div class="workspace-topbar">
        <div>
            <div class="workspace-eyebrow">
                BIOINFORMATICS RESEARCH PLATFORM
            </div>
            <div class="workspace-brand">
                GeneRescue AI
            </div>
            <div class="workspace-subtitle">
                Intelligent Genetic Rescue System for Crop Improvement
            </div>
        </div>
        <div class="workspace-status">
            <span class="status-dot"></span>
            Research Workspace
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PAGE TITLE
# =========================================================

page_icon = PAGES[page]["icon"]
page_description = PAGE_DESCRIPTIONS[page]

st.markdown(
    f"""
    <div class="page-heading">
        <div class="page-heading-label">CURRENT WORKSPACE</div>
        <div class="page-heading-title">
            {page_icon} &nbsp; {page}
        </div>
        <div class="page-heading-description">
            {page_description}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# PAGE ROUTING
# =========================================================

if page == "Research Overview":
    show_dashboard()

elif page == "Data Workspace":
    show_data_analyzer()

elif page == "Gene Discovery":
    show_gene_identification()

elif page == "Variant Explorer":
    show_variant_analysis()

elif page == "Rescue Intelligence":
    show_rescue_recommendations()

elif page == "Crop Prediction":
    show_crop_predictor()

elif page == "Research Reports":
    show_research_reports()


# =========================================================
# APPLICATION FOOTER
# =========================================================

st.markdown(
    """
    <div class="workspace-footer">
        <div class="footer-brand">GeneRescue AI</div>
        <div>
            Intelligent Genetic Rescue System for Crop Improvement
        </div>
        <div class="footer-disclaimer">
            Computational research support. Findings and recommendations
            require independent scientific and experimental validation.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
