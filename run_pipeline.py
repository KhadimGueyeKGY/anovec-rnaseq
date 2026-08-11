"""
Entry point orchestrating the Anopheles coluzzii RNA-seq analysis:
FastQC, Trim Galore, STAR alignment, Salmon quantification, and MultiQC.
Author: Khadim Gueye
"""

import csv
import sys

import yaml

from process.align import run_star_align
from process.discover import discover_samples
from process.postprocess import flagstat, index_bam
from process.qc import run_fastqc
from process.quantify import run_salmon_quant
from process.reference import build_star_index, decompress, extract_transcript_fasta
from process.report import run_multiqc
from process.trimming import run_trim_galore
from process.utils import ensure_dir, setup_logger


def load_samplesheet(path):
    with open(path) as handle:
        return list(csv.DictReader(handle))


def resolve_samples(config):
    if config.get("fastq_dir"):
        return discover_samples(config["fastq_dir"], config.get("strandedness", "reverse"))
    return load_samplesheet(config["samplesheet"])


def main(config_path):
    with open(config_path) as handle:
        config = yaml.safe_load(handle)

    outdir = ensure_dir(config["outdir"])
    logger = setup_logger(outdir / "pipeline.log")

    ref_dir = ensure_dir(outdir / "reference")
    fasta = decompress(config["fasta_gz"], ref_dir)
    gtf = decompress(config["gtf_gz"], ref_dir)

    transcript_fasta = extract_transcript_fasta(fasta, gtf, ref_dir, logger)
    star_index = build_star_index(
        fasta, gtf, ref_dir / "star_index", config["threads"], config["read_length"], logger
    )

    samples = resolve_samples(config)

    fastqc_raw_dir = outdir / "fastqc_raw"
    trim_dir = outdir / "trimmed"
    align_dir = outdir / "star"
    quant_dir = outdir / "salmon"
    qc_dir = outdir / "qc"

    for row in samples:
        sample = row["sample"]
        fastq_1 = row["fastq_1"]
        fastq_2 = row["fastq_2"]
        strandedness = row["strandedness"]

        logger.info("Processing sample %s", sample)

        run_fastqc([fastq_1, fastq_2], fastqc_raw_dir, config["threads"], logger)

        trimmed_1, trimmed_2 = run_trim_galore(fastq_1, fastq_2, trim_dir, config["threads"], logger)

        genome_bam, transcriptome_bam = run_star_align(
            sample, trimmed_1, trimmed_2, star_index, align_dir, config["threads"], logger
        )

        index_bam(genome_bam, logger)
        flagstat(genome_bam, qc_dir, logger)

        run_salmon_quant(
            sample, transcriptome_bam, transcript_fasta, strandedness, quant_dir, config["threads"], logger
        )

    run_multiqc(outdir, outdir / "multiqc", logger)

    logger.info("Pipeline completed successfully.")


if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    main(config_path)
