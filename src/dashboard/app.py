"""
STRUCTIVISION PRO — AI Vision Intelligence & Structural Tower Inspection Suite.
Enterprise Real-Time Aerial Asset Detection powered by YOLO11m Neural Networks.
"""

import io
import os
import sys
import json
import time
import zipfile
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

# Ensure project root is on sys.path for Streamlit
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import streamlit as st

# Import inference engine
from src.pipeline.inference import TowerDetector, DEFAULT_CHECKPOINTS, CLASS_NAMES, CLASS_COLORS, DetectionResult

# Streamlit Page Config
st.set_page_config(
    page_title="STRUCTIVISION PRO | AI Tower Intelligence",
    page_icon="🗼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High-End Modern Futuristic Glassmorphism Design System
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Global App Canvas */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0B192C 0%, #060D17 60%, #03070C 100%);
        color: #E2E8F0;
    }

    /* Top Brand Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(16, 44, 87, 0.45) 0%, rgba(15, 23, 42, 0.7) 100%);
        border: 1px solid rgba(0, 229, 255, 0.25);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 24px;
        backdrop-filter: blur(16px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .hero-title {
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(90deg, #00E5FF 0%, #00E676 50%, #38BDF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        line-height: 1.2;
    }
    .hero-sub {
        color: #94A3B8;
        font-size: 13.5px;
        margin-top: 4px;
    }
    .status-badge-live {
        background: rgba(0, 230, 118, 0.12);
        border: 1px solid rgba(0, 230, 118, 0.4);
        color: #00E676;
        padding: 6px 16px;
        border-radius: 30px;
        font-size: 12.5px;
        font-weight: 700;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        box-shadow: 0 0 20px rgba(0, 230, 118, 0.2);
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background: #00E676;
        border-radius: 50%;
        box-shadow: 0 0 10px #00E676;
        animation: pulse 1.8s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.9); opacity: 0.8; }
        50% { transform: scale(1.3); opacity: 1; }
        100% { transform: scale(0.9); opacity: 0.8; }
    }

    /* Glass KPI Metric Cards */
    .glass-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        backdrop-filter: blur(12px);
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        border-color: rgba(0, 229, 255, 0.35);
        box-shadow: 0 14px 40px rgba(0, 229, 255, 0.12);
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(0, 229, 255, 0.6), transparent);
    }
    .kpi-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .kpi-val {
        font-size: 34px;
        font-weight: 800;
        margin-top: 6px;
        line-height: 1;
        font-family: 'JetBrains Mono', monospace;
    }
    .val-cyan { color: #00E5FF; }
    .val-amber { color: #FFB300; }
    .val-green { color: #00E676; }
    .val-purple { color: #C084FC; }

    /* Interactive Sample Picker Cards */
    .sample-pill-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
        gap: 10px;
        margin-top: 12px;
    }
    .sample-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .sample-card:hover {
        background: rgba(0, 229, 255, 0.15);
        border-color: #00E5FF;
        transform: translateY(-2px);
    }

    /* Crop Card */
    .crop-card {
        background: rgba(15, 23, 42, 0.85);
        border: 1px solid rgba(0, 229, 255, 0.2);
        border-radius: 14px;
        padding: 14px;
        margin-bottom: 12px;
    }

    /* Streamlit UI Enhancements */
    div.stButton > button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00875A 0%, #00B074 100%) !important;
        border: none !important;
        color: white !important;
        box-shadow: 0 4px 20px rgba(0, 180, 116, 0.35) !important;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 180, 116, 0.5) !important;
    }

    /* Tabs override */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.6);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #94A3B8;
        font-weight: 600;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(0, 229, 255, 0.15) !important;
        color: #00E5FF !important;
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Connecting to Ultra-High Resolution YOLO11m Neural Engine...")
def get_detector(model_key: str, checkpoint_path_str: str) -> Optional[TowerDetector]:
    """Caches model instances across Streamlit re-renders."""
    try:
        return TowerDetector(checkpoint_path=checkpoint_path_str, model_name=model_key)
    except Exception as e:
        st.error(f"Failed to load model '{model_key}': {e}")
        return None


def get_available_samples() -> Dict[str, Path]:
    """Collects benchmark test and validation drone images."""
    samples = {}
    test_dir = Path("A:/Electrohack/data/processed/yolo/test/images")
    val_dir = Path("A:/Electrohack/data/processed/yolo/val/images")
    
    if test_dir.exists():
        for idx, f in enumerate(list(test_dir.glob("*.jpg"))[:8], 1):
            samples[f"🗼 Mission Scene #{idx} (Test Split)"] = f
    if val_dir.exists():
        for idx, f in enumerate(list(val_dir.glob("*.jpg"))[:4], 9):
            samples[f"📡 Mission Scene #{idx} (Val Split)"] = f
    return samples


def apply_optical_filters(img: Image.Image, filter_mode: str) -> Image.Image:
    """Applies real-time optical filters for edge enhancement, rust isolation, and HDR boost."""
    if filter_mode == "✨ HDR Defect Boost":
        res = ImageEnhance.Contrast(img).enhance(1.45)
        res = ImageEnhance.Sharpness(res).enhance(1.8)
        return ImageEnhance.Brightness(res).enhance(1.08)
    elif filter_mode == "🔬 Lattice Edge Sharpening":
        res = ImageEnhance.Sharpness(img).enhance(2.5)
        return ImageEnhance.Contrast(res).enhance(1.3)
    elif filter_mode == "👁 Rust & Corrosion Isolation":
        res = ImageEnhance.Color(img).enhance(1.9)
        res = ImageEnhance.Contrast(res).enhance(1.4)
        return ImageEnhance.Brightness(res).enhance(1.05)
    elif filter_mode == "🌑 Edge Contour Wireframe":
        gray = img.convert("L")
        edges = gray.filter(ImageFilter.FIND_EDGES)
        return ImageEnhance.Contrast(edges).enhance(2.0).convert("RGB")
    return img


def create_batch_zip(batch_results: List[Tuple[str, DetectionResult]]) -> bytes:
    """Packages all annotated images and JSON telemetry into a downloadable ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        summary_records = []
        for name, res in batch_results:
            img_buf = io.BytesIO()
            res.annotated_image.save(img_buf, format="JPEG", quality=95)
            clean_name = Path(name).stem
            zf.writestr(f"annotated_images/{clean_name}_detected.jpg", img_buf.getvalue())
            
            json_str = json.dumps(res.to_dict(), indent=2)
            zf.writestr(f"telemetry_json/{clean_name}_report.json", json_str)
            
            summary_records.append({
                "image_name": name,
                "total_detections": res.counts.get("total", 0),
                "supporting_towers": res.counts.get("supporting_tower", 0),
                "monopole_towers": res.counts.get("monopole_tower", 0),
                "latency_ms": round(res.inference_time_ms, 1),
                "image_width": res.image_size[0],
                "image_height": res.image_size[1],
            })
        
        df_summary = pd.DataFrame(summary_records)
        zf.writestr("batch_inspection_summary.csv", df_summary.to_csv(index=False))
        
    return buf.getvalue()


def main():
    # --- Top Hero Banner ---
    st.markdown("""
    <div class="hero-banner">
        <div>
            <h1 class="hero-title">STRUCTIVISION PRO // AERIAL VISION INTELLIGENCE</h1>
            <div class="hero-sub">Autonomous Telecommunication Infrastructure & Transmission Tower Detection Engine</div>
        </div>
        <div class="status-badge-live">
            <span class="pulse-dot"></span> NEURAL INFERENCE ACTIVE
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.markdown("<h3 style='color:#00E5FF; margin-top:0;'>⚙️ Neural Engine Settings</h3>", unsafe_allow_html=True)
        
        # 1. Model Selector (Augmented YOLO11m Default)
        model_options = {
            "⚡ Augmented YOLO11m (1024px) [Default]": "augmented",
            "🛡️ Baseline YOLO11m (640px)": "baseline"
        }
        selected_model_label = st.selectbox(
            "Model Architecture Checkpoint",
            options=list(model_options.keys()),
            index=0,
            help="Augmented model is trained at 1024px with copy-paste & mosaic for maximum lattice resolution."
        )
        selected_model_key = model_options[selected_model_label]
        target_checkpoint = DEFAULT_CHECKPOINTS[selected_model_key]

        # Checkpoint Status Card
        if target_checkpoint.exists():
            st.markdown(f"""
            <div style="background:rgba(0,230,118,0.1); border:1px solid rgba(0,230,118,0.3); border-radius:12px; padding:10px; font-size:12px; color:#E2E8F0; margin-bottom:14px;">
                <b style="color:#00E676;">Checkpoint Ready:</b> <code>{target_checkpoint.name}</code><br>
                <span style="color:#94A3B8;">Resolution: {'1024×1024 px' if selected_model_key=='augmented' else '640×640 px'}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error(f"Missing weights: {target_checkpoint}")

        # 2. Dynamic Threshold Controls
        st.markdown("<h4 style='color:#38BDF8; margin-bottom:6px;'>🎚️ Sensitivity & Precision</h4>", unsafe_allow_html=True)
        conf_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.05,
            max_value=1.00,
            value=0.20,
            step=0.05,
            help="Recommended: 0.15 - 0.25 for distant or occluded lattice towers."
        )
        iou_threshold = st.slider(
            "NMS Overlap (IoU)",
            min_value=0.10,
            max_value=0.90,
            value=0.45,
            step=0.05
        )

        st.markdown("---")
        
        # 3. Target Class Legend
        st.markdown("<h4 style='color:#E2E8F0; margin-bottom:8px;'>🏷️ Tower Architecture Classes</h4>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(0,229,255,0.1); border-left:3px solid #00E5FF; padding:8px 12px; border-radius:0 8px 8px 0; margin-bottom:8px;">
            <b style="color:#00E5FF; font-size:13px;">Class 0: Supporting Tower</b>
            <div style="font-size:11.5px; color:#94A3B8;">4-Legged lattice steel transmission towers</div>
        </div>
        <div style="background:rgba(255,179,0,0.1); border-left:3px solid #FFB300; padding:8px 12px; border-radius:0 8px 8px 0;">
            <b style="color:#FFB300; font-size:13px;">Class 1: Monopole Tower</b>
            <div style="font-size:11.5px; color:#94A3B8;">Single tubular steel / cellular mast structures</div>
        </div>
        """, unsafe_allow_html=True)

    # Initialize Detector
    detector = get_detector(selected_model_key, str(target_checkpoint))
    if detector is None:
        st.error("Model engine could not be initialized.")
        return

    # Main Navigation Tabs
    main_tabs = st.tabs([
        "🎯 Interactive Single Inspection", 
        "📁 Batch Mission & Folder Processor",
        "🔬 Optical Refining Studio"
    ])

    # =========================================================================
    # TAB 1: INTERACTIVE SINGLE INSPECTION
    # =========================================================================
    with main_tabs[0]:
        c_left, c_right = st.columns([1.1, 1], gap="medium")
        
        with c_left:
            st.markdown("#### 📤 Upload Drone Photo")
            uploaded_file = st.file_uploader(
                "Upload Image (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                key="single_uploader"
            )

        with c_right:
            st.markdown("#### ⚡ Quick Demo Benchmark Library")
            sample_dict = get_available_samples()
            selected_sample_label = st.selectbox(
                "Select a benchmark drone scene:",
                options=["[ Select Benchmark Drone Scene ]"] + list(sample_dict.keys()),
                key="sample_select_single"
            )

        # Resolve Active Image
        active_img = None
        source_label = ""
        if uploaded_file is not None:
            try:
                active_img = Image.open(uploaded_file).convert("RGB")
                source_label = uploaded_file.name
            except Exception as e:
                st.error(f"Failed to open image: {e}")
        elif selected_sample_label != "[ Select Benchmark Drone Scene ]":
            sample_p = sample_dict[selected_sample_label]
            active_img = Image.open(sample_p).convert("RGB")
            source_label = sample_p.name

        if active_img is not None:
            # Run Inference
            with st.spinner("Analyzing structural components with YOLO11m..."):
                result = detector.predict(
                    image_input=active_img,
                    conf=conf_threshold,
                    iou=iou_threshold
                )

            # --- Live KPI Metric Badges ---
            st.markdown("<br>", unsafe_allow_html=True)
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>🎯</span> Total Localized</div>
                    <div class="kpi-val val-green">{result.counts.get('total', 0)}</div>
                </div>
                """, unsafe_allow_html=True)
            with k2:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>🗼</span> Supporting Lattice</div>
                    <div class="kpi-val val-cyan">{result.counts.get('supporting_tower', 0)}</div>
                </div>
                """, unsafe_allow_html=True)
            with k3:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>📡</span> Monopole Masts</div>
                    <div class="kpi-val val-amber">{result.counts.get('monopole_tower', 0)}</div>
                </div>
                """, unsafe_allow_html=True)
            with k4:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>⚡</span> Inference Speed</div>
                    <div class="kpi-val val-purple">{result.inference_time_ms:.1f} <span style="font-size:16px;">ms</span></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # --- Interactive Visual Inspection Workspace ---
            v_col1, v_col2 = st.columns([1.2, 1], gap="large")
            
            with v_col1:
                st.markdown("#### 🖼️ Visual Overlay & Optical View")
                view_mode = st.radio(
                    "Display Layer:",
                    ["🎯 AI Detection Overlay", "📷 Original High-Res", "🔬 Lattice Edge Sharpening", "👁 Rust & Corrosion Isolation", "✨ HDR Defect Boost"],
                    horizontal=True
                )
                
                if view_mode == "🎯 AI Detection Overlay":
                    st.image(result.annotated_image, use_container_width=True, caption=f"Detection Overlay // {result.counts['total']} objects localized")
                elif view_mode == "📷 Original High-Res":
                    st.image(result.original_image, use_container_width=True, caption=f"Original Aerial Scene: {source_label} ({result.image_size[0]}×{result.image_size[1]} px)")
                else:
                    filtered_img = apply_optical_filters(result.original_image, view_mode)
                    st.image(filtered_img, use_container_width=True, caption=f"Optical Filter: {view_mode}")

                # Download Buttons
                btn_c1, btn_c2 = st.columns(2)
                with btn_c1:
                    buf = io.BytesIO()
                    result.annotated_image.save(buf, format="JPEG", quality=95)
                    st.download_button(
                        label="📥 Download Annotated Image (JPEG)",
                        data=buf.getvalue(),
                        file_name=f"structivision_{source_label}.jpg",
                        mime="image/jpeg",
                        use_container_width=True
                    )
                with btn_c2:
                    json_bytes = json.dumps(result.to_dict(), indent=2).encode("utf-8")
                    st.download_button(
                        label="📄 Download Inspection JSON",
                        data=json_bytes,
                        file_name=f"structivision_{source_label}.json",
                        mime="application/json",
                        use_container_width=True
                    )

            with v_col2:
                st.markdown("#### 🔍 Interactive Component Inspector")
                
                if result.detections:
                    st.markdown(f"**Found {len(result.detections)} component instance(s):**")
                    
                    # Component crop viewer
                    det_labels = [f"#{idx} | {d.class_name.upper()} ({d.confidence*100:.1f}%)" for idx, d in enumerate(result.detections, 1)]
                    selected_crop_idx = st.selectbox("Select Component to Zoom & Inspect:", range(len(det_labels)), format_func=lambda i: det_labels[i])
                    
                    selected_det = result.detections[selected_crop_idx]
                    x1, y1, x2, y2 = [int(v) for v in selected_det.bbox_xyxy]
                    
                    # Safe crop with padding
                    pad = 15
                    w_img, h_img = result.original_image.size
                    cx1 = max(0, x1 - pad)
                    cy1 = max(0, y1 - pad)
                    cx2 = min(w_img, x2 + pad)
                    cy2 = min(h_img, y2 + pad)
                    
                    crop_img = result.original_image.crop((cx1, cy1, cx2, cy2))
                    
                    st.markdown(f"""
                    <div class="crop-card">
                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                            <span style="font-weight:800; font-size:15px; color:{'#00E5FF' if selected_det.class_id==0 else '#FFB300'};">
                                {selected_det.class_name.replace('_', ' ').upper()}
                            </span>
                            <span style="background:rgba(0,230,118,0.2); color:#00E676; padding:3px 10px; border-radius:12px; font-weight:800; font-size:13px;">
                                {selected_det.confidence*100:.2f}% Confidence
                            </span>
                        </div>
                        <div style="font-size:12px; color:#94A3B8; font-family:'JetBrains Mono', monospace;">
                            Pixel BBox: [{x1}, {y1}, {x2}, {y2}] | Span: {x2-x1}×{y2-y1} px
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.image(crop_img, use_container_width=True, caption=f"Zoomed Structural Inspection Crop: {selected_det.class_name}")

                    # Tabular details
                    table_rows = []
                    for idx, d in enumerate(result.detections, 1):
                        table_rows.append({
                            "#": idx,
                            "Class": d.class_name,
                            "Confidence": f"{d.confidence*100:.2f}%",
                            "Bounding Box": f"[{d.bbox_xyxy[0]:.0f}, {d.bbox_xyxy[1]:.0f}, {d.bbox_xyxy[2]:.0f}, {d.bbox_xyxy[3]:.0f}]",
                        })
                    st.dataframe(table_rows, use_container_width=True)
                else:
                    if conf_threshold > 0.05:
                        probe_res = detector.predict(image_input=active_img, conf=0.05, iou=iou_threshold)
                        if probe_res.detections:
                            top_cand = max(probe_res.detections, key=lambda d: d.confidence)
                            st.info(
                                f"💡 **Sensitivity Hint**: The model identified a candidate **{top_cand.class_name}** with **{top_cand.confidence*100:.1f}%** confidence. "
                                f"Lower the **Confidence Threshold** slider in the sidebar to **{top_cand.confidence:.2f}** to reveal it."
                            )
                        else:
                            st.warning("No tower components detected above minimal 5% sensitivity.")
                    else:
                        st.warning(f"No tower components detected above confidence threshold {conf_threshold:.2f}.")
        else:
            st.info("👆 Upload a drone inspection image or select a benchmark scene above to begin.")

    # =========================================================================
    # TAB 2: BATCH MISSION & FOLDER PROCESSOR
    # =========================================================================
    with main_tabs[1]:
        st.markdown("### 📁 Batch Drone Mission Processing")
        st.markdown("<p style='color:#94A3B8; margin-top:-8px;'>Process an entire drone inspection flight folder or multi-file image set all at once.</p>", unsafe_allow_html=True)

        batch_input_mode = st.radio(
            "Select Folder Ingestion Source:",
            ["📤 Multi-File Drag & Drop (Select Entire Folder Files)", "📦 Upload Folder as ZIP Archive", "📂 Local Server Directory Path"],
            horizontal=True
        )

        batch_queue = []

        if batch_input_mode == "📤 Multi-File Drag & Drop (Select Entire Folder Files)":
            batch_files = st.file_uploader(
                "Drag and Drop or Select All Images from your Drone Folder (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="batch_multi_uploader"
            )
            if batch_files:
                for bf in batch_files:
                    try:
                        im = Image.open(bf).convert("RGB")
                        batch_queue.append((bf.name, im))
                    except Exception as e:
                        st.warning(f"Skipping {bf.name}: {e}")

        elif batch_input_mode == "📦 Upload Folder as ZIP Archive":
            zip_file = st.file_uploader(
                "Upload a .ZIP Archive Containing Drone Images",
                type=["zip"],
                key="batch_zip_uploader_tab2"
            )
            if zip_file:
                try:
                    with zipfile.ZipFile(zip_file, "r") as z:
                        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
                        for entry in z.infolist():
                            if not entry.is_dir() and Path(entry.filename).suffix.lower() in valid_exts:
                                with z.open(entry) as f:
                                    im = Image.open(io.BytesIO(f.read())).convert("RGB")
                                    batch_queue.append((Path(entry.filename).name, im))
                    st.success(f"Extracted {len(batch_queue)} image(s) from ZIP archive.")
                except Exception as e:
                    st.error(f"Error reading ZIP: {e}")

        elif batch_input_mode == "📂 Local Server Directory Path":
            f_path_str = st.text_input(
                "Folder Path on Disk:",
                value="A:\\Electrohack\\data\\processed\\yolo\\test\\images"
            )
            if f_path_str and Path(f_path_str).is_dir():
                fp = Path(f_path_str)
                valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG"}
                local_files = [p for p in fp.iterdir() if p.is_file() and p.suffix in valid_exts]
                st.info(f"Found **{len(local_files)}** drone image(s) in `{fp}`")
                if st.button("Load Folder Images into Batch Queue"):
                    for p in local_files:
                        try:
                            im = Image.open(p).convert("RGB")
                            batch_queue.append((p.name, im))
                        except Exception as e:
                            st.warning(f"Skipping {p.name}: {e}")
                    st.session_state["loaded_folder_queue"] = batch_queue

            if "loaded_folder_queue" in st.session_state and not batch_queue:
                batch_queue = st.session_state["loaded_folder_queue"]

        # Run Batch Inference
        if batch_queue:
            st.markdown(f"**Ready to process `{len(batch_queue)}` image(s) with `{selected_model_label}`**")
            
            if st.button("🚀 Process Complete Folder All-At-Once", type="primary"):
                prog_bar = st.progress(0.0)
                status_box = st.empty()
                
                batch_results: List[Tuple[str, DetectionResult]] = []
                total_b = len(batch_queue)
                start_b_time = time.perf_counter()
                
                for idx, (fname, pil_im) in enumerate(batch_queue):
                    status_box.markdown(f"⏳ Processing `{idx + 1}/{total_b}`: **{fname}**...")
                    res = detector.predict(
                        image_input=pil_im,
                        conf=conf_threshold,
                        iou=iou_threshold
                    )
                    batch_results.append((fname, res))
                    prog_bar.progress((idx + 1) / total_b)
                
                elapsed_s = time.perf_counter() - start_b_time
                status_box.success(f"✅ Processed {total_b} images in {elapsed_s:.2f} seconds ({elapsed_s*1000/max(1,total_b):.1f} ms/image)!")
                st.session_state["batch_results_store"] = batch_results

        # Batch Results Dashboard
        if "batch_results_store" in st.session_state and st.session_state["batch_results_store"]:
            b_results = st.session_state["batch_results_store"]
            
            # Aggregate KPI Metrics
            tot_b_img = len(b_results)
            tot_b_det = sum(r.counts.get("total", 0) for _, r in b_results)
            tot_b_sup = sum(r.counts.get("supporting_tower", 0) for _, r in b_results)
            tot_b_mono = sum(r.counts.get("monopole_tower", 0) for _, r in b_results)
            avg_b_speed = sum(r.inference_time_ms for _, r in b_results) / max(1, tot_b_img)

            st.markdown("---")
            st.markdown("### 📊 Batch Mission Analytics")
            bm1, bm2, bm3, bm4 = st.columns(4)
            with bm1:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>📁</span> Images Processed</div>
                    <div class="kpi-val val-green">{tot_b_img}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm2:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>🎯</span> Total Detections</div>
                    <div class="kpi-val val-cyan">{tot_b_det}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm3:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>🗼</span> Supporting / Monopole</div>
                    <div class="kpi-val val-amber">{tot_b_sup} / {tot_b_mono}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm4:
                st.markdown(f"""
                <div class="glass-card">
                    <div class="kpi-title"><span>⚡</span> Avg. Speed / Image</div>
                    <div class="kpi-val val-purple">{avg_b_speed:.1f} <span style="font-size:16px;">ms</span></div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Tabular Summary & Interactive Explorer
            b_subtab1, b_subtab2, b_subtab3 = st.tabs(["📋 Mission Data Table", "🖼️ Interactive Image Browser", "📥 1-Click Export Suite"])

            summary_rows = []
            for idx, (name, r) in enumerate(b_results, 1):
                top_c = f"{max([d.confidence for d in r.detections])*100:.1f}%" if r.detections else "N/A"
                c_names = list(set([d.class_name for d in r.detections]))
                summary_rows.append({
                    "#": idx,
                    "Image Name": name,
                    "Total Objects": r.counts.get("total", 0),
                    "Supporting Towers": r.counts.get("supporting_tower", 0),
                    "Monopole Towers": r.counts.get("monopole_tower", 0),
                    "Top Confidence": top_c,
                    "Identified Types": ", ".join(c_names) if c_names else "None",
                    "Latency (ms)": round(r.inference_time_ms, 1)
                })

            with b_subtab1:
                st.dataframe(summary_rows, use_container_width=True)

            with b_subtab2:
                names_list = [n for n, _ in b_results]
                selected_name = st.selectbox("Choose Image to Inspect:", options=names_list)
                matched_r = next(r for n, r in b_results if n == selected_name)
                
                bi_col1, bi_col2 = st.columns(2)
                with bi_col1:
                    st.image(matched_r.original_image, use_container_width=True, caption=f"Original: {selected_name}")
                with bi_col2:
                    st.image(matched_r.annotated_image, use_container_width=True, caption=f"Detection Overlay: {matched_r.counts['total']} objects localized")

            with b_subtab3:
                st.markdown("#### Export Mission Results")
                exp1, exp2 = st.columns(2)
                with exp1:
                    csv_b = pd.DataFrame(summary_rows).to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📄 Download Mission Summary (CSV)",
                        data=csv_b,
                        file_name="structivision_batch_summary.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                with exp2:
                    with st.spinner("Compiling Batch ZIP Package..."):
                        zip_pkg = create_batch_zip(b_results)
                    st.download_button(
                        label="📦 Download All Annotated Images & JSON (ZIP)",
                        data=zip_pkg,
                        file_name="structivision_annotated_mission.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

    # =========================================================================
    # TAB 3: OPTICAL REFINING STUDIO
    # =========================================================================
    with main_tabs[2]:
        st.markdown("### 🔬 Neural Optical Calibration & Image Refining Studio")
        st.markdown("<p style='color:#94A3B8; margin-top:-8px;'>Fine-tune exposure, edge contrast, and rust saturation to assist inspection in severe weather conditions.</p>", unsafe_allow_html=True)

        ref_samples = get_available_samples()
        ref_sample_label = st.selectbox(
            "Select Drone Scene to Calibrate:",
            options=list(ref_samples.keys()),
            key="ref_studio_sample"
        )
        base_ref_img = Image.open(ref_samples[ref_sample_label]).convert("RGB")

        r_c1, r_c2 = st.columns([1.1, 1], gap="large")
        with r_c2:
            st.markdown("#### Neural Enhancement Sliders")
            contrast_boost = st.slider("Contrast Boost", 100, 250, 140, 5, format="%d%%")
            brightness_boost = st.slider("Exposure & Brightness", 50, 180, 110, 5, format="%d%%")
            sharpness_boost = st.slider("Lattice Edge Sharpness", 100, 350, 180, 10, format="%d%%")
            color_boost = st.slider("Rust & Steel Saturation", 50, 250, 140, 5, format="%d%%")
            
            # Apply enhancements
            enhanced = base_ref_img.copy()
            enhanced = ImageEnhance.Contrast(enhanced).enhance(contrast_boost / 100.0)
            enhanced = ImageEnhance.Brightness(enhanced).enhance(brightness_boost / 100.0)
            enhanced = ImageEnhance.Sharpness(enhanced).enhance(sharpness_boost / 100.0)
            enhanced = ImageEnhance.Color(enhanced).enhance(color_boost / 100.0)

            # Test inference directly on enhanced image
            if st.button("⚡ Test YOLO Detection on Refined Image", type="primary", use_container_width=True):
                enh_result = detector.predict(enhanced, conf=conf_threshold, iou=iou_threshold)
                st.session_state["refined_test_result"] = enh_result

        with r_c1:
            st.markdown("#### Live Optical Enhancement Buffer")
            st.image(enhanced, use_container_width=True, caption=f"Refined Optical Buffer (Contrast: {contrast_boost}%, Sharpness: {sharpness_boost}%)")

            if "refined_test_result" in st.session_state:
                enh_res = st.session_state["refined_test_result"]
                st.markdown("#### Detection Result on Refined Buffer")
                st.image(enh_res.annotated_image, use_container_width=True, caption=f"Refined Detection: {enh_res.counts['total']} objects localized")


if __name__ == "__main__":
    main()
