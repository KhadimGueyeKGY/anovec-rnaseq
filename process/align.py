"""
Genome and transcriptome alignment of trimmed reads using STAR.
Author: Khadim Gueye
"""

from process.utils import ensure_dir, run_command


def run_star_align(sample, fastq_1, fastq_2, star_index, outdir, threads, logger):
    outdir = ensure_dir(outdir)
    prefix = outdir / f"{sample}."
    cmd = [
        "STAR",
        "--genomeDir", str(star_index),
        "--readFilesIn", str(fastq_1), str(fastq_2),
        "--readFilesCommand", "zcat",
        "--runThreadN", str(threads),
        "--outFileNamePrefix", str(prefix),
        "--outSAMtype", "BAM", "SortedByCoordinate",
        "--quantMode", "TranscriptomeSAM",
        "--outSAMattrRGline", f"ID:{sample}", f"SM:{sample}",
        "--twopassMode", "Basic",
    ]
    run_command(cmd, logger)

    genome_bam = outdir / f"{sample}.Aligned.sortedByCoord.out.bam"
    transcriptome_bam = outdir / f"{sample}.Aligned.toTranscriptome.out.bam"
    return genome_bam, transcriptome_bam
