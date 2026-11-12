
from Bio.Seq import Seq


START_CODONS = {"ATG"}
STOP_CODONS = {"TAA", "TAG", "TGA"}


def identify_orfs(sequence, min_amino_acids=30):
    """
    Identify potential ORFs across six reading frames.
    Coordinates are 1-based and inclusive.
    """

    sequence = sequence.upper().replace(" ", "").replace("\n", "")

    invalid = set(sequence) - set("ATGCN")

    if invalid:
        raise ValueError(f"Invalid DNA characters: {invalid}")

    if min_amino_acids < 1:
        raise ValueError("Minimum amino acid length must be positive.")

    results = []
    strand_sequences = [
        ("+", sequence),
        ("-", str(Seq(sequence).reverse_complement()))
    ]

    for strand, dna in strand_sequences:
        for frame in range(3):
            start_positions = []

            for position in range(frame, len(dna) - 2, 3):
                codon = dna[position:position + 3]

                if codon in START_CODONS:
                    start_positions.append(position)

                elif codon in STOP_CODONS:
                    for start in start_positions:
                        nucleotide_length = position + 3 - start
                        amino_acid_length = nucleotide_length // 3 - 1

                        if amino_acid_length >= min_amino_acids:
                            if strand == "+":
                                start_coord = start + 1
                                end_coord = position + 3
                            else:
                                start_coord = len(sequence) - (position + 2)
                                end_coord = len(sequence) - start

                            results.append({
                                "ORF_ID": f"ORF_{len(results) + 1}",
                                "Strand": strand,
                                "Frame": frame + 1,
                                "Start": start_coord,
                                "End": end_coord,
                                "Nucleotide_Length": nucleotide_length,
                                "Amino_Acid_Length": amino_acid_length,
                                "Protein_Sequence": str(
                                    Seq(dna[start:position + 3]).translate(
                                        to_stop=True
                                    )
                                )
                            })

                    start_positions = []

    return results


def identify_multiple_orfs(sequences, min_amino_acids=30):
    """Identify candidate ORFs in multiple FASTA records."""

    all_results = []

    for record in sequences:
        orfs = identify_orfs(
            record["sequence"],
            min_amino_acids
        )

        for orf in orfs:
            orf["Sequence_ID"] = record["id"]
            all_results.append(orf)

    return all_results

