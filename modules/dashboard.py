
import streamlit as st
import plotly.express as px
import pandas as pd


def show_dashboard():

    # ---------------- PAGE HEADER ----------------

    st.markdown(
        """
        <h1 style="color:#174C35; margin-bottom:5px;">
            🌱 GeneRescue AI
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <p style="color:#52675A; font-size:17px;">
            Intelligent Genetic Rescue System for Crop Improvement
        </p>
        """,
        unsafe_allow_html=True
    )

    # ---------------- WELCOME BANNER ----------------

    st.markdown(
        """
        <div style="
            background-color:#E5F3E9;
            border:1px solid #A9D2B5;
            border-left:5px solid #32865B;
            border-radius:10px;
            padding:18px 20px;
            margin:18px 0;
        ">
            <p style="
                color:#174C35;
                font-size:16px;
                font-weight:600;
                margin:0;
            ">
                Welcome! Analyze genetic datasets and explore
                evidence-based crop improvement strategies.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- PLATFORM METRICS ----------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Analysis Modules", "7")

    with col2:
        st.metric("Input Formats", "3")

    with col3:
        st.metric("Research Traits", "4")

    with col4:
        st.metric("Platform", "Active")

    st.divider()

    # ---------------- DASHBOARD CONTENT ----------------

    left, right = st.columns([1.4, 1], gap="large")

    with left:

        st.subheader("Crop Improvement Research Areas")

        # Number of supported traits in each research focus
        data = pd.DataFrame({
            "Research Focus": [
                "Environmental Stress",
                "Biotic Stress",
                "Agronomic Traits"
            ],
            "Number of Traits": [2, 1, 1]
        })

        fig = px.bar(
            data,
            x="Research Focus",
            y="Number of Traits",
            color="Research Focus",
            text="Number of Traits",
            color_discrete_sequence=[
                "#82BCE8",
                "#2876C7",
                "#F2A3A3"
            ],
            title="Distribution of Supported Research Traits"
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            height=400,
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#FFFFFF",
            font=dict(
                family="Arial",
                size=12,
                color="#344B3D"
            ),
            title_font=dict(
                size=17,
                color="#174C35"
            ),
            xaxis=dict(
                title="Research Focus",
                tickfont=dict(color="#344B3D"),
                title_font=dict(color="#344B3D")
            ),
            yaxis=dict(
                title="Number of Traits",
                tickfont=dict(color="#344B3D"),
                title_font=dict(color="#344B3D"),
                range=[0, 2.8],
                dtick=1
            ),
            showlegend=False,
            margin=dict(l=35, r=25, t=65, b=65)
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        st.caption(
            "Research focus distribution based on the four "
            "supported research traits."
        )

    with right:

        st.subheader("Analysis Workflow")

        steps = [
            ("📂", "Upload genetic data"),
            ("🔍", "Assess sequence quality"),
            ("🧬", "Identify candidate ORFs"),
            ("🧪", "Analyze genetic variants"),
            ("🌱", "Generate rescue strategies"),
            ("📑", "Export research reports")
        ]

        for icon, label in steps:

            st.markdown(
                f"""
                <div style="
                    display:flex;
                    align-items:center;
                    gap:13px;
                    background-color:#1E293B;
                    border:1px solid #34445C;
                    border-radius:10px;
                    padding:17px 16px;
                    margin-bottom:12px;
                ">
                    <span style="font-size:22px;">
                        {icon}
                    </span>
                    <span style="
                        color:#FFFFFF;
                        font-size:15px;
                        font-weight:600;
                    ">
                        {label}
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ---------------- ABOUT SECTION ----------------

    st.divider()

    st.subheader("About GeneRescue AI")

    st.markdown(
        """
        <div style="
            background-color:#FFFFFF;
            border:1px solid #D7E4D9;
            border-radius:12px;
            padding:20px;
        ">
            <p style="
                color:#20352A;
                font-size:15px;
                line-height:1.8;
                margin:0;
            ">
                GeneRescue AI integrates bioinformatics, statistical
                analysis and machine learning to support crop genetic
                research. It helps researchers explore candidate genes,
                genetic variation and possible crop improvement
                strategies.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.caption(
        "Computational research support. Predictions and "
        "recommendations require experimental validation."
    )
