
import streamlit as st
import pandas as pd

from core.report_generator import generate_pdf_report


def show_research_reports():

    # ---------------- PAGE HEADER ----------------

    st.title("📑 Research Report Generator")

    st.write(
        "Generate downloadable scientific reports "
        "from GeneRescue AI analysis results."
    )

    # ---------------- RESEARCH TRAIT ----------------

    trait = st.selectbox(
        "Select research trait",
        [
            "Drought Tolerance",
            "Salinity Tolerance",
            "Disease Resistance",
            "Yield Improvement"
        ],
        key="report_trait"
    )

    # ---------------- FILE UPLOADS ----------------

    st.subheader("Upload Analysis Results")

    col1, col2 = st.columns(2)

    with col1:
        sequence_file = st.file_uploader(
            "Sequence analysis CSV (optional)",
            type=["csv"],
            key="report_sequence"
        )

        gene_file = st.file_uploader(
            "Candidate ORF results CSV (optional)",
            type=["csv"],
            key="report_genes"
        )

    with col2:
        variant_file = st.file_uploader(
            "Variant analysis CSV (optional)",
            type=["csv"],
            key="report_variants"
        )

    # ---------------- RECOMMENDATION INTEGRATION ----------------

    saved_recommendations = st.session_state.get(
        "rescue_report_data"
    )

    recommendations = None

    st.subheader("Rescue Recommendation Integration")

    if saved_recommendations:

        if saved_recommendations.get("trait") == trait:

            recommendations = {
                "recommended_strategies":
                    saved_recommendations.get(
                        "recommended_strategies", []
                    ),
                "validation_methods":
                    saved_recommendations.get(
                        "validation_methods", []
                    )
            }

            st.markdown(
                """
                <div style="
                    background-color:#E5F3E9;
                    border:1px solid #A9D2B5;
                    border-left:5px solid #32865B;
                    border-radius:9px;
                    padding:14px;
                ">
                    <p style="color:#174C35;font-weight:600;margin:0;">
                        ✓ Previously generated rescue recommendations
                        are linked to this report.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        else:

            st.warning(
                f"Saved recommendations are for "
                f"{saved_recommendations.get('trait')}. "
                f"Generate recommendations for {trait} "
                "before including them in this report."
            )

    else:

        st.info(
            "No saved rescue recommendations found. "
            "Generate them in the Rescue Recommendations module first."
        )

    # ---------------- READ UPLOADED FILES ----------------

    sequence_results = None
    gene_results = None
    variant_summary = None

    try:

        if sequence_file:

            sequence_df = pd.read_csv(sequence_file)

            sequence_results = sequence_df.to_dict(
                orient="records"
            )

        if gene_file:

            gene_df = pd.read_csv(gene_file)

            gene_results = gene_df.to_dict(
                orient="records"
            )

        if variant_file:

            variants = pd.read_csv(variant_file)

            if "Variant_Type" not in variants.columns:

                st.error(
                    "The uploaded file must contain a "
                    "'Variant_Type' column. Upload the processed "
                    "variant analysis CSV."
                )

                return

            counts = (
                variants["Variant_Type"]
                .value_counts()
                .to_dict()
            )

            variant_summary = {
                "total_variants": len(variants),
                "variant_types": counts
            }

        # ---------------- REPORT CONTENT PREVIEW ----------------

        st.divider()

        st.subheader("Report Content Preview")

        preview_items = [
            ("Research trait", trait),
            (
                "Sequence analysis",
                "Included" if sequence_file else "Not uploaded"
            ),
            (
                "Candidate ORF results",
                "Included" if gene_file else "Not uploaded"
            ),
            (
                "Variant analysis",
                "Included" if variant_file else "Not uploaded"
            ),
            (
                "Rescue recommendations",
                "Included" if recommendations else "Not available"
            )
        ]

        preview_df = pd.DataFrame(
            preview_items,
            columns=["Report Component", "Status"]
        )

        st.dataframe(
            preview_df,
            use_container_width=True,
            hide_index=True
        )

        # ---------------- PDF GENERATION ----------------

        st.divider()

        if st.button(
            "📄 Generate PDF Research Report",
            use_container_width=True
        ):

            with st.spinner("Generating scientific PDF report..."):

                pdf = generate_pdf_report(
                    trait=trait,
                    sequence_results=sequence_results,
                    gene_results=gene_results,
                    variant_summary=variant_summary,
                    recommendations=recommendations
                )

            if not pdf:
                st.error(
                    "The report generator returned an empty PDF."
                )
                return

            st.session_state["generated_research_pdf"] = pdf
            st.session_state["generated_research_trait"] = trait

        # ---------------- DOWNLOAD REPORT ----------------

        generated_pdf = st.session_state.get(
            "generated_research_pdf"
        )

        generated_trait = st.session_state.get(
            "generated_research_trait"
        )

        if generated_pdf and generated_trait == trait:

            st.markdown(
                """
                <div style="
                    background-color:#E5F3E9;
                    border:1px solid #A9D2B5;
                    border-radius:9px;
                    padding:14px;
                    margin-top:15px;
                ">
                    <p style="color:#174C35;font-weight:600;margin:0;">
                        ✓ PDF research report generated successfully.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.download_button(
                "📥 Download GeneRescue AI Report",
                data=generated_pdf,
                file_name="GeneRescue_AI_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"Report generation failed: {e}"
        )

        st.caption(
            "Check the uploaded CSV files and their column structure."
        )
