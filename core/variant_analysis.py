
import pandas as pd


def classify_variant(ref, alt):
    """Classify a variant using reference and alternate allele lengths."""

    ref = str(ref).upper()
    alt = str(alt).upper()

    if alt in {"", ".", "NAN"} or ref in {"", ".", "NAN"}:
        return "Unknown"

    if len(ref) == 1 and len(alt) == 1:
        return "SNP"

    if len(ref) < len(alt):
        return "Insertion"

    if len(ref) > len(alt):
        return "Deletion"

    return "Complex substitution"


def analyze_variants(data):
    """Perform basic structural analysis of variant records."""

    if data is None or len(data) == 0:
        return pd.DataFrame()

    df = data.copy()

    required = {"REF", "ALT"}

    if not required.issubset(df.columns):
        raise ValueError("Dataset must contain REF and ALT columns.")

    df["Variant_Type"] = df.apply(
        lambda row: classify_variant(row["REF"], row["ALT"]),
        axis=1
    )

    if "POS" in df.columns:
        df["POS"] = pd.to_numeric(df["POS"], errors="coerce")

    df["Allele_Change"] = (
        df["REF"].astype(str) + ">" + df["ALT"].astype(str)
    )

    df["Interpretation"] = df["Variant_Type"].map({
        "SNP": "Single nucleotide substitution",
        "Insertion": "Additional nucleotide sequence",
        "Deletion": "Missing nucleotide sequence",
        "Complex substitution": "Length-preserving sequence replacement",
        "Unknown": "Insufficient allele information"
    })

    return df


def summarize_variants(data):
    """Generate descriptive statistics for variants."""

    analyzed = analyze_variants(data)

    if analyzed.empty:
        return {
            "total_variants": 0,
            "variant_types": {}
        }

    counts = analyzed["Variant_Type"].value_counts().to_dict()

    return {
        "total_variants": len(analyzed),
        "variant_types": counts,
        "snp_count": counts.get("SNP", 0),
        "insertion_count": counts.get("Insertion", 0),
        "deletion_count": counts.get("Deletion", 0),
        "complex_count": counts.get("Complex substitution", 0)
    }

