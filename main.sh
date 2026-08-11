#!/bin/bash
#
# Main entry point for the anovec-rnaseq pipeline.
# Author: Khadim Gueye
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="${1:-${SCRIPT_DIR}/config.yaml}"

cd "${SCRIPT_DIR}"
python run_pipeline.py "${CONFIG}"
