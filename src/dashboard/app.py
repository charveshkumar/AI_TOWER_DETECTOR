"""
Phase 6 — Streamlit Interactive Web Dashboard for Tower Component Detection.
Provides real-time single image & batch folder inference, checkpoint comparison,
detection visualization, and batch report export.
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
from PIL import Image
import streamlit as st

# Import inference engine
from src.pipeline.inference import TowerDetector, DEFAULT_CHECKPOINTS, CLASS_NAMES, DetectionResult

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


def create_batch_zip(batch_results: List[Tuple[str, DetectionResult]]) -> bytes:
    """Packages all annotated images and JSON telemetry into a downloadable ZIP archive."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        summary_records = []
        for name, res in batch_results:
            # Save annotated image
            img_buf = io.BytesIO()
            res.annotated_image.save(img_buf, format="JPEG", quality=95)
            clean_name = Path(name).stem
            zf.writestr(f"annotated_images/{clean_name}_detected.jpg", img_buf.getvalue())
            
            # Save individual JSON report
            json_str = json.dumps(res.to_dict(), indent=2)
            zf.writestr(f"telemetry_json/{clean_name}_report.json", json_str)
            
            # Aggregate for batch summary
            summary_records.append({
                "image_name": name,
                "total_detections": res.counts.get("total", 0),
                "supporting_towers": res.counts.get("supporting_tower", 0),
                "monopole_towers": res.counts.get("monopole_tower", 0),
                "latency_ms": round(res.inference_time_ms, 1),
                "image_width": res.image_size[0],
                "image_height": res.image_size[1],
            })
        
        # Save batch summary CSV inside ZIP
        df_summary = pd.DataFrame(summary_records)
        csv_buf = df_summary.to_csv(index=False)
        zf.writestr("batch_inspection_summary.csv", csv_buf)
        
    return buf.getvalue()


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

    # Initialize Detector
    detector = get_detector(selected_model_key, str(target_checkpoint))
    if detector is None:
        st.error("Model engine could not be initialized.")
        return

    # Mode Selector Tabs
    mode_tab1, mode_tab2 = st.tabs(["📸 Single Image Inspection", "📁 Batch Folder Inspection"])

    # =========================================================================
    # TAB 1: SINGLE IMAGE INSPECTION
    # =========================================================================
    with mode_tab1:
        col_input, col_info = st.columns([2, 1])
        
        with col_input:
            uploaded_file = st.file_uploader(
                "Upload Drone Aerial Image (JPG, JPEG, PNG)",
                type=["jpg", "jpeg", "png"],
                key="single_file_uploader",
                help="Upload an aerial photo of power transmission infrastructure."
            )

        with col_info:
            sample_dict = get_available_samples()
            sample_choice = None
            if sample_dict:
                st.markdown("**Or test with benchmark drone scenes:**")
                selected_sample_label = st.selectbox(
                    "Benchmark Demo Samples:",
                    options=["[ None / Upload Custom ]"] + list(sample_dict.keys()),
                    index=0,
                    key="single_sample_select"
                )
                if selected_sample_label != "[ None / Upload Custom ]":
                    sample_choice = sample_dict[selected_sample_label]

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

        if image_input is not None:
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

                    buf = io.BytesIO()
                    result.annotated_image.save(buf, format="JPEG", quality=95)
                    st.download_button(
                        label="📥 Download Annotated Image (JPEG)",
                        data=buf.getvalue(),
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
                    if conf_threshold > 0.05:
                        probe_res = detector.predict(image_input=image_input, conf=0.05, iou=iou_threshold)
                        if probe_res.detections:
                            top_cand = max(probe_res.detections, key=lambda d: d.confidence)
                            st.info(
                                f"💡 **Sensitivity Hint**: The model detected a candidate **{top_cand.class_name}** with **{top_cand.confidence*100:.1f}%** confidence. "
                                f"Lower the **Confidence Threshold** slider in the sidebar to **{top_cand.confidence:.2f}** or below to reveal it."
                            )
                        else:
                            st.warning("No tower components detected in this image (even at minimal 5% sensitivity).")
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
        else:
            st.info("👆 Upload an image or select a benchmark demo sample to run single detection.")

    # =========================================================================
    # TAB 2: BATCH FOLDER & MULTI-IMAGE INSPECTION
    # =========================================================================
    with mode_tab2:
        st.markdown("### 📁 Batch Drone Mission Processing")
        st.markdown("<p style='color:#8b949e; margin-top:-8px;'>Upload multiple aerial images, an image archive, or provide a local folder path to process all images at once.</p>", unsafe_allow_html=True)
        
        batch_source_type = st.radio(
            "Batch Input Source:",
            ["📤 Upload Multiple Files / Folder Selection", "📦 Upload ZIP Archive", "📂 Local Server Folder Path"],
            horizontal=True
        )

        batch_images_to_process = []  # List of tuples: (filename_or_label, PIL.Image)

        if batch_source_type == "📤 Upload Multiple Files / Folder Selection":
            uploaded_batch_files = st.file_uploader(
                "Select or Drag & Drop Multiple Images from your Folder (JPG, PNG, WEBP)",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                key="batch_file_uploader"
            )
            if uploaded_batch_files:
                for uf in uploaded_batch_files:
                    try:
                        im = Image.open(uf).convert("RGB")
                        batch_images_to_process.append((uf.name, im))
                    except Exception as e:
                        st.warning(f"Skipping unreadable file '{uf.name}': {e}")

        elif batch_source_type == "📦 Upload ZIP Archive":
            uploaded_zip = st.file_uploader(
                "Upload a ZIP archive containing drone mission images",
                type=["zip"],
                key="batch_zip_uploader"
            )
            if uploaded_zip:
                try:
                    with zipfile.ZipFile(uploaded_zip, "r") as z:
                        valid_exts = {".jpg", ".jpeg", ".png", ".webp"}
                        for entry in z.infolist():
                            if not entry.is_dir() and Path(entry.filename).suffix.lower() in valid_exts:
                                with z.open(entry) as f:
                                    im = Image.open(io.BytesIO(f.read())).convert("RGB")
                                    batch_images_to_process.append((Path(entry.filename).name, im))
                    st.success(f"Extracted {len(batch_images_to_process)} image(s) from ZIP.")
                except Exception as e:
                    st.error(f"Failed to read ZIP file: {e}")

        elif batch_source_type == "📂 Local Server Folder Path":
            folder_path_str = st.text_input(
                "Enter Local Folder Path on Disk:",
                value="A:\\Electrohack\\data\\processed\\yolo\\test\\images",
                help="Path to folder containing drone aerial images."
            )
            if folder_path_str and Path(folder_path_str).is_dir():
                folder_p = Path(folder_path_str)
                valid_exts = {".jpg", ".jpeg", ".png", ".webp", ".JPG", ".JPEG", ".PNG"}
                local_imgs = [p for p in folder_p.iterdir() if p.is_file() and p.suffix in valid_exts]
                st.info(f"Found **{len(local_imgs)}** image(s) in folder `{folder_p}`")
                if st.button("Load Folder Images for Inspection"):
                    for lp in local_imgs:
                        try:
                            im = Image.open(lp).convert("RGB")
                            batch_images_to_process.append((lp.name, im))
                        except Exception as e:
                            st.warning(f"Skipping '{lp.name}': {e}")
                    st.session_state["loaded_folder_images"] = batch_images_to_process

            if "loaded_folder_images" in st.session_state and not batch_images_to_process:
                batch_images_to_process = st.session_state["loaded_folder_images"]

        # Run Batch Inspection
        if batch_images_to_process:
            st.markdown(f"**Ready to process `{len(batch_images_to_process)}` image(s) with `{selected_model_label}`**")
            
            if st.button("🚀 Run Batch Detection All-At-Once", type="primary"):
                progress_bar = st.progress(0.0)
                status_text = st.empty()
                
                batch_results: List[Tuple[str, DetectionResult]] = []
                total_imgs = len(batch_images_to_process)
                start_batch_time = time.perf_counter()
                
                for idx, (img_name, pil_img) in enumerate(batch_images_to_process):
                    status_text.markdown(f"⏳ Processing `{idx + 1}/{total_imgs}`: **{img_name}**...")
                    res = detector.predict(
                        image_input=pil_img,
                        conf=conf_threshold,
                        iou=iou_threshold
                    )
                    batch_results.append((img_name, res))
                    progress_bar.progress((idx + 1) / total_imgs)
                
                total_batch_time_s = time.perf_counter() - start_batch_time
                status_text.success(f"✅ Completed batch inspection of {total_imgs} images in {total_batch_time_s:.2f} seconds!")
                
                # Save into session state for persistent browsing
                st.session_state["last_batch_results"] = batch_results

        # Display Batch Results
        if "last_batch_results" in st.session_state and st.session_state["last_batch_results"]:
            batch_res = st.session_state["last_batch_results"]
            
            # Aggregate Stats
            total_b_images = len(batch_res)
            total_b_detections = sum(r.counts.get("total", 0) for _, r in batch_res)
            total_b_supporting = sum(r.counts.get("supporting_tower", 0) for _, r in batch_res)
            total_b_monopole = sum(r.counts.get("monopole_tower", 0) for _, r in batch_res)
            avg_b_latency = sum(r.inference_time_ms for _, r in batch_res) / max(1, total_b_images)
            
            st.markdown("---")
            st.markdown("### 📊 Batch Inspection Analytics")
            bm1, bm2, bm3, bm4 = st.columns(4)
            with bm1:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Images Processed</div>
                    <div class="metric-val metric-val-green">{total_b_images}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm2:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Supporting Towers</div>
                    <div class="metric-val metric-val-cyan">{total_b_supporting}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm3:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Monopole Towers</div>
                    <div class="metric-val metric-val-amber">{total_b_monopole}</div>
                </div>
                """, unsafe_allow_html=True)
            with bm4:
                st.markdown(f"""
                <div class="metric-card">
                    <div style="color:#8b949e; font-size:13px; text-transform:uppercase;">Avg. Latency / Image</div>
                    <div class="metric-val metric-val-purple">{avg_b_latency:.1f} ms</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Batch Summary Table & Detailed Rows
            summary_table_rows = []
            detailed_detections_rows = []
            
            for idx, (img_name, r) in enumerate(batch_res, 1):
                top_conf_str = f"{max([d.confidence for d in r.detections])*100:.1f}%" if r.detections else "N/A"
                detected_classes = list(set([d.class_name for d in r.detections]))
                summary_table_rows.append({
                    "#": idx,
                    "Image Name": img_name,
                    "Total Detections": r.counts.get("total", 0),
                    "Supporting": r.counts.get("supporting_tower", 0),
                    "Monopole": r.counts.get("monopole_tower", 0),
                    "Top Confidence": top_conf_str,
                    "Identified Classes": ", ".join(detected_classes) if detected_classes else "None",
                    "Latency (ms)": round(r.inference_time_ms, 1)
                })
                
                for det in r.detections:
                    detailed_detections_rows.append({
                        "Image": img_name,
                        "Class": det.class_name,
                        "Confidence": f"{det.confidence*100:.2f}%",
                        "BBox [X1, Y1, X2, Y2]": f"[{det.bbox_xyxy[0]:.0f}, {det.bbox_xyxy[1]:.0f}, {det.bbox_xyxy[2]:.0f}, {det.bbox_xyxy[3]:.0f}]",
                        "Normalized [XC, YC, W, H]": f"[{det.bbox_normalized[0]:.3f}, {det.bbox_normalized[1]:.3f}, {det.bbox_normalized[2]:.3f}, {det.bbox_normalized[3]:.3f}]"
                    })

            # Sub-tabs for Batch Viewing
            b_view_tab1, b_view_tab2, b_view_tab3 = st.tabs(["📋 Batch Results Table", "🖼️ Interactive Image Inspector", "💾 Export All Data"])

            with b_view_tab1:
                st.markdown("#### Summary of Processed Images")
                st.dataframe(summary_table_rows, use_container_width=True)

            with b_view_tab2:
                st.markdown("#### Inspect Annotated Results")
                img_names = [name for name, _ in batch_res]
                selected_inspect_name = st.selectbox("Select image to inspect:", options=img_names)
                
                # Find matching result
                matched_res = next(r for name, r in batch_res if name == selected_inspect_name)
                
                ins_c1, ins_c2 = st.columns(2)
                with ins_c1:
                    st.markdown(f"**Original Image**: `{selected_inspect_name}`")
                    st.image(matched_res.original_image, use_container_width=True)
                with ins_c2:
                    st.markdown(f"**Annotated Detection Overlay** ({matched_res.counts['total']} objects)")
                    st.image(matched_res.annotated_image, use_container_width=True)
                    
                    if matched_res.detections:
                        det_info = [{"Class": d.class_name, "Confidence": f"{d.confidence*100:.1f}%", "Box": [round(x, 1) for x in d.bbox_xyxy]} for d in matched_res.detections]
                        st.dataframe(det_info, use_container_width=True)

            with b_view_tab3:
                st.markdown("#### 📥 One-Click Batch Export Options")
                exp_c1, exp_c2 = st.columns(2)
                
                with exp_c1:
                    df_sum = pd.DataFrame(summary_table_rows)
                    csv_data = df_sum.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        label="📄 Download Batch Summary (CSV)",
                        data=csv_data,
                        file_name="batch_tower_detections_summary.csv",
                        mime="text/csv",
                        use_container_width=True
                    )

                with exp_c2:
                    with st.spinner("Generating Batch ZIP Package..."):
                        zip_bytes = create_batch_zip(batch_res)
                    st.download_button(
                        label="📦 Download All Annotated Images & JSON (ZIP)",
                        data=zip_bytes,
                        file_name="batch_annotated_inspections.zip",
                        mime="application/zip",
                        use_container_width=True
                    )


if __name__ == "__main__":
    main()
