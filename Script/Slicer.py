import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

import nibabel as nib
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

NUM_SLICES = 80
SLICE_START = 45
MIN_Z_DIM = SLICE_START + NUM_SLICES  # 125


def process_subject(args):
    """Process a single NIfTI file: validate, normalize, and extract 2D slices."""
    nifti_path, dest_dir, subject_name = args
    try:
        img = nib.load(nifti_path)
        data = img.get_fdata()

        if data.ndim < 3 or data.shape[2] < MIN_Z_DIM:
            return subject_name, False, (
                f"Skipping {subject_name}: volume shape {data.shape} has fewer "
                f"than {MIN_Z_DIM} slices in the z-dimension."
            )

        p97 = np.percentile(data, 97)
        if p97 == 0:
            return subject_name, False, (
                f"Skipping {subject_name}: 97th-percentile is zero, cannot normalize."
            )

        data = data * (185.0 / p97)

        # Strip .nii.gz or .nii extension for output filenames
        if subject_name.endswith(".nii.gz"):
            base_name = subject_name[:-7]
        else:
            base_name = os.path.splitext(subject_name)[0]

        for sl in range(NUM_SLICES):
            sliced = data[:, :, SLICE_START + sl]
            image_data = Image.fromarray(sliced).convert("RGB")
            image_data.save(os.path.join(dest_dir, f"{base_name}-{sl}.jpg"))

        return subject_name, True, f"Processed {subject_name} ({NUM_SLICES} slices)"
    except Exception as exc:
        return subject_name, False, f"Error processing {subject_name}: {exc}"


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if len(sys.argv) < 3:
        logger.error("Usage: python Slicer.py <input_dir> <output_dir> [num_workers]")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    num_workers = int(sys.argv[3]) if len(sys.argv) > 3 else os.cpu_count()

    if not os.path.isdir(input_dir):
        logger.error("Input directory does not exist: %s", input_dir)
        sys.exit(1)

    dest_test_dir = os.path.join(output_dir, "Test")
    os.makedirs(dest_test_dir, exist_ok=True)

    nifti_files = sorted(
        f for f in os.listdir(input_dir)
        if f.endswith(".nii.gz") or f.endswith(".nii")
    )

    if not nifti_files:
        logger.error("No NIfTI files (.nii or .nii.gz) found in: %s", input_dir)
        sys.exit(1)

    logger.info("Found %d NIfTI file(s) in %s", len(nifti_files), input_dir)

    tasks = [
        (os.path.join(input_dir, f), dest_test_dir, f)
        for f in nifti_files
    ]

    processed, skipped = 0, 0
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(process_subject, t): t[2] for t in tasks}
        for future in as_completed(futures):
            name, success, message = future.result()
            if success:
                logger.info(message)
                processed += 1
            else:
                logger.warning(message)
                skipped += 1

    logger.info(
        "Slicing complete — processed: %d  skipped: %d  total: %d",
        processed, skipped, len(nifti_files),
    )


if __name__ == "__main__":
    main()
