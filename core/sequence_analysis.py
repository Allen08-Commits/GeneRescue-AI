
from Bio.SeqUtils import gc_fraction
from collections import Counter


VALID_DNA = set("ATGCN")


def validate_sequence(sequence):
    """Check whether a sequence contains valid DNA characters."""
    sequence = sequence.upper().replace(" ", "").replace("\n", "")

    invalid = set(sequence) - VALID_DNA

    return {
        "valid": len(sequence) > 0 and len(invalid) == 0,
        "invalid_characters": sorted(invalid),
        "length": len(sequence)
    }


def analyze_sequence(sequence):
    """Calculate basic DNA sequence characteristics."""
    sequence = sequence.upper().replace(" ", "").replace("\n", "")

    validation = validate_sequence(sequence)

    if not validation["valid"]:
        raise ValueError(
            f"Invalid DNA sequence characters: "
            f"{validation['invalid_characters']}"
        )

    counts = Counter(sequence)
    length = len(sequence)

    gc_percent = gc_fraction(sequence) * 100

    at_percent = (
        (counts["A"] + counts["T"]) / length
    ) * 100

    return {
        "length": length,
        "A": counts["A"],
        "T": counts["T"],
        "G": counts["G"],
        "C": counts["C"],
        "N": counts["N"],
        "GC_percentage": round(gc_percent, 2),
        "AT_percentage": round(at_percent, 2)
    }


def analyze_multiple_sequences(sequences):
    """Analyze multiple FASTA sequences."""
    results = []

    for record in sequences:
        result = analyze_sequence(record["sequence"])

        result["sequence_id"] = record["id"]
        results.append(result)

    return results

