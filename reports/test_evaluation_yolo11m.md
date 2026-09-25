# Phase 5 — Official Test-Set Evaluation Report (YOLO11m Baseline)

**Project Root**: `A:\Electrohack\`  
**Evaluated Checkpoint**: [`A:\Electrohack\runs\detect\yolo11m_baseline\weights\best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt)  
**Dataset Configuration**: [`A:\Electrohack\data\processed\yolo\data.yaml`](file:///A:/Electrohack/data/processed/yolo/data.yaml)  
**Evaluation Target**: Held-Out Test Split (`test/images`, $N=18$ images)  
**Output Directory**: [`A:\Electrohack\runs\detect\yolo11m_test_audit_v2\`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/)  
**Audit & Execution Timestamp**: 2026-09-25  

---

## 1. Executive Summary & Test-Set Performance

The official Phase 5 test-set evaluation was executed strictly on the held-out test split using the locked baseline model checkpoint (`best.pt`). No weights, thresholds, or dataset splits were modified.

| Metric | Overall (`all`) | `supporting_tower` (Class 0) | `monopole_tower` (Class 1) | Evaluation Scope / Status |
| :--- | :---: | :---: | :---: | :--- |
| **Evaluated Images** | **18** | 14 images with target | 4 images with target | `[TEST SPLIT]` 100% evaluated |
| **Ground-Truth Instances** | **18** | **14** instances | **4** instances | `[TEST SPLIT]` Ground truth |
| **Precision ($P$)** | **69.9%** (`0.6987`) | **74.6%** (`0.7458`) | **65.2%** (`0.6516`) | `[TEST RESULT]` Standard eval |
| **Recall ($R$)** | **56.0%** (`0.5601`) | **64.3%** (`0.6429`) | **47.7%** (`0.4774`) | `[TEST RESULT]` Standard eval |
| **mAP@50** | **58.5%** (`0.5845`) | **75.5%** (`0.7550`) | **41.4%** (`0.4140`) | `[TEST RESULT]` Standard eval |
| **mAP@50–95** | **25.1%** (`0.2508`) | **40.4%** (`0.4036`) | **9.8%** (`0.0980`) | `[TEST RESULT]` Standard eval |

---

## 2. Comparison: Validation Split vs. Held-Out Test Split

| Dimension / Metric | Validation Split ($N=18$ images) | Held-Out Test Split ($N=18$ images) | Absolute Difference ($\Delta$) | Factual Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **Class 0 Ground Truth** | 9 instances | 14 instances | +5 instances | Test set contains more supporting towers |
| **Class 1 Ground Truth** | 9 instances | 4 instances | -5 instances | Test set contains fewer monopole towers |
| **Overall Precision ($P$)**| **87.4%** | **69.9%** | -17.5% | Lower precision due to background clutter in drone test scenes |
| **Overall Recall ($R$)** | **75.0%** | **56.0%** | -19.0% | Lower recall, particularly on distant/small monopole instances |
| **Overall mAP@50** | **89.6%** | **58.5%** | -31.1% | Generalization gap between drone flight clusters |
| **Overall mAP@50–95** | **42.5%** | **25.1%** | -17.4% | Bounding box tightness drop under strict IoU thresholds |
| **Supporting Tower mAP@50**| **94.6%** | **75.5%** | -19.1% | Retains strong detection capability on lattice towers |
| **Monopole Tower mAP@50** | **84.7%** | **41.4%** | -43.3% | Lower sample support (4 instances) and slender aspect ratios |
| **Optimal Peak F1** | **0.79** (at `conf=0.348`) | **0.61** (at `conf=0.382`) | -0.18 | Peak F1 occurs at similar confidence threshold range |

---

## 3. Test Confusion Matrix Audit

Verified against [`confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix.png) and [`confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png):

### A. Matrix Orientation & Ground-Truth Breakdown
* **$Y$-Axis (Rows)**: True Class (`supporting_tower`, `monopole_tower`, `background`)
* **$X$-Axis (Columns)**: Predicted Class (`supporting_tower`, `monopole_tower`, `background`)

* **`supporting_tower` (14 Ground-Truth Instances)**:
  * **11 instances** correctly detected as `supporting_tower` (**79%** / `0.79` normalized).
  * **1 instance** misclassified as `monopole_tower` (**7%** / `0.07` normalized).
  * **2 instances** missed as background / false negatives (**14%** / `0.14` normalized).
* **`monopole_tower` (4 Ground-Truth Instances)**:
  * **3 instances** correctly detected as `monopole_tower` (**75%** / `0.75` normalized).
  * **1 instance** misclassified as `supporting_tower` (**25%** / `0.25` normalized).
  * **0 instances** missed as background (**0%** / `0.00` normalized).
* **Background False Positives**:
  * **12 candidate boxes** on background structural features predicted as `supporting_tower`.
  * **2 candidate boxes** on background features predicted as `monopole_tower`.

---

## 4. Test Curves & Threshold Analysis

Verified against test evaluation plot artifacts:

* **F1-Confidence Curve**: [`runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png)
  * Peak overall F1 on test split is **`0.61` at `conf = 0.382`**.
* **Precision-Recall Curve**: [`runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png)
  * `supporting_tower`: **`0.755` mAP@50**
  * `monopole_tower`: **`0.414` mAP@50**
  * Overall: **`0.585` mAP@50**
* **Precision-Confidence Curve**: [`runs/detect/yolo11m_test_audit_v2/BoxP_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxP_curve.png)
  * Reaches **`1.00` Precision at `conf = 0.541`**.
* **Recall-Confidence Curve**: [`runs/detect/yolo11m_test_audit_v2/BoxR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxR_curve.png)
  * Maximum test recall across all classes is **`0.91` at `conf = 0.000`**.

---

## 5. Artifact Inventory

All Phase 5 artifacts have been generated and isolated under [`runs/detect/yolo11m_test_audit_v2/`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/):

| Artifact Description | Local File Link |
| :--- | :--- |
| **Structured JSON Metrics Summary** | [`runs/detect/yolo11m_test_audit_v2/test_evaluation_summary.json`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/test_evaluation_summary.json) |
| **COCO-Format Predictions** | [`runs/detect/yolo11m_test_audit_v2/predictions.json`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/predictions.json) |
| **Raw Confusion Matrix** | [`runs/detect/yolo11m_test_audit_v2/confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix.png) |
| **Normalized Confusion Matrix** | [`runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png) |
| **Precision-Recall Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png) |
| **F1-Confidence Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png) |
| **Precision-Confidence Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxP_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxP_curve.png) |
| **Recall-Confidence Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxR_curve.png) |
| **Batch 0 Predictions Visual Overlay** | [`runs/detect/yolo11m_test_audit_v2/val_batch0_pred.jpg`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/val_batch0_pred.jpg) |
| **Batch 1 Predictions Visual Overlay** | [`runs/detect/yolo11m_test_audit_v2/val_batch1_pred.jpg`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/val_batch1_pred.jpg) |
