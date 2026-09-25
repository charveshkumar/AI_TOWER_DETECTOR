# Central configuration for Tower Component Detection System
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
QUALITY_REJECTED_DIR = DATA_DIR / "quality_rejected"
WEIGHTS_DIR = BASE_DIR / "weights"
RUNS_DIR = BASE_DIR / "runs"

# Class Mapping
CLASSES = {
    0: "supporting_tower",
    1: "monopole_tower"
}

# Image Quality Thresholds (Phase 6 baseline defaults, calibrated in Phase 3/6)
QUALITY_CONFIG = {
    "blur_threshold": 100.0,         # Laplacian variance below this is flagged as blurry
    "underexposure_threshold": 40.0, # Mean pixel intensity below this is underexposed
    "overexposure_threshold": 220.0, # Mean pixel intensity above this is overexposed
    "min_resolution": (224, 224),    # Minimum acceptable (width, height)
}

# Model Settings
MODEL_CONFIG = {
    "architecture": "yolov8m.pt",    # Modern YOLO base model (or yolov8s/yolov8n depending on compute)
    "imgsz": 640,
    "confidence_threshold": 0.25,
    "iou_threshold": 0.45
}
