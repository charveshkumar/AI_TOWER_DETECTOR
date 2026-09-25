"""
Unit & Integration Tests for Phase 6 Inference Pipeline.
Tests TowerDetector model loading, inference prediction, output contracts, and edge cases.
"""

import unittest
from pathlib import Path
from PIL import Image
import numpy as np

from src.pipeline.inference import TowerDetector, DetectionResult, DEFAULT_CHECKPOINTS


class TestInferencePipeline(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Verify checkpoint presence
        cls.baseline_ckpt = DEFAULT_CHECKPOINTS["baseline"]
        cls.augmented_ckpt = DEFAULT_CHECKPOINTS["augmented"]
        
        # Test images
        cls.test_img_dir = Path("A:/Electrohack/data/processed/yolo/test/images")
        cls.sample_images = list(cls.test_img_dir.glob("*.jpg")) if cls.test_img_dir.exists() else []

    def test_checkpoint_existence(self):
        """Verify baseline checkpoint exists."""
        self.assertTrue(self.baseline_ckpt.exists(), f"Baseline checkpoint missing: {self.baseline_ckpt}")

    def test_detector_initialization(self):
        """Test detector initialization with baseline model."""
        detector = TowerDetector(checkpoint_path=self.baseline_ckpt, model_name="baseline")
        self.assertIsNotNone(detector.model)
        self.assertEqual(detector.model_name, "baseline")

    def test_prediction_output_contract(self):
        """Test that predict() returns a valid DetectionResult with all required attributes."""
        if not self.sample_images:
            self.skipTest("No test images available.")
            
        detector = TowerDetector(checkpoint_path=self.baseline_ckpt, model_name="baseline")
        test_img_path = self.sample_images[0]
        
        result = detector.predict(test_img_path, conf=0.25, iou=0.45)
        
        self.assertIsInstance(result, DetectionResult)
        self.assertIsInstance(result.original_image, Image.Image)
        self.assertIsInstance(result.annotated_image, Image.Image)
        self.assertIn("supporting_tower", result.counts)
        self.assertIn("monopole_tower", result.counts)
        self.assertIn("total", result.counts)
        self.assertGreater(result.inference_time_ms, 0.0)
        
        # Verify serialized dict
        d = result.to_dict()
        self.assertIn("inference_time_ms", d)
        self.assertIn("counts", d)
        self.assertIn("detections", d)

    def test_prediction_from_numpy_and_pil(self):
        """Test inference directly from in-memory PIL image and numpy array."""
        detector = TowerDetector(checkpoint_path=self.baseline_ckpt, model_name="baseline")
        
        # Create synthetic test image
        synthetic_pil = Image.new("RGB", (640, 640), color=(100, 150, 200))
        result_pil = detector.predict(synthetic_pil, conf=0.5)
        self.assertIsInstance(result_pil, DetectionResult)
        
        synthetic_np = np.zeros((640, 640, 3), dtype=np.uint8)
        result_np = detector.predict(synthetic_np, conf=0.5)
        self.assertIsInstance(result_np, DetectionResult)

    def test_missing_image_error_handling(self):
        """Test that non-existent image paths raise FileNotFoundError."""
        detector = TowerDetector(checkpoint_path=self.baseline_ckpt, model_name="baseline")
        with self.assertRaises(FileNotFoundError):
            detector.predict("A:/non_existent_image_path_12345.jpg")


if __name__ == "__main__":
    unittest.main()
