
import streamlit as st
import plotly.express as px
import pandas as pd


def show_dashboard():

    # ---------------- WELCOME BANNER ----------------

    st.markdown(
        """
        <div style="
            background-color:#EAF3EB;
            border:1px solid #D3E4D6;
            border-left:5px solid #32865B;
            border-radius:12px;
            padding:22px 24px;
            margin:12px 0 25px 0;
        ">
            <h3 style="color:#174C35; margin:0 0 8px 0;">
                Welcome to GeneRescue AI
            </h3>
            <p style="
                color:#52675A;
                font-size:15px;
                margin:0;
                line-height:1.7;
            ">
                Explore genetic datasets, identify candidate genes
                and investigate computational strategies for
                crop improvement.
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

    # ---------------- RESEARCH AREAS ----------------

    st.subheader("Crop Improvement Research Areas")

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
        template="plotly_white",
        height=380,
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

    # ---------------- ABOUT SECTION ----------------

    st.divider()

    st.subheader("About GeneRescue AI")

    st.markdown(
        """
        <div style="
            background-color:#FFFFFF;
            border:1px solid #D7E4D9;
            border-radius:12px;
            padding:22px;
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
