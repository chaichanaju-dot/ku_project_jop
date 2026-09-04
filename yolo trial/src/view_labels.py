# วาดกรอบ OBB จากไฟล์ label ดิบ (ground truth ที่ label ไว้จริง ไม่ใช่ผลจากโมเดล) ทาบภาพ
# ให้ดูว่ารุ่นพี่ label แต่ละภาพไว้ยังไง
#   python src/view_labels.py                 ทำทุกภาพในโฟลเดอร์ dataset ของรุ่นพี่
#   python src/view_labels.py <ชื่อไฟล์ภาพ>    ทำเฉพาะภาพเดียว

import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

from vision import SENIOR_MODEL_PATH

DATASET_DIR = Path(r"C:\ku_project_jop\rawdata\งานของรุ่นพี่\dataset")
IMAGES_DIR = DATASET_DIR / "images"
LABELS_DIR = DATASET_DIR / "labels"
OUT_DIR = DATASET_DIR / "gt_overlays"


def _color_for(name: str) -> tuple[int, int, int]:
    h = abs(hash(name))
    return (h % 200 + 30, (h // 7) % 200 + 30, (h // 37) % 200 + 30)


def _draw_label_chip(canvas: np.ndarray, text: str, origin: tuple[int, int], color: tuple[int, int, int]) -> None:
    x, y = origin
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(canvas, (x - 4, y - th - 6), (x + tw + 4, y + baseline + 2), color, -1)
    cv2.putText(canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)


def draw_ground_truth(image_path: Path, label_path: Path, names: dict[int, str], out_path: Path) -> None:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f"เปิดภาพไม่ได้: {image_path}")
    if not label_path.exists():
        raise FileNotFoundError(f"ไม่มีไฟล์ label คู่กับภาพนี้: {label_path}")
    h, w = image.shape[:2]

    for line in label_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        values = line.split()
        cls_idx = int(values[0])
        pts = np.array(values[1:], dtype=np.float64).reshape(-1, 2)
        pts[:, 0] *= w
        pts[:, 1] *= h
        pts = pts.astype(np.int32)

        class_name = names.get(cls_idx, f"class{cls_idx}")
        color = _color_for(class_name)
        cv2.polylines(image, [pts], isClosed=True, color=color, thickness=2, lineType=cv2.LINE_AA)
        x0, y0 = pts.min(axis=0)
        _draw_label_chip(image, class_name, (int(x0), max(int(y0) - 10, 20)), color)

    cv2.imwrite(str(out_path), image)


def process_one(image_path: Path, names: dict[int, str], out_dir: Path) -> Path:
    label_path = LABELS_DIR / f"{image_path.stem}.txt"
    out_path = out_dir / f"{image_path.stem}_gt_overlay.png"
    draw_ground_truth(image_path, label_path, names, out_path)
    return out_path


def process_all(names: dict[int, str]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    images = sorted(IMAGES_DIR.iterdir())
    ok, skipped = 0, 0
    for i, image_path in enumerate(images, 1):
        try:
            process_one(image_path, names, OUT_DIR)
            ok += 1
        except FileNotFoundError as e:
            skipped += 1
            print(f"[ข้าม] {e}")
        if i % 100 == 0 or i == len(images):
            print(f"...{i}/{len(images)}")

    print(f"\nเสร็จแล้ว: {ok} ภาพ, ข้าม {skipped} ภาพ")
    print(f"ผลลัพธ์ทั้งหมดอยู่ที่: {OUT_DIR}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    names = YOLO(SENIOR_MODEL_PATH).names

    if arg is None:
        process_all(names)
    else:
        image_path = Path(arg)
        if not image_path.is_absolute() and not image_path.exists():
            image_path = IMAGES_DIR / image_path.name
        out_path = process_one(image_path, names, IMAGES_DIR)
        print(f"ภาพ: {image_path}")
        print(f"เซฟผลไว้ที่: {out_path}")
