#!/bin/bash
#
# SLURM launcher for the anovec-rnaseq Python pipeline.
# Author: Khadim Gueye
#
#SBATCH --job-name=anovec_rnaseq
#SBATCH --output=logs/anovec_rnaseq_%j.out
#SBATCH --error=logs/anovec_rnaseq_%j.err
#SBATCH --time=48:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=normal

set -euo pipefail
trap 'echo "[ERROR] ${BASH_SOURCE[0]} failed at line ${LINENO} (exit code $?)" >&2' ERR

PIPELINE_DIR="/mnt/hpc_acegid/home/khadmig/work/script/For_Lynda/anovec-rnaseq-nf"

mkdir -p "${PIPELINE_DIR}/logs"

source /mnt/hpc_acegid/home/khadmig/miniconda/etc/profile.d/conda.sh
conda activate anovec-rnaseq

cd "${PIPELINE_DIR}"
bash main.sh config.yaml
