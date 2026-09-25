"""
Phase 5 — Test-Set Evaluation & Audit Script for YOLO11m Baseline.
Evaluates the locked baseline model (best.pt) strictly on the held-out test split.
Outputs are saved into a dedicated directory: runs/detect/yolo11m_test_audit_v2/
"""

import json
import logging
import sys
from pathlib import Path
from ultralytics import YOLO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def run_test_evaluation(
    checkpoint_path: Path = Path("A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt"),
    data_yaml: Path = Path("A:/Electrohack/data/processed/yolo/data.yaml"),
    project_dir: Path = Path("A:/Electrohack/runs/detect"),
    run_name: str = "yolo11m_test_audit_v2",
    imgsz: int = 640,
    device: str = "cpu",
) -> dict:
    """
    Executes standard Ultralytics evaluation on the test split with strict API field extraction.
    """
    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}")
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset YAML not found at: {data_yaml}")

    save_dir = project_dir / run_name
    save_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("PHASE 5: TEST-SET AUDIT & EVALUATION (V2)")
    logger.info("=" * 60)
    logger.info(f"Model Checkpoint:  {checkpoint_path}")
    logger.info(f"Dataset YAML:      {data_yaml}")
    logger.info(f"Target Split:      test (Held-Out)")
    logger.info(f"Image Size:        {imgsz}")
    logger.info(f"Device:            {device}")
    logger.info(f"Output Directory:  {save_dir}")
    logger.info("=" * 60)

    model = YOLO(str(checkpoint_path))

    # Evaluate on explicit test split
    metrics = model.val(
        data=str(data_yaml),
        split="test",
        imgsz=imgsz,
        device=device,
        project=str(project_dir),
        name=run_name,
        exist_ok=True,
        save_json=True,
        plots=True,
        verbose=True
    )

    # Extract verified overall metrics
    p_overall = float(metrics.box.mp)
    r_overall = float(metrics.box.mr)
    map50_overall = float(metrics.box.map50)
    map50_95_overall = float(metrics.box.map)

    # Extract verified per-class metrics via verified Ultralytics properties
    class_metrics = {}
    class_names = list(metrics.names.values() if isinstance(metrics.names, dict) else metrics.names)
    ap50_arr = metrics.box.ap50 if hasattr(metrics.box, 'ap50') else metrics.box.all_ap[:, 0]
    maps_arr = metrics.box.maps if hasattr(metrics.box, 'maps') else metrics.box.all_ap.mean(axis=1)

    for i, name in enumerate(class_names):
        class_metrics[name] = {
            "class_id": i,
            "precision": float(metrics.box.p[i]),
            "recall": float(metrics.box.r[i]),
            "mAP50": float(ap50_arr[i]),
            "mAP50_95": float(maps_arr[i])
        }

    summary = {
        "audit_version": "v2",
        "evaluation_split": "test",
        "checkpoint": str(checkpoint_path),
        "dataset_yaml": str(data_yaml),
        "image_size": imgsz,
        "device": device,
        "overall": {
            "precision": p_overall,
            "recall": r_overall,
            "mAP50": map50_overall,
            "mAP50_95": map50_95_overall
        },
        "per_class": class_metrics,
        "classes": {
            0: "supporting_tower",
            1: "monopole_tower"
        }
    }

    # Save summary json
    summary_file = save_dir / "test_evaluation_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    logger.info("=" * 60)
    logger.info("TEST EVALUATION V2 COMPLETED")
    logger.info(f"Overall Precision: {p_overall:.4f}")
    logger.info(f"Overall Recall:    {r_overall:.4f}")
    logger.info(f"Overall mAP@50:    {map50_overall:.4f}")
    logger.info(f"Overall mAP@50-95: {map50_95_overall:.4f}")
    for name, m in class_metrics.items():
        logger.info(f"Class '{name}': P={m['precision']:.4f}, R={m['recall']:.4f}, mAP50={m['mAP50']:.4f}, mAP50-95={m['mAP50_95']:.4f}")
    logger.info(f"Saved to:          {save_dir}")
    logger.info("=" * 60)

    return summary


if __name__ == "__main__":
    run_test_evaluation()
