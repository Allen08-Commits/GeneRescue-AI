
TRAIT_STRATEGIES = {
    "Drought Tolerance": {
        "research_area": "Water stress response",
        "strategies": [
            "Investigate genes involved in ABA-mediated stress signaling.",
            "Evaluate root architecture and water-use efficiency traits.",
            "Examine osmoprotectant biosynthesis pathways.",
            "Investigate regulatory responses to water limitation."
        ],
        "validation": [
            "Controlled drought stress experiments",
            "Gene expression analysis",
            "Physiological measurements"
        ]
    },

    "Salinity Tolerance": {
        "research_area": "Salt stress response",
        "strategies": [
            "Investigate sodium and potassium transport mechanisms.",
            "Examine ion homeostasis-related pathways.",
            "Evaluate osmotic adjustment mechanisms.",
            "Study salt-responsive regulatory networks."
        ],
        "validation": [
            "Controlled salinity experiments",
            "Ion concentration measurements",
            "Gene expression analysis"
        ]
    },

    "Disease Resistance": {
        "research_area": "Plant-pathogen interaction",
        "strategies": [
            "Investigate plant immune receptor candidates.",
            "Examine pathogen recognition pathways.",
            "Study defense signaling and response genes.",
            "Evaluate candidate genes using pathogen-specific evidence."
        ],
        "validation": [
            "Pathogen challenge experiments",
            "Disease severity measurements",
            "Molecular expression studies"
        ]
    },

    "Yield Improvement": {
        "research_area": "Growth and productivity",
        "strategies": [
            "Investigate genes involved in flowering regulation.",
            "Examine grain or fruit development pathways.",
            "Study source-sink relationships.",
            "Evaluate plant architecture and biomass traits."
        ],
        "validation": [
            "Field-based yield trials",
            "Growth and development measurements",
            "Multi-environment evaluation"
        ]
    }
}


def generate_rescue_recommendations(
    trait,
    candidate_genes=None,
    supporting_evidence=None
):
    """Generate research-oriented genetic improvement suggestions."""

    if trait not in TRAIT_STRATEGIES:
        raise ValueError("Unsupported crop improvement trait.")

    information = TRAIT_STRATEGIES[trait]

    genes = candidate_genes or []
    evidence = supporting_evidence or []

    return {
        "selected_trait": trait,
        "research_area": information["research_area"],
        "candidate_genes": genes,
        "supporting_evidence": evidence,
        "recommended_strategies": information["strategies"],
        "validation_methods": information["validation"],
        "confidence": (
            "Evidence supplied for review"
            if evidence
            else "Preliminary research suggestions; no supporting evidence supplied"
        ),
        "disclaimer": (
            "These recommendations are research hypotheses. "
            "Experimental validation is required before implementation."
        )
    }


def get_supported_traits():
    """Return the available crop improvement traits."""
    return list(TRAIT_STRATEGIES.keys())

