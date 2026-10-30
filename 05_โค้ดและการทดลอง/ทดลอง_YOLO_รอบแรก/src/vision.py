# End-to-end T-BHI vision pipeline: photo -> per-element damage ratings, using two
# independent trained OBB (oriented bounding box) models plus damage_rules.py and
# element_lookup.py.
#
#   `model`        (ours, YOLO-OBB, MODEL_PATH) - finds structural elements
#                   (pier/girder/pier_cap) and generic damage area (single
#                   "damage" class, no type - see DAMAGE_CLASSES), both as
#                   oriented boxes rasterized into masks (see _obb_to_mask).
#                   Only its box shape/area is used, never a damage type -
#                   type comes only from `damage_model` below.
#   `damage_model` (senior's, YOLO-OBB, SENIOR_MODEL_PATH) - finds damage and
#                   its type independently. Its class prediction IS trusted
#                   (much larger training set, high mAP).
#
# Both models run on the SAME image, so their masks share one pixel coordinate
# system and can be directly ANDed together.
#
# Per structural element instance: bbox + pixel count (q) from `model`'s own
# mask; crop to that box and re-run both models on the crop (pass 2) to catch
# damage too small to see at full-image scale; for each OBB-confirmed damage,
# prefer the best-overlapping mask from `model` (its own box rasterized),
# falling back to the senior model's OBB box rasterized as a mask.
#
# Known gaps: no "deck" class in either model yet; the senior model's
# "strain" class has no confirmed damage_rules.py mapping yet, so it's dropped.

import sys

import cv2
import numpy as np
from ultralytics import YOLO

from damage_rules import rate_damage
from element_lookup import ELEMENT_WEIGHT, ELEMENT_IS_PRIMARY

# Produced by train.py once you've trained the OBB-relabeled dataset (default
# output location for `python src/train.py`).
MODEL_PATH = "runs/obb/train/weights/best.pt"
# Senior's OBB damage model (942 epochs, precision=0.91, recall=0.88, mAP50=0.915, mAP50-95=0.80).
SENIOR_MODEL_PATH = r"C:\ku_project_jop\rawdata\งานของรุ่นพี่\weights\best.pt"
CONF_THRESHOLD = 0.25

STRUCTURAL_CLASSES = {
    "pier bridge": "pier",
    "beam": "girder",
    "pier cap": "pier_cap",
}

DAMAGE_CLASSES = {"damage"}  # generic - our model marks damage area only, not type (senior model does that)

SENIOR_CLASS_TO_DAMAGE_TYPE = {
    "Crack": "crack",
    "Spalling": "spalling",
    "Porous_Defect": "honeycomb",
    "Steel_Exposure": "exposed_rebar",
    "Rust_Stained_Exposure": "rust_on_rebar",
    "Efflorescence": "rust_efflorescence",
}


class Instance:
    __slots__ = ("class_name", "mask", "conf")

    def __init__(self, class_name: str, mask: np.ndarray, conf: float | None = None):
        self.class_name = class_name
        self.mask = mask
        self.conf = conf  # this detection's own OBB confidence


def _obb_to_mask(corners: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    canvas = np.zeros(shape, dtype=np.uint8)
    cv2.fillPoly(canvas, [corners.astype(np.int32)], 1)
    return canvas.astype(bool)


def _detect_obb(model: YOLO, image: np.ndarray, conf: float) -> list[Instance]:
    """One OBB pass. Instance.class_name is the model's own raw class name -
    callers map it to structural/damage classes as needed."""
    result = model.predict(image, conf=conf, verbose=False)[0]
    if result.obb is None:
        return []
    shape = image.shape[:2]
    corners_all = result.obb.xyxyxyxy.cpu().numpy()
    classes = result.obb.cls.cpu().numpy().astype(int)
    confs = result.obb.conf.cpu().numpy()
    return [
        Instance(result.names[int(cls_idx)], _obb_to_mask(corners, shape), conf=float(det_conf))
        for corners, cls_idx, det_conf in zip(corners_all, classes, confs)
    ]


def _detect_damage_obb(damage_model: YOLO, image: np.ndarray, conf: float) -> list[Instance]:
    """Senior's OBB detections, remapped to damage_rules.py's damage_type via
    SENIOR_CLASS_TO_DAMAGE_TYPE; unmapped classes ("strain") are dropped."""
    out = []
    for inst in _detect_obb(damage_model, image, conf):
        damage_type = SENIOR_CLASS_TO_DAMAGE_TYPE.get(inst.class_name)
        if damage_type is not None:
            out.append(Instance(damage_type, inst.mask, conf=inst.conf))
    return out


def _bbox(mask: np.ndarray) -> tuple[int, int, int, int]:
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _shift_mask(mask: np.ndarray, offset: tuple[int, int], canvas_shape: tuple[int, int]) -> np.ndarray:
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


# Below this IoU, a candidate mask from our own (weak) model is treated as noise
# rather than a real match against the OBB-confirmed damage.
MIN_MATCH_IOU = 0.3

# At low conf thresholds, NMS doesn't always suppress two near-identical
# detections of the same object, double-weighting it in T-BHI.
DEDUPE_IOU = 0.7


def _dedupe_structural(instances: list[Instance]) -> list[Instance]:
    kept: list[Instance] = []
    for inst in instances:
        match = None
        for k in kept:
            if k.class_name != inst.class_name:
                continue
            intersection = np.count_nonzero(k.mask & inst.mask)
            union = np.count_nonzero(k.mask | inst.mask)
            if union > 0 and intersection / union >= DEDUPE_IOU:
                match = k
                break
        if match is not None:
            match.mask |= inst.mask
        else:
            kept.append(Instance(inst.class_name, inst.mask.copy()))
    return kept


def _best_matching_mask(target: np.ndarray, candidates: list[np.ndarray]) -> np.ndarray | None:
    best_mask, best_iou = None, 0.0
    for mask in candidates:
        intersection = np.count_nonzero(mask & target)
        if intersection == 0:
            continue
        union = np.count_nonzero(mask | target)
        iou = intersection / union
        if iou > best_iou:
            best_mask, best_iou = mask, iou
    return best_mask if best_iou >= MIN_MATCH_IOU else None


def analyze_image(
    model: YOLO,
    damage_model: YOLO,
    image_path: str,
    conf: float = CONF_THRESHOLD,
) -> list[dict]:
    """Returns one dict per structural element instance found:
    {"element": str, "q": int, "mask": np.ndarray, "damages": [(damage_type, mask, DamageRating), ...]}"""
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    canvas_shape = image.shape[:2]

    pass1 = _detect_obb(model, image, conf)
    structural = _dedupe_structural([inst for inst in pass1 if inst.class_name in STRUCTURAL_CLASSES])
    own_damage_masks = [inst.mask for inst in pass1 if inst.class_name in DAMAGE_CLASSES]

    damage_pass1 = _detect_damage_obb(damage_model, image, conf)

    report = []
    for element in structural:
        x0, y0, x1, y1 = _bbox(element.mask)
        q = int(element.mask.sum())

        confirmed = [d for d in damage_pass1 if np.count_nonzero(d.mask & element.mask) > 0]

        crop = image[y0:y1, x0:x1]
        if crop.size > 0:
            for d in _detect_damage_obb(damage_model, crop, conf):
                full_mask = _shift_mask(d.mask, (x0, y0), canvas_shape)
                confirmed.append(Instance(d.class_name, full_mask, conf=d.conf))
            for inst in _detect_obb(model, crop, conf):
                if inst.class_name not in DAMAGE_CLASSES:
                    continue
                own_damage_masks.append(_shift_mask(inst.mask, (x0, y0), canvas_shape))

        damages = []
        for d in confirmed:
            own_mask = _best_matching_mask(d.mask, own_damage_masks)
            damages.append(Instance(d.class_name, own_mask if own_mask is not None else d.mask, conf=d.conf))

        other_masks = {
            "crack_mask": _union([d.mask for d in damages if d.class_name == "crack"]),
            "exposed_rebar_mask": _union([d.mask for d in damages if d.class_name == "exposed_rebar"]),
            "rust_mask": _union([d.mask for d in damages if d.class_name == "rust_on_rebar"]),
            "efflorescence_mask": _union([d.mask for d in damages if d.class_name == "rust_efflorescence"]),
        }

        rated = [
            (d.class_name, d.mask, rate_damage(d.class_name, d.mask, other_masks, det_conf=d.conf))
            for d in damages
        ]

        report.append({
            "element": STRUCTURAL_CLASSES[element.class_name],
            "q": q,
            "mask": element.mask,
            "damages": rated,
        })
    return report


# BGR (cv2 order) - structure gets green, the 6 damage_types take 6 more slots
# from the dataviz skill's validated categorical palette.
_STRUCTURE_COLOR = (0, 131, 0)       # #008300 green
_OVERLAY_COLORS = {
    "crack": (72, 73, 227),               # #e34948 red
    "spalling": (52, 104, 235),           # #eb6834 orange
    "exposed_rebar": (164, 123, 232),     # #e87ba4 magenta
    "rust_on_rebar": (167, 58, 74),       # #4a3aa7 violet
    "rust_efflorescence": (0, 161, 237),  # #eda100 yellow
    "honeycomb": (214, 120, 42),          # #2a78d6 blue
}
_INK = (11, 11, 11)
_SURFACE = (251, 252, 252)


def _draw_label_chip(canvas: np.ndarray, text: str, origin: tuple[int, int], color: tuple[int, int, int]) -> None:
    x, y = origin
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 1.05, 2)
    cv2.rectangle(canvas, (x - 4, y - th - 6), (x + tw + 4, y + baseline + 2), color, -1)
    cv2.putText(canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.05, (255, 255, 255), 2, cv2.LINE_AA)


def save_overlay(image_path: str, report: list[dict], out_path: str, scale: int = 2) -> None:
    image = cv2.imread(str(image_path))
    base = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    fills = base.copy()

    classes_present = set()
    scaled_rows = []
    for row in report:
        mask_up = cv2.resize(row["mask"].astype(np.uint8), None, fx=scale, fy=scale,
                              interpolation=cv2.INTER_NEAREST)
        damages_up = []
        for damage_type, dmask, rating in row["damages"]:
            classes_present.add(damage_type)
            color = _OVERLAY_COLORS.get(damage_type, (128, 128, 128))
            dmask_up = cv2.resize(dmask.astype(np.uint8), None, fx=scale, fy=scale,
                                   interpolation=cv2.INTER_NEAREST)
            contours, _ = cv2.findContours(dmask_up, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(fills, contours, -1, color, -1)
            damages_up.append((damage_type, dmask_up, color))
        scaled_rows.append((row["element"], mask_up, damages_up))

    # translucent fill under crisp outlines, so thin damage (cracks) stays visible
    overlay = cv2.addWeighted(fills, 0.28, base, 0.72, 0)

    for element_name, mask_up, damages_up in scaled_rows:
        contours, _ = cv2.findContours(mask_up, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(overlay, contours, -1, _STRUCTURE_COLOR, 3, cv2.LINE_AA)
        ys, xs = np.where(mask_up)
        if len(xs):
            _draw_label_chip(overlay, element_name, (int(xs.min()), max(int(ys.min()) - 10, 20)), _STRUCTURE_COLOR)

        for damage_type, dmask_up, color in damages_up:
            contours, _ = cv2.findContours(dmask_up, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, color, 2, cv2.LINE_AA)
            ys, xs = np.where(dmask_up)
            if len(xs):
                _draw_label_chip(overlay, damage_type, (int(xs.min()), max(int(ys.min()) - 10, 20)), color)

    legend_items = [("structure", _STRUCTURE_COLOR)] + [
        (name, _OVERLAY_COLORS[name]) for name in _OVERLAY_COLORS if name in classes_present
    ]
    legend_font_scale = 0.65
    pad, row_h, swatch_w = 10, 30, 30
    max_text_w = max(
        cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX, legend_font_scale, 1)[0][0]
        for name, _ in legend_items
    )
    box_w = pad + swatch_w + 10 + max_text_w + pad
    box_h = row_h * len(legend_items) + pad
    lx, ly = 12, 12
    cv2.rectangle(overlay, (lx, ly), (lx + box_w, ly + box_h), _SURFACE, -1)
    cv2.rectangle(overlay, (lx, ly), (lx + box_w, ly + box_h), _INK, 1, cv2.LINE_AA)
    for i, (name, color) in enumerate(legend_items):
        y = ly + pad + row_h * i + row_h // 2
        cv2.line(overlay, (lx + pad, y), (lx + pad + swatch_w, y), color, 5, cv2.LINE_AA)
        cv2.putText(overlay, name, (lx + pad + swatch_w + 10, y + 5), cv2.FONT_HERSHEY_SIMPLEX, legend_font_scale,
                    _INK, 1, cv2.LINE_AA)

    cv2.imwrite(str(out_path), overlay)


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
    test_conf = float(sys.argv[2]) if len(sys.argv) > 2 else CONF_THRESHOLD

    model = YOLO(MODEL_PATH)
    damage_model = YOLO(SENIOR_MODEL_PATH)
    report = analyze_image(model, damage_model, image_path, conf=test_conf)

    print(f"ภาพ: {image_path}")
    print(f"โมเดลโครงสร้าง: {MODEL_PATH}")
    print(f"โมเดลความเสียหาย: {SENIOR_MODEL_PATH} (conf={test_conf})\n")
    print_report(report)
