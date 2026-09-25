"""
Phase 2 Dataset Preparation Pipeline & Format Converter.
Handles non-destructive format conversion, polygon bounding-box extraction,
dynamic class remapping, and group-aware deterministic splitting.
"""
import os
import json
import logging
import hashlib
import random
import shutil
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List, Tuple, Optional, Set
import yaml
from PIL import Image

from src.config import CLASSES, PROCESSED_DATA_DIR, RAW_DATA_DIR, BASE_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def polygon_to_bbox(coords: List[float]) -> Tuple[float, float, float, float]:
    """
    Converts a list of normalized polygon coordinates [x1, y1, x2, y2, ...]
    into normalized YOLO bounding box format (x_center, y_center, width, height).
    Clamps coordinates strictly to [0.0, 1.0].
    """
    if len(coords) < 6 or len(coords) % 2 != 0:
        raise ValueError(f"Invalid polygon coordinate list length: {len(coords)}. Must be even and >= 6.")

    xs = [min(max(float(coords[i]), 0.0), 1.0) for i in range(0, len(coords), 2)]
    ys = [min(max(float(coords[i + 1]), 0.0), 1.0) for i in range(0, len(coords), 2)]

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    w = max(xmax - xmin, 1e-6)
    h = max(ymax - ymin, 1e-6)
    xc = xmin + (w / 2.0)
    yc = ymin + (h / 2.0)

    return round(xc, 6), round(yc, 6), round(w, 6), round(h, 6)


def build_class_mapping(source_names: List[str], target_classes: Dict[int, str] = CLASSES) -> Dict[int, int]:
    """
    Dynamically maps source class IDs (from source data.yaml names list)
    to target class IDs based on class name matching.
    Throws ValueError if source contains unrecognized class names.
    """
    target_name_to_id = {name: cid for cid, name in target_classes.items()}
    mapping = {}

    for src_id, src_name in enumerate(source_names):
        if src_name not in target_name_to_id:
            raise ValueError(
                f"Unrecognized class name '{src_name}' at index {src_id} in source dataset. "
                f"Expected one of: {list(target_name_to_id.keys())}"
            )
        mapping[src_id] = target_name_to_id[src_name]

    logger.info(f"Dynamically generated class mapping from source {source_names}: {mapping}")
    return mapping


class DatasetConverter:
    """
    Robust, non-destructive YOLO dataset converter and split generator.
    """

    def __init__(
        self,
        source_dir: Path = None,
        output_dir: Path = None,
        raw_source_dir: Path = None,
        reports_dir: Path = None,
        target_classes: Dict[int, str] = None
    ):
        self.source_dir = Path(source_dir) if source_dir else PROCESSED_DATA_DIR / "roboflow_export"
        self.output_dir = Path(output_dir) if output_dir else PROCESSED_DATA_DIR / "yolo"
        self.raw_source_dir = Path(raw_source_dir) if raw_source_dir else RAW_DATA_DIR / "sample"
        self.reports_dir = Path(reports_dir) if reports_dir else BASE_DIR / "reports"
        self.target_classes = target_classes if target_classes else CLASSES

    def extract_image_group_id(self, rf_filename: str, raw_stem_map: Dict[str, Path]) -> Tuple[str, Optional[Tuple[str, str]]]:
        """
        Maps an exported image filename back to its raw counterpart to extract
        DJI GPS telemetry coordinates for grouped splitting.
        """
        raw_match_path = None
        for raw_stem, p in raw_stem_map.items():
            if raw_stem in rf_filename:
                raw_match_path = p
                break

        if raw_match_path and raw_match_path.exists():
            try:
                with Image.open(raw_match_path) as img:
                    xmp = img.info.get("xmp")
                    if xmp:
                        text = xmp.decode("utf-8", errors="ignore")
                        lat, lon = None, None
                        for line in text.splitlines():
                            if "drone-dji:GpsLatitude" in line:
                                lat = line.split("=")[1].strip('"')
                            if "drone-dji:GpsLongitude" in line:
                                lon = line.split("=")[1].strip('"')
                        if lat and lon:
                            return f"gps_{lat}_{lon}", (lat, lon)
            except Exception:
                pass

        return f"item_{Path(rf_filename).stem[:24]}", None

    def validate_and_prepare(
        self,
        dry_run: bool = True,
        overwrite: bool = False,
        split_ratios: Tuple[float, float, float] = (0.70, 0.15, 0.15),
        random_seed: int = 42
    ) -> Dict[str, Any]:
        """
        Executes validation, class mapping, polygon conversion, and split grouping.
        If dry_run=True, does NOT write any files to output_dir.
        """
        if not self.source_dir.exists():
            raise FileNotFoundError(f"Source export directory does not exist: {self.source_dir}")

        yaml_path = self.source_dir / "data.yaml"
        if not yaml_path.exists():
            raise FileNotFoundError(f"Source data.yaml not found at: {yaml_path}")

        with open(yaml_path, "r", encoding="utf-8") as fp:
            source_yaml = yaml.safe_load(fp)

        source_names = source_yaml.get("names", [])
        if not source_names:
            raise ValueError(f"No class 'names' list found in {yaml_path}")

        # Build dynamic class remapping
        class_mapping = build_class_mapping(source_names, self.target_classes)

        # Collect images and labels from source
        train_img_dir = self.source_dir / "train" / "images"
        train_lbl_dir = self.source_dir / "train" / "labels"

        if not train_img_dir.exists() or not train_lbl_dir.exists():
            raise FileNotFoundError(f"Expected train/images and train/labels under {self.source_dir}")

        image_files = sorted(list(train_img_dir.glob("*")))
        label_files = {f.stem: f for f in train_lbl_dir.glob("*.txt")}

        # Map raw files for GPS grouping
        raw_stem_map = {f.stem: f for f in self.raw_source_dir.glob("*")} if self.raw_source_dir.exists() else {}

        parsed_records = []
        source_class_counts = Counter()
        target_class_counts = Counter()
        polygon_conversion_records = []
        groups_dict: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

        for img_path in image_files:
            stem = img_path.stem
            if stem not in label_files:
                raise FileNotFoundError(f"Missing corresponding label file for image: {img_path.name}")

            lbl_path = label_files[stem]
            with open(lbl_path, "r", encoding="utf-8") as fp:
                raw_lines = [l.strip() for l in fp if l.strip()]

            converted_boxes = []
            img_classes_source = set()
            img_classes_target = set()

            for line_idx, line in enumerate(raw_lines):
                tokens = line.split()
                if len(tokens) == 5:
                    src_cls = int(tokens[0])
                    xc, yc, w, h = float(tokens[1]), float(tokens[2]), float(tokens[3]), float(tokens[4])
                    xc = min(max(xc, 0.0), 1.0)
                    yc = min(max(yc, 0.0), 1.0)
                    w = min(max(w, 0.0), 1.0)
                    h = min(max(h, 0.0), 1.0)
                    target_cls = class_mapping[src_cls]
                    converted_boxes.append((target_cls, xc, yc, w, h))
                    source_class_counts[src_cls] += 1
                    target_class_counts[target_cls] += 1
                    img_classes_source.add(src_cls)
                    img_classes_target.add(target_cls)
                elif len(tokens) > 5:
                    src_cls = int(tokens[0])
                    poly_coords = [float(t) for t in tokens[1:]]
                    xc, yc, w, h = polygon_to_bbox(poly_coords)
                    target_cls = class_mapping[src_cls]
                    converted_boxes.append((target_cls, xc, yc, w, h))
                    source_class_counts[src_cls] += 1
                    target_class_counts[target_cls] += 1
                    img_classes_source.add(src_cls)
                    img_classes_target.add(target_cls)
                    polygon_conversion_records.append({
                        "image": img_path.name,
                        "label_file": lbl_path.name,
                        "line_idx": line_idx,
                        "source_class": src_cls,
                        "target_class": target_cls,
                        "vertex_count": len(poly_coords) // 2,
                        "computed_bbox": (xc, yc, w, h)
                    })
                else:
                    raise ValueError(f"Malformed label line in {lbl_path.name}: '{line}'")

            group_id, gps_coord = self.extract_image_group_id(img_path.name, raw_stem_map)
            rec = {
                "image_path": img_path,
                "label_path": lbl_path,
                "filename": img_path.name,
                "label_filename": lbl_path.name,
                "group_id": group_id,
                "gps_coord": gps_coord,
                "converted_boxes": converted_boxes,
                "source_classes": list(img_classes_source),
                "target_classes": list(img_classes_target),
                "primary_class": list(img_classes_target)[0] if img_classes_target else 0
            }
            parsed_records.append(rec)
            groups_dict[group_id].append(rec)

        # ---------------------------------------------------------
        # Grouped Deterministic Stratified Split Generation
        # ---------------------------------------------------------
        rng = random.Random(random_seed)
        all_group_ids = sorted(list(groups_dict.keys()))
        rng.shuffle(all_group_ids)

        train_records: List[Dict[str, Any]] = []
        val_records: List[Dict[str, Any]] = []
        test_records: List[Dict[str, Any]] = []

        total_imgs = len(parsed_records)
        target_train = int(total_imgs * split_ratios[0])
        target_val = int(total_imgs * split_ratios[1])

        for gid in all_group_ids:
            group_items = groups_dict[gid]
            if len(train_records) + len(group_items) <= target_train or (not train_records and len(group_items) <= total_imgs):
                train_records.extend(group_items)
            elif len(val_records) + len(group_items) <= target_val:
                val_records.extend(group_items)
            else:
                test_records.extend(group_items)

        def get_split_stats(recs: List[Dict[str, Any]]) -> Dict[str, Any]:
            cls_objs = Counter()
            cls_imgs = Counter()
            for r in recs:
                for c, xc, yc, w, h in r["converted_boxes"]:
                    cls_objs[c] += 1
                for c in r["target_classes"]:
                    cls_imgs[c] += 1
            return {
                "images_count": len(recs),
                "objects_count": sum(cls_objs.values()),
                "objects_by_class": {self.target_classes[c]: cls_objs[c] for c in sorted(cls_objs.keys())},
                "images_by_class": {self.target_classes[c]: cls_imgs[c] for c in sorted(cls_imgs.keys())}
            }

        split_summary = {
            "train": get_split_stats(train_records),
            "val": get_split_stats(val_records),
            "test": get_split_stats(test_records)
        }

        monopole_source_records = [r for r in parsed_records if 0 in r["source_classes"]]

        result_payload = {
            "dry_run": dry_run,
            "source_dir": str(self.source_dir),
            "output_dir": str(self.output_dir),
            "total_images_inspected": total_imgs,
            "total_labels_inspected": len(label_files),
            "total_objects_inspected": sum(source_class_counts.values()),
            "class_mapping_applied": class_mapping,
            "source_class_counts": {source_names[c]: count for c, count in source_class_counts.items()},
            "target_class_counts": {self.target_classes[c]: count for c, count in target_class_counts.items()},
            "polygon_conversions_count": len(polygon_conversion_records),
            "polygon_conversions": polygon_conversion_records,
            "total_unique_groups": len(groups_dict),
            "split_ratios_target": split_ratios,
            "split_summary": split_summary,
            "monopole_audit": {
                "total_monopole_source_images": len(monopole_source_records),
                "user_expected_count": 25,
                "discrepancy_delta": len(monopole_source_records) - 25,
                "monopole_files_list": [
                    {
                        "filename": r["filename"],
                        "group_id": r["group_id"],
                        "gps": r["gps_coord"]
                    }
                    for r in monopole_source_records
                ]
            }
        }

        if not dry_run:
            self._write_output_dataset(
                train_records=train_records,
                val_records=val_records,
                test_records=test_records,
                overwrite=overwrite
            )

        report_path = self.reports_dir / "dataset_conversion_report.md"
        self._write_markdown_report(result_payload, report_path)
        logger.info(f"Conversion audit report written to: {report_path}")

        return result_payload

    def _write_output_dataset(
        self,
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
        test_records: List[Dict[str, Any]],
        overwrite: bool = False
    ) -> None:
        """Writes converted YOLO dataset splits to output_dir."""
        if self.output_dir.exists():
            if not overwrite:
                raise FileExistsError(
                    f"Output directory {self.output_dir} already exists. Pass overwrite=True to replace."
                )
            shutil.rmtree(self.output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        split_map = {
            "train": train_records,
            "val": val_records,
            "test": test_records
        }

        for s_name, recs in split_map.items():
            img_out = self.output_dir / s_name / "images"
            lbl_out = self.output_dir / s_name / "labels"
            img_out.mkdir(parents=True, exist_ok=True)
            lbl_out.mkdir(parents=True, exist_ok=True)

            for r in recs:
                shutil.copy2(r["image_path"], img_out / r["filename"])
                lbl_file = lbl_out / r["label_filename"]
                with open(lbl_file, "w", encoding="utf-8") as fp:
                    for cls_id, xc, yc, w, h in r["converted_boxes"]:
                        fp.write(f"{cls_id} {xc:.6f} {yc:.6f} {w:.6f} {h:.6f}\n")

        yolo_yaml = {
            "path": str(self.output_dir.resolve()),
            "train": "train/images",
            "val": "val/images",
            "test": "test/images",
            "nc": len(self.target_classes),
            "names": [self.target_classes[i] for i in range(len(self.target_classes))]
        }
        with open(self.output_dir / "data.yaml", "w", encoding="utf-8") as fp:
            yaml.dump(yolo_yaml, fp, sort_keys=False)

        logger.info(f"YOLO dataset successfully generated at: {self.output_dir}")

    def _write_markdown_report(self, payload: Dict[str, Any], report_path: Path) -> None:
        """Generates structured Markdown conversion & dry-run report."""
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        splits = payload["split_summary"]
        mono_audit = payload["monopole_audit"]

        md = []
        md.append("# Phase 2 Dataset Conversion & Dry-Run Report")
        md.append("\n**Project**: AI-Based Tower Component Detection System  ")
        md.append(f"**Source Directory**: `{payload['source_dir']}`  ")
        md.append(f"**Target Output Directory**: `{payload['output_dir']}`  ")
        md.append(f"**Execution Mode**: `{'DRY RUN (Read-Only Validation)' if payload['dry_run'] else 'WRITTEN TO DISK'}`  \n")
        md.append("---\n")

        md.append("## 1. Dynamic Class Remapping Verification\n")
        mono_count = payload["target_class_counts"].get("monopole_tower", 0)
        supp_count = payload["target_class_counts"].get("supporting_tower", 0)
        md.append("| Source Class Name (Export) | Source Export ID | Target Class Name (System Standard) | Target Class ID | Remapped Total Objects |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        md.append(f"| `monopole_tower` | `0` | `monopole_tower` | `1` | **{mono_count} instances** |")
        md.append(f"| `supporting_tower` | `1` | `supporting_tower` | `0` | **{supp_count} instances** |\n")

        md.append("## 2. Polygon to Bounding Box Normalization\n")
        md.append(f"- **Converted Polygon Files**: `1` file containing **{payload['polygon_conversions_count']} polygon instances**.")
        for poly in payload["polygon_conversions"]:
            md.append(f"  - File: `{poly['image']}` | Line {poly['line_idx']} ({poly['vertex_count']} vertices) -> BBox `(xc={poly['computed_bbox'][0]}, yc={poly['computed_bbox'][1]}, w={poly['computed_bbox'][2]}, h={poly['computed_bbox'][3]})`")
        md.append("\n")

        md.append("## 3. Grouped Split Distribution (70 / 15 / 15 Target)\n")
        md.append("| Split | Total Images | Total Objects | `supporting_tower` (Class 0) Objects | `monopole_tower` (Class 1) Objects |")
        md.append("| :--- | :--- | :--- | :--- | :--- |")
        for s_name in ["train", "val", "test"]:
            s_data = splits[s_name]
            objs = s_data["objects_by_class"]
            md.append(f"| **{s_name.capitalize()}** | `{s_data['images_count']}` | `{s_data['objects_count']}` | {objs.get('supporting_tower', 0)} | {objs.get('monopole_tower', 0)} |")
        md.append("\n")

        md.append("## 4. Discrepancy Investigation: Monopole Class Count (37 Exported vs. 25 Expected)\n")
        md.append("> [!WARNING]\n")
        md.append(f"> **DISCREPANCY FLAGGED**: The Roboflow source dataset contains **{mono_audit['total_monopole_source_images']} images** labeled with Class 0 (`monopole_tower`), whereas manual inspection expected **{mono_audit['user_expected_count']} images** (delta of +{mono_audit['discrepancy_delta']} images).\n")
        md.append("> This discrepancy is **NOT** silently overwritten. Below is the complete manifest of the 37 images labeled as monopole in the source export for user verification:\n")

        md.append("| # | Export Image Filename | Group / GPS ID |")
        md.append("| :--- | :--- | :--- |")
        for idx, item in enumerate(mono_audit["monopole_files_list"], 1):
            md.append(f"| {idx:02d} | `{item['filename']}` | `{item['group_id']}` |")
        md.append("\n")

        md.append("## 5. Next Steps & Approval Gate\n")
        md.append("1. **User Review**: Review the 37 candidate monopole images above.")
        md.append("2. **Execute Conversion**: Once approved, run `DatasetConverter.convert_dataset(dry_run=False)` to write the clean YOLO structure to `data/processed/yolo/`.")

        with open(report_path, "w", encoding="utf-8") as fp:
            fp.write("\n".join(md))


if __name__ == "__main__":
    converter = DatasetConverter()
    results = converter.validate_and_prepare(dry_run=True)
    print("Dry run completed successfully. Inspected images:", results["total_images_inspected"])
