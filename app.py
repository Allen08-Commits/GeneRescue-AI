
"""GeneRescue AI - Main Streamlit Application."""

import streamlit as st

# 1. Configure Streamlit BEFORE importing application modules
st.set_page_config(
    page_title="GeneRescue AI",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# 2. Load CSS
css_path = BASE_DIR / "assets" / "style.css"

if css_path.exists():
    css = css_path.read_text(encoding="utf-8")
    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


# 3. Initialize session state
if "gr_started" not in st.session_state:
    st.session_state["gr_started"] = False

if "gr_active_tool" not in st.session_state:
    st.session_state["gr_active_tool"] = "Sequence Analysis"


# 4. Import workspace only after page configuration
try:
    from modules.research_workspace import (
        TOOLS,
        render_tool,
        render_welcome,
    )

except Exception as error:
    st.error("GeneRescue AI workspace could not be loaded.")
    st.exception(error)
    st.stop()


# 5. Application styling
st.markdown("""
<style>
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

.block-container {
    max-width: 1420px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

.gr-topbar {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 18px;
    background: white;
    border: 1px solid #dce7dd;
    border-radius: 14px;
    margin-bottom: 20px;
}

.gr-brand {
    color: #204f36;
    font-size: 23px;
    font-weight: 800;
}

.gr-kicker {
    color: #718176;
    font-size: 10px;
    letter-spacing: 1.4px;
    font-weight: 700;
}

.gr-footer {
    text-align: center;
    color: #829287;
    font-size: 12px;
    margin-top: 35px;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)


# 6. Main application
try:

    if not st.session_state["gr_started"]:

        render_welcome()

    else:

        st.markdown("""
        <div class="gr-topbar">
            <div style="font-size:30px;">🌱</div>
            <div>
                <div class="gr-brand">GeneRescue AI</div>
                <div class="gr-kicker">
                    INTELLIGENT GENETIC RESCUE SYSTEM
                    FOR CROP IMPROVEMENT
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        selected_tool = st.radio(
            "Research Tools",
            TOOLS,
            horizontal=True,
            label_visibility="collapsed",
            key="gr_tool_navigation",
        )

        st.session_state["gr_active_tool"] = selected_tool

        st.markdown("---")

        st.title(selected_tool)

        render_tool(selected_tool)

        st.markdown("---")

        if st.button("← Back to Welcome Page"):
            st.session_state["gr_started"] = False
            st.rerun()

    st.markdown("""
    <div class="gr-footer">
        GeneRescue AI | Bioinformatics Research Workspace
        <br>
        Research findings require independent scientific validation.
    </div>
    """, unsafe_allow_html=True)

except Exception as error:
    st.error("A problem occurred while rendering the research workspace.")
    st.exception(error)
