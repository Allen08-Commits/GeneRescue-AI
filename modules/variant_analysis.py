
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_dataset
from core.variant_analysis import (
    analyze_variants,
    summarize_variants
)


def show_variant_analysis():

    # ---------------- PAGE HEADER ----------------

    st.title("🧪 Genetic Variant Analysis")

    st.write(
        "Investigate genetic variations using uploaded CSV or VCF files."
    )

    # ---------------- FILE UPLOAD ----------------

    uploaded_file = st.file_uploader(
        "Upload variant dataset",
        type=["csv", "vcf"],
        key="variant_upload"
    )

    if uploaded_file is None:

        st.markdown(
            """
            <div style="
                background-color:#E8F3EA;
                border:1px solid #B7D6BE;
                border-left:5px solid #32865B;
                border-radius:10px;
                padding:18px;
                margin-top:15px;
            ">
                <p style="
                    color:#174C35;
                    font-weight:600;
                    margin:0;
                ">
                    🧪 Upload a variant CSV or VCF dataset to begin.
                </p>
                <p style="
                    color:#52675A;
                    font-size:13px;
                    margin:6px 0 0 0;
                ">
                    The application will classify genetic variants
                    and generate a summary of their distribution.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # ---------------- DATA PROCESSING ----------------

    try:

        data = load_dataset(uploaded_file)

        if not isinstance(data, pd.DataFrame):
            st.error(
                "Please upload a CSV or VCF variant dataset."
            )
            return

        if data.empty:
            st.warning(
                "The uploaded dataset contains no variants."
            )
            return

        results = analyze_variants(data)
        summary = summarize_variants(data)

        if results is None or results.empty:
            st.warning(
                "No variant analysis results were generated."
            )
            return

        st.success(
            f"Successfully loaded: {uploaded_file.name}"
        )

        st.divider()

        # ---------------- VARIANT SUMMARY ----------------

        st.subheader("Variant Summary")

        variant_types = summary.get("variant_types", {})

        # Find complex substitution count from classification summary
        complex_count = sum(
            count
            for variant_type, count in variant_types.items()
            if "complex" in str(variant_type).lower()
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Total Variants",
                summary["total_variants"]
            )

        with col2:
            st.metric(
                "SNPs",
                summary["snp_count"]
            )

        with col3:
            st.metric(
                "Insertions",
                summary["insertion_count"]
            )

        with col4:
            st.metric(
                "Deletions",
                summary["deletion_count"]
            )

        with col5:
            st.metric(
                "Complex",
                complex_count
            )

        st.divider()

        # ---------------- VARIANT CLASSIFICATION ----------------

        st.subheader("Variant Classification")

        chart_data = pd.DataFrame(
            list(variant_types.items()),
            columns=["Variant Type", "Count"]
        )

        if not chart_data.empty:

            fig = px.pie(
                chart_data,
                names="Variant Type",
                values="Count",
                hole=0.48,
                title="Distribution of Genetic Variants",
                color_discrete_sequence=[
                    "#82BCE8",
                    "#2876C7",
                    "#F2A3A3",
                    "#EF4444",
                    "#70A889"
                ]
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Count: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                ),
                marker=dict(
                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                )
            )

            fig.update_layout(
                height=430,
                template="plotly_white",
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="Arial",
                    size=13,
                    color="#344B3D"
                ),
                title=dict(
                    text="Distribution of Genetic Variants",
                    font=dict(
                        size=19,
                        color="#174C35"
                    ),
                    x=0.02
                ),
                legend=dict(
                    title="Variant Category",
                    font=dict(
                        size=12,
                        color="#344B3D"
                    ),
                    orientation="v",
                    x=1.02,
                    y=0.5
                ),
                margin=dict(
                    l=30,
                    r=150,
                    t=75,
                    b=35
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )

        else:

            st.info(
                "No variant categories were available for visualization."
            )

        st.divider()

        # ---------------- DETAILED RESULTS ----------------

        st.subheader("Detailed Variant Results")

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

        # ---------------- DOWNLOAD ----------------

        st.subheader("Download Results")

        st.download_button(
            "⬇️ Download Variant Analysis CSV",
            results.to_csv(index=False),
            "variant_analysis.csv",
            "text/csv",
            use_container_width=True
        )

        # ---------------- SCIENTIFIC DISCLAIMER ----------------

        st.markdown(
            """
            <div style="
                background-color:#FFF7E6;
                border:1px solid #E8C982;
                border-left:5px solid #D69E28;
                border-radius:10px;
                padding:16px;
                margin-top:18px;
            ">
                <p style="
                    color:#76520C;
                    font-weight:700;
                    margin:0 0 6px 0;
                ">
                    Scientific Interpretation Notice
                </p>
                <p style="
                    color:#604A20;
                    font-size:14px;
                    margin:0;
                ">
                    Structural classification does not establish
                    whether a variant is harmful, beneficial or
                    functionally significant. Further biological
                    and experimental validation is required.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error(
            f"Variant analysis failed: {e}"
        )

        st.caption(
            "Check the uploaded CSV or VCF file structure and try again."
        )

import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_dataset
from core.variant_analysis import (
    analyze_variants,
    summarize_variants
)


def show_variant_analysis():

    # ---------------- PAGE HEADER ----------------

    st.title("🧪 Genetic Variant Analysis")

    st.write(
        "Investigate genetic variations using uploaded CSV or VCF files."
    )

    # ---------------- FILE UPLOAD ----------------

    uploaded_file = st.file_uploader(
        "Upload variant dataset",
        type=["csv", "vcf"],
        key="variant_upload"
    )

    if uploaded_file is None:

        st.markdown(
            """
            <div style="
                background-color:#E8F3EA;
                border:1px solid #B7D6BE;
                border-left:5px solid #32865B;
                border-radius:10px;
                padding:18px;
                margin-top:15px;
            ">
                <p style="
                    color:#174C35;
                    font-weight:600;
                    margin:0;
                ">
                    🧪 Upload a variant CSV or VCF dataset to begin.
                </p>
                <p style="
                    color:#52675A;
                    font-size:13px;
                    margin:6px 0 0 0;
                ">
                    The application will classify genetic variants
                    and generate a summary of their distribution.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # ---------------- DATA PROCESSING ----------------

    try:

        data = load_dataset(uploaded_file)

        if not isinstance(data, pd.DataFrame):
            st.error(
                "Please upload a CSV or VCF variant dataset."
            )
            return

        if data.empty:
            st.warning(
                "The uploaded dataset contains no variants."
            )
            return

        results = analyze_variants(data)
        summary = summarize_variants(data)

        if results is None or results.empty:
            st.warning(
                "No variant analysis results were generated."
            )
            return

        st.success(
            f"Successfully loaded: {uploaded_file.name}"
        )

        st.divider()

        # ---------------- VARIANT SUMMARY ----------------

        st.subheader("Variant Summary")

        variant_types = summary.get("variant_types", {})

        # Find complex substitution count from classification summary
        complex_count = sum(
            count
            for variant_type, count in variant_types.items()
            if "complex" in str(variant_type).lower()
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Total Variants",
                summary["total_variants"]
            )

        with col2:
            st.metric(
                "SNPs",
                summary["snp_count"]
            )

        with col3:
            st.metric(
                "Insertions",
                summary["insertion_count"]
            )

        with col4:
            st.metric(
                "Deletions",
                summary["deletion_count"]
            )

        with col5:
            st.metric(
                "Complex",
                complex_count
            )

        st.divider()

        # ---------------- VARIANT CLASSIFICATION ----------------

        st.subheader("Variant Classification")

        chart_data = pd.DataFrame(
            list(variant_types.items()),
            columns=["Variant Type", "Count"]
        )

        if not chart_data.empty:

            fig = px.pie(
                chart_data,
                names="Variant Type",
                values="Count",
                hole=0.48,
                title="Distribution of Genetic Variants",
                color_discrete_sequence=[
                    "#82BCE8",
                    "#2876C7",
                    "#F2A3A3",
                    "#EF4444",
                    "#70A889"
                ]
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Count: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                ),
                marker=dict(
                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                )
            )

            fig.update_layout(
                height=430,
                template="plotly_white",
                paper_bgcolor="#FFFFFF",
                plot_bgcolor="#FFFFFF",
                font=dict(
                    family="Arial",
                    size=13,
                    color="#344B3D"
                ),
                title=dict(
                    text="Distribution of Genetic Variants",
                    font=dict(
                        size=19,
                        color="#174C35"
                    ),
                    x=0.02
                ),
                legend=dict(
                    title="Variant Category",
                    font=dict(
                        size=12,
                        color="#344B3D"
                    ),
                    orientation="v",
                    x=1.02,
                    y=0.5
                ),
                margin=dict(
                    l=30,
                    r=150,
                    t=75,
                    b=35
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "responsive": True
                }
            )

        else:

            st.info(
                "No variant categories were available for visualization."
            )

        st.divider()

        # ---------------- DETAILED RESULTS ----------------

        st.subheader("Detailed Variant Results")

        st.dataframe(
            results,
            use_container_width=True,
            hide_index=True
        )

        # ---------------- DOWNLOAD ----------------

        st.subheader("Download Results")

        st.download_button(
            "⬇️ Download Variant Analysis CSV",
            results.to_csv(index=False),
            "variant_analysis.csv",
            "text/csv",
            use_container_width=True
        )

        # ---------------- SCIENTIFIC DISCLAIMER ----------------

        st.markdown(
            """
            <div style="
                background-color:#FFF7E6;
                border:1px solid #E8C982;
                border-left:5px solid #D69E28;
                border-radius:10px;
                padding:16px;
                margin-top:18px;
            ">
                <p style="
                    color:#76520C;
                    font-weight:700;
                    margin:0 0 6px 0;
                ">
                    Scientific Interpretation Notice
                </p>
                <p style="
                    color:#604A20;
                    font-size:14px;
                    margin:0;
                ">
                    Structural classification does not establish
                    whether a variant is harmful, beneficial or
                    functionally significant. Further biological
                    and experimental validation is required.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    except Exception as e:

        st.error(
            f"Variant analysis failed: {e}"
        )

        st.caption(
            "Check the uploaded CSV or VCF file structure and try again."
        )
