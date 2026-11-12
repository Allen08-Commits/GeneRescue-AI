
import pandas as pd
from Bio import SeqIO
from io import StringIO


def load_fasta(file):
    """Read DNA or protein sequences from a FASTA file."""
    try:
        content = file.getvalue().decode("utf-8")
        records = list(SeqIO.parse(StringIO(content), "fasta"))

        if not records:
            raise ValueError("No FASTA sequences found.")

        return [
            {
                "id": record.id,
                "description": record.description,
                "sequence": str(record.seq).upper()
            }
            for record in records
        ]

    except Exception as e:
        raise ValueError(f"FASTA loading failed: {e}")


def load_csv(file):
    """Read a CSV dataset."""
    try:
        return pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"CSV loading failed: {e}")


def load_vcf(file):
    """Read basic VCF variant records without external VCF dependencies."""
    try:
        content = file.getvalue().decode("utf-8")
        records = []

        for line in content.splitlines():
            if not line or line.startswith("##"):
                continue

            if line.startswith("#CHROM"):
                continue

            columns = line.split("\t")

            if len(columns) < 8:
                continue

            records.append({
                "CHROM": columns[0],
                "POS": int(columns[1]),
                "ID": columns[2],
                "REF": columns[3],
                "ALT": columns[4],
                "QUAL": columns[5],
                "FILTER": columns[6],
                "INFO": columns[7]
            })

        return pd.DataFrame(records)

    except Exception as e:
        raise ValueError(f"VCF loading failed: {e}")


def load_dataset(file):
    """Automatically identify and load supported file types."""
    filename = file.name.lower()

    if filename.endswith((".fasta", ".fa", ".fna", ".faa")):
        return load_fasta(file)

    elif filename.endswith(".csv"):
        return load_csv(file)

    elif filename.endswith(".vcf"):
        return load_vcf(file)

    else:
        raise ValueError(
            "Unsupported file format. Upload FASTA, CSV or VCF."
        )

