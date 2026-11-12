
import streamlit as st

from core.rescue_engine import (
    generate_rescue_recommendations,
    get_supported_traits
)


def show_rescue_recommendations():

    # ---------------- PAGE HEADER ----------------

    st.title("🌱 Genetic Rescue Recommendation Engine")

    st.write(
        "Explore potential genetic improvement strategies "
        "based on selected crop traits."
    )

    # ---------------- USER INPUT ----------------

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
        placeholder=(
            "Enter relevant published findings or "
            "dataset observations."
        )
    )

    st.caption(
        "Provide candidate genes and supporting evidence "
        "to help contextualize the recommendations."
    )

    # ---------------- GENERATE RECOMMENDATIONS ----------------

    if st.button(
        "🌱 Generate Rescue Recommendations",
        use_container_width=True
    ):

        genes = [
            gene.strip()
            for gene in gene_input.split(",")
            if gene.strip()
        ]

        evidence = [
            evidence_input.strip()
        ] if evidence_input.strip() else []

        try:

            with st.spinner(
                "Generating crop improvement recommendations..."
            ):

                result = generate_rescue_recommendations(
                    trait,
                    candidate_genes=genes,
                    supporting_evidence=evidence
                )

            # ---------------- SAVE FOR PDF REPORT ----------------

            st.session_state["rescue_report_data"] = {
                "trait": result["selected_trait"],
                "recommended_strategies": result["recommended_strategies"],
                "validation_methods": result["validation_methods"],
                "candidate_genes": result["candidate_genes"],
                "research_area": result["research_area"],
                "confidence": result["confidence"],
                "disclaimer": result["disclaimer"]
            }

            st.session_state["rescue_display_data"] = result

        except Exception as e:

            st.error(
                f"Recommendation generation failed: {e}"
            )

            return

    # ---------------- DISPLAY SAVED RESULTS ----------------

    result = st.session_state.get("rescue_display_data")

    if result is None:
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
                <p style="color:#174C35;font-weight:600;margin:0;">
                    🌱 Select a research objective and generate
                    recommendations to begin.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # ---------------- RESEARCH OBJECTIVE ----------------

    st.divider()

    st.subheader("Research Objective")

    st.markdown(
        f"""
        <div style="
            background-color:#E5F3E9;
            border:1px solid #A9D2B5;
            border-left:5px solid #32865B;
            border-radius:10px;
            padding:16px;
        ">
            <span style="color:#174C35;font-weight:700;">
                {result["selected_trait"]}
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write(
        f"**Research area:** {result['research_area']}"
    )

    # ---------------- CANDIDATE GENES ----------------

    st.subheader("Candidate Genes")

    candidate_genes = result["candidate_genes"]

    if candidate_genes:

        gene_columns = st.columns(min(len(candidate_genes), 3))

        for index, gene in enumerate(candidate_genes):

            with gene_columns[index % len(gene_columns)]:

                st.markdown(
                    f"""
                    <div style="
                        background-color:#FFFFFF;
                        border:1px solid #D7E4D9;
                        border-radius:9px;
                        padding:14px;
                        margin-bottom:10px;
                    ">
                        <span style="color:#174C35;font-weight:600;">
                            🧬 {gene}
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.caption("No candidate genes supplied.")

    # ---------------- IMPROVEMENT STRATEGIES ----------------

    st.subheader("Potential Improvement Strategies")

    strategies = result["recommended_strategies"]

    for index, strategy in enumerate(strategies, start=1):

        st.markdown(
            f"""
            <div style="
                background-color:#FFFFFF;
                border:1px solid #D7E4D9;
                border-left:4px solid #32865B;
                border-radius:9px;
                padding:14px 16px;
                margin-bottom:10px;
            ">
                <span style="
                    color:#174C35;
                    font-weight:700;
                ">
                    Strategy {index}
                </span>
                <p style="
                    color:#20352A;
                    margin:6px 0 0 0;
                    line-height:1.6;
                ">
                    {strategy}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- EXPERIMENTAL VALIDATION ----------------

    st.subheader("Suggested Experimental Validation")

    methods = result["validation_methods"]

    for index, method in enumerate(methods, start=1):

        st.markdown(
            f"""
            <div style="
                background-color:#EFF6F0;
                border:1px solid #D7E4D9;
                border-radius:9px;
                padding:12px 16px;
                margin-bottom:9px;
            ">
                <span style="color:#174C35;font-weight:600;">
                    {index}. {method}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ---------------- EVIDENCE STATUS ----------------

    st.subheader("Evidence Status")

    st.markdown(
        f"""
        <div style="
            background-color:#E8F1FA;
            border:1px solid #B8D0E8;
            border-left:5px solid #3978A8;
            border-radius:9px;
            padding:15px;
        ">
            <p style="color:#214B70;margin:0;font-weight:600;">
                {result["confidence"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- SCIENTIFIC DISCLAIMER ----------------

    st.markdown(
        f"""
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
                line-height:1.6;
            ">
                {result["disclaimer"]}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ---------------- PDF REPORT LINK ----------------

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
                ✓ Recommendations saved for Research Report generation.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
