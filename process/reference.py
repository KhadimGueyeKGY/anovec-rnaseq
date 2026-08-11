"""
Reference preparation: transcript FASTA extraction and STAR genome index build.
Author: Khadim Gueye
"""

import gzip
import math
import shutil
from pathlib import Path

from process.utils import ensure_dir, run_command


def decompress(gz_path, outdir):
    outdir = ensure_dir(outdir)
    out_path = outdir / Path(gz_path).stem
    if not out_path.exists():
        with gzip.open(gz_path, "rb") as f_in, open(out_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    return out_path


def extract_transcript_fasta(genome_fasta, gtf, outdir, logger):
    outdir = ensure_dir(outdir)
    transcript_fasta = outdir / "transcripts.fa"
    if not transcript_fasta.exists():
        cmd = ["gffread", "-w", str(transcript_fasta), "-g", str(genome_fasta), str(gtf)]
        run_command(cmd, logger)
    return transcript_fasta


def genome_sa_index_nbases(genome_fasta):
    genome_length = 0
    with open(genome_fasta) as handle:
        for line in handle:
            if not line.startswith(">"):
                genome_length += len(line.strip())
    return min(14, int(math.log2(genome_length) / 2 - 1))


def build_star_index(genome_fasta, gtf, outdir, threads, read_length, logger):
    outdir = ensure_dir(outdir)
    if (outdir / "SAindex").exists():
        return outdir

    cmd = [
        "STAR",
        "--runMode", "genomeGenerate",
        "--genomeDir", str(outdir),
        "--genomeFastaFiles", str(genome_fasta),
        "--sjdbGTFfile", str(gtf),
        "--sjdbOverhang", str(read_length - 1),
        "--runThreadN", str(threads),
        "--genomeSAindexNbases", str(genome_sa_index_nbases(genome_fasta)),
    ]
    run_command(cmd, logger)
    return outdir
