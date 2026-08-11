"""
Alignment post-processing and basic QC metrics using samtools.
Author: Khadim Gueye
"""

from pathlib import Path

from process.utils import ensure_dir, run_command


def index_bam(bam_file, logger):
    run_command(["samtools", "index", str(bam_file)], logger)
    return Path(f"{bam_file}.bai")


def flagstat(bam_file, outdir, logger):
    outdir = ensure_dir(outdir)
    stats_file = outdir / f"{Path(bam_file).stem}.flagstat.txt"
    result = run_command(["samtools", "flagstat", str(bam_file)], logger)
    stats_file.write_text(result.stdout)
    return stats_file
