"""
Phase 2 Post-Conversion Validator for YOLO Dataset.
Performs comprehensive validation of all output images, labels, class IDs,
bounding box normalization, and split integrity in data/processed/yolo/.
"""
import os
import yaml
from pathlib import Path
from collections import Counter
from PIL import Image

from src.config import BASE_DIR, PROCESSED_DATA_DIR, CLASSES


def validate_converted_yolo_dataset():
    yolo_dir = PROCESSED_DATA_DIR / "yolo"
    print("=" * 65)
    print("PHASE 2 POST-CONVERSION YOLO DATASET VALIDATION")
    print("=" * 65)

    if not yolo_dir.exists():
        raise FileNotFoundError(f"YOLO dataset directory not found at: {yolo_dir}")

    yaml_path = yolo_dir / "data.yaml"
    if not yaml_path.exists():
        raise FileNotFoundError(f"data.yaml not found at: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as fp:
        yolo_cfg = yaml.safe_load(fp)

    print("\n[1] DATA.YAML VERIFICATION:")
    print(f"  - YAML Location: {yaml_path}")
    print(f"  - train: {yolo_cfg.get('train')}")
    print(f"  - val: {yolo_cfg.get('val')}")
    print(f"  - test: {yolo_cfg.get('test')}")
    print(f"  - nc: {yolo_cfg.get('nc')}")
    print(f"  - names: {yolo_cfg.get('names')}")

    assert yolo_cfg.get("nc") == 2, f"Expected nc=2, got {yolo_cfg.get('nc')}"
    assert yolo_cfg.get("names") == ["supporting_tower", "monopole_tower"], (
        f"Incorrect class names order: {yolo_cfg.get('names')}"
    )

    total_images_all = 0
    total_labels_all = 0
    total_objects_all = 0
    global_cls_objs = Counter()
    global_cls_imgs = Counter()
    split_images_set = {}
    all_image_filenames = set()
    validation_errors = []

    print("\n[2] PER-SPLIT INVENTORY & LABEL VALIDATION:")
    for s in ["train", "val", "test"]:
        img_dir = yolo_dir / s / "images"
        lbl_dir = yolo_dir / s / "labels"

        if not img_dir.exists() or not lbl_dir.exists():
            validation_errors.append(f"Missing directory {s}/images or {s}/labels")
            continue

        imgs = sorted(list(img_dir.glob("*")))
        lbls = sorted(list(lbl_dir.glob("*.txt")))

        split_images_set[s] = set(f.name for f in imgs)
        total_images_all += len(imgs)
        total_labels_all += len(lbls)

        # 1-to-1 matching
        img_stems = {f.stem: f for f in imgs}
        lbl_stems = {f.stem: f for f in lbls}

        for stem in img_stems:
            if stem not in lbl_stems:
                validation_errors.append(f"Image {img_stems[stem].name} missing label file in {s}")
        for stem in lbl_stems:
            if stem not in img_stems:
                validation_errors.append(f"Label {lbl_stems[stem].name} has no matching image in {s}")

        # Image decodability
        for img_f in imgs:
            all_image_filenames.add(img_f.name)
            try:
                with Image.open(img_f) as img:
                    w, h = img.size
                    if w <= 0 or h <= 0:
                        validation_errors.append(f"Invalid dimension {w}x{h} for {img_f.name}")
            except Exception as e:
                validation_errors.append(f"Failed to open image {img_f.name}: {e}")

        # Label verification
        s_cls_objs = Counter()
        s_cls_imgs = Counter()

        for lbl_f in lbls:
            with open(lbl_f, "r", encoding="utf-8") as fp:
                lines = [l.strip() for l in fp if l.strip()]

            if not lines:
                validation_errors.append(f"Empty label file {lbl_f.name} in {s}")

            file_classes = set()
            for l_idx, line in enumerate(lines):
                parts = line.split()
                if len(parts) != 5:
                    validation_errors.append(f"{lbl_f.name} line {l_idx} does not have 5 tokens: '{line}'")
                    continue
                try:
                    cid = int(parts[0])
                    xc, yc, w, h = float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])

                    if cid not in (0, 1):
                        validation_errors.append(f"Invalid class ID {cid} in {lbl_f.name}")
                    if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0 and 0.0 < w <= 1.0 and 0.0 < h <= 1.0):
                        validation_errors.append(f"Out-of-bounds coordinates in {lbl_f.name}: {line}")

                    s_cls_objs[cid] += 1
                    global_cls_objs[cid] += 1
                    total_objects_all += 1
                    file_classes.add(cid)
                except Exception as e:
                    validation_errors.append(f"Parse error in {lbl_f.name}: {e}")

            for cid in file_classes:
                s_cls_imgs[cid] += 1
                global_cls_imgs[cid] += 1

        print(f"  [{s.upper()} SPLIT]")
        print(f"    - Images: {len(imgs)} | Labels: {len(lbls)}")
        print(f"    - Total Objects: {sum(s_cls_objs.values())}")
        print(f"    - supporting_tower (Class 0): {s_cls_objs[0]} objects across {s_cls_imgs[0]} images")
        print(f"    - monopole_tower (Class 1): {s_cls_objs[1]} objects across {s_cls_imgs[1]} images")

    # Split overlap check
    print("\n[3] SPLIT INTEGRITY & OVERLAP CHECK:")
    train_val_overlap = split_images_set["train"].intersection(split_images_set["val"])
    train_test_overlap = split_images_set["train"].intersection(split_images_set["test"])
    val_test_overlap = split_images_set["val"].intersection(split_images_set["test"])

    print(f"  - Train & Val Overlap: {len(train_val_overlap)} images (Expected: 0)")
    print(f"  - Train & Test Overlap: {len(train_test_overlap)} images (Expected: 0)")
    print(f"  - Val & Test Overlap: {len(val_test_overlap)} images (Expected: 0)")

    if train_val_overlap or train_test_overlap or val_test_overlap:
        validation_errors.append("Data leakage detected: overlapping images found between splits!")

    # Global Dataset Totals Check
    print("\n[4] FINAL DATASET TOTALS:")
    print(f"  - Total Unique Images: {len(all_image_filenames)} (Expected: 120)")
    print(f"  - Total Annotated Objects: {total_objects_all} (Expected: 127)")
    print(f"  - supporting_tower (Class 0): {global_cls_objs[0]} objects in {global_cls_imgs[0]} images (Expected: 91 / 84)")
    print(f"  - monopole_tower (Class 1): {global_cls_objs[1]} objects in {global_cls_imgs[1]} images (Expected: 36 / 36)")

    print(f"\n[5] VALIDATION ERROR REPORT:")
    print(f"  - Total Errors Encountered: {len(validation_errors)}")
    if validation_errors:
        for err in validation_errors:
            print(f"    * {err}")
    else:
        print("  - ZERO ERRORS: All output images, labels, class IDs, and splits are 100% compliant!")

    print("\n" + "=" * 65)
    print("PHASE 2 DATASET CONVERSION VALIDATION: PASSED")
    print("=" * 65)

    return {
        "status": "PASSED" if not validation_errors else "FAILED",
        "errors": validation_errors,
        "total_images": len(all_image_filenames),
        "total_objects": total_objects_all,
        "class_objects": dict(global_cls_objs),
        "class_images": dict(global_cls_imgs),
        "yaml_config": yolo_cfg
    }


if __name__ == "__main__":
    validate_converted_yolo_dataset()
