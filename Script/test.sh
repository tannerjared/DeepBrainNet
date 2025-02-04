#!/bin/bash
# test.sh

DATA_PATH=''
OUT_PATH=''
MODEL=''

print_usage() {
  printf "\n\nUsage:\n\n"
  printf "\tRequired Parameters:\n\n" 
  printf "\t %s\n\n " "[-d]: Path containing aligned nifti images" "[-o]: Output directory for prediction csv" "[-m]: Specify Model file (.h5)"
  printf "\nExample: ./test.sh -d /myPath/ -o ./outputPath/ -m ../myModel.h5\n\n"
  exit 1
}

while getopts 'uhd:o:m:' flag; do
  case "${flag}" in
    u) print_usage ;;
    h) print_usage ;;
    d) DATA_PATH="${OPTARG}" ;;
    o) OUT_PATH="${OPTARG}" ;;
    m) MODEL="${OPTARG}" ;;
    *) print_usage; exit 1 ;;
  esac
done

export CUDA_VISIBLE_DEVICES=0

rm -rf ../tmp/
mkdir -p ../tmp/Test/All/

python Slicer.py $DATA_PATH ../tmp/
python Model_Test.py ../tmp/Test/All/ ${OUT_PATH}pred.csv $MODEL