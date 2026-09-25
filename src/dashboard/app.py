"""
Phase 6 — Streamlit Interactive Web Dashboard for Tower Component Detection.
Provides real-time model inference, checkpoint comparison, detection visualization,
and inspection report export.
"""

import io
import os
import sys
import json
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure project root is on sys.path for Streamlit
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PIL import Image
import streamlit as st

# Import inference engine
from src.pipeline.inference import TowerDetector, DEFAULT_CHECKPOINTS, CLASS_NAMES

# Streamlit Page Config
st.set_page_config(
    page_title="AI Tower Component Detection | Electrohack",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom High-End Styling
st.markdown("""
<style>
    /* Global Typography & Palette */
    .main {
        background-color: #0d1117;
        color: #e6edf3;
    }
    .stApp {
        background: radial-gradient(circle at 10% 20%, rgba(13, 25, 45, 0.8) 0%, rgba(10, 15, 25, 1) 90%);
    }
    
    /* Header Container */
    .header-box {
        background: linear-gradient(135deg, rgba(16, 36, 64, 0.6) 0%, rgba(20, 50, 90, 0.3) 100%);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    /* Metric Card */
    .metric-card {
        background: rgba(22, 27, 34, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    .metric-val {
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }
    .metric-val-cyan { color: #00E5FF; }
    .metric-val-amber { color: #FF9100; }
    .metric-val-green { color: #00E676; }
    .metric-val-purple { color: #B388FF; }

    /* Legend Pill */
    .legend-pill {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 13px;
        font-weight: 600;
        margin-right: 8px;
    }
    .pill-cyan { background: rgba(0, 229, 255, 0.15); color: #00E5FF; border: 1px solid #00E5FF; }
    .pill-amber { background: rgba(255, 145, 0, 0.15); color: #FF9100; border: 1px solid #FF9100; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading YOLO Neural Network Checkpoint...")
def get_detector(model_key: str, checkpoint_path_str: str) -> Optional[TowerDetector]:
    """Caches model instances across Streamlit re-renders."""
    try:
        return TowerDetector(checkpoint_path=checkpoint_path_str, model_name=model_key)
    except Exception as e:
        st.error(f"Failed to load model '{model_key}': {e}")
        return None


def get_available_samples() -> Dict[str, Path]:
    """Collects sample test and validation drone images for quick demo testing."""
    samples = {}
    test_dir = Path("A:/Electrohack/data/processed/yolo/test/images")
    val_dir = Path("A:/Electrohack/data/processed/yolo/val/images")
    
    if test_dir.exists():
        for f in list(test_dir.glob("*.jpg"))[:6]:
            samples[f"Test Split — {f.name[:25]}..."] = f
    if val_dir.exists():
        for f in list(val_dir.glob("*.jpg"))[:4]:
            samples[f"Val Split — {f.name[:25]}..."] = f
    return samples


def main():
    # --- Sidebar Configuration ---
    with st.sidebar:
        st.markdown("### ⚙️ System Configuration")
        
        # 1. Model Selector (Augmented YOLO11m default)
        model_options = {
            "Augmented YOLO11m (1024px)": "augmented",
            "Baseline YOLO11m (640px)": "baseline"
        }
        selected_model_label = st.selectbox(
            "Select Model Checkpoint",
            options=list(model_options.keys()),
            index=0
        )
        selected_model_key = model_options[selected_model_label]
        target_checkpoint = DEFAULT_CHECKPOINTS[selected_model_key]

        # Checkpoint Status
        if target_checkpoint.exists():
            st.success(f"Checkpoint Loaded: `{target_checkpoint.name}`")
        else:
            st.error(f"Checkpoint missing at: {target_checkpoint}")

        st.markdown("---")
        
        # 2. Threshold Controls
        st.markdown("### 🎚️ Detection Thresholds")
        conf_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.05,
            max_value=1.00,
            value=0.20,
            step=0.05,
            help="Filters out bounding boxes below this confidence level. Recommended: 0.15 - 0.25 for balanced detection."
        )
        iou_threshold = st.slider(
            "NMS IoU Threshold",
            min_value=0.10,
            max_value=0.90,
            value=0.45,
            step=0.05,
            help="Non-Maximum Suppression threshold for merging overlapping bounding boxes."
        )

        st.markdown("---")
        
        # 3. Class Legend
        st.markdown("### 🏷️ Target Classes")
        st.markdown('<span class="legend-pill pill-cyan">Class 0: Supporting Tower</span>', unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px; color:#8b949e; margin-left:8px;'>Lattice structure transmission towers</p>", unsafe_allow_html=True)
        st.markdown('<span class="legend-pill pill-amber">Class 1: Monopole Tower</span>', unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px; color:#8b949e; margin-left:8px;'>Single tubular steel or concrete masts</p>", unsafe_allow_html=True)

        st.markdown("---")
        
        # 4. Quick Sample Loader
        sample_dict = get_available_samples()
        sample_choice = None
        if sample_dict:
            st.markdown("### 🖼️ Quick Demo Samples")
            selected_sample_label = st.selectbox(
                "Test with benchmark drone scenes:",
                options=["[ None / Upload Custom ]"] + list(sample_dict.keys()),
                index=0
            )
            if selected_sample_label != "[ None / Upload Custom ]":
                sample_choice = sample_dict[selected_sample_label]

    # --- Main Header Panel ---
    st.markdown("""
    <div class="header-box">
        <h1 style="margin:0; color:#00E5FF; font-size:2.2rem; font-weight:700;">
            🗼 AI Tower Component Detection System
        </h1>
        <p style="margin-top:8px; margin-bottom:0; color:#8b949e; font-size:1.05rem;">
            Real-time automated aerial asset inspection powered by Ultralytics YOLO11m.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # --- File Upload or Sample Selection ---
    col_input, col_info = st.columns([2, 1])
    
    with col_input:
        uploaded_file = st.file_uploader(
            "Upload Drone Aerial Image (JPG, JPEG, PNG)",
            type=["jpg", "jpeg", "png"],
            help="Upload an aerial photo of power transmission infrastructure."
        )

    with col_info:
        st.markdown("""
        <div style="background:rgba(22,27,34,0.6); padding:16px; border-radius:8px; border:1px solid rgba(255,255,255,0.05); font-size:13px; color:#8b949e;">
            <b style="color:#e6edf3;">System Capabilities:</b>
            <ul style="margin-top:6px; margin-bottom:0; padding-left:18px;">
                <li>High-resolution inference (up to 1024px)</li>
                <li>Real-time component categorization</li>
                <li>Bounding box coordinates & confidence export</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Determine Active Image Input
    image_input = None
    source_label = ""
    if uploaded_file is not None:
        try:
            image_input = Image.open(uploaded_file).convert("RGB")
            source_label = uploaded_file.name
        except Exception as e:
            st.error(f"Error opening uploaded image: {e}")
    elif sample_choice is not None:
        try:
            image_input = Image.open(sample_choice).convert("RGB")
            source_label = sample_choice.name
        except Exception as e:
            st.error(f"Error opening sample image: {e}")

    if image_input is None:
        st.info("👆 Upload an image or select a benchmark demo sample from the sidebar to run detection.")
        return

    # --- Execute Inference ---
    detector = get_detector(selected_model_key, str(target_checkpoint))
    if detector is None:
        st.error("Model engine could not be initialized.")
        return

    with st.spinner("Executing neural network component analysis..."):
        result = detector.predict(
            image_input=image_input,
            conf=conf_threshold,
            iou=iou_threshold
        )

    # --- Display Metric Badges ---
    st.markdown("### 📊 Detection Summary")
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Total Detections</div>
            <div class="metric-val metric-val-green">{result.counts.get('total', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Supporting Towers</div>
            <div class="metric-val metric-val-cyan">{result.counts.get('supporting_tower', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Monopole Towers</div>
            <div class="metric-val metric-val-amber">{result.counts.get('monopole_tower', 0)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Inference Latency</div>
            <div class="metric-val metric-val-purple">{result.inference_time_ms:.1f} ms</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # --- Visual Results Tabs ---
    tab_visual, tab_table, tab_json = st.tabs(["🖼️ Visual Inspection", "📋 Detections Table", "📄 Telemetry & Export"])

    with tab_visual:
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown(f"**Original Image**: `{source_label}` ({result.image_size[0]}×{result.image_size[1]} px)")
            st.image(result.original_image, use_container_width=True)
        with v_col2:
            st.markdown(f"**AI Detection Overlay** ({result.counts['total']} objects found)")
            st.image(result.annotated_image, use_container_width=True)

            # Download annotated image button
            buf = io.BytesIO()
            result.annotated_image.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            st.download_button(
                label="📥 Download Annotated Image (JPEG)",
                data=byte_im,
                file_name=f"annotated_{source_label}.jpg" if source_label else "annotated_tower_detection.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

    with tab_table:
        if result.detections:
            table_data = []
            for idx, d in enumerate(result.detections, 1):
                table_data.append({
                    "#": idx,
                    "Class": d.class_name,
                    "Confidence": f"{d.confidence*100:.2f}%",
                    "BBox (Pixels) [X1, Y1, X2, Y2]": f"[{d.bbox_xyxy[0]:.0f}, {d.bbox_xyxy[1]:.0f}, {d.bbox_xyxy[2]:.0f}, {d.bbox_xyxy[3]:.0f}]",
                    "Normalized [XC, YC, W, H]": f"[{d.bbox_normalized[0]:.3f}, {d.bbox_normalized[1]:.3f}, {d.bbox_normalized[2]:.3f}, {d.bbox_normalized[3]:.3f}]"
                })
            st.dataframe(table_data, use_container_width=True)
        else:
            # Dynamic low-confidence probe to assist user
            if conf_threshold > 0.05:
                probe_res = detector.predict(image_input=image_input, conf=0.05, iou=iou_threshold)
                if probe_res.detections:
                    top_cand = max(probe_res.detections, key=lambda d: d.confidence)
                    st.info(
                        f"💡 **Sensitivity Hint**: The model detected a candidate **{top_cand.class_name}** with **{top_cand.confidence*100:.1f}%** confidence. "
                        f"Lower the **Confidence Threshold** slider in the sidebar to **{top_cand.confidence:.2f}** or below to reveal it."
                    )
                else:
                    st.warning(f"No tower components detected in this image (even at minimal 5% sensitivity).")
            else:
                st.warning(f"No tower components detected above confidence threshold {conf_threshold:.2f}.")

    with tab_json:
        st.markdown("#### Inspection Metadata JSON")
        json_str = json.dumps(result.to_dict(), indent=2)
        st.json(result.to_dict())
        st.download_button(
            label="📥 Download Inspection Report (JSON)",
            data=json_str,
            file_name=f"inspection_report_{source_label}.json" if source_label else "inspection_report.json",
            mime="application/json",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
