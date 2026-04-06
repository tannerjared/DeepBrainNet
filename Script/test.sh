#! /bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DATA_PATH=''
OUT_PATH=''
MODEL=''
GPU_DEVICE='0'

print_usage() {
  printf "\n\nUsage:\n\n"
  printf "\tRequired Parameters:\n\n"
  printf "\t  %s\n" \
    "[-d]: Path containing aligned NIfTI images" \
    "[-o]: Output directory for prediction CSV" \
    "[-m]: Path to model file (.h5)"
  printf "\n\tOptional Parameters:\n\n"
  printf "\t  %s\n" \
    "[-g]: GPU device index (default: 0; use -1 for CPU only)"
  printf "\nExample: ./test.sh -d /myPath/ -o ./outputPath/ -m ../Models/DBN_model.h5\n\n"
  exit 1
}

while getopts 'uhd:o:m:g:' flag; do
  case "${flag}" in
    u) print_usage ;;
    h) print_usage ;;
    d) DATA_PATH="${OPTARG}" ;;
    o) OUT_PATH="${OPTARG}" ;;
    m) MODEL="${OPTARG}" ;;
    g) GPU_DEVICE="${OPTARG}" ;;
    *) print_usage ;;
  esac
done

# Validate required arguments
if [[ -z "$DATA_PATH" || -z "$OUT_PATH" || -z "$MODEL" ]]; then
  printf "Error: -d, -o, and -m are required.\n" >&2
  print_usage
fi

if [[ ! -d "$DATA_PATH" ]]; then
  printf "Error: Data directory does not exist: %s\n" "$DATA_PATH" >&2
  exit 1
fi

if [[ ! -f "$MODEL" ]]; then
  printf "Error: Model file not found: %s\n" "$MODEL" >&2
  exit 1
fi

export CUDA_VISIBLE_DEVICES="$GPU_DEVICE"

# Create output directory if it doesn't exist
mkdir -p "$OUT_PATH"

# Use a temporary directory and ensure it is cleaned up on exit
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT
mkdir -p "$TMP_DIR/Test"

START_TIME=$(date +%s)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting DeepBrainNet brain age prediction"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Data:   $DATA_PATH"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Output: ${OUT_PATH}pred.csv"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Model:  $MODEL"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] GPU:    $CUDA_VISIBLE_DEVICES"

SUBJECT_COUNT=$(find "$DATA_PATH" -maxdepth 1 \( -name "*.nii.gz" -o -name "*.nii" \) | wc -l)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Subjects found: $SUBJECT_COUNT"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Step 1/2: Slicing NIfTI volumes..."
python "$SCRIPT_DIR/Slicer.py" "$DATA_PATH" "$TMP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Step 2/2: Running brain age prediction..."
python "$SCRIPT_DIR/Model_Test.py" "$TMP_DIR" "${OUT_PATH}pred.csv" "$MODEL"

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Pipeline complete in ${ELAPSED}s. Output: ${OUT_PATH}pred.csv"
