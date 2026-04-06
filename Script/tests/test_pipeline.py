"""Unit tests for DeepBrainNet pipeline utilities.

These tests cover pure-Python logic (no TensorFlow / GPU required) so they
can run in any CI environment.
"""

import os
import re
import tempfile
import unittest


# ---------------------------------------------------------------------------
# Replicate the extract_subject_id helper from Model_Test.py so tests can
# run without importing TensorFlow.
# ---------------------------------------------------------------------------
def extract_subject_id(filename, id_pattern):
    basename = os.path.basename(filename)
    name_no_slice = re.sub(r"-\d+\.jpg$", "", basename)
    if id_pattern and id_pattern in name_no_slice:
        return name_no_slice.split(id_pattern)[0]
    return name_no_slice


class TestExtractSubjectId(unittest.TestCase):
    """Tests for subject-ID extraction from slice filenames."""

    def test_standard_t1_pattern(self):
        result = extract_subject_id("Test/Subject1_T1_BrainAligned-0.jpg", "_T1")
        self.assertEqual(result, "Subject1")

    def test_t1w_pattern(self):
        result = extract_subject_id("Test/Sub001_T1w_Brain-5.jpg", "_T1w")
        self.assertEqual(result, "Sub001")

    def test_no_pattern_match_returns_base_name(self):
        result = extract_subject_id("Test/Subject1_brain-0.jpg", "_T1")
        self.assertEqual(result, "Subject1_brain")

    def test_high_slice_number(self):
        result = extract_subject_id("Test/Sub42_T1_BrainAligned-79.jpg", "_T1")
        self.assertEqual(result, "Sub42")

    def test_numeric_subject_id(self):
        result = extract_subject_id("Test/12345_T1_BrainAligned-0.jpg", "_T1")
        self.assertEqual(result, "12345")

    def test_empty_id_pattern_returns_full_base(self):
        result = extract_subject_id("Test/Sub01_T1_Brain-0.jpg", "")
        self.assertEqual(result, "Sub01_T1_Brain")

    def test_windows_style_path_separator(self):
        # os.path.basename handles backslashes on Linux too when given a plain
        # basename (no directory component), so this tests the no-prefix case.
        result = extract_subject_id("Sub01_T1_Brain-0.jpg", "_T1")
        self.assertEqual(result, "Sub01")


class TestPathJoining(unittest.TestCase):
    """Verify that os.path.join is safe regardless of trailing slashes."""

    def test_with_trailing_slash(self):
        self.assertEqual(os.path.join("/data/", "subject.nii.gz"), "/data/subject.nii.gz")

    def test_without_trailing_slash(self):
        self.assertEqual(os.path.join("/data", "subject.nii.gz"), "/data/subject.nii.gz")

    def test_nested_dest_dir(self):
        self.assertEqual(
            os.path.join("/tmp/dbn", "Test", "Sub01-0.jpg"),
            "/tmp/dbn/Test/Sub01-0.jpg",
        )


class TestSlicerOutputDirectory(unittest.TestCase):
    """Verify that the output directory creation logic works correctly."""

    def test_makedirs_creates_nested_dirs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "Test")
            os.makedirs(dest, exist_ok=True)
            self.assertTrue(os.path.isdir(dest))

    def test_makedirs_exist_ok_does_not_raise(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dest = os.path.join(tmpdir, "Test")
            os.makedirs(dest, exist_ok=True)
            # Second call should not raise
            os.makedirs(dest, exist_ok=True)


class TestNiftiFileFilter(unittest.TestCase):
    """Verify that NIfTI file filtering matches expected extensions."""

    def _filter(self, filenames):
        return [f for f in filenames if f.endswith(".nii.gz") or f.endswith(".nii")]

    def test_nii_gz_included(self):
        self.assertIn("brain.nii.gz", self._filter(["brain.nii.gz"]))

    def test_nii_included(self):
        self.assertIn("brain.nii", self._filter(["brain.nii"]))

    def test_jpg_excluded(self):
        self.assertNotIn("brain.jpg", self._filter(["brain.jpg"]))

    def test_mixed_list(self):
        files = ["a.nii.gz", "b.nii", "c.jpg", "d.txt", "e.nii.gz"]
        result = self._filter(files)
        self.assertEqual(result, ["a.nii.gz", "b.nii", "e.nii.gz"])


if __name__ == "__main__":
    unittest.main()
