"""
Phase 6 Investigation Script:
Analyzes why the baseline model predicts monopole_tower for certain supporting tower images,
while the augmented model correctly classifies them.
Tests across validation split images and target test images at thresholds [0.10, 0.20, 0.35].
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


def run_investigation():
    base_ckpt = DEFAULT_CHECKPOINTS["baseline"]
    aug_ckpt = DEFAULT_CHECKPOINTS["augmented"]

    base_model = YOLO(str(base_ckpt))
    aug_model = YOLO(str(aug_ckpt))

    logger.info("=== CHECKPOINT EMBEDDED METADATA ===")
    logger.info(f"Baseline ({base_ckpt.name}) names:  {base_model.names}")
    logger.info(f"Augmented ({aug_ckpt.name}) names: {aug_model.names}")

    # Specific 4 target images
    test_img_dir = Path("A:/Electrohack/data/processed/yolo/test/images")
    test_lbl_dir = Path("A:/Electrohack/data/processed/yolo/test/labels")
    
    target_stems = [
        "img_6aae5e19d772407e_JPG.rf.d1684b185d60c6d8ad9afae5e44dc0f9",
        "img_00351f186c1f4a42_jpg.rf.befbfc7f19527cb6587311bddb2a0227",
        "img_0d0ed694e9b8486e_JPG.rf.e5feee19715c04431440a8d80bdfac56",
        "img_14321e8f0c474503_jpg.rf.954f1a97e0de876a9bf8b5da99dc5511"
    ]

    target_results = []
    thresholds = [0.10, 0.20, 0.35]

    for stem in target_stems:
        img_path = test_img_dir / f"{stem}.jpg"
        lbl_path = test_lbl_dir / f"{stem}.txt"
        
        gt_classes = []
        if lbl_path.exists():
            gt_classes = [int(l.split()[0]) for l in lbl_path.read_text().splitlines() if l.strip()]

        entry = {
            "image": img_path.name,
            "ground_truth_ids": gt_classes,
            "ground_truth_names": [CLASS_NAMES.get(cid, str(cid)) for cid in gt_classes],
            "baseline": {},
            "augmented": {}
        }

        for conf in thresholds:
            # Baseline direct inference
            b_res = base_model.predict(img_path, conf=conf, imgsz=640, verbose=False)[0]
            entry["baseline"][f"conf_{conf:.2f}"] = [
                {
                    "class_id": int(b.cls.item()),
                    "class_name": base_model.names[int(b.cls.item())],
                    "conf": round(float(b.conf.item()), 4),
                    "bbox": [round(x, 1) for x in b.xyxy[0].tolist()]
                }
                for b in b_res.boxes
            ]

            # Augmented direct inference
            a_res = aug_model.predict(img_path, conf=conf, imgsz=1024, verbose=False)[0]
            entry["augmented"][f"conf_{conf:.2f}"] = [
                {
                    "class_id": int(b.cls.item()),
                    "class_name": aug_model.names[int(b.cls.item())],
                    "conf": round(float(b.conf.item()), 4),
                    "bbox": [round(x, 1) for x in b.xyxy[0].tolist()]
                }
                for b in a_res.boxes
            ]

        target_results.append(entry)

    # Now evaluate full validation split (18 images)
    val_img_dir = Path("A:/Electrohack/data/processed/yolo/val/images")
    val_lbl_dir = Path("A:/Electrohack/data/processed/yolo/val/labels")
    val_images = list(val_img_dir.glob("*.jpg"))

    val_results = []
    for img_path in val_images:
        lbl_path = val_lbl_dir / f"{img_path.stem}.txt"
        gt_classes = [int(l.split()[0]) for l in lbl_path.read_text().splitlines() if l.strip()]

        b_res = base_model.predict(img_path, conf=0.20, imgsz=640, verbose=False)[0]
        a_res = aug_model.predict(img_path, conf=0.20, imgsz=1024, verbose=False)[0]

        val_results.append({
            "image": img_path.name,
            "ground_truth_ids": gt_classes,
            "ground_truth_names": [CLASS_NAMES.get(cid, str(cid)) for cid in gt_classes],
            "baseline_preds_conf020": [
                {"class_id": int(b.cls.item()), "class_name": base_model.names[int(b.cls.item())], "conf": round(float(b.conf.item()), 4)}
                for b in b_res.boxes
            ],
            "augmented_preds_conf020": [
                {"class_id": int(b.cls.item()), "class_name": aug_model.names[int(b.cls.item())], "conf": round(float(b.conf.item()), 4)}
                for b in a_res.boxes
            ]
        })

    report = {
        "checkpoints": {
            "baseline": str(base_ckpt),
            "augmented": str(aug_ckpt)
        },
        "target_images_analysis": target_results,
        "validation_split_analysis": val_results
    }

    out_file = Path("A:/Electrohack/reports/diagnostics/classification_investigation_results.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Investigation data saved to: {out_file}")


if __name__ == "__main__":
    run_investigation()
