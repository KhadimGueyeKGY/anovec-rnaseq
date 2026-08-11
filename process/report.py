"""
Aggregated QC report generation using MultiQC.
Author: Khadim Gueye
"""

from process.utils import ensure_dir, run_command


def run_multiqc(search_dir, outdir, logger):
    outdir = ensure_dir(outdir)
    script = (
        "import os, sys\n"
        "os.setxattr = lambda *a, **k: None\n"
        "from multiqc.__main__ import run_multiqc\n"
        "sys.exit(run_multiqc())"
    )
    cmd = ["python", "-c", script, str(search_dir), "--outdir", str(outdir), "--force"]
    run_command(cmd, logger)
    return outdir
