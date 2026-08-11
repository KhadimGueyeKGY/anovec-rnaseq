"""
Fetch NCBI Gene name, description, and functional designation for the
genes listed in references/gene_annotation_targets.tsv.

For each RefSeq transcript accession, queries NCBI Entrez (esearch against
the gene database, then efetch in docsum format) to recover the gene
symbol (Name), the gene description, and OtherDesignations (function).
Requires NCBI Entrez Direct (esearch, efetch) on PATH and internet access;
on this cluster this script must run on the login node, since compute
nodes have no outbound network access. The script is resumable: genes
already present in the output file are skipped on a re-run.

Genes whose GTF transcript_name is not a RefSeq accession (mitochondrial
genes such as ND4, recorded directly by gene symbol) are not queried
against NCBI, since a bare symbol is ambiguous across species; the symbol
is used as-is for gene_name.

Output: references/gene_annotations.tsv (gene_id, accession, gene_name,
description, function), loaded by the notebook for the Excel export, the
top differentially expressed genes heatmap, and the gene expression word
cloud figure.

Author: Khadim Gueye
"""

import re
import subprocess
import time
from pathlib import Path

REFSEQ_ACCESSION_RE = re.compile(r"^[NX][MR]_\d")

REPO_ROOT = Path(__file__).resolve().parents[2]
TARGETS_PATH = REPO_ROOT / "references" / "gene_annotation_targets.tsv"
OUT_PATH = REPO_ROOT / "references" / "gene_annotations.tsv"
REQUEST_DELAY_SECONDS = 0.4

NAME_RE = re.compile(r"<Name>(.*?)</Name>")
DESC_RE = re.compile(r"<Description>(.*?)</Description>")
OTHER_RE = re.compile(r"<OtherDesignations>(.*?)</OtherDesignations>")


def unescape(text):
    return (
        text.replace("&apos;", "'")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def fetch_one(accession):
    if not REFSEQ_ACCESSION_RE.match(accession):
        return (accession, "", "")
    try:
        search = subprocess.run(
            ["esearch", "-db", "gene", "-query", accession],
            capture_output=True, text=True, timeout=30,
        )
        if search.returncode != 0 or "<Count>0</Count>" in search.stdout:
            return None
        fetch = subprocess.run(
            ["efetch", "-format", "docsum"],
            input=search.stdout, capture_output=True, text=True, timeout=30,
        )
        if fetch.returncode != 0:
            return None
    except subprocess.TimeoutExpired:
        return None
    xml = fetch.stdout
    name_match = NAME_RE.search(xml)
    desc_match = DESC_RE.search(xml)
    other_match = OTHER_RE.search(xml)
    return (
        unescape(name_match.group(1)) if name_match else "",
        unescape(desc_match.group(1)) if desc_match else "",
        unescape(other_match.group(1)) if other_match else "",
    )


def already_done():
    done = set()
    if OUT_PATH.exists():
        with open(OUT_PATH) as handle:
            next(handle)
            for line in handle:
                done.add(line.split("\t")[0])
    return done


def main():
    with open(TARGETS_PATH) as handle:
        targets = [line.rstrip("\n").split("\t") for line in handle.readlines()[1:]]

    done_genes = already_done()
    mode = "a" if done_genes else "w"

    with open(OUT_PATH, mode) as out:
        if mode == "w":
            out.write("gene_id\taccession\tgene_name\tdescription\tfunction\n")
            out.flush()
        total = len(targets)
        for i, (gene_id, accession) in enumerate(targets, 1):
            if gene_id in done_genes:
                continue
            result = fetch_one(accession)
            gene_name, description, function = result if result is not None else ("", "", "")
            out.write(f"{gene_id}\t{accession}\t{gene_name}\t{description}\t{function}\n")
            out.flush()
            print(f"{i}/{total} {gene_id} done", flush=True)
            time.sleep(REQUEST_DELAY_SECONDS)


if __name__ == "__main__":
    main()
