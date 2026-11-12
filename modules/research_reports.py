
import streamlit as st
import pandas as pd

from core.report_generator import generate_pdf_report


def show_research_reports():

    st.title("📑 Research Report Generator")

    st.write(
        "Generate downloadable scientific reports "
        "from GeneRescue AI analysis results."
    )

    trait = st.selectbox(
        "Select research trait",
        [
            "Drought Tolerance",
            "Salinity Tolerance",
            "Disease Resistance",
            "Yield Improvement"
        ]
    )

    sequence_file = st.file_uploader(
        "Upload sequence analysis CSV (optional)",
        type=["csv"],
        key="report_sequence"
    )

    gene_file = st.file_uploader(
        "Upload candidate ORF results CSV (optional)",
        type=["csv"],
        key="report_genes"
    )

    variant_file = st.file_uploader(
        "Upload variant analysis CSV (optional)",
        type=["csv"],
        key="report_variants"
    )

    sequence_results = None
    gene_results = None
    variant_summary = None

    # Retrieve saved rescue recommendations.
    saved_recommendations = st.session_state.get(
        "rescue_report_data"
    )

    recommendations = None

    if saved_recommendations:

        if saved_recommendations["trait"] == trait:

            recommendations = {
                "recommended_strategies":
                    saved_recommendations["recommended_strategies"],

                "validation_methods":
                    saved_recommendations["validation_methods"]
            }

            st.success(
                "Previously generated rescue recommendations "
                "found and linked to this report."
            )

        else:
            st.warning(
                "Saved recommendations are for "
                f"{saved_recommendations['trait']}. "
                "Generate recommendations for {trait} "
                "before including them in this report."
            )

    else:
        st.info(
            "No saved rescue recommendations found. "
            "Generate them in the Rescue Recommendations module first."
        )

    try:

        if sequence_file:
            sequence_results = pd.read_csv(
                sequence_file
            ).to_dict("records")

        if gene_file:
            gene_results = pd.read_csv(
                gene_file
            ).to_dict("records")

        if variant_file:

            variants = pd.read_csv(variant_file)

            if "Variant_Type" not in variants.columns:
                st.error(
                    "Upload the processed variant analysis CSV."
                )
                return

            counts = variants["Variant_Type"].value_counts().to_dict()

            variant_summary = {
                "total_variants": len(variants),
                "variant_types": counts
            }

        if st.button("Generate PDF Research Report"):

            pdf = generate_pdf_report(
                trait=trait,
                sequence_results=sequence_results,
                gene_results=gene_results,
                variant_summary=variant_summary,
                recommendations=recommendations
            )

            st.success("PDF report generated successfully!")

            st.download_button(
                "📥 Download GeneRescue AI Report",
                data=pdf,
                file_name="GeneRescue_AI_Report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Report generation failed: {e}")
