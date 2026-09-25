"""
Phase 5.5 — High-Accuracy Augmented Fine-Tuning Script for YOLO11m.
Includes high-resolution inputs (imgsz=1024), Copy-Paste, MixUp, Mosaic,
scale-jittering, and Cosine LR scheduling to maximize generalization on unseen drone data.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def train_yolo11m_augmented(
    data_yaml: Path = Path("A:/Electrohack/data/processed/yolo/data.yaml"),
    model_weights: str = "yolo11m.pt",
    epochs: int = 120,
    imgsz: int = 1024,
    batch_size: int = 8,
    patience: int = 40,
    device: str = "0",
    seed: int = 42,
    project_dir: Path = Path("A:/Electrohack/runs/detect"),
    run_name: str = "yolo11m_augmented",
) -> dict:
    """
    Trains YOLO11m with rich data augmentation and higher input resolution.
    """
    from ultralytics import YOLO

    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset YAML not found at: {data_yaml}")

    save_dir = project_dir / run_name
    save_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("HIGH-ACCURACY AUGMENTED TRAINING (YOLO11m)")
    logger.info("=" * 60)
    logger.info(f"Dataset:       {data_yaml}")
    logger.info(f"Base Weights:  {model_weights}")
    logger.info(f"Image Size:    {imgsz}x{imgsz} (High Resolution)")
    logger.info(f"Epochs:        {epochs} (Patience: {patience})")
    logger.info(f"Device:        {device}")
    logger.info(f"Augmentations: Mosaic=1.0, MixUp=0.15, Copy-Paste=0.3, Scale=0.5, Degrees=10.0")
    logger.info("=" * 60)

    model = YOLO(model_weights)

    start_time = time.time()

    results = model.train(
        data=str(data_yaml.resolve()),
        epochs=epochs,
        imgsz=imgsz,
        batch=batch_size,
        patience=patience,
        device=device,
        seed=seed,
        project=str(project_dir.resolve()),
        name=run_name,
        exist_ok=True,
        save=True,
        plots=True,
        # --- Advanced Augmentation Hyperparameters ---
        mosaic=1.0,          # 4-image mosaic (learns small & composite scales)
        mixup=0.15,          # Mixes image backgrounds (prevents background false alarms)
        copy_paste=0.30,     # Pastes towers onto diverse backgrounds (fixes monopole class imbalance)
        scale=0.50,          # Scale jitter +/- 50% (handles varying drone altitudes)
        degrees=10.0,        # Rotation +/- 10 degrees (handles camera roll)
        fliplr=0.5,          # Horizontal flip (50% probability)
        hsv_h=0.015,         # Hue variation (overcast vs sunny skies)
        hsv_s=0.7,           # Saturation variation
        hsv_v=0.4,           # Brightness/exposure variation
        cos_lr=True,         # Cosine learning rate schedule for smoother generalization
        weight_decay=0.001,  # Stronger L2 regularization against overfitting on 84 images
        close_mosaic=10,     # Disable mosaic for the final 10 epochs for crisp bounding box convergence
        verbose=True
    )

    elapsed_time = time.time() - start_time
    logger.info(f"Augmented Training Finished in {elapsed_time/60:.2f} minutes.")
    return {"status": "success", "run_dir": str(save_dir)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO11m with High-Accuracy Augmentations")
    parser.add_argument("--data", type=str, default="A:/Electrohack/data/processed/yolo/data.yaml")
    parser.add_argument("--model", type=str, default="yolo11m.pt")
    parser.add_argument("--epochs", type=int, default=120)
    parser.add_argument("--imgsz", type=int, default=1024)
    parser.add_argument("--batch", type=int, default=8)
    parser.add_argument("--patience", type=int, default=40)
    parser.add_argument("--device", type=str, default="0")
    parser.add_argument("--name", type=str, default="yolo11m_augmented")

    args = parser.parse_args()
    train_yolo11m_augmented(
        data_yaml=Path(args.data),
        model_weights=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch,
        patience=args.patience,
        device=args.device,
        run_name=args.name,
    )
