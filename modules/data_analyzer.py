
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_dataset
from core.sequence_analysis import analyze_multiple_sequences
from core.quality_assessment import assess_multiple_sequences


def show_data_analyzer():

    # ---------------- PAGE HEADER ----------------

    st.title("🧬 Genetic Data Analyzer")

    st.write(
        "Upload genetic datasets and perform sequence-level "
        "analysis and quality assessment."
    )

    # ---------------- FILE UPLOAD ----------------

    uploaded_file = st.file_uploader(
        "Upload genetic dataset",
        type=["fasta", "fa", "fna", "faa", "csv", "vcf"],
        help="Supported formats: FASTA, FA, FNA, FAA, CSV and VCF."
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
                    📂 Upload a FASTA, CSV or VCF file to begin
                    your genetic data analysis.
                </p>
                <p style="
                    color:#52675A;
                    font-size:13px;
                    margin:6px 0 0 0;
                ">
                    Your dataset will be processed to generate
                    sequence statistics and quality assessment results.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        return

    # ---------------- DATA PROCESSING ----------------

    try:

        data = load_dataset(uploaded_file)

        st.success(
            f"Successfully loaded: {uploaded_file.name}"
        )

        st.divider()

        # ==================================================
        # FASTA / SEQUENCE ANALYSIS
        # ==================================================

        if isinstance(data, list):

            st.subheader("Sequence Overview")

            if not data:
                st.warning("The uploaded file contains no sequences.")
                return

            sequence_df = pd.DataFrame([
                {
                    "Sequence ID": record["id"],
                    "Length (bp/aa)": len(record["sequence"])
                }
                for record in data
            ])

            st.dataframe(
                sequence_df,
                use_container_width=True,
                hide_index=True
            )

            # ---------------- ANALYSIS ----------------

            results = analyze_multiple_sequences(data)
            quality = assess_multiple_sequences(data)

            result_df = pd.DataFrame(results)
            quality_df = pd.DataFrame(quality)

            if result_df.empty:
                st.warning("No sequence analysis results were generated.")
                return

            # ---------------- SUMMARY METRICS ----------------

            st.subheader("Analysis Summary")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Sequences",
                    len(data)
                )

            with col2:
                st.metric(
                    "Average Sequence Length",
                    f"{sequence_df['Length (bp/aa)'].mean():,.2f}"
                )

            with col3:

                if "GC_percentage" in result_df.columns:
                    avg_gc = result_df["GC_percentage"].mean()

                    st.metric(
                        "Average GC Content",
                        f"{avg_gc:.2f}%"
                    )
                else:
                    st.metric(
                        "Average GC Content",
                        "N/A"
                    )

            st.divider()

            # ---------------- SEQUENCE RESULTS ----------------

            st.subheader("Sequence Analysis Results")

            st.dataframe(
                result_df,
                use_container_width=True,
                hide_index=True
            )

            # ---------------- QUALITY ASSESSMENT ----------------

            st.subheader("Quality Assessment")

            st.dataframe(
                quality_df,
                use_container_width=True,
                hide_index=True
            )

            # ---------------- GC CONTENT CHART ----------------

            if (
                "GC_percentage" in result_df.columns
                and "sequence_id" in result_df.columns
            ):

                st.subheader("GC Content Across Sequences")

                chart_data = result_df.copy()

                chart_data["GC_percentage"] = pd.to_numeric(
                    chart_data["GC_percentage"],
                    errors="coerce"
                )

                chart_data = chart_data.dropna(
                    subset=["GC_percentage"]
                )

                if not chart_data.empty:

                    fig = px.bar(
                        chart_data,
                        x="sequence_id",
                        y="GC_percentage",
                        text="GC_percentage",
                        color="GC_percentage",
                        color_continuous_scale=[
                            "#B7DCC0",
                            "#32865B",
                            "#174C35"
                        ],
                        labels={
                            "sequence_id": "Sequence ID",
                            "GC_percentage": "GC Content (%)"
                        },
                        title="GC Content Distribution"
                    )

                    fig.update_traces(
                        texttemplate="%{text:.2f}%",
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
                            size=18,
                            color="#174C35"
                        ),
                        xaxis_title="Sequence ID",
                        yaxis_title="GC Content (%)",
                        coloraxis_showscale=False,
                        margin=dict(
                            l=40,
                            r=25,
                            t=65,
                            b=65
                        )
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False}
                    )

            # ---------------- DOWNLOAD RESULTS ----------------

            st.divider()

            st.subheader("Download Analysis Results")

            col1, col2 = st.columns(2)

            with col1:

                st.download_button(
                    "⬇️ Download Sequence Analysis CSV",
                    result_df.to_csv(index=False),
                    "sequence_analysis.csv",
                    "text/csv",
                    use_container_width=True
                )

            with col2:

                st.download_button(
                    "⬇️ Download Quality Results CSV",
                    quality_df.to_csv(index=False),
                    "quality_assessment.csv",
                    "text/csv",
                    use_container_width=True
                )

        # ==================================================
        # CSV / VCF DATASET ANALYSIS
        # ==================================================

        elif isinstance(data, pd.DataFrame):

            st.subheader("Dataset Preview")

            if data.empty:
                st.warning("The uploaded dataset is empty.")
                return

            st.dataframe(
                data.head(100),
                use_container_width=True,
                hide_index=True
            )

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Total Records",
                    f"{len(data):,}"
                )

            with col2:
                st.metric(
                    "Total Columns",
                    len(data.columns)
                )

            st.write(
                "**Available Columns:**",
                ", ".join(map(str, data.columns))
            )

            st.download_button(
                "⬇️ Download Uploaded Dataset",
                data.to_csv(index=False),
                "uploaded_dataset.csv",
                "text/csv",
                use_container_width=True
            )

        else:

            st.warning(
                "The uploaded file could not be converted "
                "into a supported sequence or tabular dataset."
            )

    except Exception as e:

        st.error(
            f"Analysis error: {e}"
        )

        st.caption(
            "Check the uploaded file format and its contents, "
            "then try again."
        )
