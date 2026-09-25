# Phase 1 Dataset Inspection & Read-Only Audit Report

**Project**: AI-Based Tower Component Detection System  
**Target Dataset Location**: `A:\Electrohack\data\raw\sample`  
**Total Dataset Footprint**: 799.25 MB across 124 files  

---

## Executive Summary & Gate Status

> [!IMPORTANT]

> **CRITICAL FINDINGS**:

> 1. **Zero Ground-Truth Annotations**: The raw dataset contains **124 valid images** and **0 annotation files** (0 bounding boxes).

> 2. **Identical Duplicates**: **4 exact duplicate file pairs** were detected with matching SHA-256 signatures.

> 3. **High Drone Capture Proportion**: **85 / 124 images (68.5%)** are high-resolution 20MP drone inspection shots with DJI telemetry and GPS coordinates.

> 4. **YOLO Incompatibility**: Direct YOLO training is **blocked** until ground-truth annotations are provided or established, and structured splits are generated.


## 1. Inventory & File Statistics

| Metric | Value | Status / Assessment |
| :--- | :--- | :--- |
| **Total Image Files** | `124` | All readable and uncorrupted |
| **Total Annotation Files** | `0` | Missing (No XML, JSON, or TXT labels) |
| **Total Bounding Boxes** | `0` | 0 Ground-truth instances |
| **Corrupted Files** | `0` | 0 files (100% integrity pass) |
| **Exact Duplicate Pairs** | `4` | 4 redundant duplicate pairs identified |
| **Predefined Splits** | `No` | No train/val/test subdirectories |
| **Total Dataset Size** | `799.25 MB` | High-res drone images account for >98% of size |

## 2. Image Formats & Resolution Distribution

### Format Breakdown

| Format | File Count | Percentage |
| :--- | :--- | :--- |
| **JPEG** | 38 | 30.65% |
| **MPO** | 85 | 68.55% |
| **PNG** | 1 | 0.81% |


### Dimension & Size Statistics

| Metric | Min | Max | Mean | Median | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Width (px)** | 120.0 | 5472.0 | 3923.23 | 5472.0 | 2291.5 |
| **Height (px)** | 260.0 | 3648.0 | 2672.88 | 3648.0 | 1450.86 |
| **Aspect Ratio (W/H)** | 0.46 | 1.78 | 1.37 | 1.5 | 0.31 |
| **File Size (KB)** | 6.07 | 10408.76 | 6600.22 | 9490.93 | 4450.35 |

### Top Resolution Clusters

| Resolution | Count | Domain Description |
| :--- | :--- | :--- |
| `474x316` | 1 | Web / Scraped / Mobile Thumbnail |
| `5472x3648` | 85 | DJI Mavic 2 Pro (Hasselblad L1D-20c Drone) |
| `480x480` | 1 | Web / Scraped / Mobile Thumbnail |
| `170x260` | 1 | Web / Scraped / Mobile Thumbnail |
| `344x496` | 1 | Web / Scraped / Mobile Thumbnail |
| `380x260` | 1 | Web / Scraped / Mobile Thumbnail |
| `391x260` | 1 | Web / Scraped / Mobile Thumbnail |
| `532x800` | 1 | Web / Scraped / Mobile Thumbnail |


## 3. Duplicate Analysis & Data Leakage Risks

### Exact Duplicate Pairs (SHA-256 Collisions)

| Duplicate File | Original Reference File | SHA-256 Hash | Size |
| :--- | :--- | :--- | :--- |
| `img_29c096afeb0f4b7f.JPG` | `img_071c8e9f3df7415a.JPG` | `45700b92940e903b...` | 9.47 MB |
| `img_2bc4c71be05a4ddf.JPG` | `img_03a380add45d48ab.JPG` | `4c6da0d3eb33dcf6...` | 8.61 MB |
| `img_69e6287b52a74e3d.JPG` | `img_09401dd6590e4a35.JPG` | `5bf7b95057167f1c...` | 8.97 MB |
| `img_b4c54c0927624533.JPG` | `img_7f301fb5fe5e48ff.JPG` | `1aa7c75b25c11137...` | 9.4 MB |


### Data Leakage Hazards

#### Risk: Exact Duplicates (CRITICAL)

- **Impact**: Found 4 exact duplicate image pairs with identical SHA-256 hashes under different filenames. Naive splitting would leak training samples into validation/test.
- **Mitigation Strategy**: Exact duplicates must be deduplicated before split assignment. Drone images belonging to identical GPS coordinates / flight bursts must be split as grouped entities (group-based / site-based splitting) rather than random splitting.

#### Risk: Drone Flight Burst Sequence / Near-Duplicates (HIGH)

- **Impact**: 85 images are high-resolution DJI drone captures taken in bursts at identical tower inspection locations. Random splitting across frames of the same flight will cause spatial/visual leakage.
- **Mitigation Strategy**: Exact duplicates must be deduplicated before split assignment. Drone images belonging to identical GPS coordinates / flight bursts must be split as grouped entities (group-based / site-based splitting) rather than random splitting.

## 4. Quality & Exposure Profiling

| Quality Metric | Min | Max | Mean | Median | Threshold Trigger | Flagged Count |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Laplacian Blur Variance** | 12.78 | 3718.81 | 717.29 | 578.04 | `< 100.0` (Severe Blur) | 1 |
| **Brightness Mean** | 53.49 | 217.41 | 105.35 | 95.78 | `< 40` (Under) / `> 220` (Over) | 0 |

## 5. Classes & YOLO Object Detection Compatibility

| Check | Finding | Action Required |
| :--- | :--- | :--- |
| **Target Classes** | `0: supporting_tower`, `1: monopole_tower` | Defined in system architecture |
| **Dataset Ground Truth** | 0 annotations present in `data/raw/sample` | Awaiting organizer label file or annotation source |
| **Bounding Box Coordinates** | N/A (No boxes exist) | Ground truth coordinates needed |
| **YOLO Format Compliance** | Non-compliant | Require normalized text format (`<class> <xc> <yc> <w> <h>`) |

## 6. Recommendations & Next Steps for Phase 2

1. **Clarify Annotation Source**: Verify whether the organizers provide a companion annotation archive or if this raw sample serves as a test/unlabeled benchmark suite.

2. **Deduplication**: Exclude the 4 redundant duplicate image files during conversion to prevent test leakage.

3. **Site/GPS Grouped Splitting**: Implement deterministic split generation that isolates drone GPS clusters into separate splits.

4. **Resolution Normalization**: Configure input resizing (e.g. 640x640 letterbox) to handle both 20MP drone imagery and low-res thumbnails seamlessly.
