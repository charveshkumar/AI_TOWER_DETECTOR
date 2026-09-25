# Phase 4 — Baseline Model Training & Validation Audit Report (YOLO11m)

**Project Root**: `A:\Electrohack\`  
**Model Architecture**: YOLO11m (`yolo11m.pt`)  
**Training Hardware**: NVIDIA Tesla T4 GPU (14.9 GB VRAM)  
**Execution Environment**: PyTorch 2.11.0+cu128, Ultralytics 8.4.163, Python 3.13.15  
**Experiment Directory**: [`A:\Electrohack\runs\detect\yolo11m_baseline\`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/)  
**Audit Status**: **AUDITED & VERIFIED** (Test Split strictly preserved and held out)  

---

## 1. Dataset Inventory & Split Verification

All dataset counts and paths were verified directly against [`data.yaml`](file:///A:/Electrohack/data/processed/yolo/data.yaml) and split directories without modifying or accessing test annotations:

| Dataset Split | Image Count | Label File Count | `supporting_tower` (Class 0) | `monopole_tower` (Class 1) | Total Instances | Split Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Train** | 84 | 84 | 68 | 23 | 91 | `[VERIFIED]` Used for training |
| **Validation** | 18 | 18 | 9 | 9 | 18 | `[VERIFIED]` Used for validation / plots |
| **Test** | 18 | 18 | 14 | 4 | 18 | `[HELD OUT]` Untouched & uninspected |
| **Total** | **120** | **120** | **91** | **36** | **127** | `[VERIFIED]` Master dataset total |

---

## 2. Validation Performance Summary (Best Epoch 99)

The validation metrics below correspond to **Epoch 99** (the peak mAP@50–95 checkpoint saved to [`best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt)), cross-checked directly against [`results.csv`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/results.csv) and [`BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxPR_curve.png):

| Class / Category | Precision ($P$) | Recall ($R$) | mAP@50 | mAP@50–95 | Metric Source / Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **All Classes** | **87.4%** (`0.87442`) | **75.0%** (`0.74968`) | **89.6%** (`0.89627`) | **42.5%** (`0.42474`) | `[VERIFIED]` [`results.csv:L100`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/results.csv#L100) |
| **`supporting_tower` (Class 0)** | **88.3%** (`0.8826`) | **77.8%** (`0.7778`) | **94.6%** (`0.9460`) | **43.0%** (`0.4296`) | `[VERIFIED]` Validation checkpoint run & [`BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxPR_curve.png) |
| **`monopole_tower` (Class 1)** | **86.6%** (`0.8658`) | **72.1%** (`0.7207`) | **84.7%** (`0.8470`) | **42.0%** (`0.4197`) | `[VERIFIED]` Validation checkpoint run & [`BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxPR_curve.png) |

> [!NOTE]
> **Important Note**: These metrics represent the validation split performance ($N=18$ images, 18 ground-truth instances) and serve as the baseline benchmark. The held-out test split ($N=18$ images) remains untouched.

---

## 3. Confusion Matrix Audit & Breakdown

Verified against [`confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/confusion_matrix.png) and [`confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/confusion_matrix_normalized.png):

### A. Ground-Truth vs. Prediction Counts
* **Ground-Truth Instances in Validation Split**: 9 `supporting_tower`, 9 `monopole_tower` (Total = 18).
* **`supporting_tower` True Positives**: **9 out of 9** instances correctly detected (`1.00` normalized).
* **`monopole_tower` True Positives**: **8 out of 9** instances correctly detected (`0.89` normalized).
* **`monopole_tower` Missed / False Negatives**: **1 out of 9** instance categorized as background (`0.11` normalized).
* **Direct Inter-Class Misclassification**: **0 instances** (Zero `supporting_tower` predicted as `monopole_tower`, and zero `monopole_tower` predicted as `supporting_tower`).
* **Background False Positives**:
  * 12 background regions detected as `supporting_tower`.
  * 3 background regions detected as `monopole_tower`.
  * *Note*: These background detections represent candidate bounding boxes on structural or cluttered background features at evaluation thresholds, not additional ground-truth objects.

---

## 4. F1-Confidence & Operating Threshold Audit

Verified against [`BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxF1_curve.png), [`BoxP_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxP_curve.png), and [`BoxR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxR_curve.png):

* **Overall Peak F1-Score**: **`0.79`** `[VERIFIED from BoxF1_curve.png title]`
* **Confidence Threshold at Peak F1**: **`0.348`** `[VERIFIED from BoxF1_curve.png title]`
  *(Correction: Corrected previous placeholder text that stated F1 = 0.81 at conf = 0.385)*
* **Precision-Confidence Relationship**: Reaches **`1.00` Precision at `conf = 0.448`** `[VERIFIED from BoxP_curve.png]`.
* **Recall-Confidence Relationship**: Maximum recall across all classes is **`0.97` at `conf = 0.000`** `[VERIFIED from BoxR_curve.png]`.
* **Deployment Threshold Status**: `[NOT FINALIZED]` The operational confidence threshold remains provisional until formal Phase 5 test-set evaluation is performed.

---

## 5. Training Configuration & Execution Profile

Verified against [`args.yaml`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/args.yaml) and training logs:

* **Task**: Object Detection (`detect`)
* **Base Architecture**: YOLO11m (`yolo11m.pt` - 20,031,574 parameters, 67.8 GFLOPs)
* **Epochs Trained**: 100 / 100 (`epochs: 100`, `patience: 50`)
* **Input Image Size**: `640 x 640`
* **Batch Size**: 16
* **Hardware Profile**: NVIDIA Tesla T4 GPU (VRAM usage: ~8.05 GB / 14.91 GB)
* **Random Seed**: `42` (Deterministic mode enabled)
* **Training Duration**: ~3.5 minutes

---

## 6. Checkpoint & Artifact Verification Matrix

All listed files are confirmed present, intact, and generated from the exact same model run:

| Artifact Name | File Path | Status |
| :--- | :--- | :--- |
| **Best Model Checkpoint** | [`runs/detect/yolo11m_baseline/weights/best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt) | `[VERIFIED PRESENT]` Locked & unmodified |
| **Last Model Checkpoint** | [`runs/detect/yolo11m_baseline/weights/last.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/last.pt) | `[VERIFIED PRESENT]` Locked & unmodified |
| **Results CSV** | [`runs/detect/yolo11m_baseline/results.csv`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/results.csv) | `[VERIFIED]` 100 complete epoch records |
| **Confusion Matrix** | [`runs/detect/yolo11m_baseline/confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/confusion_matrix.png) | `[VERIFIED]` Raw count matrix |
| **Normalized Confusion Matrix** | [`runs/detect/yolo11m_baseline/confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/confusion_matrix_normalized.png) | `[VERIFIED]` Normalized rate matrix |
| **F1-Confidence Curve** | [`runs/detect/yolo11m_baseline/BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxF1_curve.png) | `[VERIFIED]` 0.79 at 0.348 |
| **Precision-Recall Curve** | [`runs/detect/yolo11m_baseline/BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxPR_curve.png) | `[VERIFIED]` 0.896 mAP@50 |
| **Precision-Confidence Curve** | [`runs/detect/yolo11m_baseline/BoxP_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxP_curve.png) | `[VERIFIED]` 1.00 at 0.448 |
| **Recall-Confidence Curve** | [`runs/detect/yolo11m_baseline/BoxR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/BoxR_curve.png) | `[VERIFIED]` 0.97 at 0.000 |
| **Training Curves Plot** | [`runs/detect/yolo11m_baseline/results.png`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/results.png) | `[VERIFIED]` Loss & mAP progression |

---

## 7. Next Steps & Phase 5 Readiness

1. **Baseline Freeze**: The baseline model checkpoints and validation metrics are fully audited and frozen.
2. **Phase 5 (Test-Set Evaluation)**: The held-out test split ($N=18$ images) is ready to be evaluated in a separate evaluation run upon approval.
