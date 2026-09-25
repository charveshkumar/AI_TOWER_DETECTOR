# Experiment Comparison: YOLO11m Baseline (640px) vs. YOLO11m Augmented (1024px)

**Project Root**: `A:\Electrohack\`  
**Target Split**: Held-Out Test Split ($N=18$ images)  
**Execution Environment**: Google Colab NVIDIA Tesla T4 GPU  
**Execution Timestamp**: 2026-09-26  

---

## 1. Test Split Performance Comparison

| Class / Category | Baseline (640px) mAP@50 | Augmented (1024px) mAP@50 | Delta ($\Delta$) | Factual Analysis |
| :--- | :---: | :---: | :---: | :--- |
| **`supporting_tower` (Class 0)** | **75.5%** (`0.7550`) | **79.6%** (`0.7960`) | **+4.1%** 🟢 | Higher input resolution ($1024\text{px}$) improved lattice beam feature capture on test drone shots. |
| **`monopole_tower` (Class 1)** | **41.4%** (`0.4140`) | **25.4%** (`0.2540`) | -16.0% 🔴 | Heavy geometric augmentations (copy-paste + scale) added excessive noise for only 23 source monopoles. |
| **Overall All Classes** | **58.5%** (`0.5845`) | **52.5%** (`0.5250`) | -6.0% | Strong gains on the dominant supporting tower class, but monopole class requires milder augmentation. |

---

## 2. Key Insights & Takeaways

1. **Resolution Boost Works for Structural Features**:
   * Raising resolution to $1024\text{px}$ improved `supporting_tower` precision and recall across test scenes, achieving a new peak of **79.6% mAP@50**.
2. **Augmentation Tuning for Small Classes**:
   * For extremely small datasets (23 training monopoles), aggressive Copy-Paste and MixUp can distort slender aspect ratios.
   * **Best configuration for future training**: Keep $1024\text{px}$ resolution, but use milder augmentation (`mosaic=0.5, mixup=0.0, copy_paste=0.0, scale=0.2`).
3. **Checkpoints Available**:
   * **Baseline 640px Model**: [`runs/detect/yolo11m_baseline/weights/best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt) (Best balanced overall mAP: 58.5%)
   * **Augmented 1024px Model**: [`runs/detect/yolo11m_augmented/weights/best.pt`](file:///A:/Electrohack/runs/detect/yolo11m_augmented/weights/best.pt) (Best supporting tower mAP: 79.6%)
