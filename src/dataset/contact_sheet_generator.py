"""
Monopole Tower Contact Sheet & Review Generator.
Generates multi-page visual contact sheets and review CSV for all 37 monopole images.
"""
import os
import csv
from pathlib import Path
import cv2
import numpy as np

from src.config import BASE_DIR, PROCESSED_DATA_DIR, RAW_DATA_DIR


def generate_monopole_contact_sheets():
    rf_dir = PROCESSED_DATA_DIR / "roboflow_export" / "train"
    raw_dir = RAW_DATA_DIR / "sample"
    out_dir = BASE_DIR / "reports" / "monopole_review"
    out_dir.mkdir(parents=True, exist_ok=True)
    indiv_dir = out_dir / "individual_annotated"
    indiv_dir.mkdir(parents=True, exist_ok=True)

    lbl_dir = rf_dir / "labels"
    img_dir = rf_dir / "images"
    raw_files = list(raw_dir.glob("*"))

    monopole_entries = []
    for lbl_f in sorted(list(lbl_dir.glob("*.txt"))):
        with open(lbl_f, "r", encoding="utf-8") as fp:
            lines = [l.strip() for l in fp if l.strip()]
        has_cls_0 = any(int(l.split()[0]) == 0 for l in lines)
        if has_cls_0:
            img_candidates = list(img_dir.glob(f"{lbl_f.stem}.*"))
            if img_candidates:
                img_f = img_candidates[0]
                boxes = []
                for l in lines:
                    parts = l.split()
                    cls_id = int(parts[0])
                    if cls_id == 0:
                        if len(parts) == 5:
                            boxes.append((float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])))
                        elif len(parts) > 5:
                            coords = [float(p) for p in parts[1:]]
                            xs, ys = coords[0::2], coords[1::2]
                            xmin, xmax = min(xs), max(xs)
                            ymin, ymax = min(ys), max(ys)
                            w, h = xmax - xmin, ymax - ymin
                            xc, yc = xmin + w / 2.0, ymin + h / 2.0
                            boxes.append((xc, yc, w, h))

                raw_match = ""
                for rf in raw_files:
                    if rf.stem in img_f.name:
                        raw_match = rf.name
                        break

                monopole_entries.append({
                    "label_file": lbl_f.name,
                    "image_file": img_f.name,
                    "image_path": img_f,
                    "raw_match": raw_match,
                    "boxes": boxes
                })

    # 1. Write CSV
    csv_path = out_dir / "monopole_manual_review.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as fp:
        writer = csv.writer(fp)
        writer.writerow([
            "index",
            "export_filename",
            "raw_matched_filename",
            "source_class_id",
            "source_class_name",
            "num_boxes",
            "bounding_boxes_xc_yc_w_h",
            "manual_review",
            "notes"
        ])
        for idx, e in enumerate(monopole_entries, 1):
            bbox_str = "; ".join([f"[{b[0]:.4f}, {b[1]:.4f}, {b[2]:.4f}, {b[3]:.4f}]" for b in e["boxes"]])
            writer.writerow([
                idx,
                e["image_file"],
                e["raw_match"],
                0,
                "monopole_tower",
                len(e["boxes"]),
                bbox_str,
                "",
                ""
            ])

    # 2. Render individual annotated images and cards
    rendered_cards = []
    card_w, card_h = 420, 480

    for idx, e in enumerate(monopole_entries, 1):
        cv_img = cv2.imread(str(e["image_path"]))
        h_orig, w_orig = cv_img.shape[:2]

        annotated = cv_img.copy()
        for xc, yc, w, h in e["boxes"]:
            x1 = int((xc - w / 2.0) * w_orig)
            y1 = int((yc - h / 2.0) * h_orig)
            x2 = int((xc + w / 2.0) * w_orig)
            y2 = int((yc + h / 2.0) * h_orig)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w_orig - 1, x2), min(h_orig - 1, y2)

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 230, 255), 2)
            label_text = f"monopole ({w*100:.0f}%x{h*100:.0f}%)"
            (lw, lh), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
            cv2.rectangle(annotated, (x1, max(0, y1 - 18)), (x1 + lw + 6, max(18, y1)), (0, 230, 255), -1)
            cv2.putText(annotated, label_text, (x1 + 3, max(14, y1 - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

        indiv_path = indiv_dir / f"{idx:02d}_{Path(e['image_file']).stem[:32]}.jpg"
        cv2.imwrite(str(indiv_path), annotated)

        # Build card
        card = np.zeros((card_h, card_w, 3), dtype=np.uint8)
        card[:] = (26, 26, 30)

        img_resized = cv2.resize(annotated, (380, 380), interpolation=cv2.INTER_AREA)
        card[45:425, 20:400] = img_resized
        cv2.rectangle(card, (19, 44), (400, 425), (60, 60, 70), 1)

        # Header Badge
        cv2.rectangle(card, (20, 10), (80, 36), (0, 140, 255), -1)
        cv2.putText(card, f"#{idx:02d}", (28, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)

        raw_title = e["raw_match"] if e["raw_match"] else e["image_file"][:24]
        cv2.putText(card, raw_title, (90, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (220, 220, 220), 1, cv2.LINE_AA)

        # Footer
        short_export = e["image_file"]
        if len(short_export) > 42:
            short_export = short_export[:20] + "..." + short_export[-18:]
        cv2.putText(card, short_export, (20, 448), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 160), 1, cv2.LINE_AA)
        cv2.putText(card, f"Class: 0 (monopole_tower) | {len(e['boxes'])} bbox", (20, 468), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 210, 255), 1, cv2.LINE_AA)

        rendered_cards.append(card)

    # 3. Assemble Multi-Page Contact Sheets (3x3 grid = 9 per page)
    cols = 3
    rows = 3
    cards_per_page = cols * rows
    num_pages = (len(rendered_cards) + cards_per_page - 1) // cards_per_page

    header_margin = 80
    margin = 20
    page_w = cols * card_w + (cols + 1) * margin
    page_h = rows * card_h + (rows + 1) * margin + header_margin

    saved_contact_sheets = []
    for p in range(num_pages):
        page_img = np.zeros((page_h, page_w, 3), dtype=np.uint8)
        page_img[:] = (16, 16, 20)

        # Banner
        cv2.rectangle(page_img, (0, 0), (page_w, header_margin - 10), (32, 34, 40), -1)
        cv2.putText(page_img, "MONOPOLE TOWER (SOURCE CLASS 0) VISUAL CONTACT SHEET", (margin, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 230, 255), 2, cv2.LINE_AA)
        cv2.putText(page_img, f"Page {p+1} of {num_pages} | Images #{p*cards_per_page + 1:02d} - #{min((p+1)*cards_per_page, len(monopole_entries)):02d} of 37 | Dataset: Roboflow Export Train", (margin, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180, 180, 190), 1, cv2.LINE_AA)

        start_idx = p * cards_per_page
        end_idx = min(start_idx + cards_per_page, len(rendered_cards))

        for i in range(start_idx, end_idx):
            local_idx = i - start_idx
            r = local_idx // cols
            c = local_idx % cols
            x = margin + c * (card_w + margin)
            y = header_margin + r * (card_h + margin)
            page_img[y:y + card_h, x:x + card_w] = rendered_cards[i]

        cs_file = out_dir / f"monopole_contact_sheet_page_{p+1}.jpg"
        cv2.imwrite(str(cs_file), page_img, [int(cv2.IMWRITE_JPEG_QUALITY), 95])
        saved_contact_sheets.append(cs_file)

    return {
        "csv_path": csv_path,
        "contact_sheets": saved_contact_sheets,
        "individual_annotated_dir": indiv_dir,
        "total_images": len(monopole_entries)
    }


if __name__ == "__main__":
    res = generate_monopole_contact_sheets()
    print("Generation complete.")
    print("CSV:", res["csv_path"])
    print("Contact Sheets:", [str(p) for p in res["contact_sheets"]])
