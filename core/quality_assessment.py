
def assess_sequence_quality(sequence):
    """Evaluate basic sequence quality indicators."""

    sequence = sequence.upper().replace(" ", "").replace("\n", "")
    length = len(sequence)

    if length == 0:
        return {
            "quality": "Invalid",
            "score": 0,
            "issues": ["Empty sequence"]
        }

    allowed = set("ATGCN")
    invalid = set(sequence) - allowed

    if invalid:
        return {
            "quality": "Invalid",
            "score": 0,
            "issues": [f"Invalid characters: {sorted(invalid)}"]
        }

    n_count = sequence.count("N")
    ambiguous_percentage = (n_count / length) * 100

    gc_count = sequence.count("G") + sequence.count("C")
    gc_percentage = (gc_count / length) * 100

    issues = []
    score = 100

    if ambiguous_percentage > 5:
        score -= 30
        issues.append("High ambiguous nucleotide content")

    elif ambiguous_percentage > 1:
        score -= 10
        issues.append("Moderate ambiguous nucleotide content")

    if length < 100:
        score -= 20
        issues.append("Short sequence length")

    if gc_percentage < 20 or gc_percentage > 80:
        score -= 15
        issues.append("Unusual GC composition")

    score = max(0, score)

    if score >= 85:
        quality = "High"
    elif score >= 60:
        quality = "Moderate"
    else:
        quality = "Low"

    if not issues:
        issues.append("No major basic quality concerns detected")

    return {
        "quality": quality,
        "score": score,
        "length": length,
        "GC_percentage": round(gc_percentage, 2),
        "ambiguous_percentage": round(ambiguous_percentage, 2),
        "issues": issues
    }


def assess_multiple_sequences(sequences):
    """Assess quality across multiple sequences."""

    results = []

    for record in sequences:
        result = assess_sequence_quality(record["sequence"])
        result["sequence_id"] = record["id"]
        results.append(result)

    return results

