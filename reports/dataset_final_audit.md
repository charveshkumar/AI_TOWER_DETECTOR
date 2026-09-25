# Comprehensive Final Dataset Audit Report

**Project**: AI-Based Tower Component Detection System  
**Raw Dataset Path**: `A:\Electrohack\data\raw\sample`  
**Processed Roboflow Export Path**: `A:\Electrohack\data\processed\roboflow_export`  
**Audited On**: 2026-09-25  

---

## 1. Executive Summary & Verification Matrix

| Metric / Audit Item | Raw Dataset (`sample/`) | Roboflow Export (`roboflow_export/`) | Target / Architecture Config | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Image Files** | `124` | `120` | 120 unique images | Verified (4 duplicates excluded in export) |
| **Unique Images (SHA-256)** | `120` | `120` | 120 | 100% Unique |
| **Exact Duplicate Pairs** | `4` | `0` | 0 in final dataset | Resolved by Roboflow deduplication |
| **Total Label Files** | `0` (Unannotated) | `120` | 120 (`.txt`) | 1-to-1 matching with images |
| **Missing / Orphaned Labels** | N/A | `0` missing / `0` orphaned | 0 | Perfect pairing |
| **Empty Label Files** | N/A | `0` empty files | 0 | All images have annotations |
| **Total Annotated Objects** | `0` | `127` | 127 total objects | Verified |
| **Class Order in `data.yaml`** | N/A | `0: monopole, 1: supporting` | `0: supporting, 1: monopole` | **CRITICAL MISMATCH (Flipped IDs)** |
| **Dataset Splits on Disk** | None | Only `train/` (120 files) | `train/`, `val/`, `test/` | **CRITICAL: Splits missing on disk** |

## 2. Verified Class Distribution (Image-Level vs. Object-Level)

### A. Target Specification Mapping (`src/config.py` Standard)

> **Target Rule**: Class `0` = `supporting_tower`, Class `1` = `monopole_tower`

| Class Name | Target Class ID | Roboflow Export Class ID | Total Objects (BBoxes) | Total Unique Images Containing Class | % of Objects | % of Images |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`supporting_tower`** | `0` | `1` | **90** | **83** | 70.87% | 69.17% |
| **`monopole_tower`** | `1` | `0` | **37** | **37** | 29.13% | 30.83% |
| **Total** | — | — | **127** | **120** | 100.0% | 100.0% |

### B. Co-Occurrence Analysis

- **Images with Single Class**: `120 / 120` (100% of images contain components of only one class).
- **Images with Multiple Classes**: `0 / 120` (No mixed tower images exist in the export).
- **Max Objects per Image**: 1 image contains 8 components (`img_00eeee4fc7754a82...`), while the remaining 119 images contain exactly 1 component.

## 3. Label Format & Quality Diagnostics

| Quality Check | Result | Details / Affected Files |
| :--- | :--- | :--- |
| **Coordinate Bounds (`0.0 <= c <= 1.0`)** | **0 errors** | All coordinates strictly inside normalized unit square |
| **Malformed Line Formats** | **0 errors** | All lines parseable as numerical tokens |
| **Standard 5-Token BBoxes** | **119 files** | Formatted as `<cls> <xc> <yc> <w> <h>` |
| **Polygon Segmentation Format** | **1 file** (1 entries) | `img_00eeee4fc7754a82_JPG.rf.8af42aa1141ebc257467120c6b3c4ace.txt` contains 8 polygon segmentation lines |

## 4. Deduplication & Cross-Dataset Reconciliation

### Duplicate Resolution

- Raw `data/raw/sample` contained **124 images** with **4 redundant SHA-256 duplicate pairs**:
  1. `img_29c096afeb0f4b7f.JPG` == `img_071c8e9f3df7415a.JPG`
  2. `img_2bc4c71be05a4ddf.JPG` == `img_03a380add45d48ab.JPG`
  3. `img_69e6287b52a74e3d.JPG` == `img_09401dd6590e4a35.JPG`
  4. `img_b4c54c0927624533.JPG` == `img_7f301fb5fe5e48ff.JPG`
- Roboflow export properly discarded the 4 duplicates (`['img_2bc4c71be05a4ddf', 'img_b4c54c0927624533', 'img_29c096afeb0f4b7f', 'img_69e6287b52a74e3d']`), yielding exactly **120 unique images**.

### Related-Scene Leakage Hazard

- **Drone Burst Flights**: **85 images** originate from DJI drone inspection bursts across **81 unique GPS locations**.
- **Leakage Mechanism**: Randomly shuffling consecutive drone frames across train and test splits will cause extreme validation leakage due to identical background and lighting.
- **Resolution**: Group-based / site-stratified splitting must be applied during Phase 2.

## 5. Comparison with Previous Reports

1. **Comparison with Phase 1 Audit (`dataset_audit.md`)**:
   - *Phase 1 Report*: Correctly identified 124 raw images, 4 exact duplicates, 0 annotations in raw folder, and 85 drone captures.
   - *Reconciliation*: The Roboflow export resolved the 4 duplicates and provided 120 images with 127 annotations.
2. **Comparison with Preliminary Validation (`dataset_validation.md`)**:
   - *Preliminary Report*: Noted 120 images, 120 labels, inverted class mapping, missing val/test splits, and 1 polygon file.
   - *Reconciliation*: Confirmed. The final audit provides exact image-level vs object-level breakdowns (90 objects across 83 images for `supporting_tower`; 37 objects across 37 images for `monopole_tower`).

## 6. Pre-Training Blockers & Action Items

> [!CAUTION]

> **BLOCKERS BEFORE TRAINING**:

> 1. **Class Remapping**: Label files currently encode `monopole_tower` as `0` and `supporting_tower` as `1`. They must be inverted to match `src/config.py` (`supporting_tower = 0`, `monopole_tower = 1`).

> 2. **Split Creation**: `val` and `test` directories do not exist on disk. A deterministic split pipeline must create `data/processed/yolo/{train,val,test}`.

> 3. **Polygon Bounding Box Extraction**: Convert the 8 polygon instances in `img_00eeee4fc7754a82...txt` to standard `[xc, yc, w, h]` bounding boxes.

> 4. **Update `data.yaml`**: Update paths to point to the newly created splits with names `['supporting_tower', 'monopole_tower']`.
