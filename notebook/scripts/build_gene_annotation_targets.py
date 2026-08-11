"""
Build the gene-to-RefSeq-accession lookup used for NCBI Gene annotation.

Reads the AcolN3 GTF to associate every gene_id with the RefSeq transcript
accession recorded by VectorBase (transcript_name attribute, preferring the
transcript tagged Ensembl_canonical), then restricts the list to the genes
found significant in notebook/tables/gene_counts_analysis.xlsx (sheets
up_in_field and up_in_ngousso). The gene_counts_analysis.xlsx file must
already exist, i.e. the notebook must have been run through the
differential expression and Excel export cells at least once.

Output: references/gene_annotation_targets.tsv (gene_id, accession),
consumed by fetch_gene_annotations.py.

Author: Khadim Gueye
"""

import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
GTF_PATH = Path("/mnt/hpc_acegid/home/khadmig/work/data/For_Lynda/260718_VH00635_9_AAJ2KFGM5/output_analysis/reference/Anopheles_coluzzii.AcolN3.63.gtf")
EXCEL_PATH = REPO_ROOT / "notebook" / "tables" / "gene_counts_analysis.xlsx"
OUT_PATH = REPO_ROOT / "references" / "gene_annotation_targets.tsv"


def parse_gene_accessions(gtf_path):
    canonical_accession = {}
    any_accession = {}
    with open(gtf_path) as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 9 or fields[2] != "transcript":
                continue
            attrs = fields[8]
            gene_match = re.search(r'gene_id "([^"]+)"', attrs)
            name_match = re.search(r'transcript_name "([^"]+)"', attrs)
            if not gene_match or not name_match:
                continue
            gene_id = gene_match.group(1)
            accession = name_match.group(1)
            any_accession.setdefault(gene_id, accession)
            if 'tag "Ensembl_canonical"' in attrs:
                canonical_accession[gene_id] = accession
    return canonical_accession, any_accession


def main():
    canonical_accession, any_accession = parse_gene_accessions(GTF_PATH)

    up_field = pd.read_excel(EXCEL_PATH, "up_in_field")["gene_id"].tolist()
    up_ngousso = pd.read_excel(EXCEL_PATH, "up_in_ngousso")["gene_id"].tolist()
    target_genes = sorted(set(up_field) | set(up_ngousso))

    rows = []
    for gene_id in target_genes:
        accession = canonical_accession.get(gene_id) or any_accession.get(gene_id)
        if accession is not None:
            rows.append((gene_id, accession))

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["gene_id", "accession"]).to_csv(OUT_PATH, sep="\t", index=False)

    print(f"Significant genes: {len(target_genes)}")
    print(f"Resolved to a RefSeq accession: {len(rows)}")
    print(f"Missing accession: {len(target_genes) - len(rows)}")
    print(f"Written: {OUT_PATH}")


if __name__ == "__main__":
    main()
