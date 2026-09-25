"""
Unit tests for Phase 2 DatasetConverter and polygon conversion logic.
Uses standard library unittest for seamless test execution.
"""
import unittest
import tempfile
from pathlib import Path
from src.dataset.converter import polygon_to_bbox, build_class_mapping, DatasetConverter
from src.config import CLASSES


class TestDatasetConverter(unittest.TestCase):

    def test_polygon_to_bbox_standard(self):
        # Polygon defining a rectangle from (0.2, 0.3) to (0.6, 0.7)
        poly = [0.2, 0.3, 0.6, 0.3, 0.6, 0.7, 0.2, 0.7]
        xc, yc, w, h = polygon_to_bbox(poly)
        self.assertAlmostEqual(xc, 0.4, places=4)
        self.assertAlmostEqual(yc, 0.5, places=4)
        self.assertAlmostEqual(w, 0.4, places=4)
        self.assertAlmostEqual(h, 0.4, places=4)

    def test_polygon_to_bbox_out_of_bounds_clamping(self):
        # Polygon with vertices outside [0, 1]
        poly = [-0.1, 0.2, 1.2, 0.2, 1.2, 0.8, -0.1, 0.8]
        xc, yc, w, h = polygon_to_bbox(poly)
        self.assertTrue(0.0 <= xc <= 1.0)
        self.assertTrue(0.0 <= yc <= 1.0)
        self.assertTrue(0.0 < w <= 1.0)
        self.assertTrue(0.0 < h <= 1.0)
        self.assertEqual(xc, 0.5)
        self.assertEqual(w, 1.0)

    def test_polygon_to_bbox_invalid_length(self):
        with self.assertRaises(ValueError):
            polygon_to_bbox([0.1, 0.2, 0.3])

    def test_build_class_mapping_inverted_roboflow(self):
        # Roboflow export has: ['monopole_tower', 'supporting_tower']
        source_names = ["monopole_tower", "supporting_tower"]
        target_classes = {0: "supporting_tower", 1: "monopole_tower"}
        mapping = build_class_mapping(source_names, target_classes)
        # Source 0 (monopole) should map to Target 1 (monopole)
        # Source 1 (supporting) should map to Target 0 (supporting)
        self.assertEqual(mapping[0], 1)
        self.assertEqual(mapping[1], 0)

    def test_build_class_mapping_unknown_class(self):
        source_names = ["car", "tree"]
        target_classes = {0: "supporting_tower", 1: "monopole_tower"}
        with self.assertRaises(ValueError):
            build_class_mapping(source_names, target_classes)

    def test_converter_dry_run_safety(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_dir = Path(tmp_dir) / "yolo_test_out"
            converter = DatasetConverter(output_dir=output_dir)
            res = converter.validate_and_prepare(dry_run=True)
            self.assertTrue(res["dry_run"])
            self.assertFalse(output_dir.exists())
            self.assertEqual(res["total_images_inspected"], 120)
            self.assertEqual(res["total_objects_inspected"], 127)
            self.assertEqual(res["polygon_conversions_count"], 8)


if __name__ == "__main__":
    unittest.main()
