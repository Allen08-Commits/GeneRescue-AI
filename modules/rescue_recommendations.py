
import streamlit as st

from core.rescue_engine import (
    generate_rescue_recommendations,
    get_supported_traits
)


def show_rescue_recommendations():

    st.title("🌱 Genetic Rescue Recommendation Engine")

    st.write(
        "Explore potential genetic improvement strategies "
        "based on selected crop traits."
    )

    trait = st.selectbox(
        "Select crop improvement objective",
        get_supported_traits()
    )

    gene_input = st.text_area(
        "Candidate gene IDs (optional)",
        placeholder="Example: Gene_001, Gene_002"
    )

    evidence_input = st.text_area(
        "Supporting research evidence (optional)",
        placeholder="Enter relevant published findings or dataset observations."
    )

    if st.button("Generate Rescue Recommendations"):

        genes = [
            gene.strip()
            for gene in gene_input.split(",")
            if gene.strip()
        ]

        evidence = [
            evidence_input.strip()
        ] if evidence_input.strip() else []

        try:

            result = generate_rescue_recommendations(
                trait,
                candidate_genes=genes,
                supporting_evidence=evidence
            )

            st.subheader("Research Objective")
            st.success(result["selected_trait"])

            st.write("Research area:", result["research_area"])

            st.subheader("Candidate Genes")

            if result["candidate_genes"]:
                for gene in result["candidate_genes"]:
                    st.write("🧬", gene)
            else:
                st.info("No candidate genes supplied.")

            st.subheader("Potential Improvement Strategies")

            for strategy in result["recommended_strategies"]:
                st.markdown(f"- {strategy}")

            st.subheader("Suggested Experimental Validation")

            for method in result["validation_methods"]:
                st.markdown(f"- {method}")

            st.subheader("Evidence Status")
            st.info(result["confidence"])

            st.warning(result["disclaimer"])

        except Exception as e:
            st.error(f"Recommendation generation failed: {e}")

