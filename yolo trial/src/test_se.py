"""
test_se.py - ทดสอบเฉพาะโมเดลรุ่นพี่ (YOLO-OBB damage model) โดยไม่ผ่าน pipeline
T-BHI เต็มรูปแบบ (vision.py/main.py) - ใช้ตอนอยากรู้เร็วๆ ว่าภาพมีความเสียหาย
อะไรบ้าง ก่อนจะรวมเข้ากับโมเดลโครงสร้างของเราเอง

รัน: python src/test_se.py <path_ภาพ_หรือโฟลเดอร์> [conf]
     ไม่ใส่ argument = ใช้ conf default 0.25
     ถ้าเป็นโฟลเดอร์ จะรันทุกภาพในโฟลเดอร์นั้น (ไม่ลงโฟลเดอร์ย่อย)

ผลลัพธ์ (ต่อภาพ):
  1. รายการความเสียหายที่เจอ พิมพ์ใน terminal (class, confidence, กรอบ OBB)
  2. ภาพ overlay เซฟเป็น <ชื่อภาพ>_senior_overlay.png ในโฟลเดอร์เดียวกับภาพ input
"""

import sys
from pathlib import Path

import cv2
import numpy as np
from ultralytics import YOLO

# ตำแหน่งจริงของไฟล์น้ำหนักโมเดลรุ่นพี่บนเครื่องนี้ (bridge_model-2, YOLO-OBB,
# เทรน 942 epoch บน 1042+115 ภาพ, precision=0.91, mAP50-95=0.80 - ดู
# results.csv ในโฟลเดอร์เดียวกัน). วางไว้คนละที่กับโปรเจกต์นี้เพราะเป็นงานรุ่นพี่
# ไม่ได้เทรนเอง จึงอ้าง path ตรงไปที่ต้นฉบับแทนที่จะก็อปปี้ไฟล์ 6.9MB เข้ามาในนี้
SENIOR_MODEL_PATH = r"C:\ku_project_jop\rawdata\งานของรุ่นพี่\weights\best.pt"
CONF_THRESHOLD = 0.25

# BGR (cv2 ใช้ลำดับนี้) - สีต่างกันตาม class ที่โมเดลรุ่นพี่ทายได้ (รวม "strain"
# ที่ยังไม่รู้ความหมายด้วย เพราะสคริปต์นี้แค่โชว์ผลดิบ ไม่ได้ map เป็น damage_type
# ของ damage_rules.py เหมือน vision.py)
_COLORS = {
    "Crack": (72, 73, 227),
    "Spalling": (52, 104, 235),
    "Porous_Defect": (214, 120, 42),
    "Steel_Exposure": (164, 123, 232),
    "Rust_Stained_Exposure": (167, 58, 74),
    "Efflorescence": (0, 161, 237),
    "strain": (128, 128, 128),
}
_INK = (11, 11, 11)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp"}


def _draw_label_chip(canvas: np.ndarray, text: str, origin: tuple[int, int], color: tuple[int, int, int]) -> None:
    x, y = origin
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
    cv2.rectangle(canvas, (x - 4, y - th - 6), (x + tw + 4, y + baseline + 2), color, -1)
    cv2.putText(canvas, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)


def test_image(model: YOLO, image_path: str, conf: float) -> None:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)

    result = model.predict(image, conf=conf, verbose=False)[0]
    overlay = image.copy()

    print(f"\nภาพ: {image_path}")
    print(f"โมเดล: {SENIOR_MODEL_PATH} (conf={conf})\n")

    if result.obb is None or len(result.obb) == 0:
        print("(ไม่พบความเสียหายในภาพนี้)")
    else:
        corners_all = result.obb.xyxyxyxy.cpu().numpy()
        classes = result.obb.cls.cpu().numpy().astype(int)
        confs = result.obb.conf.cpu().numpy()

        print(f"{'class':<24}{'conf':>6}   กรอบ OBB (4 มุม)")
        print("-" * 70)
        for corners, cls_idx, det_conf in zip(corners_all, classes, confs):
            class_name = result.names[int(cls_idx)]
            corners_int = corners.astype(np.int32)
            print(f"{class_name:<24}{det_conf:>6.2f}   {corners_int.tolist()}")

            color = _COLORS.get(class_name, (128, 128, 128))
            cv2.polylines(overlay, [corners_int], isClosed=True, color=color, thickness=2, lineType=cv2.LINE_AA)
            x0, y0 = corners_int.min(axis=0)
            _draw_label_chip(overlay, f"{class_name} {det_conf:.2f}", (int(x0), max(int(y0) - 10, 20)), color)

    out_path = Path(image_path).with_name(f"{Path(image_path).stem}_senior_overlay.png")
    cv2.imwrite(str(out_path), overlay)
    print(f"\nภาพผลตรวจจับ: {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ใช้งาน: python src/test_se.py <path_ภาพ_หรือโฟลเดอร์> [conf]")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    test_conf = float(sys.argv[2]) if len(sys.argv) > 2 else CONF_THRESHOLD

    model = YOLO(SENIOR_MODEL_PATH)

    if input_path.is_dir():
        image_paths = sorted(p for p in input_path.iterdir() if p.suffix.lower() in IMAGE_EXTENSIONS)
        if not image_paths:
            print(f"ไม่พบไฟล์ภาพในโฟลเดอร์ {input_path}")
            sys.exit(1)
        for p in image_paths:
            test_image(model, p, test_conf)
    elif input_path.is_file():
        test_image(model, input_path, test_conf)
    else:
        print(f"ไม่พบไฟล์หรือโฟลเดอร์ {input_path}")
        sys.exit(1)
