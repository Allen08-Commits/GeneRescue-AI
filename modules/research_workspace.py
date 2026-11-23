"""GeneRescue AI research workspace: six tools, live database retrieval and reports."""
from __future__ import annotations

from datetime import datetime, timezone
from io import BytesIO, StringIO
import html

import pandas as pd
import plotly.express as px
import streamlit as st
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
from Bio.SeqUtils.ProtParam import ProteinAnalysis

from core.gene_identification import identify_orfs
from core.variant_analysis import analyze_variants, summarize_variants
from core.crop_prediction import train_crop_model, predict_crop_trait
from core.rescue_engine import generate_rescue_recommendations, get_supported_traits
from integrations.biological_databases import (
    DatabaseAPIError, ncbi_gene_search, ncbi_transcript_search,
    ncbi_fetch_fasta, ensembl_plant_search, ensembl_gene_transcripts,
    ensembl_transcript_cdna, uniprot_search, uniprot_entry, uniprot_fasta,
    interpro_search, pubmed_search,
)

TOOLS = [
    "Sequence Analysis", "Gene Discovery", "Variant Analysis",
    "Database Explorer", "Functional Annotation", "Crop Intelligence"
]

def _pdf_bytes(title: str, lines: list[str]) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.units import mm
    from xml.sax.saxutils import escape

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm,
                            topMargin=18*mm, bottomMargin=18*mm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("GRTitle", parent=styles["Title"], textColor=colors.HexColor("#20543A"),
                                 alignment=TA_CENTER, fontSize=20, spaceAfter=12)
    heading = ParagraphStyle("GRHeading", parent=styles["Heading2"], textColor=colors.HexColor("#20543A"))
    story = [Paragraph("GeneRescue AI", title_style), Paragraph(escape(title), heading),
             Paragraph("Generated: " + datetime.now(timezone.utc).isoformat(timespec="seconds"), styles["Normal"]),
             Spacer(1, 10)]
    for line in lines:
        story.append(Paragraph(escape(str(line)), styles["BodyText"]))
        story.append(Spacer(1, 5))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Research output is computational evidence, not experimental confirmation. Verify source records and validate biological interpretations independently.", styles["Italic"]))
    doc.build(story)
    return buffer.getvalue()

def _report(title, lines, key):
    try:
        payload = _pdf_bytes(title, lines)
        st.download_button("Download PDF report", payload,
                           file_name=f"GeneRescue_{key}.pdf", mime="application/pdf",
                           key=f"pdf_{key}")
    except Exception as exc:
        st.warning(f"PDF generation unavailable: {exc}")

def _provenance(prov):
    st.caption(f"Source: {prov.get('database','')} · Retrieved: {prov.get('retrieved_at_utc','')} · Query: {prov.get('query','')}")

def _fasta_records(upload):
    text = upload.getvalue().decode("utf-8-sig")
    records = list(SeqIO.parse(StringIO(text), "fasta"))
    if not records:
        raise ValueError("No FASTA records found. Check that the file uses FASTA headers beginning with '>'.")
    return [{"id": r.id, "description": r.description, "sequence": str(r.seq).upper()} for r in records]

def _read_variant_file(upload):
    name = upload.name.lower()
    if name.endswith(".vcf"):
        rows=[]
        for line in upload.getvalue().decode("utf-8-sig").splitlines():
            if not line or line.startswith("#"): continue
            parts=line.split("\t")
            if len(parts)>=8:
                for alt in parts[4].split(","):
                    rows.append({"CHROM":parts[0],"POS":parts[1],"ID":parts[2],
                                 "REF":parts[3],"ALT":alt,"QUAL":parts[5],
                                 "FILTER":parts[6],"INFO":parts[7]})
        return pd.DataFrame(rows)
    return pd.read_csv(upload)

def render_welcome():
    st.markdown("""
    <div class="gr-hero">
      <div class="gr-hero-mark">🌱</div>
      <div class="gr-eyebrow">BIOINFORMATICS RESEARCH WORKSPACE</div>
      <h1>GeneRescue AI</h1>
      <p>Intelligent Genetic Rescue System for Crop Improvement</p>
      <span>Explore sequences, discover candidate genes, investigate variants and retrieve evidence from live biological databases.</span>
    </div>
    """, unsafe_allow_html=True)
    st.write("")
    cols=st.columns(3)
    descriptions=[
        ("🧬","Sequence Analysis","DNA, RNA and protein sequence statistics"),
        ("🔬","Gene Discovery","Six-frame ORF identification"),
        ("🧪","Variant Analysis","Structural variant classification"),
        ("🌐","Database Explorer","NCBI, Ensembl Plants, UniProt and PubMed"),
        ("🧫","Functional Annotation","Protein records, domains and annotations"),
        ("🌾","Crop Intelligence","Trait research and labeled-data prediction"),
    ]
    for i,(icon,title,desc) in enumerate(descriptions):
        with cols[i%3]:
            st.markdown(f'<div class="gr-tool-card"><div class="gr-tool-icon">{icon}</div><b>{title}</b><p>{desc}</p></div>', unsafe_allow_html=True)
    if st.button("Open Research Workspace  →", type="primary", use_container_width=True):
        st.session_state["gr_started"]=True
        st.rerun()
    st.caption("No account required. Uploaded data and analysis history remain in the current Streamlit session.")

def render_sequence_analysis():
    st.subheader("Sequence Analysis")
    st.write("Analyze uploaded FASTA records or a sequence entered directly.")
    uploaded=st.file_uploader("Upload FASTA", type=["fa","fasta","fna","faa"], key="seq_fasta")
    seq_type=st.selectbox("Sequence type", ["DNA","RNA","Protein"], key="seq_type")
    pasted=st.text_area("Or paste a sequence", height=110, placeholder="Paste sequence letters only", key="seq_paste")
    records=[]
    try:
        if uploaded:
            records=_fasta_records(uploaded)
        elif pasted.strip():
            records=[{"id":"Pasted_sequence","description":"Pasted sequence","sequence":"".join(pasted.split()).upper()}]
    except Exception as exc:
        st.error(str(exc))
        return
    if not records:
        st.info("Upload a FASTA file or paste a sequence to begin.")
        return
    rows=[]
    for rec in records:
        seq=rec["sequence"]
        invalid=set(seq)-set("ATGCN" if seq_type=="DNA" else "AUGCN" if seq_type=="RNA" else "ABCDEFGHIKLMNPQRSTVWXYZ*")
        if invalid:
            st.warning(f"{rec['id']}: invalid symbols for {seq_type}: {', '.join(sorted(invalid))}")
            continue
        row={"Sequence ID":rec["id"],"Length":len(seq),"Type":seq_type}
        if seq_type in ("DNA","RNA"):
            normalized=seq.replace("U","T")
            row["GC (%)"]=round(gc_fraction(normalized)*100,2)
            bases = "ATGC" if seq_type == "DNA" else "AUGC"
            for base in bases:
                row[base] = seq.count(base)
            row["Ambiguous N"] = seq.count("N")
        else:
            try:
                analysis=ProteinAnalysis(seq.rstrip("*"))
                row["Molecular weight (Da)"]=round(analysis.molecular_weight(),2)
                row["Aromaticity"]=round(analysis.aromaticity(),4)
                row["Instability index"]=round(analysis.instability_index(),2)
                row["Isoelectric point"]=round(analysis.isoelectric_point(),2)
            except Exception as exc:
                row["Protein calculation note"]=str(exc)
        rows.append(row)
    if not rows:
        return
    df=pd.DataFrame(rows)
    st.dataframe(df,use_container_width=True,hide_index=True)
    st.metric("Sequences analyzed",len(df))
    st.download_button("Download analysis CSV",df.to_csv(index=False), "sequence_analysis.csv","text/csv")
    _report("Sequence Analysis", [f"{r['Sequence ID']}: length {r['Length']} ({r['Type']})" for r in rows], "sequence_analysis")
    if seq_type in ("DNA","RNA") and len(records)==1:
        seq=records[0]["sequence"]
        counts={b:seq.count(b) for b in ("A","T","U","G","C","N")}
        chart=pd.DataFrame({"Nucleotide":list(counts),"Count":list(counts.values())})
        st.plotly_chart(px.bar(chart,x="Nucleotide",y="Count",title="Nucleotide composition"),use_container_width=True)

def render_gene_discovery():
    st.subheader("Gene Discovery")
    st.write("Identify candidate open reading frames across six reading frames in uploaded DNA FASTA.")
    upload=st.file_uploader("Upload DNA FASTA",type=["fa","fasta","fna"],key="orf_fasta")
    minimum=st.number_input("Minimum ORF protein length (amino acids)",min_value=1,max_value=5000,value=30)
    if upload:
        try:
            records=_fasta_records(upload)
            chosen=st.selectbox("Select sequence", [r["id"] for r in records])
            record=next(r for r in records if r["id"]==chosen)
            if st.button("Identify candidate ORFs",type="primary"):
                results=identify_orfs(record["sequence"],int(minimum))
                st.session_state["gr_orf_results"]=results
                st.session_state["gr_orf_source"]=chosen
            results=st.session_state.get("gr_orf_results")
            if results is not None:
                if not results:
                    st.info("No ORFs met the selected minimum length.")
                else:
                    df=pd.DataFrame(results)
                    st.metric("Candidate ORFs",len(df))
                    st.dataframe(df.drop(columns=["Protein_Sequence"],errors="ignore"),use_container_width=True,hide_index=True)
                    st.download_button("Download ORF results CSV",df.to_csv(index=False),"candidate_orfs.csv","text/csv")
                    fasta="\n".join(f">{r['ORF_ID']}|{r['Strand']}|{r['Start']}-{r['End']}\n{r['Protein_Sequence']}" for r in results)
                    st.download_button("Download predicted protein FASTA",fasta,"candidate_orf_proteins.fasta","text/plain")
                    _report("Gene Discovery", [f"{r['ORF_ID']} {r['Strand']}:{r['Start']}-{r['End']} | {r['Amino_Acid_Length']} aa" for r in results], "gene_discovery")
                    with st.expander("Protein translations"):
                        for r in results[:30]:
                            st.code(f">{r['ORF_ID']}\n{r['Protein_Sequence']}")
        except Exception as exc:
            st.error(f"Gene discovery failed: {exc}")
    else:
        st.info("Upload a nucleotide FASTA file to identify candidate ORFs.")

def render_variant_analysis():
    st.subheader("Variant Analysis")
    st.write("Classify variants from VCF or CSV files. This module performs structural classification, not pathogenicity prediction.")
    upload=st.file_uploader("Upload VCF or CSV",type=["vcf","csv"],key="variant_upload")
    if upload:
        try:
            df=_read_variant_file(upload)
            if df.empty:
                st.warning("No variant records were found.")
                return
            analyzed=analyze_variants(df)
            summary=summarize_variants(analyzed)
            cols=st.columns(4)
            for col,(label,key) in zip(cols,[("Total","total_variants"),("SNPs","snp_count"),("Insertions","insertion_count"),("Deletions","deletion_count")]):
                col.metric(label,summary.get(key,0))
            st.dataframe(analyzed,use_container_width=True,hide_index=True)
            chart=pd.DataFrame(list(summary["variant_types"].items()),columns=["Variant type","Count"])
            if not chart.empty:
                st.plotly_chart(px.pie(chart,names="Variant type",values="Count",hole=.45,title="Variant type distribution"),use_container_width=True)
            st.download_button("Download annotated variants CSV",analyzed.to_csv(index=False),"annotated_variants.csv","text/csv")
            _report("Variant Analysis",[f"Total variants: {summary['total_variants']}"]+[f"{k}: {v}" for k,v in summary["variant_types"].items()],"variant_analysis")
        except Exception as exc:
            st.error(f"Variant analysis failed: {exc}")
            st.caption("CSV files must include REF and ALT columns. VCF files are parsed from their standard columns.")

def render_database_explorer():
    st.subheader("Live Database Explorer")
    st.write("Search public biological databases on demand. Results include source links and retrieval timestamps.")
    db=st.selectbox("Database",["NCBI Gene","NCBI Transcript / Nucleotide","Ensembl Plants","UniProtKB","PubMed"])
    query=st.text_input("Search term / gene symbol / accession",placeholder="e.g. OsNAC6, BRCA1, drought tolerance")
    organism=st.text_input("Organism filter (optional)",placeholder="e.g. Oryza sativa")
    limit=st.slider("Maximum records",1,30,10)
    species=st.selectbox("Ensembl Plants species",["oryza_sativa","zea_mays","triticum_aestivum","arabidopsis_thaliana","glycine_max","solanum_lycopersicum"],disabled=db!="Ensembl Plants")
    if st.button("Search live database",type="primary",disabled=not query.strip()):
        try:
            with st.spinner(f"Retrieving records from {db}..."):
                if db=="NCBI Gene": rows,prov=ncbi_gene_search(query,organism,limit)
                elif db=="NCBI Transcript / Nucleotide": rows,prov=ncbi_transcript_search(query,organism,limit)
                elif db=="Ensembl Plants": rows,prov=ensembl_plant_search(query,species)
                elif db=="UniProtKB": rows,prov=uniprot_search(query,limit)
                else: rows,prov=pubmed_search(query,limit)
            st.session_state["gr_db_rows"]=rows
            st.session_state["gr_db_prov"]=prov
            st.session_state["gr_db_name"]=db
            st.session_state["gr_db_query"]=query.strip()
        except Exception as exc:
            st.error(f"{db} request failed: {exc}")
    rows=st.session_state.get("gr_db_rows")
    prov=st.session_state.get("gr_db_prov")
    if rows is not None and st.session_state.get("gr_db_name")==db and st.session_state.get("gr_db_query")==query.strip():
        if rows:
            st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True)
            st.download_button("Download retrieved records CSV",pd.DataFrame(rows).to_csv(index=False),"database_records.csv","text/csv")
        else:
            st.info("The live database returned no matching records.")
        if prov: _provenance(prov)
        if rows:
            _report(f"{db} retrieval", [str(row) for row in rows[:30]], "database_explorer")
    st.divider()
    st.markdown("**Retrieve transcript cDNA from Ensembl Plants**")
    gene_id=st.text_input("Ensembl gene ID",placeholder="Paste an Ensembl plant gene stable ID",key="ensembl_gene_id")
    if st.button("Retrieve transcripts",disabled=not gene_id.strip()):
        try:
            transcripts,prov=ensembl_gene_transcripts(gene_id.strip())
            st.session_state["gr_transcripts"]=transcripts
            st.session_state["gr_transcript_prov"]=prov
            st.session_state["gr_transcript_gene"]=gene_id.strip()
        except Exception as exc: st.error(f"Transcript retrieval failed: {exc}")
    transcripts=st.session_state.get("gr_transcripts")
    if transcripts is not None and st.session_state.get("gr_transcript_gene")==gene_id.strip():
        gene_meta=(st.session_state.get("gr_transcript_prov") or {}).get("gene",{})
        if gene_meta: st.json(gene_meta)
        if transcripts:
            txdf=pd.DataFrame(transcripts)
            st.dataframe(txdf,use_container_width=True,hide_index=True)
            txid=st.selectbox("Select transcript to retrieve cDNA", [x["Transcript ID"] for x in transcripts])
            if st.button("Download transcript cDNA sequence"):
                try:
                    fasta,prov=ensembl_transcript_cdna(txid)
                    st.code(fasta)
                    st.download_button("Download cDNA FASTA",fasta,f"{txid}.fasta","text/plain")
                    _provenance(prov)
                except Exception as exc: st.error(f"cDNA retrieval failed: {exc}")
        else: st.info("No transcript records were returned for this gene ID.")
        _provenance(st.session_state.get("gr_transcript_prov",{}))
    st.divider()
    st.markdown("**Retrieve NCBI nucleotide FASTA by accession**")
    accession=st.text_input("NCBI nucleotide accession",placeholder="e.g. NM_001...")
    if st.button("Fetch NCBI FASTA",disabled=not accession.strip()):
        try:
            fasta,prov=ncbi_fetch_fasta(accession.strip())
            st.session_state["gr_ncbi_fasta"]=fasta
            st.session_state["gr_ncbi_fasta_prov"]=prov
        except Exception as exc: st.error(f"FASTA retrieval failed: {exc}")
    if st.session_state.get("gr_ncbi_fasta"):
        st.code(st.session_state["gr_ncbi_fasta"][:12000])
        st.download_button("Download NCBI FASTA",st.session_state["gr_ncbi_fasta"],f"{accession or 'sequence'}.fasta","text/plain")
        _provenance(st.session_state.get("gr_ncbi_fasta_prov",{}))

def render_functional_annotation():
    """Retrieve and present UniProt, InterPro and PubMed evidence clearly."""
    st.subheader("Functional Annotation")
    st.write(
        "Characterize a protein using live UniProtKB records, InterPro domain "
        "matches and supporting PubMed literature."
    )

    accession = st.text_input(
        "UniProt accession",
        placeholder="e.g. P04637",
        key="annotation_accession",
        help="Enter a UniProt accession such as P04637. The page retrieves live records.",
    ).strip()

    if not accession:
        st.info("Enter a UniProt accession to begin protein characterization.")
    else:
        left, right = st.columns([1, 1])
        with left:
            retrieve_uniprot = st.button(
                "Retrieve protein annotation",
                type="primary",
                use_container_width=True,
                key="retrieve_functional_uniprot",
            )
        with right:
            retrieve_interpro = st.button(
                "Retrieve domain matches",
                use_container_width=True,
                key="retrieve_functional_interpro",
            )

        if retrieve_uniprot:
            try:
                with st.spinner("Retrieving protein record and FASTA from UniProtKB..."):
                    entry, prov = uniprot_entry(accession)
                    fasta, fasta_prov = uniprot_fasta(accession)
                st.session_state["gr_uniprot_entry"] = entry
                st.session_state["gr_uniprot_fasta"] = fasta
                st.session_state["gr_uniprot_prov"] = prov
                st.session_state["gr_uniprot_fasta_prov"] = fasta_prov
                st.session_state["gr_uniprot_accession"] = accession
                st.success("UniProtKB record retrieved.")
            except Exception as exc:
                st.error(f"UniProtKB retrieval failed: {exc}")

        if retrieve_interpro:
            try:
                with st.spinner("Retrieving InterPro domain and family matches..."):
                    rows, prov = interpro_search(accession)
                st.session_state["gr_interpro_rows"] = rows
                st.session_state["gr_interpro_prov"] = prov
                st.session_state["gr_interpro_accession"] = accession
                st.success(f"InterPro retrieval completed: {len(rows)} match(es).")
            except Exception as exc:
                st.error(f"InterPro retrieval failed: {exc}")

    entry = st.session_state.get("gr_uniprot_entry")
    active_uniprot = st.session_state.get("gr_uniprot_accession") == accession
    if entry and active_uniprot:
        protein_desc = entry.get("proteinDescription", {})
        recommended = protein_desc.get("recommendedName", {})
        rec = recommended.get("fullName", {}).get("value", "")
        if not rec:
            submissions = protein_desc.get("submissionNames", [])
            if submissions:
                rec = submissions[0].get("fullName", {}).get("value", "")
        org_data = entry.get("organism", {})
        org = org_data.get("scientificName", "Not provided")
        gene_names = entry.get("genes", [])
        gene_symbol = ""
        if gene_names:
            gene_symbol = gene_names[0].get("geneName", {}).get("value", "")
        seq = entry.get("sequence", {})
        sequence = seq.get("value", "")
        length = seq.get("length", len(sequence) if sequence else "Not provided")
        entry_type = entry.get("entryType", "Not provided")
        primary_accession = entry.get("primaryAccession", accession)

        # Extract readable biological-function statements from UniProt comments.
        function_texts = []
        subcellular_texts = []
        for comment in entry.get("comments", []):
            comment_type = comment.get("commentType", "")
            texts = []
            for item in comment.get("texts", []):
                value = item.get("value", "")
                if value:
                    texts.append(value)
            if comment_type == "FUNCTION" and texts:
                function_texts.extend(texts)
            elif comment_type == "SUBCELLULAR LOCATION":
                for location in comment.get("subcellularLocations", []):
                    location_value = location.get("location", {}).get("value", "")
                    if location_value:
                        subcellular_texts.append(location_value)

        keywords = [
            item.get("name", "")
            for item in entry.get("keywords", [])
            if item.get("name")
        ]
        go_terms = []
        for ref in entry.get("uniProtKBCrossReferences", []):
            if ref.get("database") == "GO":
                props = {p.get("key"): p.get("value") for p in ref.get("properties", [])}
                go_terms.append({
                    "GO ID": ref.get("id", ""),
                    "Term": props.get("GoTerm", ""),
                })

        st.divider()
        st.markdown("### Protein overview")
        st.markdown(f"**{rec or 'Protein name not provided'}**")
        st.caption(f"{primary_accession} · {org} · {entry_type}")

        metric_cols = st.columns(4)
        metric_cols[0].metric("Amino acids", length)
        metric_cols[1].metric("Gene symbol", gene_symbol or "Not provided")
        metric_cols[2].metric("Sequence mass", f"{seq.get(' molWeight', seq.get('molWeight', 'N/A'))} Da" if seq.get("molWeight") else "Not provided")
        metric_cols[3].metric("Keywords", len(keywords))

        if function_texts:
            st.markdown("### Biological function")
            for text_item in function_texts:
                st.write(text_item)
        else:
            st.info("UniProtKB did not provide a FUNCTION comment for this record.")

        detail_cols = st.columns(2)
        with detail_cols[0]:
            st.markdown("**Subcellular location**")
            if subcellular_texts:
                for location in sorted(set(subcellular_texts)):
                    st.write(f"• {location}")
            else:
                st.caption("No subcellular location statement was returned.")
        with detail_cols[1]:
            st.markdown("**Functional keywords**")
            if keywords:
                st.write(", ".join(keywords))
            else:
                st.caption("No keywords were returned.")

        if go_terms:
            st.markdown("### Gene Ontology cross-references")
            st.dataframe(pd.DataFrame(go_terms), use_container_width=True, hide_index=True)

        if sequence:
            st.markdown("### Protein sequence")
            st.caption(f"{len(sequence)} amino acids · UniProtKB sequence")
            st.code(
                "\\n".join(sequence[i:i + 60] for i in range(0, len(sequence), 60)),
                language="text",
            )
            fasta = st.session_state.get("gr_uniprot_fasta", "")
            if fasta:
                st.download_button(
                    "Download protein FASTA",
                    data=fasta,
                    file_name=f"{primary_accession}.fasta",
                    mime="text/plain",
                    key="download_functional_fasta",
                )

        st.caption(
            f"Source: UniProtKB · Retrieved: "
            f"{st.session_state.get('gr_uniprot_prov', {}).get('retrieved_at_utc', 'Not recorded')}"
        )
        st.markdown(f"[Open UniProtKB record](https://www.uniprot.org/uniprotkb/{primary_accession})")

        with st.expander("Technical details and raw UniProt response"):
            st.json(entry)

        report_lines = [
            f"Accession: {primary_accession}",
            f"Protein: {rec}",
            f"Gene symbol: {gene_symbol}",
            f"Organism: {org}",
            f"Length: {length} amino acids",
            "Biological function: " + " ".join(function_texts),
            "Subcellular location: " + ", ".join(sorted(set(subcellular_texts))),
            "Keywords: " + ", ".join(keywords),
        ]
        _report("Functional Protein Annotation", report_lines, "functional_annotation")

    domains = st.session_state.get("gr_interpro_rows")
    active_interpro = st.session_state.get("gr_interpro_accession") == accession
    if domains is not None and active_interpro:
        st.divider()
        st.markdown("### InterPro domain and family analysis")
        st.metric("InterPro matches", len(domains))
        if domains:
            domain_df = pd.DataFrame(domains)
            preferred = [
                "InterPro accession", "Name", "Type",
                "Source database", "Entry URL",
            ]
            display_cols = [c for c in preferred if c in domain_df.columns]
            st.dataframe(
                domain_df[display_cols] if display_cols else domain_df,
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Download domain matches CSV",
                data=domain_df.to_csv(index=False),
                file_name=f"{accession}_interpro_domains.csv",
                mime="text/csv",
                key="download_interpro_csv",
            )
            st.caption(
                "InterPro matches identify database-defined families, domains and "
                "conserved sites. The current API response does not provide residue "
                "coordinates in this table, so no domain positions are inferred."
            )
            with st.expander("Technical details and raw InterPro results"):
                st.json(domains)
            _report(
                "InterPro Domain and Family Matches",
                [f"{row.get('InterPro accession', '')}: {row.get('Name', '')} "
                 f"({row.get('Type', '')})" for row in domains],
                "interpro_domains",
            )
        else:
            st.info("No InterPro matches were returned for this accession.")
        _provenance(st.session_state.get("gr_interpro_prov", {}))
        st.markdown(
            f"[Open InterPro results](https://www.ebi.ac.uk/interpro/protein/UniProt/{accession})"
        )

    st.divider()
    st.markdown("### Supporting literature")
    st.write("Search PubMed for publications related to this protein, gene or biological function.")
    litquery = st.text_input(
        "PubMed search query",
        value=accession if accession else "",
        placeholder="e.g. TP53 DNA repair apoptosis",
        key="functional_pubmed_query",
    )
    if st.button(
        "Search supporting literature",
        disabled=not litquery.strip(),
        key="functional_pubmed_search",
    ):
        try:
            with st.spinner("Searching PubMed..."):
                articles, prov = pubmed_search(litquery.strip(), 10)
            st.session_state["gr_pubmed_articles"] = articles
            st.session_state["gr_pubmed_prov"] = prov
            st.session_state["gr_pubmed_query"] = litquery.strip()
        except Exception as exc:
            st.error(f"PubMed search failed: {exc}")

    articles = st.session_state.get("gr_pubmed_articles")
    if articles is not None and st.session_state.get("gr_pubmed_query") == litquery.strip():
        if not articles:
            st.info("PubMed returned no matching articles for this query.")
        for index, article in enumerate(articles):
            title = article.get("Title") or "Untitled article"
            year = article.get("Year") or "Year not available"
            with st.expander(f"{year} · {title}"):
                st.write(article.get("Journal", ""))
                st.write(article.get("Abstract") or "No abstract available.")
                pmid = article.get("PMID", "")
                url = article.get("URL") or (
                    f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""
                )
                if url:
                    st.markdown(f"[Open PubMed record]({url})")
        _provenance(st.session_state.get("gr_pubmed_prov", {}))
        if articles:
            lit_lines = [
                f"{item.get('PMID', '')}: {item.get('Title', '')} "
                f"({item.get('Year', '')})"
                for item in articles
            ]
            _report("PubMed Supporting Literature", lit_lines, "pubmed_literature")

def render_crop_intelligence():
    st.subheader("Crop Intelligence")
    st.write("Combine trait-focused research hypotheses with machine-learning analysis of your own labeled crop dataset.")
    tab1,tab2=st.tabs(["Trait research recommendations","Crop trait prediction"])
    with tab1:
        trait=st.selectbox("Crop improvement objective",get_supported_traits(),key="crop_trait")
        genes=st.text_input("Candidate gene IDs (optional)")
        evidence=st.text_area("Supporting evidence or observations (optional)")
        if st.button("Generate research recommendations",type="primary"):
            result=generate_rescue_recommendations(trait,[x.strip() for x in genes.split(",") if x.strip()],[evidence] if evidence.strip() else [])
            st.session_state["gr_crop_recommendations"]=result
        result=st.session_state.get("gr_crop_recommendations")
        if result:
            st.write(f"**Research area:** {result['research_area']}")
            st.markdown("**Potential strategies**")
            for x in result["recommended_strategies"]: st.markdown(f"- {x}")
            st.markdown("**Suggested validation**")
            for x in result["validation_methods"]: st.markdown(f"- {x}")
            st.warning(result["disclaimer"])
            _report("Crop Intelligence Recommendations",[result["selected_trait"],result["research_area"]]+result["recommended_strategies"]+result["validation_methods"],"crop_intelligence")
    with tab2:
        upload=st.file_uploader("Upload your labeled crop dataset (CSV)",type=["csv"],key="crop_ml_upload")
        if upload:
            try:
                data=pd.read_csv(upload)
                st.dataframe(data.head(15),use_container_width=True,hide_index=True)
                target=st.selectbox("Select target label column",list(data.columns),key="crop_ml_target")
                if st.button("Train crop trait model"):
                    results=train_crop_model(data,target)
                    st.session_state["gr_crop_model"]=results
                    st.session_state["gr_crop_model_target"]=target
                results=st.session_state.get("gr_crop_model")
                if results:
                    st.metric("Held-out test accuracy",f"{results['accuracy']}%")
                    st.caption(f"Training samples: {results['training_samples']} · Test samples: {results['test_samples']}")
                    st.dataframe(results["feature_importance"].head(20),use_container_width=True,hide_index=True)
                    st.warning("Model performance depends on dataset quality and validation design. Predictions are not proof of causal genetic effects or field performance.")
            except Exception as exc: st.error(f"Crop model failed: {exc}")

def render_tool(tool):
    renderers={
        "Sequence Analysis":render_sequence_analysis,
        "Gene Discovery":render_gene_discovery,
        "Variant Analysis":render_variant_analysis,
        "Database Explorer":render_database_explorer,
        "Functional Annotation":render_functional_annotation,
        "Crop Intelligence":render_crop_intelligence,
    }
    renderers[tool]()
