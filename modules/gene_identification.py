
import streamlit as st
import pandas as pd

from core.data_loader import load_fasta
from core.gene_identification import identify_multiple_orfs


def show_gene_identification():

    st.title("🔬 Gene Identification Engine")

    st.write(
        "Identify potential open reading frames from uploaded "
        "DNA sequences."
    )

    uploaded_file = st.file_uploader(
        "Upload FASTA file",
        type=["fasta", "fa", "fna"],
        key="gene_fasta"
    )

    min_length = st.slider(
        "Minimum ORF protein length (amino acids)",
        min_value=10,
        max_value=200,
        value=30
    )

    if uploaded_file:

        try:
            sequences = load_fasta(uploaded_file)

            st.success(
                f"{len(sequences)} sequences successfully loaded."
            )

            if st.button("Identify Candidate ORFs"):

                results = identify_multiple_orfs(
                    sequences,
                    min_amino_acids=min_length
                )

                if results:

                    df = pd.DataFrame(results)

                    st.subheader("Candidate ORF Results")

                    st.metric(
                        "Potential ORFs Identified",
                        len(df)
                    )

                    st.dataframe(
                        df.drop(columns=["Protein_Sequence"]),
                        use_container_width=True
                    )

                    with st.expander("View predicted protein sequences"):
                        st.dataframe(
                            df[[
                                "ORF_ID",
                                "Sequence_ID",
                                "Protein_Sequence"
                            ]],
                            use_container_width=True
                        )

                    st.download_button(
                        "Download ORF Results",
                        df.to_csv(index=False),
                        "candidate_orfs.csv",
                        "text/csv"
                    )

                else:
                    st.warning(
                        "No candidate ORFs found with the selected "
                        "minimum length."
                    )

        except Exception as e:
            st.error(f"Gene identification failed: {e}")

    st.caption(
        "ORFs are computationally identified candidate coding "
        "regions, not experimentally confirmed genes."
    )

