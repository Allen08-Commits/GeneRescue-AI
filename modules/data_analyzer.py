
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_dataset
from core.sequence_analysis import analyze_multiple_sequences
from core.quality_assessment import assess_multiple_sequences


def show_data_analyzer():

    st.title("🧬 Genetic Data Analyzer")

    st.write(
        "Upload genetic datasets and perform sequence-level "
        "analysis and quality assessment."
    )

    uploaded_file = st.file_uploader(
        "Upload genetic dataset",
        type=["fasta", "fa", "fna", "faa", "csv", "vcf"]
    )

    if uploaded_file is None:
        st.info("Upload a FASTA, CSV or VCF file to begin.")
        return

    try:
        data = load_dataset(uploaded_file)

        st.success(f"Successfully loaded: {uploaded_file.name}")

        if isinstance(data, list):

            st.subheader("Sequence Overview")

            sequence_df = pd.DataFrame([
                {
                    "Sequence ID": record["id"],
                    "Length": len(record["sequence"])
                }
                for record in data
            ])

            st.dataframe(
                sequence_df,
                use_container_width=True
            )

            results = analyze_multiple_sequences(data)
            quality = assess_multiple_sequences(data)

            result_df = pd.DataFrame(results)
            quality_df = pd.DataFrame(quality)

            st.subheader("Sequence Analysis Results")
            st.dataframe(result_df, use_container_width=True)

            st.subheader("Quality Assessment")
            st.dataframe(quality_df, use_container_width=True)

            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Total Sequences",
                    len(data)
                )

            with col2:
                st.metric(
                    "Average Sequence Length",
                    round(sequence_df["Length"].mean(), 2)
                )

            fig = px.bar(
                result_df,
                x="sequence_id",
                y="GC_percentage",
                title="GC Content Across Sequences",
                labels={
                    "sequence_id": "Sequence ID",
                    "GC_percentage": "GC Content (%)"
                }
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.download_button(
                "Download Sequence Analysis CSV",
                result_df.to_csv(index=False),
                "sequence_analysis.csv",
                "text/csv"
            )

            st.download_button(
                "Download Quality Results CSV",
                quality_df.to_csv(index=False),
                "quality_assessment.csv",
                "text/csv"
            )

        elif isinstance(data, pd.DataFrame):

            st.subheader("Dataset Preview")

            st.dataframe(
                data.head(100),
                use_container_width=True
            )

            st.metric("Total Records", len(data))

            st.write("Columns:", ", ".join(data.columns))

            st.download_button(
                "Download Dataset",
                data.to_csv(index=False),
                "uploaded_dataset.csv",
                "text/csv"
            )

    except Exception as e:
        st.error(f"Analysis error: {e}")

