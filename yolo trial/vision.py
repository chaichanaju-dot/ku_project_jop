"""
vision.py - end-to-end T-BHI vision pipeline: photo -> per-element damage
ratings, using the trained YOLO-seg model plus damage_rules.py and
element_lookup.py.

Pass 1 (full image): run the model once on the whole photo. Split detections
into structural elements (pier / girder / pier_cap - see STRUCTURAL_CLASSES)
and damage instances (crack / spalling / exposed rebar / stain).

Per structural element instance:
  - bounding box + pixel count (q) straight from its own mask
  - crop the original image to that box and run the SAME model again
    (pass 2), to catch damage too small to see reliably at full-image scale
    (thin cracks etc. - see the guide's section 8.2)
  - shift pass-2 damage masks back into full-image pixel coordinates by
    adding the crop's (x0, y0) offset, so pass-1 and pass-2 damage masks for
    this element all live in one consistent coordinate frame
  - call damage_rules.rate_damage() for every damage instance found (pass 1
    + pass 2), passing sibling damage masks as other_masks_dict so overlap
    rules (crack-over-rust, etc.) apply
  - print one row per element: name, q, and every damage found with its
    pixel count and rated level

Known gaps in the current trained model (data.yaml has 7 classes):
  - no "deck" class yet, only pier bridge / beam / pier cap are trainable
    structural classes, so ELEMENT_WEIGHT["deck"] can never be exercised here
  - "stain" is one generic class standing in for both rust staining and
    efflorescence - _stain_damage_type() resolves it to "rust_on_rebar" vs
    "rust_efflorescence" by checking overlap with exposed rebar
"""

import sys

import cv2
import numpy as np
from ultralytics import YOLO

from damage_rules import rate_damage
from element_lookup import ELEMENT_WEIGHT, ELEMENT_IS_PRIMARY

# Best-performing of the completed segmentation training runs (highest
# val mAP50-mask); see runs/segment/*/results.csv.
MODEL_PATH = "runs/segment/train-4/weights/best.pt"
CONF_THRESHOLD = 0.25

# trained class name -> element_lookup.py key
STRUCTURAL_CLASSES = {
    "pier bridge": "pier",
    "beam": "girder",
    "pier cap": "pier_cap",
}

# trained class name -> damage_rules.py damage_type; "stain" is resolved per
# instance by _stain_damage_type() since the model can't tell rust from
# efflorescence
DAMAGE_CLASSES = {
    "crack": "crack",
    "spalling": "spalling",
    "Exposed Rebar": "exposed_rebar",
    "stain": None,
}


class Instance:
    __slots__ = ("class_name", "mask")

    def __init__(self, class_name: str, mask: np.ndarray):
        self.class_name = class_name
        self.mask = mask


def _detect(model: YOLO, image, conf: float) -> list[Instance]:
    """One segmentation pass. `image` is a path or a BGR numpy array."""
    result = model.predict(image, retina_masks=True, conf=conf, verbose=False)[0]
    if result.masks is None:
        return []
    masks = result.masks.data.cpu().numpy().astype(bool)
    classes = result.boxes.cls.cpu().numpy().astype(int)
    return [Instance(result.names[c], m) for m, c in zip(masks, classes)]


def _bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    """(x0, y0, x1, y1), x1/y1 exclusive - tight box around a mask's True pixels."""
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _shift_mask(mask: np.ndarray, offset: tuple[int, int], canvas_shape: tuple[int, int]) -> np.ndarray:
    """Place a crop-local mask into a full-image-sized canvas at (x0, y0)."""
    x0, y0 = offset
    canvas = np.zeros(canvas_shape, dtype=bool)
    h, w = mask.shape
    canvas[y0:y0 + h, x0:x0 + w] = mask
    return canvas


def _union(masks: list[np.ndarray]) -> np.ndarray | None:
    if not masks:
        return None
    out = masks[0].copy()
    for m in masks[1:]:
        out |= m
    return out


def _stain_damage_type(stain_mask: np.ndarray, exposed_rebar_masks: list[np.ndarray]) -> str:
    """stain overlapping exposed rebar = rust on steel, otherwise rust/efflorescence on concrete."""
    for rebar_mask in exposed_rebar_masks:
        if np.count_nonzero(stain_mask & rebar_mask) > 0:
            return "rust_on_rebar"
    return "rust_efflorescence"


def analyze_image(model: YOLO, image_path: str, conf: float = CONF_THRESHOLD) -> list[dict]:
    """
    Run the full 2-pass pipeline on one image.

    Returns one dict per structural element instance found:
      {"element": str, "q": int, "mask": np.ndarray,
       "damages": [(damage_type, mask, DamageRating), ...]}
    "mask" is the element's own footprint (full-image coordinates) and each
    damage's mask is also in full-image coordinates - main.py uses both to
    build a per-pixel condition-level map.
    """
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    canvas_shape = image.shape[:2]

    pass1 = _detect(model, image, conf)
    structural = [inst for inst in pass1 if inst.class_name in STRUCTURAL_CLASSES]
    damage_pass1 = [inst for inst in pass1 if inst.class_name in DAMAGE_CLASSES]

    report = []
    for element in structural:
        x0, y0, x1, y1 = _bbox(element.mask)
        q = int(element.mask.sum())

        # damage from pass 1 that actually falls inside this element's mask
        damages = [d for d in damage_pass1 if np.count_nonzero(d.mask & element.mask) > 0]

        # pass 2: re-run the same model on the crop to catch finer damage
        crop = image[y0:y1, x0:x1]
        if crop.size > 0:
            for inst in _detect(model, crop, conf):
                if inst.class_name not in DAMAGE_CLASSES:
                    continue
                full_mask = _shift_mask(inst.mask, (x0, y0), canvas_shape)
                damages.append(Instance(inst.class_name, full_mask))

        exposed_rebar_masks = [d.mask for d in damages if d.class_name == "Exposed Rebar"]
        stain_masks = [d.mask for d in damages if d.class_name == "stain"]
        other_masks = {
            "crack_mask": _union([d.mask for d in damages if d.class_name == "crack"]),
            "exposed_rebar_mask": _union(exposed_rebar_masks),
            "rust_mask": _union(stain_masks),
            "efflorescence_mask": _union(stain_masks),
        }

        rated = []
        for d in damages:
            damage_type = DAMAGE_CLASSES[d.class_name]
            if damage_type is None:  # stain
                damage_type = _stain_damage_type(d.mask, exposed_rebar_masks)
            rating = rate_damage(damage_type, d.mask, other_masks)
            rated.append((damage_type, d.mask, rating))

        report.append({
            "element": STRUCTURAL_CLASSES[element.class_name],
            "q": q,
            "mask": element.mask,
            "damages": rated,
        })
    return report


def print_report(report: list[dict]) -> None:
    print(f"{'ชิ้นส่วน':<12}{'q (px)':>8}   ความเสียหายที่เจอ (พิกเซล -> ระดับ)")
    print("-" * 70)
    if not report:
        print("(ไม่พบชิ้นส่วนโครงสร้างในภาพนี้)")
        return
    for row in report:
        w = ELEMENT_WEIGHT.get(row["element"], "?")
        primary = ELEMENT_IS_PRIMARY.get(row["element"], "?")
        header = f"{row['element']:<12}{row['q']:>8}"
        if not row["damages"]:
            print(f"{header}   (ไม่พบความเสียหาย) [W={w}, primary={primary}]")
            continue
        for i, (damage_type, mask, rating) in enumerate(row["damages"]):
            prefix = header if i == 0 else " " * 20
            suffix = f" [W={w}, primary={primary}]" if i == 0 else ""
            print(f"{prefix}   {damage_type} {int(mask.sum())}px -> level {rating.level} ({rating.confidence}){suffix}")


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else (
        "train/images/image_0001431_jpg.rf.4aad1bc1d6feb6de3f5953a1ec74cfda.jpg"
    )
    # NOTE: this model was trained for only 20 epochs on a very small dataset
    # (see train.py) so its confidence scores are extremely low even on
    # training images (~0.01-0.02). CONF_THRESHOLD (0.25) is what a properly
    # trained model should use; we drop to 0.01 here purely to get any
    # detections out of this checkpoint and exercise the full pipeline.
    test_conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01

    model = YOLO(MODEL_PATH)
    report = analyze_image(model, image_path, conf=test_conf)

    print(f"ภาพ: {image_path}")
    print(f"โมเดล: {MODEL_PATH} (conf={test_conf})\n")
    print_report(report)
