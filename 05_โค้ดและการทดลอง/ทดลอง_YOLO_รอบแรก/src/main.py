# photo in, T-BHI out. Wires together vision.analyze_image() (photo -> elements + rated
# damage), the per-pixel condition-level map, element_lookup.py's W/is_primary tables, and
# bridge_health.calculate_tbhi().

import os
import sys

import numpy as np
from ultralytics import YOLO

from vision import analyze_image, save_overlay, print_report, MODEL_PATH, SENIOR_MODEL_PATH
from element_lookup import ELEMENT_WEIGHT, ELEMENT_IS_PRIMARY
from bridge_health import Element, calculate_tbhi, band_status, mandatory_floor, C_HI

# "deck" has no trained class yet, so it's excluded here - requiring it would make
# T-BHI un-computable forever (see vision.py's STRUCTURAL_CLASSES).
REQUIRED_STRUCTURAL_CLASSES = {"pier", "girder", "pier_cap"}


def _level_map(element_mask: np.ndarray, damages: list[tuple]) -> np.ndarray:
    """Per-pixel condition level (0-5) for one structural element - a pixel with no
    damage defaults to 5 (healthy); a pixel under multiple damages takes the worst."""
    levels = np.full(element_mask.shape, 5, dtype=np.int8)
    for _damage_type, mask, rating in damages:
        levels[mask] = np.minimum(levels[mask], rating.level)
    return levels


def _proportions(element_mask: np.ndarray, levels: np.ndarray) -> dict[int, float]:
    total = int(element_mask.sum())
    proportions = {}
    for level in range(6):
        count = int(np.count_nonzero((levels == level) & element_mask))
        if count:
            proportions[level] = count / total
    return proportions


def _row_proportions(row: dict) -> tuple[int, dict[int, float]]:
    levels = _level_map(row["mask"], row["damages"])
    return row["q"], _proportions(row["mask"], levels)


def build_elements(report: list[dict]) -> list[Element]:
    elements = []
    counts = {}
    for row in report:
        name = row["element"]
        counts[name] = counts.get(name, 0) + 1
        q, proportions = _row_proportions(row)
        elements.append(Element(
            name=f"{name}_{counts[name]}",
            q=q,
            W=ELEMENT_WEIGHT[name],
            is_primary=ELEMENT_IS_PRIMARY[name],
            proportions=proportions,
        ))
    return elements


def merge_proportions(qs: list[int], proportions_list: list[dict[int, float]]) -> dict[int, float]:
    """q-weighted mean of several photos' proportions for the SAME physical element, so
    seeing it from more angles doesn't inflate its apparent size."""
    total_q = sum(qs)
    merged: dict[int, float] = {}
    for q, proportions in zip(qs, proportions_list):
        for level, frac in proportions.items():
            merged[level] = merged.get(level, 0.0) + q * frac
    return {level: value / total_q for level, value in merged.items()}


def merge_element_group(class_name: str, label: str, rows: list[dict]) -> Element:
    """Combine several photos' detections of ONE physical element into a single Element.
    q uses the LARGEST single view (not the sum), so N angles of one pier don't count
    as N piers' worth of area."""
    qs, proportions_list = [], []
    for row in rows:
        q, proportions = _row_proportions(row)
        qs.append(q)
        proportions_list.append(proportions)

    return Element(
        name=f"{class_name}_{label}",
        q=max(qs),
        W=ELEMENT_WEIGHT[class_name],
        is_primary=ELEMENT_IS_PRIMARY[class_name],
        proportions=merge_proportions(qs, proportions_list),
    )


def print_element_summary(e: Element) -> None:
    print(f"\n=== {e.name} (q={e.q} [max ของทุกมุม], W={e.W}, primary={e.is_primary}) รวมจากหลายมุม ===")
    for level in sorted(e.proportions, reverse=True):
        print(f"  ระดับ {level} (C_hi={C_HI[level]:.2f}): {e.proportions[level]:.3f}")
    print(f"  EHI = {e.ehi:.2f}")


def print_detailed_report(report: list[dict], elements: list[Element], compute_tbhi: bool = True) -> None:
    """compute_tbhi=False skips the T-BHI section - `elements` here covers only ONE
    photo, and printing a T-BHI for it would imply that photo is the whole bridge."""
    for row, e in zip(report, elements):
        print(f"\n=== {e.name} (W={e.W}, primary={e.is_primary}) ===")
        print(f"q (พื้นที่ทั้งหมด) = {row['q']} px")

        if not row["damages"]:
            print("ความเสียหายที่พบ: (ไม่พบ)")
        else:
            print("ความเสียหายที่พบ:")
            for damage_type, mask, rating in row["damages"]:
                print(f"  - {damage_type:<20} {int(mask.sum()):>7} px "
                      f"-> ระดับ {rating.level} (C_hi={C_HI[rating.level]:.2f}, "
                      f"confidence={rating.confidence})")

        print("สัดส่วนพื้นที่ต่อระดับ (proportions):")
        terms = []
        for level in sorted(e.proportions, reverse=True):
            frac = e.proportions[level]
            px = round(frac * e.q)
            print(f"  ระดับ {level} (C_hi={C_HI[level]:.2f}): {frac:.3f}  (~{px} px)")
            terms.append(f"{C_HI[level]:.2f}*{frac:.3f}")

        print(f"EHI = ({' + '.join(terms)}) * 100 = {e.ehi:.2f}")

    if not compute_tbhi:
        missing = sorted(REQUIRED_STRUCTURAL_CLASSES - {row["element"] for row in report})
        print("\n=== คำนวณ T-BHI รวม ===")
        print(f"ข้ามการคำนวณ T-BHI: ภาพนี้ยังไม่พบชิ้นส่วนครบ (ขาด: {', '.join(missing)}) "
              f"- แสดงเฉพาะข้อมูลการตรวจจับด้านบนเท่านั้น")
        return

    print("\n=== คำนวณ T-BHI รวม ===")
    numerator_terms = [f"{e.q}*{e.W}*{e.ehi:.2f}" for e in elements]
    denominator_terms = [f"{e.q}*{e.W}" for e in elements]
    numerator = sum(e.q * e.W * e.ehi for e in elements)
    denominator = sum(e.q * e.W for e in elements)
    print(f"T-BHI = ({' + '.join(numerator_terms)})")
    print(f"      / ({' + '.join(denominator_terms)})")
    print(f"      = {numerator:.1f} / {denominator} = {numerator / denominator:.2f}")

    tbhi, final_status = calculate_tbhi(elements)
    print(f"\nสถานะจากคะแนน (ก่อนกฎบังคับ) = {band_status(tbhi)}")
    print(f"กฎบังคับจากชิ้นส่วนหลัก (Primary) = {mandatory_floor(elements) or '(ไม่มี)'}")
    print(f"สถานะสุดท้าย = {final_status}")


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def _list_images(folder: str) -> list[str]:
    names = sorted(os.listdir(folder))
    return [
        os.path.join(folder, name) for name in names
        if os.path.splitext(name)[1].lower() in IMAGE_EXTENSIONS
    ]


def process_image(model: YOLO, damage_model: YOLO, image_path: str, conf: float) -> tuple[list[Element], set[str]]:
    """Run the pipeline on one photo. Returns (elements, structural classes found),
    both empty if nothing structural was found."""
    report = analyze_image(model, damage_model, image_path, conf=conf)

    print(f"\nภาพ: {image_path}")

    if not report:
        print("ไม่พบชิ้นส่วนโครงสร้างในภาพนี้ - ข้ามภาพนี้ไป")
        return [], set()

    classes_present = {row["element"] for row in report}
    elements = build_elements(report)
    print_detailed_report(report, elements, compute_tbhi=REQUIRED_STRUCTURAL_CLASSES <= classes_present)

    base = os.path.splitext(os.path.basename(image_path))[0]
    overlay_path = f"{base}_overlay.png"
    save_overlay(image_path, report, overlay_path)
    print(f"\nภาพผลตรวจจับ: {overlay_path}")

    return elements, classes_present


def process_element_group_folder(model: YOLO, damage_model: YOLO, folder: str, conf: float) -> tuple[list[Element], set[str]]:
    """One folder = several photos of the SAME physical element(s) (e.g. multiple
    angles of one pier). Every photo is analyzed and gets its own overlay, but
    detections are merged into one Element per class (merge_element_group) so
    N angles of one pier contribute ONE pier, not N."""
    label = os.path.basename(os.path.normpath(folder))
    rows_by_class: dict[str, list[dict]] = {}

    for image_path in _list_images(folder):
        report = analyze_image(model, damage_model, image_path, conf=conf)
        print(f"\nภาพ: {image_path}")

        if not report:
            print("ไม่พบชิ้นส่วนโครงสร้างในภาพนี้ - ข้ามภาพนี้ไป")
            continue

        print_report(report)

        base = os.path.splitext(os.path.basename(image_path))[0]
        overlay_path = os.path.join(folder, f"{base}_overlay.png")
        save_overlay(image_path, report, overlay_path)
        print(f"ภาพผลตรวจจับ: {overlay_path}")

        for row in report:
            rows_by_class.setdefault(row["element"], []).append(row)

    elements = [merge_element_group(name, label, rows) for name, rows in rows_by_class.items()]
    for e in elements:
        print_element_summary(e)
    return elements, set(rows_by_class.keys())


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else (
        "train/images/image_0001431_jpg.rf.4aad1bc1d6feb6de3f5953a1ec74cfda.jpg"
    )
    conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.25

    model = YOLO(MODEL_PATH)
    damage_model = YOLO(SENIOR_MODEL_PATH)

    # Every element instance goes into one combined list - T-BHI is computed once
    # for the whole bridge, since a single photo often can't cover the whole thing.
    all_elements: list[Element] = []
    all_classes_found: set[str] = set()
    is_single_file = os.path.isfile(input_path)

    if is_single_file:
        elements, classes = process_image(model, damage_model, input_path, conf)
        all_elements.extend(elements)
        all_classes_found |= classes

    elif os.path.isdir(input_path):
        entries = sorted(os.listdir(input_path))
        subfolders = [
            os.path.join(input_path, name) for name in entries
            if os.path.isdir(os.path.join(input_path, name))
        ]
        loose_images = _list_images(input_path)

        if not subfolders and not loose_images:
            print(f"ไม่พบไฟล์ภาพหรือโฟลเดอร์ย่อยใน {input_path}")
            sys.exit(1)

        # Loose images directly inside input_path: each is assumed to show a
        # DIFFERENT part of the bridge, so no merging across these.
        for image_path in loose_images:
            elements, classes = process_image(model, damage_model, image_path, conf)
            all_elements.extend(elements)
            all_classes_found |= classes

        # Subfolders: each is a group of photos of the SAME physical element
        # (e.g. "เสา1/"), merged into one Element per class.
        for folder in subfolders:
            print(f"\n### กลุ่มภาพ: {folder} (รวมเป็นชิ้นส่วนเดียวกัน) ###")
            elements, classes = process_element_group_folder(model, damage_model, folder, conf)
            all_elements.extend(elements)
            all_classes_found |= classes

    else:
        print(f"ไม่พบไฟล์หรือโฟลเดอร์ {input_path}")
        sys.exit(1)

    if not all_elements:
        print("\nไม่พบชิ้นส่วนโครงสร้างเลย - คำนวณ T-BHI ไม่ได้")
        sys.exit(1)

    missing_classes = sorted(REQUIRED_STRUCTURAL_CLASSES - all_classes_found)

    # A lone image can't represent "the whole bridge" if it's missing a structural
    # class, so stop here rather than computing a misleading T-BHI.
    if is_single_file and missing_classes:
        print(f"\n=== สรุปรวมทั้งหมด ({len(all_elements)} ชิ้นส่วน) ===")
        print(f"ข้ามการคำนวณ T-BHI รวม: ภาพเดียวที่ให้มายังไม่มีชิ้นส่วนครบ (ขาด: {', '.join(missing_classes)})")
        print("แสดงเฉพาะข้อมูลการตรวจจับที่พิมพ์ไว้ด้านบนเท่านั้น")
        sys.exit(0)

    print(f"\n=== สรุปรวมทั้งหมด ({len(all_elements)} ชิ้นส่วน) ===")
    tbhi, status = calculate_tbhi(all_elements)
    print(f"\nT-BHI รวม = {tbhi:.2f}")
    print(f"สถานะสุดท้าย = {status}")

    # Folder input: still compute T-BHI even if not every class was found (may be a
    # partial inspection run), but make the caveat explicit.
    if missing_classes:
        print(f"\n[คำเตือน] ยังไม่พบชิ้นส่วนครบทุกประเภท (ขาด: {', '.join(missing_classes)}) "
              f"- ค่า T-BHI นี้อาจไม่ได้แทนสภาพทั้งสะพานจริง")
