
import streamlit as st
import pandas as pd

from core.data_loader import load_fasta
from core.gene_identification import identify_multiple_orfs


def show_gene_identification():

    # ---------------- PAGE HEADER ----------------

    st.title("🔬 Gene Identification Engine")

    st.write(
        "Identify potential open reading frames from uploaded "
        "DNA sequences."
    )

    # ---------------- FILE UPLOAD ----------------

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

    if uploaded_file is None:

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
                    🧬 Upload a FASTA file to identify candidate ORFs.
                </p>
                <p style="color:#52675A;font-size:13px;margin:6px 0 0 0;">
                    Adjust the minimum protein length to control
                    which predicted coding regions are reported.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(
            "Supported formats: FASTA, FA and FNA."
        )

        return

    # ---------------- SEQUENCE LOADING ----------------

    try:

        sequences = load_fasta(uploaded_file)

        if not sequences:
            st.warning("No sequences were found in the uploaded file.")
            return

        st.markdown(
            f"""
            <div style="
                background-color:#E5F3E9;
                border:1px solid #A9D2B5;
                border-radius:9px;
                padding:14px 18px;
                margin:12px 0;
            ">
                <span style="color:#174C35;font-weight:600;">
                    ✓ {len(sequences)} sequences successfully loaded.
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader("Sequence Input Summary")

        st.metric(
            "Sequences Loaded",
            len(sequences)
        )

        # ---------------- ORF IDENTIFICATION ----------------

        if st.button(
            "🧬 Identify Candidate ORFs",
            use_container_width=True
        ):

            with st.spinner("Identifying candidate open reading frames..."):

                results = identify_multiple_orfs(
                    sequences,
                    min_amino_acids=min_length
                )

            if results:

                df = pd.DataFrame(results)

                if df.empty:
                    st.warning("No candidate ORFs were identified.")
                    return

                st.session_state["gene_orf_results"] = df

            else:

                st.session_state["gene_orf_results"] = pd.DataFrame()

        # ---------------- DISPLAY RESULTS ----------------

        if "gene_orf_results" in st.session_state:

            df = st.session_state["gene_orf_results"]

            if df.empty:

                st.warning(
                    "No candidate ORFs found with the selected "
                    "minimum protein length. Try reducing the slider value."
                )

                return

            st.divider()

            st.subheader("Candidate ORF Results")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Potential ORFs Identified",
                    len(df)
                )

            with col2:
                if "Nucleotide_Length" in df.columns:
                    st.metric(
                        "Average ORF Length",
                        f"{df['Nucleotide_Length'].mean():,.0f} bp"
                    )

            with col3:
                if "Amino_Acid_Length" in df.columns:
                    st.metric(
                        "Average Protein Length",
                        f"{df['Amino_Acid_Length'].mean():,.0f} aa"
                    )

            # Hide protein sequence from the main results table
            display_df = df.drop(
                columns=["Protein_Sequence"],
                errors="ignore"
            )

            # Give long identifiers more room
            column_config = {}

            if "Sequence_ID" in display_df.columns:
                column_config["Sequence_ID"] = (
                    st.column_config.TextColumn(
                        "Sequence ID",
                        width="large"
                    )
                )

            if "ORF_ID" in display_df.columns:
                column_config["ORF_ID"] = (
                    st.column_config.TextColumn(
                        "ORF ID",
                        width="medium"
                    )
                )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config=column_config
            )

            # ---------------- PROTEIN SEQUENCES ----------------

            if "Protein_Sequence" in df.columns:

                with st.expander("🧬 View Predicted Protein Sequences"):

                    protein_columns = [
                        column for column in [
                            "ORF_ID",
                            "Sequence_ID",
                            "Protein_Sequence"
                        ]
                        if column in df.columns
                    ]

                    protein_df = df[protein_columns]

                    st.dataframe(
                        protein_df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Sequence_ID": st.column_config.TextColumn(
                                "Sequence ID",
                                width="large"
                            ),
                            "Protein_Sequence": st.column_config.TextColumn(
                                "Predicted Protein Sequence",
                                width="large"
                            )
                        }
                    )

            # ---------------- DOWNLOAD RESULTS ----------------

            st.divider()

            st.subheader("Download Results")

            st.download_button(
                "⬇️ Download ORF Results CSV",
                df.to_csv(index=False),
                "candidate_orfs.csv",
                "text/csv",
                use_container_width=True
            )

            # ---------------- SCIENTIFIC DISCLAIMER ----------------

            st.markdown(
                """
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
                    ">
                        ORFs are computationally identified candidate
                        coding regions. They are not experimentally
                        confirmed genes or validated protein products.
                        Further biological validation is required.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

    except Exception as e:

        st.error(f"Gene identification failed: {e}")

        st.caption(
            "Check the FASTA file format and sequence contents, "
            "then try again."
        )
