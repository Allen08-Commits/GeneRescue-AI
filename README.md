# GeneRescue AI

GeneRescue AI is a Streamlit bioinformatics research workspace for crop-improvement research.

## Six research tools
1. Sequence Analysis
2. Gene Discovery
3. Variant Analysis
4. Database Explorer
5. Functional Annotation
6. Crop Intelligence

## Live public database integrations
- NCBI E-utilities: Gene, Nucleotide/RefSeq and PubMed searches; nucleotide FASTA retrieval.
- Ensembl Plants REST API: plant gene symbol cross-references, gene transcript lists and transcript cDNA sequence retrieval.
- UniProt REST API: protein searches, records and FASTA retrieval.
- InterPro API: protein family/domain matches.

Queries are made on demand. The app displays source provenance and retrieval timestamps where available. Network/API availability and rate limits are controlled by the source databases.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit Community Cloud
- Repository: your GitHub repository
- Branch: `main`
- Main file: `app.py`

Optional NCBI configuration can be supplied as environment variables or Streamlit secrets:
- `NCBI_EMAIL`
- `NCBI_API_KEY`

Do not commit credentials or private datasets.

## Data and scientific limitations
- Uploaded datasets are processed within the Streamlit session; this project does not require accounts or Supabase.
- No sample/demo datasets are bundled.
- ORFs are computational candidates, not experimentally confirmed genes.
- Variant classification is structural and does not establish pathogenicity or functional impact.
- Crop prediction is only as reliable as the supplied labeled dataset and validation design.
- Rescue suggestions are research hypotheses requiring experimental validation.
