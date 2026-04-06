import argparse
import logging
import os
import re
import sys

import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import ImageDataGenerator

logger = logging.getLogger(__name__)

BATCH_SIZE = 80
AGE_MIN = 5.0
AGE_MAX = 100.0


def extract_subject_id(filename, id_pattern):
    """Extract subject ID from a slice filename.

    Strips the leading subdirectory, the slice suffix (-N.jpg), and
    everything from the first occurrence of *id_pattern* onward.

    Example:
        "Test/Sub01_T1_BrainAligned-0.jpg" with id_pattern="_T1" → "Sub01"
    """
    basename = os.path.basename(filename)
    name_no_slice = re.sub(r"-\d+\.jpg$", "", basename)
    if id_pattern and id_pattern in name_no_slice:
        return name_no_slice.split(id_pattern)[0]
    return name_no_slice


def parse_args():
    parser = argparse.ArgumentParser(description="DeepBrainNet brain age prediction")
    parser.add_argument("tmp_dir", help="Temporary directory containing the Test/ slice images")
    parser.add_argument("output_csv", help="Output CSV file path")
    parser.add_argument("model", help="Path to the .h5 model file")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE,
                        help=f"Inference batch size (default: {BATCH_SIZE})")
    parser.add_argument("--id-pattern", default="_T1",
                        help="Delimiter used to split filenames for subject ID extraction "
                             "(default: _T1)")
    parser.add_argument("--verbose", action="store_true",
                        help="Enable verbose/debug logging")
    return parser.parse_args()


def main():
    args = parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Validate inputs
    if not os.path.isfile(args.model):
        logger.error("Model file not found: %s", args.model)
        sys.exit(1)
    if not args.model.endswith(".h5"):
        logger.warning("Model file does not have an .h5 extension: %s", args.model)
    if not os.path.isdir(args.tmp_dir):
        logger.error("Temporary directory does not exist: %s", args.tmp_dir)
        sys.exit(1)

    logger.info("Loading model from %s", args.model)
    model = load_model(args.model)
    if args.verbose:
        model.summary(print_fn=logger.debug)
    logger.info("Model loaded successfully")

    batch_size = args.batch_size
    datagen_test = ImageDataGenerator(rescale=1.0 / 255)

    test_generator = datagen_test.flow_from_directory(
        directory=args.tmp_dir,
        batch_size=batch_size,
        seed=42,
        shuffle=False,
        class_mode=None,
    )

    n_images = test_generator.n
    if n_images == 0:
        logger.error("No images found in %s", args.tmp_dir)
        sys.exit(1)
    if n_images % batch_size != 0:
        logger.warning(
            "Number of images (%d) is not a multiple of batch size (%d). "
            "Predictions for the final partial batch may be padded.",
            n_images, batch_size,
        )

    logger.info("Running inference on %d images (batch size: %d)", n_images, batch_size)

    IDlist = [
        extract_subject_id(fname, args.id_pattern)
        for fname in test_generator.filenames
    ]

    test_generator.reset()
    raw_predictions = model.predict(
        test_generator,
        verbose=1,
        steps=int(np.ceil(n_images / batch_size)),
    )

    prediction_data = pd.DataFrame({
        "ID": IDlist,
        "Prediction": raw_predictions.flatten()[:n_images],
    })

    final_rows = [
        {"ID": subject_id, "Pred_Age": float(np.median(group["Prediction"].values))}
        for subject_id, group in prediction_data.groupby("ID")
    ]
    out_data = pd.DataFrame(final_rows)

    # QC: flag predictions outside the plausible age range
    flagged = out_data[~out_data["Pred_Age"].between(AGE_MIN, AGE_MAX)]
    if not flagged.empty:
        logger.warning(
            "%d subject(s) have predictions outside the plausible range "
            "[%.0f, %.0f]:\n%s",
            len(flagged), AGE_MIN, AGE_MAX, flagged.to_string(index=False),
        )

    logger.info(
        "Summary — subjects: %d  mean: %.2f  std: %.2f  min: %.2f  max: %.2f",
        len(out_data),
        out_data["Pred_Age"].mean(),
        out_data["Pred_Age"].std(),
        out_data["Pred_Age"].min(),
        out_data["Pred_Age"].max(),
    )

    # Ensure output directory exists
    out_dir = os.path.dirname(os.path.abspath(args.output_csv))
    os.makedirs(out_dir, exist_ok=True)

    out_data.to_csv(args.output_csv, index=False)
    logger.info("Predictions written to %s", args.output_csv)


if __name__ == "__main__":
    main()
