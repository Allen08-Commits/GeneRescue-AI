
import streamlit as st
import plotly.express as px
import pandas as pd


def show_dashboard():

    st.markdown(
        "<h1 style='color:#174C35;'>🌱 GeneRescue AI</h1>",
        unsafe_allow_html=True
    )

    st.write(
        "Intelligent Genetic Rescue System for Crop Improvement"
    )

    st.success(
        "Welcome! Analyze genetic datasets and explore "
        "evidence-based crop improvement strategies."
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Analysis Modules", "6")

    with col2:
        st.metric("Input Formats", "3")

    with col3:
        st.metric("Research Traits", "4")

    with col4:
        st.metric("Platform", "Active")

    st.divider()

    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("Crop Improvement Research Areas")

        data = pd.DataFrame({
            "Trait": [
                "Drought Tolerance",
                "Salinity Tolerance",
                "Disease Resistance",
                "Yield Improvement"
            ],
            "Research Focus": [
                "Environmental Stress",
                "Environmental Stress",
                "Biotic Stress",
                "Agronomic Traits"
            ]
        })

        fig = px.bar(
            data,
            x="Trait",
            color="Research Focus",
            title="Supported Research Areas",
            height=350
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Analysis Workflow")

        steps = [
            "📂 Upload genetic data",
            "🔍 Assess sequence quality",
            "🧬 Identify candidate ORFs",
            "🧪 Analyze genetic variants",
            "🌱 Generate rescue strategies",
            "📑 Export research reports"
        ]

        for step in steps:
            st.info(step)

    st.divider()

    st.subheader("About GeneRescue AI")

    st.write(
        "GeneRescue AI integrates bioinformatics, statistical "
        "analysis and machine learning to support crop genetic "
        "research. It helps researchers explore candidate genes, "
        "genetic variation and possible crop improvement strategies."
    )

