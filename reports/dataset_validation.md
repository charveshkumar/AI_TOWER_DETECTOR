# Dataset Validation Report — Roboflow Export

**Project**: AI-Based Tower Component Detection System  
**Dataset Inspected**: `data/processed/roboflow_export/`  
**Configuration File**: `data/processed/roboflow_export/data.yaml`  
**Date & Timestamp**: 2026-09-25  

---

## Executive Summary & Training Readiness Gate

> [!WARNING]
> **TRAINING READINESS: NOT READY (Action Required)**  
> The Roboflow export successfully provides 120 annotated images with 127 component instances, having deduplicated the 4 redundant raw images. However, **training is currently blocked** due to three critical discrepancies:
> 1. **Flipped Class Mapping**: `data.yaml` defines `0: monopole_tower, 1: supporting_tower`, which directly conflicts with project requirements (`0: supporting_tower, 1: monopole_tower`).
> 2. **Missing Validation & Test Splits**: `data.yaml` points to `../valid/images` and `../test/images`, but only `train/` exists in the filesystem.
> 3. **Mixed Polygon Segmentation Annotation**: 1 file contains YOLO polygon segmentation format rather than standard 5-token bounding boxes.

---

## 1. Dataset Configuration (`data.yaml`) Inspection

| Parameter | Value in `data.yaml` | Project Requirement / Actual Path | Discrepancy / Action |
| :--- | :--- | :--- | :--- |
| `train` | `../train/images` | `data/processed/roboflow_export/train/images` (120 images) | Valid relative path |
| `val` | `../valid/images` | `data/processed/roboflow_export/valid/images` (**MISSING**) | Directory does not exist on disk |
| `test` | `../test/images` | `data/processed/roboflow_export/test/images` (**MISSING**) | Directory does not exist on disk |
| `nc` | `2` | `2` | Match |
| `names[0]` | `monopole_tower` | `supporting_tower` | **MISMATCH (Flipped ID 0)** |
| `names[1]` | `supporting_tower` | `monopole_tower` | **MISMATCH (Flipped ID 1)** |

---

## 2. Class Verification & Mapping Integrity

- **Specification**:
  - Class `0`: `supporting_tower`
  - Class `1`: `monopole_tower`
- **Current Roboflow Export**:
  - Class `0`: `monopole_tower` (37 instances)
  - Class `1`: `supporting_tower` (90 instances)
- **Impact**: Training directly with current label IDs without re-indexing will invert the model's predictions, causing detection and evaluation metrics to swap classes.

---

## 3. Split Counts, Labels & Annotation Quality

### Split Inventory

| Split | Image Files | Label Files (`.txt`) | Total Instances | Empty Label Files | Missing Labels |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | 120 | 120 | 127 | 0 | 0 |
| **Validation** | 0 | 0 | 0 | 0 | Missing directory |
| **Test** | 0 | 0 | 0 | 0 | Missing directory |
| **Total** | **120** | **120** | **127** | **0** | **0** |

### Per-Class Instance Breakdown (in Roboflow Export)

| Class Name | Export Class ID | Required Class ID | Instance Count | % of Dataset |
| :--- | :--- | :--- | :--- | :--- |
| **`supporting_tower`** | `1` | `0` | 90 | 70.87% |
| **`monopole_tower`** | `0` | `1` | 37 | 29.13% |
| **Total** | — | — | **127** | **100.0%** |

### Annotation Integrity & Bounding Box Checks

- **1-to-1 Image-Label Match**: Every image has an exactly corresponding `.txt` label file.
- **Coordinate Normalization**: All bounding box coordinates `[x_center, y_center, width, height]` lie strictly within `[0.0, 1.0]`.
- **Bounding Box Dimensions**: 119 files follow standard 5-token YOLO bounding box format (`<cls> <xc> <yc> <w> <h>`).
- **Polygon Segmentation Entry**: 1 label file (`img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.txt`) contains 8 lines with multi-point segmentation polygons (`<cls> <x1> <y1> <x2> <y2> ...`).

---

## 4. Deduplication & Data Leakage Analysis

1. **Deduplication Check**:
   - The 4 duplicate images identified in Phase 1 (`img_29c096afeb0f4b7f`, `img_69e6287b52a74e3d`, `img_2bc4c71be05a4ddf`, `img_b4c54c0927624533`) are **excluded** from `roboflow_export/train/images`.
   - All 120 images in the export are unique.
2. **Data Leakage Hazard**:
   - Because all 120 images are placed into a single `train/` directory, there is currently no held-out validation or test set to evaluate true generalization performance.
   - When generating `train`, `val`, and `test` splits in Phase 2, consecutive drone frames must be partitioned by site/GPS cluster rather than naive random splitting to avoid spatial/visual leakage.

---

## 5. Review of Existing Codebase Modules

- **[`requirements.txt`](file:///A:/Electrohack/requirements.txt)**: Specifies `ultralytics>=8.1.0`, `torch>=2.2.0`, `opencv-python>=4.8.0`, `streamlit>=1.30.0`. Ready for training and inference dependencies.
- **[`src/config.py`](file:///A:/Electrohack/src/config.py)**: Correctly defines `CLASSES = {0: "supporting_tower", 1: "monopole_tower"}`. Paths point to `data/processed` and `data/raw`.
- **[`src/dataset/converter.py`](file:///A:/Electrohack/src/dataset/converter.py)**: To be implemented in Phase 2 to handle class ID remapping (0 <-> 1), polygon-to-bbox conversion, and stratified/grouped train/val/test split generation.
- **[`src/models/train.py`](file:///A:/Electrohack/src/models/train.py)**: To be implemented in Phase 4 to launch YOLO training with standard hyperparameters.

---

## 6. Recommended Action Plan for Phase 2 (Dataset Preparation)

1. **Class Remapping & Standardization**:
   - Remap class IDs in all label files so that `supporting_tower = 0` and `monopole_tower = 1`.
   - Convert polygon segmentation entries to standard normalized bounding boxes (`[min_x, min_y, max_x, max_y]` -> `[xc, yc, w, h]`).
2. **Stratified Split Generation**:
   - Generate deterministic 70% / 15% / 15% (or 80% / 10% / 10%) `train`, `val`, and `test` splits.
   - Store clean splits under `data/processed/splits/` or `data/processed/yolo/`.
3. **Generate Updated `data.yaml`**:
   - Create a clean `data.yaml` with correct absolute/relative split paths and verified class order: `['supporting_tower', 'monopole_tower']`.
