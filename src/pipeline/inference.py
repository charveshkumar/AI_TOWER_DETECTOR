"""
Phase 6 — Tower Detection Inference Pipeline.
Provides a robust, object-oriented inference engine for YOLO11m baseline and augmented models.
"""

import io
import time
import logging
from pathlib import Path
from typing import Union, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from PIL import Image, ImageDraw, ImageFont
import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Default checkpoint registry
DEFAULT_CHECKPOINTS = {
    "baseline": Path("A:/Electrohack/runs/detect/yolo11m_baseline/weights/best.pt"),
    "augmented": Path("A:/Electrohack/runs/detect/yolo11m_augmented/weights/best.pt"),
}

CLASS_NAMES = {
    0: "supporting_tower",
    1: "monopole_tower"
}

# Distinct UI Palette (Supporting: Cyan #00E5FF, Monopole: Amber #FF9100)
CLASS_COLORS = {
    0: (0, 229, 255),    # Cyan RGB
    1: (255, 145, 0),    # Amber RGB
}


@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: List[float]  # [x1, y1, x2, y2] in pixels
    bbox_normalized: List[float]  # [xc, yc, w, h] in [0, 1]


@dataclass
class DetectionResult:
    original_image: Image.Image
    annotated_image: Image.Image
    detections: List[Detection] = field(default_factory=list)
    counts: Dict[str, int] = field(default_factory=dict)
    inference_time_ms: float = 0.0
    model_name: str = "baseline"
    checkpoint_path: str = ""
    image_size: Tuple[int, int] = (0, 0)  # (width, height)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "checkpoint_path": self.checkpoint_path,
            "inference_time_ms": round(self.inference_time_ms, 2),
            "image_size": {"width": self.image_size[0], "height": self.image_size[1]},
            "counts": self.counts,
            "detections": [
                {
                    "class_id": d.class_id,
                    "class_name": d.class_name,
                    "confidence": round(d.confidence, 4),
                    "bbox_xyxy": [round(x, 1) for x in d.bbox_xyxy],
                    "bbox_normalized": [round(x, 4) for x in d.bbox_normalized],
                }
                for d in self.detections
            ]
        }


class TowerDetector:
    """
    Inference Engine for AI-based Tower Component Detection.
    Loads and caches YOLO models with dynamic threshold configuration.
    """
    def __init__(
        self,
        checkpoint_path: Optional[Union[str, Path]] = None,
        model_name: str = "baseline"
    ):
        self.model_name = model_name
        if checkpoint_path is None:
            checkpoint_path = DEFAULT_CHECKPOINTS.get(model_name, DEFAULT_CHECKPOINTS["baseline"])
        
        self.checkpoint_path = Path(checkpoint_path)
        if not self.checkpoint_path.exists():
            raise FileNotFoundError(f"Model checkpoint not found at: {self.checkpoint_path}")
        
        logger.info(f"Loading YOLO model from: {self.checkpoint_path}")
        from ultralytics import YOLO
        self.model = YOLO(str(self.checkpoint_path))

    def _load_image(self, image_input: Union[str, Path, Image.Image, np.ndarray, bytes]) -> Image.Image:
        """Converts diverse image inputs into a clean RGB PIL Image."""
        if isinstance(image_input, (str, Path)):
            p = Path(image_input)
            if not p.exists():
                raise FileNotFoundError(f"Image not found at: {p}")
            return Image.open(p).convert("RGB")
        elif isinstance(image_input, bytes):
            return Image.open(io.BytesIO(image_input)).convert("RGB")
        elif isinstance(image_input, np.ndarray):
            return Image.fromarray(image_input).convert("RGB")
        elif isinstance(image_input, Image.Image):
            return image_input.convert("RGB")
        else:
            raise TypeError(f"Unsupported image input type: {type(image_input)}")

    def predict(
        self,
        image_input: Union[str, Path, Image.Image, np.ndarray, bytes],
        conf: float = 0.25,
        iou: float = 0.45,
        imgsz: Optional[int] = None
    ) -> DetectionResult:
        """
        Runs model inference on an input image.
        """
        pil_img = self._load_image(image_input)
        w, h = pil_img.size

        # Determine optimal resolution based on model type
        if imgsz is None:
            imgsz = 1024 if "augmented" in self.model_name.lower() else 640

        start_time = time.perf_counter()
        
        # Run YOLO inference
        results = self.model.predict(
            source=pil_img,
            conf=conf,
            iou=iou,
            imgsz=imgsz,
            verbose=False
        )
        
        inference_time_ms = (time.perf_counter() - start_time) * 1000.0

        detections: List[Detection] = []
        counts = {"supporting_tower": 0, "monopole_tower": 0, "total": 0}

        if len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                cls_id = int(box.cls.item())
                confidence = float(box.conf.item())
                xyxy = box.xyxy[0].tolist()
                
                # Normalized bbox [xc, yc, w, h]
                x1, y1, x2, y2 = xyxy
                box_w = max(0.0, x2 - x1)
                box_h = max(0.0, y2 - y1)
                xc = (x1 + x2) / 2.0 / w
                yc = (y1 + y2) / 2.0 / h
                norm_w = box_w / w
                norm_h = box_h / h

                cls_name = CLASS_NAMES.get(cls_id, f"class_{cls_id}")
                
                det = Detection(
                    class_id=cls_id,
                    class_name=cls_name,
                    confidence=confidence,
                    bbox_xyxy=xyxy,
                    bbox_normalized=[xc, yc, norm_w, norm_h]
                )
                detections.append(det)

                if cls_name in counts:
                    counts[cls_name] += 1
                else:
                    counts[cls_name] = 1
                counts["total"] += 1

        # Render custom high-resolution annotated image
        annotated_img = self._annotate_image(pil_img, detections)

        return DetectionResult(
            original_image=pil_img,
            annotated_image=annotated_img,
            detections=detections,
            counts=counts,
            inference_time_ms=inference_time_ms,
            model_name=self.model_name,
            checkpoint_path=str(self.checkpoint_path),
            image_size=(w, h)
        )

    def _annotate_image(self, img: Image.Image, detections: List[Detection]) -> Image.Image:
        """
        Renders crisp bounding boxes and high-contrast label badges.
        """
        annotated = img.copy()
        draw = ImageDraw.Draw(annotated)
        w, h = img.size

        # Dynamic font scaling based on image dimension
        base_font_size = max(14, int(min(w, h) * 0.025))
        try:
            font = ImageFont.truetype("arial.ttf", base_font_size)
        except Exception:
            font = ImageFont.load_default()

        line_width = max(3, int(min(w, h) * 0.004))

        for d in detections:
            color = CLASS_COLORS.get(d.class_id, (0, 255, 0))
            x1, y1, x2, y2 = d.bbox_xyxy

            # Bounding box
            draw.rectangle([x1, y1, x2, y2], outline=color, width=line_width)

            # Label badge text
            label_text = f" {d.class_name.upper()} | {d.confidence*100:.1f}% "
            
            # Badge text bounding box
            try:
                bbox_text = font.getbbox(label_text)
                text_w = bbox_text[2] - bbox_text[0]
                text_h = bbox_text[3] - bbox_text[1]
            except Exception:
                text_w, text_h = len(label_text) * (base_font_size * 0.6), base_font_size + 4

            # Place badge above box if space permits, else inside
            badge_y1 = max(0, y1 - text_h - 6) if (y1 - text_h - 6) >= 0 else y1
            badge_y2 = badge_y1 + text_h + 6
            badge_x1 = x1
            badge_x2 = x1 + text_w + 8

            # Draw background tag
            draw.rectangle([badge_x1, badge_y1, badge_x2, badge_y2], fill=color)
            # Text fill (dark text for high contrast on cyan/amber badges)
            draw.text((badge_x1 + 4, badge_y1 + 2), label_text, fill=(10, 15, 25), font=font)

        return annotated
