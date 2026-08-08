"""
main.py - photo in, T-BHI out.

Wires the whole pipeline together:
  vision.analyze_image()   photo -> structural elements + damage instances,
                            each damage instance already rated 0-5 by
                            damage_rules.rate_damage() (see vision.py)
  _level_map()              per structural element: paint a per-pixel
                             condition-level canvas. A pixel with no damage
                             on it defaults to level 5 (healthy); a pixel
                             covered by more than one damage instance takes
                             the worst (lowest) level, per AASHTO's
                             Multi-Path Distress principle (guide section 2.3)
  _proportions()             per-pixel levels -> {level: fraction of the
                             element's area}, the "y_ei" input EHI needs
  element_lookup.py          element name -> W (weight), is_primary
  bridge_health.Element       packs q / W / is_primary / proportions
  bridge_health.calculate_tbhi()   elements -> (T-BHI, status)
"""

import sys

import numpy as np
from ultralytics import YOLO

from vision import analyze_image, MODEL_PATH
from element_lookup import ELEMENT_WEIGHT, ELEMENT_IS_PRIMARY
from bridge_health import Element, calculate_tbhi


def _level_map(element_mask: np.ndarray, damages: list[tuple]) -> np.ndarray:
    """Per-pixel condition level (0-5) for one structural element."""
    levels = np.full(element_mask.shape, 5, dtype=np.int8)
    for _damage_type, mask, rating in damages:
        levels[mask] = np.minimum(levels[mask], rating.level)
    return levels


def _proportions(element_mask: np.ndarray, levels: np.ndarray) -> dict[int, float]:
    """Fraction of the element's own area at each level 0-5, summing to 1.0."""
    total = int(element_mask.sum())
    proportions = {}
    for level in range(6):
        count = int(np.count_nonzero((levels == level) & element_mask))
        if count:
            proportions[level] = count / total
    return proportions


def build_elements(report: list[dict]) -> list[Element]:
    """vision.analyze_image()'s report -> bridge_health.Element list."""
    elements = []
    counts = {}
    for row in report:
        name = row["element"]
        counts[name] = counts.get(name, 0) + 1

        levels = _level_map(row["mask"], row["damages"])
        proportions = _proportions(row["mask"], levels)

        elements.append(Element(
            name=f"{name}_{counts[name]}",
            q=row["q"],
            W=ELEMENT_WEIGHT[name],
            is_primary=ELEMENT_IS_PRIMARY[name],
            proportions=proportions,
        ))
    return elements


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else (
        "train/images/image_0001431_jpg.rf.4aad1bc1d6feb6de3f5953a1ec74cfda.jpg"
    )
    # See vision.py's note: this checkpoint is badly undertrained, so a very
    # low conf is needed just to get any detections out of it at all.
    conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.01

    model = YOLO(MODEL_PATH)
    report = analyze_image(model, image_path, conf=conf)

    print(f"ภาพ: {image_path}\n")

    if not report:
        print("ไม่พบชิ้นส่วนโครงสร้างในภาพนี้ - คำนวณ T-BHI ไม่ได้")
        sys.exit(1)

    elements = build_elements(report)

    print(f"{'ชิ้นส่วน':<14}{'q':>8}{'W':>5}{'primary':>9}{'EHI':>10}  proportions")
    for e in elements:
        print(f"{e.name:<14}{e.q:>8}{e.W:>5}{str(e.is_primary):>9}{e.ehi:>10.2f}  "
              f"{ {k: round(v, 3) for k, v in sorted(e.proportions.items())} }")

    tbhi, status = calculate_tbhi(elements)
    print(f"\nT-BHI = {tbhi:.2f}")
    print(f"สถานะ = {status}")
