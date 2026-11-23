import pandas as pd

from core.gene_identification import identify_orfs
from core.variant_analysis import analyze_variants, summarize_variants
from core.sequence_analysis import analyze_sequence


def test_orf_identification_finds_candidate():
    sequence = "ATG" + "AAA" * 10 + "TAA"
    results = identify_orfs(sequence, min_amino_acids=5)
    assert results
    assert results[0]["Amino_Acid_Length"] >= 5


def test_variant_classification_summary():
    data = pd.DataFrame({
        "REF": ["A", "AT", "G"],
        "ALT": ["G", "A", "T"],
        "POS": [10, 20, 30],
    })
    result = analyze_variants(data)
    summary = summarize_variants(result)
    assert summary["total_variants"] == 3
    assert summary["snp_count"] == 2
    assert summary["deletion_count"] == 1


def test_sequence_statistics():
    result = analyze_sequence("ATGCATGC")
    assert result["length"] == 8
    assert result["GC_percentage"] == 50.0

