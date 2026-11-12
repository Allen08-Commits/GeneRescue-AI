
import streamlit as st
import pandas as pd
import plotly.express as px

from core.data_loader import load_dataset
from core.variant_analysis import (
    analyze_variants,
    summarize_variants
)


def show_variant_analysis():

    st.title("🧪 Genetic Variant Analysis")

    st.write(
        "Investigate genetic variations using uploaded CSV or VCF files."
    )

    uploaded_file = st.file_uploader(
        "Upload variant dataset",
        type=["csv", "vcf"],
        key="variant_upload"
    )

    if uploaded_file:

        try:
            data = load_dataset(uploaded_file)

            if not isinstance(data, pd.DataFrame):
                st.error("Please upload a CSV or VCF variant dataset.")
                return

            if data.empty:
                st.warning("The uploaded dataset contains no variants.")
                return

            results = analyze_variants(data)
            summary = summarize_variants(data)

            st.subheader("Variant Summary")

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Total Variants", summary["total_variants"])
            col2.metric("SNPs", summary["snp_count"])
            col3.metric("Insertions", summary["insertion_count"])
            col4.metric("Deletions", summary["deletion_count"])

            st.subheader("Variant Classification")

            chart_data = pd.DataFrame(
                list(summary["variant_types"].items()),
                columns=["Variant Type", "Count"]
            )

            if not chart_data.empty:

                fig = px.pie(
                    chart_data,
                    names="Variant Type",
                    values="Count",
                    hole=0.4,
                    title="Distribution of Genetic Variants"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            st.subheader("Detailed Variant Results")

            st.dataframe(
                results,
                use_container_width=True
            )

            st.download_button(
                "Download Variant Analysis",
                results.to_csv(index=False),
                "variant_analysis.csv",
                "text/csv"
            )

            st.info(
                "Structural classification does not establish "
                "whether a variant is harmful, beneficial or "
                "functionally significant."
            )

        except Exception as e:
            st.error(f"Variant analysis failed: {e}")

    else:
        st.info("Upload a variant dataset to start.")

