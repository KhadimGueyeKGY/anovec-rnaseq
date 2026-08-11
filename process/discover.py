"""
Automatic discovery of paired-end FASTQ files from an input directory,
tolerant of common extensions and mate-naming conventions.
Author: Khadim Gueye
"""

import re
from pathlib import Path

FASTQ_EXTENSIONS = [".fastq.gz", ".fq.gz", ".fastq", ".fq"]

MATE_1_PATTERNS = [r"_R1", r"_r1", r"_1", r"_F"]
MATE_2_PATTERNS = [r"_R2", r"_r2", r"_2", r"_R"]


def strip_extension(filename):
    for ext in FASTQ_EXTENSIONS:
        if filename.endswith(ext):
            return filename[: -len(ext)], ext
    return None, None


def split_mate_and_sample(stem):
    for pattern in MATE_1_PATTERNS:
        match = re.search(pattern, stem)
        if match:
            return stem[: match.start()], 1
    for pattern in MATE_2_PATTERNS:
        match = re.search(pattern, stem)
        if match:
            return stem[: match.start()], 2
    return None, None


def discover_samples(fastq_dir, strandedness="reverse"):
    fastq_dir = Path(fastq_dir)
    mates = {}

    for entry in sorted(fastq_dir.iterdir()):
        if not entry.is_file():
            continue
        stem, ext = strip_extension(entry.name)
        if stem is None:
            continue
        sample, mate = split_mate_and_sample(stem)
        if sample is None:
            continue
        mates.setdefault(sample, {})[mate] = str(entry)

    samples = []
    for sample, pair in sorted(mates.items()):
        if 1 in pair and 2 in pair:
            samples.append(
                {
                    "sample": sample,
                    "fastq_1": pair[1],
                    "fastq_2": pair[2],
                    "strandedness": strandedness,
                }
            )
    return samples
