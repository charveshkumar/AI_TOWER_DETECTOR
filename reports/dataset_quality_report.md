# Phase 3 — Dataset Quality Validation Report

**Project**: AI-Based Tower Component Detection System  
**Validated Dataset Directory**: `A:\Electrohack\data\processed\yolo`  
**Audit Timestamp**: 2026-09-25  
**Overall Readiness Gate**: **`READY WITH WARNINGS`**  

---

## 1. Executive Summary & Verification Matrix

| Quality Dimension | Evaluated Target | Actual Finding | Gate Status |
| :--- | :--- | :--- | :--- |
| **Dataset Inventory** | 120 images $\leftrightarrow$ 120 labels | 120 images $\leftrightarrow$ 120 labels (100% 1-to-1 match) | **PASSED** |
| **Class Mapping Accuracy** | `0: supporting_tower`, `1: monopole_tower` | Verified strictly mapped across all splits | **PASSED** |
| **Total Annotated Objects** | 127 bounding boxes | 127 total bounding boxes | **PASSED** |
| **Coordinate Bounds** | $0.0 \le xc, yc, w, h \le 1.0$ | 0 out-of-bound errors, 0 empty files | **PASSED** |
| **Split Hash Overlap** | 0 image overlaps | 0 hash overlaps between train, val, and test | **PASSED** |
| **GPS Cluster Leakage** | 0 multi-split flight clusters | 0 GPS flight bursts leaked across splits | **PASSED** |
| **Automated Anomaly Flags** | Geometric & quality sweeps | 6 images flagged for visual confirmation | **WARNING (Needs Review)** |

## 2. Per-Split Distribution & Balance

| Split | Images Count | % of Dataset | Total BBoxes | `supporting_tower` (Class 0) | `monopole_tower` (Class 1) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train** | `84` | `70.0%` | `91` | 68 objects | 23 objects |
| **Val** | `18` | `15.0%` | `18` | 9 objects | 9 objects |
| **Test** | `18` | `15.0%` | `18` | 14 objects | 4 objects |
| **Total** | **120** | **100.0%** | **127** | **91 objects (84 images)** | **36 objects (36 images)** |

## 3. Bounding Box Geometry & Shape Profiling

| Geometric Metric | Min | Max | Median | Mean | 25th %ile | 75th %ile |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Normalized Area ($w \times h$)** | 0.0006 | 0.563 | 0.2752 | 0.2716 | 0.2299 | 0.3251 |
| **Aspect Ratio ($w / h$)** | 0.1035 | 2.2089 | 0.3359 | 0.4424 | 0.2948 | 0.4781 |
| **Normalized Width ($w$)** | 0.0314 | 0.6133 | 0.3047 | 0.3126 | 0.2627 | 0.3525 |
| **Normalized Height ($h$)** | 0.0184 | 1.0 | 0.9141 | 0.8367 | 0.7979 | 0.9746 |

## 4. Image Quality & Degradation Profiling

| Quality Feature | Min | Max | Median | Mean | Target Safe Range | Flagged Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Laplacian Blur Variance** | 60.9195 | 3299.3572 | 1721.4901 | 1636.9188 | $\ge 100.0$ | 2 |
| **Mean Luminance / Exposure** | 53.418 | 217.3472 | 95.7408 | 105.4868 | $40.0 \le L \le 220.0$ | 0 |

## 5. Split Integrity & Leakage Verification

- **Image Hash Overlap**: 0 image SHA-256 collisions between `train`, `val`, and `test` splits.
- **GPS Flight Grouping**: All 81 drone flight coordinate clusters are strictly contained inside single partitions (0 cluster splits across train/val/test).
- **Data Leakage Risk**: **NONE DETECTED**.

## 6. Images Flagged for Human Review

Total images flagged for visual inspection: **6** (refer to [`reports/quality_validation/full_dataset_review.csv`](file:///A:/Electrohack/reports/quality_validation/full_dataset_review.csv) for the interactive ledger).

| # | Split | Image Filename | Assigned Class | Automated Flags |
| :--- | :--- | :--- | :--- | :--- |
| 01 | `train` | `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.jpg` | `supporting_tower` | Tiny BBox (Area=0.06%), Tiny BBox (Area=0.08%), Tiny BBox (Area=0.08%), Tiny BBox (Area=0.15%), Tiny BBox (Area=0.13%), Tiny BBox (Area=0.46%) |
| 02 | `train` | `img_1025992249b44a03_jpg.rf.2f227c80b086c8b27aa5042baa6a0790.jpg` | `monopole_tower` | Low Sharpness (Laplacian Var=60.9) |
| 03 | `train` | `img_c68ae09ce4034f44_jpg.rf.471b6d1f59d9f4e225c20be0c278563e.jpg` | `monopole_tower` | Narrow BBox Aspect Ratio (0.11:1) |
| 04 | `train` | `img_de01e7783ccf4d37_jpg.rf.16d52f8fdd6ab0432d8f9e9a11f72a99.jpg` | `monopole_tower` | Narrow BBox Aspect Ratio (0.13:1) |
| 05 | `train` | `img_ha7e2u2d72db_jpg.rf.b39cf471554880fc1a212f47bc7eb954.jpg` | `monopole_tower` | Narrow BBox Aspect Ratio (0.10:1) |
| 06 | `val` | `img_8de203dea6e347ba_jpg.rf.cbc1b6a5ea4aaaf92b23de05aecce4f2.jpg` | `monopole_tower` | Low Sharpness (Laplacian Var=87.5) |


## 7. Final Training Readiness Determination

> [!IMPORTANT]

> **READINESS STATUS: `READY WITH WARNINGS`**

> - **Structural Quality**: 100% compliant with standard YOLO architecture formats.

> - **Zero Data Leakage**: GPS cluster splitting protects hold-out evaluation validity.

> - **Human Review Recommendation**: Review the flagged items in [`reports/quality_validation/full_dataset_review.csv`](file:///A:/Electrohack/reports/quality_validation/full_dataset_review.csv) and multi-page contact sheets in [`reports/quality_validation/contact_sheets/`](file:///A:/Electrohack/reports/quality_validation/contact_sheets/) prior to initiating Phase 4 baseline model training.
