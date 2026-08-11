"""
Raw and trimmed read quality control using FastQC.
Author: Khadim Gueye
"""

from process.utils import ensure_dir, run_command


def run_fastqc(fastq_files, outdir, threads, logger):
    outdir = ensure_dir(outdir)
    cmd = ["fastqc", "--threads", str(threads), "--outdir", str(outdir)]
    cmd += [str(fastq) for fastq in fastq_files]
    run_command(cmd, logger)
    return outdir
