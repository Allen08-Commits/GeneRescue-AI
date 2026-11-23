"""Live biological database clients for GeneRescue AI.

All searches are performed on demand against public APIs.
No demonstration or fabricated records are returned.
"""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import requests

SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": "GeneRescueAI/2.1 (bioinformatics research application)",
    "Accept": "application/json",
})
TIMEOUT = 25

class DatabaseAPIError(RuntimeError):
    pass

def _get(url: str, params=None, headers=None):
    try:
        response = SESSION.get(url, params=params, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:
        raise DatabaseAPIError(f"Database request failed: {exc}") from exc

def _provenance(database: str, url: str, query: str = ""):
    return {
        "database": database,
        "query": query,
        "source_url": url,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def _ncbi_setting(name: str) -> str:
    value = os.getenv(name, "")
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(name, ""))
    except Exception:
        return ""

def ncbi_gene_search(query: str, organism: str = "", limit: int = 10):
    term = query.strip()
    if organism.strip():
        term += f" AND {organism.strip()}[Organism]"
    if not term:
        raise ValueError("Enter a gene name, symbol or search term.")
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = {"db": "gene", "term": term, "retmode": "json", "retmax": limit}
    email = _ncbi_setting("NCBI_EMAIL")
    api_key = _ncbi_setting("NCBI_API_KEY")
    if email: params["email"] = email
    if api_key: params["api_key"] = api_key
    data = _get(f"{base}/esearch.fcgi", params).json()
    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return [], _provenance("NCBI Gene", f"https://www.ncbi.nlm.nih.gov/gene/?term={requests.utils.quote(term)}", term)
    summary_params = {"db": "gene", "id": ",".join(ids), "retmode": "json"}
    if email: summary_params["email"] = email
    if api_key: summary_params["api_key"] = api_key
    summaries = _get(f"{base}/esummary.fcgi", summary_params).json().get("result", {})
    rows = []
    for uid in ids:
        item = summaries.get(uid, {})
        rows.append({
            "Gene ID": uid,
            "Symbol": item.get("name", ""),
            "Description": item.get("description", ""),
            "Organism": item.get("organism", {}).get("scientificname", ""),
            "Chromosome": item.get("chromosome", ""),
            "Map location": item.get("maplocation", ""),
            "NCBI URL": f"https://www.ncbi.nlm.nih.gov/gene/{uid}",
        })
    return rows, _provenance("NCBI Gene", f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi", term)

def ncbi_transcript_search(query: str, organism: str = "", limit: int = 10):
    term = f'({query.strip()}) AND (biomol_mrna[PROP] OR refseq[filter])'
    if organism.strip():
        term += f" AND {organism.strip()}[Organism]"
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = {"db": "nuccore", "term": term, "retmode": "json", "retmax": limit}
    if _ncbi_setting("NCBI_EMAIL"): params["email"] = _ncbi_setting("NCBI_EMAIL")
    if _ncbi_setting("NCBI_API_KEY"): params["api_key"] = _ncbi_setting("NCBI_API_KEY")
    data = _get(f"{base}/esearch.fcgi", params).json()
    ids = data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        return [], _provenance("NCBI Nucleotide", f"https://www.ncbi.nlm.nih.gov/nuccore/?term={requests.utils.quote(term)}", term)
    sums = _get(f"{base}/esummary.fcgi", {"db":"nuccore","id":",".join(ids),"retmode":"json"}).json().get("result", {})
    rows = []
    for uid in ids:
        item = sums.get(uid, {})
        acc = item.get("accessionversion", "")
        rows.append({
            "UID": uid, "Accession": acc, "Title": item.get("title", ""),
            "Length": item.get("slen", ""), "Molecule": item.get("moltype", ""),
            "Organism": item.get("organism", ""),
            "URL": f"https://www.ncbi.nlm.nih.gov/nuccore/{acc or uid}",
        })
    return rows, _provenance("NCBI Nucleotide", f"{base}/esearch.fcgi", term)

def ncbi_fetch_fasta(accession: str):
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    response = _get(url, {"db":"nuccore","id":accession.strip(),"rettype":"fasta","retmode":"text"})
    return response.text, _provenance("NCBI Nucleotide FASTA", response.url, accession)

def ensembl_plant_search(symbol: str, species: str):
    url = f"https://rest.ensembl.org/xrefs/symbol/{species}/{requests.utils.quote(symbol.strip())}"
    data = _get(url, headers={"Content-Type":"application/json"}).json()
    rows = [{"ID": x.get("id",""), "Type": x.get("type",""), "Display name": x.get("display_id","")} for x in data]
    return rows, _provenance("Ensembl Plants", url, f"{symbol} ({species})")

def ensembl_gene_transcripts(gene_id: str):
    url = f"https://rest.ensembl.org/lookup/id/{requests.utils.quote(gene_id)}"
    record = _get(url, params={"expand":1}, headers={"Content-Type":"application/json"}).json()
    transcripts = []
    for tx in record.get("Transcript", []):
        transcripts.append({
            "Transcript ID": tx.get("id",""),
            "Biotype": tx.get("biotype",""),
            "Start": tx.get("start",""),
            "End": tx.get("end",""),
            "Strand": tx.get("strand",""),
            "Canonical": tx.get("is_canonical", 0) == 1,
        })
    prov = _provenance("Ensembl Plants", url, gene_id)
    prov["gene"] = {k: record.get(k) for k in ("id","display_name","description","biotype","seq_region_name","start","end","strand")}
    return transcripts, prov

def ensembl_transcript_cdna(transcript_id: str):
    url = f"https://rest.ensembl.org/sequence/id/{requests.utils.quote(transcript_id)}"
    response = _get(url, params={"type":"cdna"}, headers={"Content-Type":"text/plain"})
    return response.text, _provenance("Ensembl Plants transcript cDNA", response.url, transcript_id)

def uniprot_search(query: str, limit: int = 10):
    url = "https://rest.uniprot.org/uniprotkb/search"
    data = _get(url, {"query":query.strip(),"format":"json","size":limit,
        "fields":"accession,id,protein_name,organism_name,length,reviewed"}).json()
    rows=[]
    for r in data.get("results", []):
        protein = r.get("proteinDescription",{}).get("recommendedName",{}).get("fullName",{}).get("value","")
        if not protein:
            names = r.get("proteinDescription",{}).get("submissionNames",[])
            protein = names[0].get("fullName",{}).get("value","") if names else ""
        org = r.get("organism",{}).get("scientificName","")
        rows.append({
            "Accession":r.get("primaryAccession",""),
            "Entry":r.get("uniProtkbId",""),
            "Protein":protein,
            "Organism":org,
            "Length":r.get("sequence",{}).get("length",""),
            "Reviewed":r.get("entryType",""),
            "URL":f"https://www.uniprot.org/uniprotkb/{r.get('primaryAccession','')}",
        })
    return rows, _provenance("UniProtKB", url, query)

def uniprot_fasta(accession: str):
    url=f"https://rest.uniprot.org/uniprotkb/{requests.utils.quote(accession.strip())}.fasta"
    response=_get(url, headers={"Accept":"text/plain"})
    return response.text, _provenance("UniProtKB FASTA", response.url, accession)

def uniprot_entry(accession: str):
    url=f"https://rest.uniprot.org/uniprotkb/{requests.utils.quote(accession.strip())}.json"
    return _get(url).json(), _provenance("UniProtKB", url, accession)

def interpro_search(accession: str, limit: int = 50):
    url=f"https://www.ebi.ac.uk/interpro/api/entry/interpro/protein/uniprot/{requests.utils.quote(accession.strip())}/"
    response=_get(url, params={"format":"json","page_size":limit})
    data=response.json()
    rows=[]
    for item in data.get("results", []):
        metadata=item.get("metadata",{})
        rows.append({
            "InterPro accession":metadata.get("accession",""),
            "Name":metadata.get("name",""),
            "Type":metadata.get("type",""),
            "Source database":item.get("source_database",""),
            "Entry URL":metadata.get("source_database_url",""),
        })
    return rows, _provenance("InterPro", response.url, accession)

def pubmed_search(query: str, limit: int = 10):
    base="https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    search=_get(f"{base}/esearch.fcgi", {"db":"pubmed","term":query.strip(),"retmode":"json","retmax":limit}).json()
    ids=search.get("esearchresult",{}).get("idlist",[])
    if not ids:
        return [], _provenance("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", query)
    xml=_get(f"{base}/efetch.fcgi", {"db":"pubmed","id":",".join(ids),"retmode":"xml"}).text
    import xml.etree.ElementTree as ET
    root=ET.fromstring(xml)
    rows=[]
    for article in root.findall(".//PubmedArticle"):
        pmid=article.findtext(".//PMID","")
        title=" ".join("".join(article.find(".//ArticleTitle").itertext()).split()) if article.find(".//ArticleTitle") is not None else ""
        abstract_parts=[" ".join("".join(x.itertext()).split()) for x in article.findall(".//Abstract/AbstractText")]
        journal=article.findtext(".//Journal/Title","")
        year=article.findtext(".//PubDate/Year","")
        rows.append({"PMID":pmid,"Title":title,"Journal":journal,"Year":year,
                     "Abstract":" ".join(abstract_parts),
                     "URL":f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"})
    return rows, _provenance("PubMed", f"{base}/efetch.fcgi", query)

