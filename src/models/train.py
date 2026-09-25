"""
YOLO11m Baseline Training Script for Tower Component Detection System.
Trains YOLO11m on processed YOLO dataset (train split, val split for validation).
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def get_unique_run_name(project_dir: Path, base_name: str) -> str:
    """Generate a unique experiment run name if base_name already exists."""
    if not (project_dir / base_name).exists():
        return base_name
    counter = 1
    while (project_dir / f"{base_name}_{counter}").exists():
        counter += 1
    return f"{base_name}_{counter}"


def train_yolo11m(
    data_yaml: Path = Path("A:/Electrohack/data/processed/yolo/data.yaml"),
    model_weights: str = "yolo11m.pt",
    epochs: int = 100,
    imgsz: int = 640,
    batch_size: int = -1,
    patience: int = 20,
    device: str = "cpu",
    seed: int = 42,
    project_dir: Path = Path("A:/Electrohack/runs/detect"),
    run_name: str = "yolo11m_baseline",
) -> dict:
    """
    Executes YOLO11m baseline model training.
    """
    from ultralytics import YOLO
    import torch

    # Verify paths
    if not data_yaml.exists():
        raise FileNotFoundError(f"Dataset YAML not found at: {data_yaml}")

    project_dir.mkdir(parents=True, exist_ok=True)
    unique_run_name = get_unique_run_name(project_dir, run_name)
    save_dir = project_dir / unique_run_name

    logger.info("=" * 60)
    logger.info("PHASE 4: YOLO11m BASELINE MODEL TRAINING")
    logger.info("=" * 60)
    logger.info(f"Dataset YAML:        {data_yaml}")
    logger.info(f"Model Architecture:  {model_weights}")
    logger.info(f"Epochs:              {epochs} (Patience: {patience})")
    logger.info(f"Image Size:          {imgsz}")
    logger.info(f"Device:              {device}")
    logger.info(f"Seed:                {seed}")
    logger.info(f"Output Directory:    {save_dir}")
    logger.info(f"PyTorch Version:     {torch.__version__}")
    logger.info(f"CUDA Available:      {torch.cuda.is_available()}")
    logger.info("=" * 60)

    # Load model
    logger.info(f"Loading pretrained model weights: {model_weights}...")
    model = YOLO(model_weights)

    # For CPU training, autobatch (-1) is not used; default to 8
    if device == "cpu" or not torch.cuda.is_available():
        device = "cpu"
        actual_batch = 8 if batch_size == -1 else batch_size
    else:
        actual_batch = batch_size

    start_time = time.time()

    # Train model
    results = model.train(
        data=str(data_yaml.resolve()),
        epochs=epochs,
        imgsz=imgsz,
        batch=actual_batch,
        patience=patience,
        device=device,
        seed=seed,
        project=str(project_dir.resolve()),
        name=unique_run_name,
        save=True,
        exist_ok=False,
        plots=True,
        verbose=True,
    )

    elapsed_time = time.time() - start_time
    hours, rem = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(rem, 60)
    duration_str = f"{int(hours):02d}:{int(minutes):02d}:{seconds:05.2f}"

    # Best & last checkpoints
    best_ckpt = save_dir / "weights" / "best.pt"
    last_ckpt = save_dir / "weights" / "last.pt"
    results_csv = save_dir / "results.csv"

    best_epoch = None
    total_epochs_trained = 0
    final_metrics = {}

    if results_csv.exists():
        import pandas as pd
        try:
            df = pd.read_csv(results_csv)
            df.columns = [c.strip() for c in df.columns]
            total_epochs_trained = len(df)
            # Find best epoch based on metrics/mAP50-95(B) or mAP50(B)
            map_col = "metrics/mAP50-95(B)" if "metrics/mAP50-95(B)" in df.columns else "metrics/mAP50(B)"
            if map_col in df.columns:
                best_idx = df[map_col].idxmax()
                best_epoch = int(df.loc[best_idx, "epoch"]) if "epoch" in df.columns else int(best_idx + 1)
                best_row = df.loc[best_idx].to_dict()
                final_metrics = {
                    "best_epoch": best_epoch,
                    "precision": float(best_row.get("metrics/precision(B)", 0.0)),
                    "recall": float(best_row.get("metrics/recall(B)", 0.0)),
                    "mAP50": float(best_row.get("metrics/mAP50(B)", 0.0)),
                    "mAP50_95": float(best_row.get("metrics/mAP50-95(B)", 0.0)),
                }
        except Exception as e:
            logger.warning(f"Failed to parse results.csv: {e}")

    # Compile metrics summary
    metrics_dict = {
        "run_name": unique_run_name,
        "run_directory": str(save_dir),
        "best_checkpoint": str(best_ckpt) if best_ckpt.exists() else None,
        "last_checkpoint": str(last_ckpt) if last_ckpt.exists() else None,
        "training_duration_seconds": elapsed_time,
        "training_duration_formatted": duration_str,
        "epochs_requested": epochs,
        "epochs_completed": total_epochs_trained,
        "best_epoch": best_epoch,
        "metrics": final_metrics,
        "device": device,
        "pytorch_version": torch.__version__,
        "dataset_yaml": str(data_yaml),
        "classes": {
            0: "supporting_tower",
            1: "monopole_tower"
        }
    }

    # Save summary json
    summary_path = save_dir / "training_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=2)

    logger.info("=" * 60)
    logger.info("TRAINING COMPLETE")
    logger.info(f"Duration:        {duration_str}")
    logger.info(f"Epochs Trained:  {total_epochs_trained} / {epochs} (Best Epoch: {best_epoch})")
    logger.info(f"Precision:       {final_metrics.get('precision', 'N/A')}")
    logger.info(f"Recall:          {final_metrics.get('recall', 'N/A')}")
    logger.info(f"mAP@50:          {final_metrics.get('mAP50', 'N/A')}")
    logger.info(f"mAP@50-95:       {final_metrics.get('mAP50_95', 'N/A')}")
    logger.info(f"Best Checkpoint: {best_ckpt}")
    logger.info(f"Last Checkpoint: {last_ckpt}")
    logger.info(f"Summary Saved:   {summary_path}")
    logger.info("=" * 60)

    return metrics_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train YOLO11m Baseline for Tower Detection")
    parser.add_argument("--data", type=str, default="A:/Electrohack/data/processed/yolo/data.yaml")
    parser.add_argument("--model", type=str, default="yolo11m.pt")
    parser.add_argument("--epochs", type=int, default=100)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=-1)
    parser.add_argument("--patience", type=int, default=20)
    parser.add_argument("--device", type=str, default="cpu")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--project", type=str, default="A:/Electrohack/runs/detect")
    parser.add_argument("--name", type=str, default="yolo11m_baseline")

    args = parser.parse_args()

    train_yolo11m(
        data_yaml=Path(args.data),
        model_weights=args.model,
        epochs=args.epochs,
        imgsz=args.imgsz,
        batch_size=args.batch,
        patience=args.patience,
        device=args.device,
        seed=args.seed,
        project_dir=Path(args.project),
        run_name=args.name,
    )
