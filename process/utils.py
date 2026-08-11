"""
Shared helpers for running external tools and logging pipeline steps.
Author: Khadim Gueye
"""

import logging
import subprocess
import sys
from pathlib import Path


def setup_logger(log_file):
    logger = logging.getLogger("anovec_rnaseq")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def run_command(cmd, logger, cwd=None):
    logger.info("Running: %s", " ".join(str(part) for part in cmd))
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(result.stderr)
        raise RuntimeError(
            f"Command failed with exit code {result.returncode}: {' '.join(str(part) for part in cmd)}"
        )
    return result


def ensure_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path
