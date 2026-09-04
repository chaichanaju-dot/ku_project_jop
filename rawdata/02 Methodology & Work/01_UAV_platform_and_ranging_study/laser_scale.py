"""laser_scale.py — หามาตราส่วน mm/pixel จากจุดเลเซอร์ 4 จุด แล้ววัดความกว้างรอยแตก
เหมือน crack_scale.py (ArUco) ทุกประการ ต่างแค่แหล่ง scale reference:
4 จุดเลเซอร์ (สี+ความสว่าง) แทนมุม marker พิมพ์กระดาษ

ข้อกำหนดฮาร์ดแวร์ที่ทำให้วิธีนี้ใช้ได้: เลเซอร์ 4 ตัวต้องยิง "ขนานกัน"
(ไม่ใช่ลู่เข้า/บานออกแบบ laser rangefinder) ระยะจริงระหว่างจุดบนผิวจึงคงที่
ทุกระยะห่างจากผิว ไม่ต้องรู้ระยะ/focal length/calibration เหมือน ArUco

รันไฟล์นี้ตรง ๆ (python laser_scale.py) จะรัน self-check ด้วยภาพสังเคราะห์
ทดสอบกับ OpenCV 4.10.0 / numpy 2.3.5 / Python 3.13
"""
import cv2
import numpy as np

from crack_scale import crack_width_mm  # ความกว้างรอยแตกเป็น mask ไม่ผูกกับ ArUco เลย ใช้ร่วมกันได้ตรงๆ

DOT_SPACING_MM = 200.0  # ระยะจริงระหว่างจุดเลเซอร์ (วัดตอนประกอบ rig ด้วยเวอร์เนีย ไม่ใช่ค่าที่ตั้งใจ)
HSV_LO = (35, 80, 200)  # ช่วงสี HSV ของจุดเลเซอร์ — ค่าเริ่มต้น = เขียวสว่างจัด ปรับตามเลเซอร์จริงที่ใช้
HSV_HI = (85, 255, 255)
MIN_DOT_AREA_PX = 4  # blob เล็กกว่านี้ถือเป็นสัญญาณรบกวน ตัดทิ้ง


def _order_points(pts):
    """เรียง 4 จุดใดๆ ให้เป็น TL,TR,BR,BL ไม่สนตำแหน่งเริ่มต้น/การหมุน
    (sum เล็กสุด=TL, sum ใหญ่สุด=BR, y-x เล็กสุด=TR, y-x ใหญ่สุด=BL)"""
    s = pts.sum(axis=1)
    d = np.diff(pts, axis=1).ravel()
    return np.array([pts[np.argmin(s)], pts[np.argmin(d)],
                      pts[np.argmax(s)], pts[np.argmax(d)]], dtype=np.float32)


def find_laser_dots(img, hsv_lo=HSV_LO, hsv_hi=HSV_HI, min_area=MIN_DOT_AREA_PX):
    """คืน 4 จุดเลเซอร์ (เรียง TL,TR,BR,BL) หรือ None ถ้าหาไม่ครบ 4 จุด
    ตัด blob เล็กกว่า min_area ทิ้งก่อน แล้วเอา 4 blob ที่ใหญ่สุดที่เหลือ"""
    mask = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), hsv_lo, hsv_hi)
    n, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
    areas = stats[1:, cv2.CC_STAT_AREA]
    pts = centroids[1:][areas >= min_area]
    areas = areas[areas >= min_area]
    if len(pts) < 4:
        return None
    top4 = pts[np.argsort(-areas)[:4]]
    return _order_points(top4.astype(np.float32))


def scale_mm_per_px(img, dot_spacing_mm=DOT_SPACING_MM, hsv_lo=HSV_LO, hsv_hi=HSV_HI):
    """มาตราส่วนเฉลี่ยจากด้านทั้ง 4 ของสี่เหลี่ยมจุดเลเซอร์
    ใช้ได้เมื่อกล้องเกือบตั้งฉากกับผิว (เอียงไม่เกิน ~15 องศา) — เหมือน crack_scale.scale_mm_per_px"""
    c = find_laser_dots(img, hsv_lo, hsv_hi)
    if c is None:
        return None
    side = np.mean([np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)])
    return dot_spacing_mm / side


def rectify(img, dot_spacing_mm=DOT_SPACING_MM, px_per_mm=2.0, margin_mm=20.0,
            hsv_lo=HSV_LO, hsv_hi=HSV_HI):
    """แก้ภาพเอียงให้กลับเป็นระนาบตรง (fronto-parallel) โดยใช้ 4 จุดเลเซอร์แทนมุม ArUco
    คืน (ภาพที่แก้แล้ว, mm/px ซึ่งคงที่เท่ากันทั้งภาพ) — เหมือน crack_scale.rectify"""
    c = find_laser_dots(img, hsv_lo, hsv_hi)
    if c is None:
        return None, None
    s = dot_spacing_mm * px_per_mm
    m = margin_mm * px_per_mm
    dst = np.float32([[m, m], [m + s, m], [m + s, m + s], [m, m + s]])
    H = cv2.getPerspectiveTransform(c, dst)
    h, w = img.shape[:2]
    out = cv2.warpPerspective(img, H, (w, h), borderValue=(235, 235, 235))
    return out, 1.0 / px_per_mm


# ---------- self-check ด้วยภาพสังเคราะห์ ----------

def _synth(size=900, thickness=6, dot_radius=15, warp=False):
    """4 จุดเลเซอร์เขียว เป็นสี่เหลี่ยม 400x400 px (=200 mm ที่ 2 px/mm) + เส้น 'รอยแตก' หนึ่งเส้น"""
    img = np.full((size, size, 3), 235, np.uint8)
    for x, y in [(100, 100), (500, 100), (500, 500), (100, 500)]:
        cv2.circle(img, (x, y), dot_radius, (0, 255, 0), -1)  # BGR เขียว
    cv2.line(img, (660, 60), (660, 860), (40, 40, 40), thickness)
    if warp:
        src = np.float32([[0, 0], [size, 0], [size, size], [0, size]])
        dst = np.float32([[70, 40], [size - 25, 0], [size - 80, size - 30], [15, size - 70]])
        img = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (size, size),
                                  borderValue=(235, 235, 235))
    return img


def _crack_mask(img):
    """threshold หารอยแตก (มืด) — จุดเลเซอร์เขียวสว่างไม่ติด threshold นี้อยู่แล้ว ไม่ต้อง exclude เพิ่ม"""
    return cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 0, 80)


if __name__ == "__main__":
    flat = _synth()

    # ground truth: นับพิกเซลจริงที่ถูกวาด ไม่ใช่เชื่อค่า thickness ที่สั่ง
    gt_px = int((_crack_mask(flat)[450] > 0).sum())
    gt_mm = gt_px * 0.5

    s = scale_mm_per_px(flat)
    print(f"[1] มาตราส่วน ภาพตั้งฉาก : {s:.4f} mm/px   (จริง 0.5000)")
    assert abs(s - 0.5) < 0.005, s

    w = crack_width_mm(_crack_mask(flat), s)
    print(f"[2] ความกว้างรอยแตก      : {w:.2f} mm      (จริง {gt_mm:.2f} mm = {gt_px} px)")
    assert abs(w - gt_mm) < 0.1, (w, gt_mm)

    # ภาพเอียง: ค่าเฉลี่ย 4 ด้านเริ่มเพี้ยน แต่ rectify แล้วต้องกลับมาถูก
    tilted = _synth(warp=True)
    s_naive = scale_mm_per_px(tilted)
    err = abs(s_naive - 0.5) / 0.5 * 100
    print(f"[3] มาตราส่วน ภาพเอียง   : {s_naive:.4f} mm/px -> คลาดเคลื่อน {err:.1f}%")

    rect, s_rect = rectify(tilted)
    w2 = crack_width_mm(_crack_mask(rect), s_rect)
    print(f"[4] หลัง rectify         : {s_rect:.4f} mm/px, ความกว้าง {w2:.2f} mm (จริง {gt_mm:.2f} mm)")
    assert abs(w2 - gt_mm) < 0.6, (w2, gt_mm)

    print("OK — ผ่านทุกข้อ")
