# AI-Based Tower Component Detection System

An end-to-end computer vision system engineered for automated detection and classification of transmission/telecom tower components with integrated image quality validation, per-class confidence analytics, and a web dashboard.

---

## 1. Problem Specification

The system detects and localizes two primary tower component classes:
- **Class `0`**: `supporting_tower`
- **Class `1`**: `monopole_tower`

### End-to-End Pipeline Workflow
1. **Input Ingestion**: Ingest image from file or dashboard upload.
2. **Quality Validation**: Pre-inference check against severe blur (Laplacian variance), underexposure, and overexposure (luminance histogram analysis). Unsuitable images are rejected with descriptive diagnostic feedback.
3. **Object Detection**: High-accuracy bounding box detection via modern YOLO architecture.
4. **Post-Processing & Analytics**:
   - Bounding boxes rendered with class labels and confidence scores.
   - Per-class average confidence calculated and reported independently.
5. **Interactive Dashboard**: Web interface for image testing, quality feedback, bounding box rendering, and metric visualization.

---

## 2. Project Architecture & Directory Layout

```
Electrohack/
├── data/
│   ├── raw/                 # Read-only original organizer dataset (never modified)
│   ├── processed/           # Converted, clean YOLO-format dataset splits (train/val/test)
│   └── quality_rejected/   # Sample images rejected by the quality validation filter
├── src/
│   ├── __init__.py
│   ├── config.py            # Central configuration, hyperparameters, class mappings, paths
│   ├── dataset/
│   │   ├── __init__.py
│   │   ├── inspector.py     # Non-destructive dataset auditing (integrity, distribution, formats)
│   │   └── converter.py     # Deterministic format conversion & split generation
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   └── quality_filter.py# Blur, exposure, and integrity validation algorithms
│   ├── models/
│   │   ├── __init__.py
│   │   ├── train.py         # Baseline & fine-tuning training pipelines
│   │   └── evaluate.py      # Independent evaluation metrics (mAP50, mAP50-95, PR curves)
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── inference.py     # Unified inference engine (Quality check + Detection + Analytics)
│   └── dashboard/
│       ├── __init__.py
│       └── app.py           # Streamlit web dashboard
├── tests/
│   ├── __init__.py
│   ├── test_quality_filter.py
│   └── test_inference.py
├── weights/                 # Model checkpoints (.pt)
├── runs/                    # Training runs, validation outputs, and logs
├── requirements.txt         # Project dependencies
├── .gitignore
└── README.md
```

---

## 3. Phased Execution Roadmap

- [x] **PHASE 0 — Project Initialization**: Repository scaffolding, architectural design, dependency specification, and environment checks.
- [ ] **PHASE 1 — Dataset Inspection**: Deep read-only analysis of raw data (file integrity, annotation schema, class balance, aspect ratios, corrupted entries).
- [ ] **PHASE 2 — Dataset Preparation**: Clean, reproducible conversion to standard YOLO format with stratified train/val/test splits.
- [ ] **PHASE 3 — Dataset Quality Validation**: Statistical profiling of dataset image quality to calibrate rejection thresholds.
- [ ] **PHASE 4 — Baseline Model Training**: Train baseline detector on training split using standard YOLO backbone.
- [ ] **PHASE 5 — Model Evaluation**: Rigorous evaluation on held-out validation/test splits (mAP@0.5, mAP@0.5:0.95, per-class metrics).
- [ ] **PHASE 6 — Image-Quality Filtering Module**: Production-ready image rejection filter for blur and extreme exposure.
- [ ] **PHASE 7 — Inference Pipeline**: Modular end-to-end Python pipeline outputting annotated images, bounding boxes, and per-class average confidences.
- [ ] **PHASE 8 — Dashboard**: Interactive web UI allowing image uploads, quality rejection reporting, detection overlays, and class confidence breakdowns.
- [ ] **PHASE 9 — End-to-End Testing**: Integration and stress testing of all components.
- [ ] **PHASE 10 — Final Documentation**: Final report, architecture documentation, and usage guides.

---

## 4. Development & Data Integrity Principles

1. **Zero Data Mutation**: Raw datasets in `data/raw/` are strictly read-only.
2. **No Fabricated Labels**: Annotations will only be derived from verified organizer inputs.
3. **Reproducibility**: All dataset transformations and splits are deterministic and logged.
4. **Modular Separation**: Decoupled architecture where quality checking, detection modeling, and UI operate independently.
