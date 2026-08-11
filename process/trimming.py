"""
Adapter and quality trimming of paired-end reads using Trim Galore.
Author: Khadim Gueye
"""

from pathlib import Path

from process.discover import strip_extension
from process.utils import ensure_dir, run_command


def run_trim_galore(fastq_1, fastq_2, outdir, threads, logger):
    outdir = ensure_dir(outdir)
    cmd = [
        "trim_galore",
        "--paired",
        "--cores", str(threads),
        "--output_dir", str(outdir),
        str(fastq_1),
        str(fastq_2),
    ]
    run_command(cmd, logger)

    base_1, _ = strip_extension(Path(fastq_1).name)
    base_2, _ = strip_extension(Path(fastq_2).name)
    trimmed_1 = outdir / f"{base_1}_val_1.fq.gz"
    trimmed_2 = outdir / f"{base_2}_val_2.fq.gz"
    return trimmed_1, trimmed_2
