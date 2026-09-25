"""
Diagnostic Script for Inference Discrepancies and Failure Analysis.
Evaluates both baseline and augmented models across confidence sweeps [0.05, 0.10, 0.25, 0.35, 0.50]
on supporting towers, monopoles, and raw drone samples.
Saves diagnostic visual overlays and structured JSON logs under reports/diagnostics/.
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
from ultralytics import YOLO

from src.pipeline.inference import TowerDetector, DEFAULT_CHECKPOINTS, CLASS_NAMES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DIAGNOSTIC_DIR = Path("A:/Electrohack/reports/diagnostics")
DIAGNOSTIC_DIR.mkdir(parents=True, exist_ok=True)


def run_diagnostics():
    baseline_path = DEFAULT_CHECKPOINTS["baseline"]
    augmented_path = DEFAULT_CHECKPOINTS["augmented"]

    logger.info("=" * 60)
    logger.info("DIAGNOSING INFERENCE PIPELINE & DETECTION THRESHOLDS")
    logger.info(f"Baseline Checkpoint:  {baseline_path}")
    logger.info(f"Augmented Checkpoint: {augmented_path}")
    logger.info("=" * 60)

    # 1. Collect target images
    test_img_dir = Path("A:/Electrohack/data/processed/yolo/test/images")
    val_img_dir = Path("A:/Electrohack/data/processed/yolo/val/images")
    raw_img_dir = Path("A:/Electrohack/data/raw/sample")

    # Select representative test supporting towers, monopoles, and raw drone shots
    test_images = list(test_img_dir.glob("*.jpg")) if test_img_dir.exists() else []
    val_images = list(val_img_dir.glob("*.jpg")) if val_img_dir.exists() else []
    raw_images = list(raw_img_dir.glob("*.JPG")) + list(raw_img_dir.glob("*.jpg")) if raw_img_dir.exists() else []

    logger.info(f"Found {len(test_images)} test images, {len(val_images)} val images, {len(raw_images)} raw images.")

    detector_baseline = TowerDetector(checkpoint_path=baseline_path, model_name="baseline")
    detector_augmented = TowerDetector(checkpoint_path=augmented_path, model_name="augmented")

    thresholds = [0.05, 0.10, 0.25, 0.35, 0.50]
    
    diagnostic_report = {
        "checkpoints": {
            "baseline": str(baseline_path),
            "augmented": str(augmented_path)
        },
        "threshold_sweep": thresholds,
        "results_by_image": []
    }

    # Evaluate across all test images
    for img_path in test_images[:10]:
        img_entry = {
            "filename": img_path.name,
            "path": str(img_path),
            "baseline_predictions": {},
            "augmented_predictions": {}
        }

        for conf in thresholds:
            # Baseline inference
            res_base = detector_baseline.predict(img_path, conf=conf, iou=0.45)
            img_entry["baseline_predictions"][f"conf_{conf:.2f}"] = {
                "total": res_base.counts["total"],
                "supporting": res_base.counts.get("supporting_tower", 0),
                "monopole": res_base.counts.get("monopole_tower", 0),
                "detections": [
                    {
                        "class": d.class_name,
                        "conf": round(d.confidence, 4),
                        "bbox": [round(x, 1) for x in d.bbox_xyxy]
                    }
                    for d in res_base.detections
                ]
            }

            # Augmented inference
            res_aug = detector_augmented.predict(img_path, conf=conf, iou=0.45)
            img_entry["augmented_predictions"][f"conf_{conf:.2f}"] = {
                "total": res_aug.counts["total"],
                "supporting": res_aug.counts.get("supporting_tower", 0),
                "monopole": res_aug.counts.get("monopole_tower", 0),
                "detections": [
                    {
                        "class": d.class_name,
                        "conf": round(d.confidence, 4),
                        "bbox": [round(x, 1) for x in d.bbox_xyxy]
                    }
                    for d in res_aug.detections
                ]
            }

        # Save annotated image for comparison at conf=0.10 and conf=0.35
        res_base_low = detector_baseline.predict(img_path, conf=0.10)
        res_base_low.annotated_image.save(DIAGNOSTIC_DIR / f"baseline_conf0.10_{img_path.stem}.jpg")
        
        res_base_std = detector_baseline.predict(img_path, conf=0.35)
        res_base_std.annotated_image.save(DIAGNOSTIC_DIR / f"baseline_conf0.35_{img_path.stem}.jpg")

        res_aug_std = detector_augmented.predict(img_path, conf=0.35)
        res_aug_std.annotated_image.save(DIAGNOSTIC_DIR / f"augmented_conf0.35_{img_path.stem}.jpg")

        diagnostic_report["results_by_image"].append(img_entry)

    # Save complete json report
    out_json = DIAGNOSTIC_DIR / "diagnostic_sweep_results.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(diagnostic_report, f, indent=2)

    logger.info(f"Diagnostic sweep complete. Results written to: {out_json}")


if __name__ == "__main__":
    run_diagnostics()
