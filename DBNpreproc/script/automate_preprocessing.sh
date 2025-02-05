#!/bin/bash
# automate_preprocessing.sh
# This script loops over all T1 files in the specified input directory,
# runs the ANTs cortical-thickness pipeline for brain extraction/segmentation,
# and then registers the skull-stripped brain to the MNI152 1mm template using FSL FLIRT.
#
# It expects input T1 files to be named like: sub-*_T1w.nii.gz.
# Usage inside the container:
#    ./automate_preprocessing.sh /data/input /data/output
#
# All template files are assumed to be in /opt/app/templates.

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 INPUT_DIR OUTPUT_DIR"
    exit 1
fi

export ITK_GLOBAL_DEFAULT_NUMBER_OF_THREADS=4

INPUT_DIR="$1"
OUTPUT_DIR="$2"

# Set template file paths (all files are in /opt/app/templates)
TEMPLATE_MNI="/opt/app/templates/MNI152_T1_1mm_brain_LPS_filled.nii.gz"
BRAIN_TEMPLATE="/opt/app/templates/T_template0.nii.gz"
BRAIN_CEREBELLUM="/opt/app/templates/T_template0_BrainCerebellum.nii.gz"
BRAIN_PROB_MASK="/opt/app/templates/T_template0_BrainCerebellumProbabilityMask.nii.gz"
BRAIN_EXTRACT_MASK="/opt/app/templates/T_template0_BrainCerebellumExtractionMask.nii.gz"
PRIORS="/opt/app/templates/Priors2/priors%d.nii.gz"

# Ensure the output directory exists.
mkdir -p "$OUTPUT_DIR"

# Loop over T1 files in INPUT_DIR with names like sub-*_T1w.nii.gz
for T1FILE in "$INPUT_DIR"/sub-*_T1w.nii.gz; do
    # Extract the base filename (e.g. "sub-123_T1w.nii.gz")
    BASENAME=$(basename "$T1FILE")
    # Extract participant ID using a sed pattern (assumes format sub-<ID>_T1w.nii.gz)
    PARTICIPANT_ID=$(echo "$BASENAME" | sed -E 's/sub-([^_]+)_T1w\.nii(\.gz)?/\1/')
    
    echo "Processing participant: $PARTICIPANT_ID"
    
    # Create a subject-specific working directory in the OUTPUT_DIR.
    SUBJ_DIR="$OUTPUT_DIR/sub-$PARTICIPANT_ID"
    mkdir -p "$SUBJ_DIR"
    
    # Change into the subject directory.
    cd "$SUBJ_DIR" || { echo "Cannot change directory to $SUBJ_DIR"; exit 1; }
    
    # Run the ANTs cortical thickness pipeline.
    # -q 1 uses quick registration parameters.
    antsCorticalThickness.sh \
      -d 3 \
      -a "$T1FILE" \
      -e "$BRAIN_TEMPLATE" \
      -t "$BRAIN_CEREBELLUM" \
      -m "$BRAIN_PROB_MASK" \
      -f "$BRAIN_EXTRACT_MASK" \
      -p "$PRIORS" \
      -q 1 \
      -o "${SUBJ_DIR}/antsCT/"
    
    # Check that the expected skull-stripped brain exists.
    if [ ! -f "${SUBJ_DIR}/antsCT/ExtractedBrain0N4.nii.gz" ]; then
      echo "Error: antsCT output not found for participant $PARTICIPANT_ID."
      continue
    fi
    
    # Copy and rename the skull-stripped brain to follow the convention.
    FINAL_FILENAME="${SUBJ_DIR}/sub-${PARTICIPANT_ID}_T1_BrainAligned.nii.gz"
    cp "${SUBJ_DIR}/antsCT/ExtractedBrain0N4.nii.gz" "$FINAL_FILENAME"
    
    # Use FSL FLIRT to register the skull-stripped brain to the MNI152 1mm template.
    flirt -in "$FINAL_FILENAME" \
          -ref "$TEMPLATE_MNI" \
          -omat "${SUBJ_DIR}/sub-${PARTICIPANT_ID}_T1_BrainAligned.mat" \
          -out "$FINAL_FILENAME" \
          -dof 12 \
          -searchrx -180 180 -searchry -180 180 -searchrz -180 180
    
    echo "Finished processing participant $PARTICIPANT_ID. Output saved as $FINAL_FILENAME"
done
echo "All subjects processed."
