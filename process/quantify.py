"""
Transcript-level quantification using Salmon in alignment-based mode.
Author: Khadim Gueye
"""

from process.utils import ensure_dir, run_command

LIBTYPE_MAP = {
    "forward": "ISF",
    "reverse": "ISR",
    "unstranded": "IU",
}


def run_salmon_quant(sample, transcriptome_bam, transcript_fasta, strandedness, outdir, threads, logger):
    outdir = ensure_dir(outdir)
    sample_outdir = outdir / sample
    libtype = LIBTYPE_MAP.get(strandedness, "A")
    cmd = [
        "salmon", "quant",
        "--libType", libtype,
        "--alignments", str(transcriptome_bam),
        "--targets", str(transcript_fasta),
        "--threads", str(threads),
        "--output", str(sample_outdir),
        "--gcBias",
    ]
    run_command(cmd, logger)
    return sample_outdir / "quant.sf"
