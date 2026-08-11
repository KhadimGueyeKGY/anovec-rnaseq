# anovec-rnaseq-nf

RNA-seq analysis pipeline for *Anopheles coluzzii*: Ngousso laboratory colony
versus field-collected mosquitoes (Akoda, Osun State, Nigeria).

Implemented in Python, calling the same tools as nf-core/rnaseq
(FastQC, Trim Galore, STAR, Salmon, samtools, MultiQC) directly via
subprocess, since Nextflow cannot run on this cluster's login node
and the compute nodes have no internet access.

## 1. Tools to install

Create the conda environment from `environment.yml`:

```
conda env create -f environment.yml
conda activate anovec-rnaseq
```

Tools installed: FastQC, Trim Galore, STAR, Salmon, samtools, gffread, MultiQC.

## 2. Reference database

Genome and annotation are already included in `references/`:

- `Anopheles_coluzzii.AcolN3.dna.toplevel.fa.gz`
- `Anopheles_coluzzii.AcolN3.63.gtf.gz`

Source: Ensembl Metazoa, release 63, assembly AcolN3 (GCA_943734685.1).
Checksums are provided alongside (`CHECKSUMS_fasta`, `CHECKSUMS_gtf`).

## 3. Input data

Two ways to provide samples:

- `samplesheet.csv`: explicit list (sample, fastq_1, fastq_2, strandedness)
- `fastq_dir`: point `config.yaml` at a folder and samples are auto-discovered

Auto-discovery accepts `.fastq`, `.fq`, `.fastq.gz`, `.fq.gz`, and mate pairs
named `_R1`/`_R2`, `_1`/`_2`, or `_F`/`_R`.

Current samplesheet: six paired-end, stranded samples (NEBNext Ultra II
Directional kit, strandedness `reverse`):

- Ng1, Ng2, Ng3: Ngousso colony
- NE1, NE2, NE3: field-collected, Akoda, Osun State, Nigeria

## 4. Configuration

Edit `config.yaml` to set paths, thread count, and read length.

## 5. Running the pipeline

Submit as a SLURM job:

```
sbatch run_pipeline.sbatch
```

Or run directly (for testing on an allocated compute node):

```
bash main.sh config.yaml
```

## 6. Pipeline steps

1. Decompress reference genome and GTF
2. Extract transcript FASTA (gffread) and build STAR genome index
3. FastQC on raw reads
4. Adapter/quality trimming (Trim Galore)
5. STAR alignment (genome + transcriptome BAM)
6. samtools index and flagstat on the genome BAM
7. Salmon quantification (alignment-based, on the transcriptome BAM)
8. MultiQC aggregated report

## 7. Repository layout

```
anovec-rnaseq-nf/
├── main.sh                    entry point, calls run_pipeline.py
├── run_pipeline.py            orchestrates all steps for every sample
├── run_pipeline.sbatch        SLURM launcher
├── config.yaml
├── samplesheet.csv
├── environment.yml
├── process/                   one module per pipeline step
├── notebook/
│   ├── rnaseq_qc_summary.ipynb   downstream analysis notebook
│   ├── environment.yml           analysis-only conda environment
│   ├── scripts/                  gene name annotation scripts (section 11)
│   ├── figures/                  exported figures (PNG)
│   └── tables/                   exported result tables (Excel)
└── references/
    ├── Anopheles_coluzzii.AcolN3.dna.toplevel.fa.gz
    ├── Anopheles_coluzzii.AcolN3.63.gtf.gz
    ├── gene_annotation_targets.tsv   built by notebook/scripts (section 11)
    └── gene_annotations.tsv          built by notebook/scripts (section 11)
```

## 8. Output

Results are written under the `outdir` set in `config.yaml`:

```
outdir/
├── reference/
├── fastqc_raw/
├── trimmed/
├── star/
├── salmon/
├── qc/
├── multiqc/
└── pipeline.log
```

## 10. Downstream analysis notebook

`notebook/rnaseq_qc_summary.ipynb` covers QC, transcript- and gene-level
detection, PCA, PyDESeq2 differential expression, and Excel/figure export.
It has its own conda environment (`notebook/environment.yml`):

```
conda env create -f notebook/environment.yml
conda activate rnaseq-analysis
```

Outputs are written to `notebook/figures/` and `notebook/tables/`.

## 11. Gene name annotation

The AcolN3 GTF (VectorBase/Ensembl Metazoa) does not carry gene names or
functional descriptions for most genes. For the genes found significant
by PyDESeq2, gene name and function are recovered from NCBI Gene, using
the RefSeq transcript accession already present in the GTF
(`transcript_name` attribute) as the cross-reference key.

Run after the notebook has produced `notebook/tables/gene_counts_analysis.xlsx`
(the differential expression step), from a machine with internet access
(the login node on this cluster; compute nodes are offline):

```
python notebook/scripts/build_gene_annotation_targets.py
python notebook/scripts/fetch_gene_annotations.py
```

This writes `references/gene_annotation_targets.tsv` (gene_id, RefSeq
accession) and `references/gene_annotations.tsv` (gene_id, accession,
gene_name, description, function). `fetch_gene_annotations.py` is
resumable and rate-limited for NCBI Entrez usage without an API key.
Re-running the notebook's annotation cell onward then fills in gene names
in the Excel export, the top differentially expressed genes heatmap, and
the gene expression word cloud figure, falling back to the gene ID when
no name is available.

## 12. Notes

- Contamination screening (blood meal, *Wolbachia*, *Plasmodium*) is a
  separate, not yet implemented step.
