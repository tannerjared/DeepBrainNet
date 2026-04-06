#!/usr/bin/env python3
"""End-to-end DeepBrainNet brain age prediction pipeline.

This script is a convenience wrapper around Slicer.py and Model_Test.py.
It handles temporary-directory management, GPU configuration, and logging,
so you can run the full pipeline with a single command:

    python run_dbn.py --data /path/to/niftis --output results.csv \\
                      --model ../Models/DBN_model.h5

Run with --help for all available options.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time

logger = logging.getLogger(__name__)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_args():
    parser = argparse.ArgumentParser(
        description="DeepBrainNet end-to-end brain age prediction pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python run_dbn.py --data /data/brains/ --output results.csv --model ../Models/DBN_model.h5

  # CPU-only mode
  python run_dbn.py --data /data/ --output results.csv --model ../Models/DBN_model.h5 --cpu-only

  # Custom GPU, parallel workers, and flexible subject ID pattern
  python run_dbn.py --data /data/ --output results.csv --model ../Models/DBN_model.h5 \\
      --gpu 1 --workers 8 --id-pattern _T1w
        """,
    )
    parser.add_argument("--data", required=True,
                        help="Directory containing skull-stripped, MNI152-registered NIfTI images")
    parser.add_argument("--output", required=True,
                        help="Output CSV file path for predicted brain ages")
    parser.add_argument("--model", required=True,
                        help="Path to the pre-trained DeepBrainNet .h5 model file")
    parser.add_argument("--gpu", default="0",
                        help="CUDA GPU device index (default: 0)")
    parser.add_argument("--cpu-only", action="store_true",
                        help="Disable GPU and run entirely on CPU")
    parser.add_argument("--batch-size", type=int, default=80,
                        help="Batch size for model inference (default: 80)")
    parser.add_argument("--id-pattern", default="_T1",
                        help="Delimiter used to extract subject ID from filenames "
                             "(default: _T1). E.g. use _T1w for files like Sub01_T1w_brain.nii.gz")
    parser.add_argument("--workers", type=int, default=None,
                        help="Number of parallel workers for NIfTI slicing "
                             "(default: number of CPU cores)")
    parser.add_argument("--no-cleanup", action="store_true",
                        help="Keep the temporary slice directory after processing")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose/debug output")
    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Configure GPU / CPU
    if args.cpu_only:
        os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
        logger.info("Running on CPU only (GPU disabled)")
    else:
        os.environ.setdefault("CUDA_VISIBLE_DEVICES", args.gpu)
        logger.info("CUDA_VISIBLE_DEVICES=%s", os.environ["CUDA_VISIBLE_DEVICES"])

    # Validate inputs up front
    if not os.path.isdir(args.data):
        logger.error("Data directory does not exist: %s", args.data)
        sys.exit(1)
    if not os.path.isfile(args.model):
        logger.error("Model file not found: %s", args.model)
        sys.exit(1)

    out_dir = os.path.dirname(os.path.abspath(args.output))
    os.makedirs(out_dir, exist_ok=True)

    tmp_dir = tempfile.mkdtemp(prefix="dbn_slices_")
    os.makedirs(os.path.join(tmp_dir, "Test"), exist_ok=True)

    start = time.time()
    logger.info("Temporary slice directory: %s", tmp_dir)

    try:
        # Step 1: slice NIfTI volumes into 2D JPEGs
        logger.info("Step 1/2 — Slicing NIfTI volumes into 2D images...")
        slicer_cmd = [
            sys.executable,
            os.path.join(SCRIPT_DIR, "Slicer.py"),
            args.data,
            tmp_dir,
        ]
        if args.workers is not None:
            slicer_cmd.append(str(args.workers))
        subprocess.run(slicer_cmd, check=True)

        # Step 2: run brain age prediction
        logger.info("Step 2/2 — Running brain age prediction...")
        model_cmd = [
            sys.executable,
            os.path.join(SCRIPT_DIR, "Model_Test.py"),
            tmp_dir,
            args.output,
            args.model,
            "--batch-size", str(args.batch_size),
            "--id-pattern", args.id_pattern,
        ]
        if args.verbose:
            model_cmd.append("--verbose")
        subprocess.run(model_cmd, check=True)

    finally:
        if args.no_cleanup:
            logger.info("Temporary files kept at: %s", tmp_dir)
        else:
            shutil.rmtree(tmp_dir, ignore_errors=True)
            logger.info("Temporary directory removed")

    elapsed = time.time() - start
    logger.info("Pipeline complete in %.1f seconds. Output: %s", elapsed, args.output)


if __name__ == "__main__":
    main()
