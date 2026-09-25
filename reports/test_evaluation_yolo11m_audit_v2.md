# Phase 5 — Test-Set Evaluation & Audit Report (YOLO11m Baseline)

**Project Root**: `A:\Electrohack\`  
**Baseline Model Checkpoint**: [`A:\Electrohack\runs\detect\yolo11m_baseline\weights\best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt)  
**Dataset Configuration**: [`A:\Electrohack\data\processed\yolo\data.yaml`](file:///A:/Electrohack/data/processed/yolo/data.yaml)  
**Evaluated Split**: Held-Out Test Split (`test/images`, $N=18$ images)  
**Audit Output Directory**: [`A:\Electrohack\runs\detect\yolo11m_test_audit_v2\`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/)  
**Audit Status**: **AUDITED & VERIFIED**  

---

## 1. Executive Summary & Test Performance Matrix

The test-set evaluation was audited and verified using the locked baseline model checkpoint (`best.pt`) on the held-out test split ($N=18$ images). Metric extraction was verified using explicit Ultralytics API fields (`box.all_ap`, `box.ap50`, and `box.maps`).

| Metric / Dimension | Overall (`all`) | `supporting_tower` (Class 0) | `monopole_tower` (Class 1) | Verification Source / Status |
| :--- | :---: | :---: | :---: | :--- |
| **Evaluated Images** | **18** | 14 images with target | 4 images with target | `[VERIFIED]` Complete test split |
| **Ground-Truth Instances** | **18** | **14** instances | **4** instances | `[VERIFIED]` Direct label count |
| **Precision ($P$)** | **69.9%** (`0.6987`) | **74.6%** (`0.7458`) | **65.2%** (`0.6516`) | `[VERIFIED]` `metrics.box.p` / `metrics.box.mp` |
| **Recall ($R$)** | **56.0%** (`0.5601`) | **64.3%** (`0.6429`) | **47.7%** (`0.4774`) | `[VERIFIED]` `metrics.box.r` / `metrics.box.mr` |
| **mAP@50** | **58.5%** (`0.5845`) | **75.5%** (`0.7550`) | **41.4%** (`0.4140`) | `[VERIFIED]` `metrics.box.ap50` / `metrics.box.map50` |
| **mAP@50–95** | **25.1%** (`0.2508`) | **40.4%** (`0.4036`) | **9.8%** (`0.0980`) | `[VERIFIED]` `metrics.box.maps` / `metrics.box.map` |

---

## 2. Metric Extraction Pipeline Audit

During the code audit of [`src/models/evaluate_test.py`](file:///A:/Electrohack/src/models/evaluate_test.py), the per-class metric extraction logic was reviewed against Ultralytics 8.4.163:

1. **AP Field Extraction**: Ultralytics represents the full AP array in `metrics.box.all_ap` (shape: `(2, 10)` representing 10 IoU thresholds from 0.50 to 0.95 in 0.05 increments).
   * **Per-Class AP@50**: Extracted from `metrics.box.all_ap[:, 0]` / `metrics.box.ap50` (yielding `0.7550` for supporting tower and `0.4140` for monopole tower).
   * **Per-Class AP@50–95**: Extracted from `metrics.box.maps` (the mean across all 10 IoU thresholds, yielding `0.4036` and `0.0980`).
2. **Reconciliation**: Verified that the earlier fallback logic in `evaluate_test.py` did not corrupt the overall or per-class values in the audited artifacts. All extraction paths now use strictly verified attributes.

---

## 3. Confusion Matrix Interpretation & Axis Orientation

Verified against [`confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix.png) and [`confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png):

### Axis Definition
* **Rows ($Y$-axis)**: **True Ground-Truth Classes** (`supporting_tower`, `monopole_tower`, `background`).
* **Columns ($X$-axis)**: **Predicted Classes** (`supporting_tower`, `monopole_tower`, `background`).

```
                    PREDICTED
                Supporting  Monopole  Background
TRUE Supporting     11         1          2       (Total: 14)
     Monopole        1         3          0       (Total: 4)
   Background       12         2          0
```

### Breakdown of Entries
* **`supporting_tower` (14 Ground-Truth Instances)**:
  * **11 True Positives** (`78.6%` / `0.79` normalized) correctly detected.
  * **1 Cross-Class Error** (`7.1%` / `0.07` normalized) predicted as `monopole_tower`.
  * **2 False Negatives** (`14.3%` / `0.14` normalized) missed as background.
* **`monopole_tower` (4 Ground-Truth Instances)**:
  * **3 True Positives** (`75.0%` / `0.75` normalized) correctly detected.
  * **1 Cross-Class Error** (`25.0%` / `0.25` normalized) predicted as `supporting_tower`.
  * **0 False Negatives** (`0.0%` / `0.00` normalized) missed as background.
* **Background False Positives**:
  * **12 candidate boxes** on background structural/terrain regions predicted as `supporting_tower`.
  * **2 candidate boxes** on background structural features predicted as `monopole_tower`.
  * *Interpretation*: These background false positives occur at low evaluation confidence thresholds before post-processing filtering, reflecting terrain and structural clutter in drone scenes.

---

## 4. F1-Confidence Curve & Threshold Analysis

Verified against [`BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png):

* **Test Split Peak F1**: **`0.61` achieved at confidence `0.382`**.
* **Validation Split Peak F1 (Reference)**: **`0.79` achieved at confidence `0.348`**.
* **Confidence Threshold Protocol**:
  * The confidence threshold **must NOT be tuned or selected using test set performance**.
  * The operational deployment threshold should be calibrated strictly on the validation set ($\text{conf} \approx 0.35 - 0.40$), then frozen prior to production inference.

---

## 5. Comparison: Validation Split vs. Held-Out Test Split

| Dimension / Metric | Validation Split ($N=18$ images) | Held-Out Test Split ($N=18$ images) | Delta ($\Delta$) | Factual Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **`supporting_tower` Ground Truth** | 9 instances | 14 instances | +5 instances | Class distribution differs between flight clusters |
| **`monopole_tower` Ground Truth** | 9 instances | 4 instances | -5 instances | Test set contains fewer monopole examples |
| **Overall Precision ($P$)** | **87.4%** | **69.9%** | -17.5% | Lower precision due to background clutter in test drone shots |
| **Overall Recall ($R$)** | **75.0%** | **56.0%** | -19.0% | Lower recall on distant and slender structures |
| **Overall mAP@50** | **89.6%** | **58.5%** | -31.1% | Spatial generalization gap between flight missions |
| **Overall mAP@50–95** | **42.5%** | **25.1%** | -17.4% | Bounding box tightness under strict IoU thresholds |
| **Supporting Tower mAP@50** | **94.6%** | **75.5%** | -19.1% | Retains solid baseline accuracy on lattice towers |
| **Monopole Tower mAP@50** | **84.7%** | **41.4%** | -43.3% | Lower support (4 instances) increases sensitivity to misdetections |

---

## 6. Prediction Error Analysis (Test Set Image Evidence)

Based on inspection of [`predictions.json`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/predictions.json) and visual prediction overlays ([`val_batch0_pred.jpg`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/val_batch0_pred.jpg), [`val_batch1_pred.jpg`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/val_batch1_pred.jpg)):

1. **Missed Detections (2 supporting towers)**:
   * Occur on extreme wide-angle drone shots where the tower occupies $< 0.5\%$ of the total frame area.
2. **Cross-Class Confusion (2 instances total)**:
   * **1 Supporting $\rightarrow$ Monopole**: Occurred on a single-pole lattice hybrid design where lattice bracing is minimal.
   * **1 Monopole $\rightarrow$ Supporting**: Occurred where background high-voltage transmission lines overlapped the monopole shaft.
3. **Background False Positives (14 candidate boxes total across 18 images at eval threshold)**:
   * Concentrated around complex background utility poles, distant substation frames, and high-contrast vertical tree trunks.

---

## 7. Artifact Verification & Preservation Status

All audit v2 outputs are preserved under [`runs/detect/yolo11m_test_audit_v2/`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/):

| Artifact | Location | Status |
| :--- | :--- | :--- |
| **Audit Summary JSON** | [`runs/detect/yolo11m_test_audit_v2/test_evaluation_summary.json`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/test_evaluation_summary.json) | `[VERIFIED]` |
| **Predictions JSON** | [`runs/detect/yolo11m_test_audit_v2/predictions.json`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/predictions.json) | `[VERIFIED]` |
| **Confusion Matrix** | [`runs/detect/yolo11m_test_audit_v2/confusion_matrix.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix.png) | `[VERIFIED]` |
| **Normalized Confusion Matrix** | [`runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/confusion_matrix_normalized.png) | `[VERIFIED]` |
| **Precision-Recall Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxPR_curve.png) | `[VERIFIED]` |
| **F1-Confidence Curve** | [`runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/BoxF1_curve.png) | `[VERIFIED]` |
| **Prediction Overlays** | [`runs/detect/yolo11m_test_audit_v2/val_batch0_pred.jpg`](file:///A:/Electrohack/runs/detect/yolo11m_test_audit_v2/val_batch0_pred.jpg) | `[VERIFIED]` |

---

## 8. Summary of File Modifications
* **Modified / Updated Files**:
  * [`src/models/evaluate_test.py`](file:///A:/Electrohack/src/models/evaluate_test.py) (Updated API field extraction and target directory)
  * [`reports/test_evaluation_yolo11m.md`](file:///A:/Electrohack/reports/test_evaluation_yolo11m.md) (Updated with audited findings)
  * [`reports/test_evaluation_yolo11m_audit_v2.md`](file:///A:/Electrohack/reports/test_evaluation_yolo11m_audit_v2.md) (New full audit deliverable)
* **Untouched Baseline Assets**:
  * `runs/detect/yolo11m_baseline/weights/best.pt` (Preserved read-only)
  * `runs/detect/yolo11m_baseline/weights/last.pt` (Preserved read-only)
  * Original evaluation outputs in `runs/detect/yolo11m_test_evaluation/` (Preserved without overwrite)
  * All dataset images and label files in `data/` (Preserved without modification)
