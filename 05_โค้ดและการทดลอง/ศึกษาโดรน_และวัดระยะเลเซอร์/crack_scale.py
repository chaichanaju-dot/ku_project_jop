"""crack_scale.py — หามาตราส่วน mm/pixel จาก ArUco marker แล้ววัดความกว้างรอยแตก
ไม่ต้องรู้ระยะ ไม่ต้องรู้ focal length ไม่ต้อง calibrate กล้อง

รันไฟล์นี้ตรง ๆ (python crack_scale.py) จะรัน self-check ด้วยภาพสังเคราะห์
ทดสอบกับ OpenCV 4.13.0 / numpy 2.5.0 / Python 3.13
"""
import cv2
import numpy as np

MARKER_MM = 200.0  # ขนาดจริงของ marker ที่พิมพ์ออกมา — วัดด้วยเวอร์เนีย ไม่ใช่ค่าที่สั่งพิมพ์
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
_detector = cv2.aruco.ArucoDetector(DICT)


def find_marker(img):
    """คืน 4 มุมของ marker ตัวแรกที่เจอ (เรียง TL,TR,BR,BL) หรือ None ถ้าไม่เจอ"""
    corners, ids, _ = _detector.detectMarkers(img)
    return None if ids is None else corners[0][0]


def scale_mm_per_px(img):
    """มาตราส่วนเฉลี่ยจากด้านทั้ง 4 ของ marker
    ใช้ได้เมื่อกล้องเกือบตั้งฉากกับผิว (เอียงไม่เกิน ~15 องศา)"""
    c = find_marker(img)
    if c is None:
        return None
    side = np.mean([np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)])
    return MARKER_MM / side


def rectify(img, px_per_mm=2.0, margin_mm=20.0):
    """แก้ภาพเอียงให้กลับเป็นระนาบตรง (fronto-parallel)
    คืน (ภาพที่แก้แล้ว, mm/px ซึ่งคงที่เท่ากันทั้งภาพ)
    px_per_mm=2.0 -> 0.5 mm/px

    margin_mm: เว้นขอบขาวรอบ marker ในภาพผลลัพธ์ — ห้ามตั้งเป็น 0
    ArUco ต้องมี quiet zone (ขอบขาว) รอบตัว ถ้า warp ให้ marker ชิดขอบภาพพอดี
    จะ detect ไม่เจออีกเลย และโค้ดที่ตัด marker ออกจาก mask จะพลาดทั้งก้อน
    """
    c = find_marker(img)
    if c is None:
        return None, None
    s = MARKER_MM * px_per_mm
    m = margin_mm * px_per_mm
    dst = np.float32([[m, m], [m + s, m], [m + s, m + s], [m, m + s]])
    H = cv2.getPerspectiveTransform(c.astype(np.float32), dst)
    h, w = img.shape[:2]
    # borderValue = สีพื้นกระดาษ ไม่ใช่ดำ — ไม่งั้นขอบดำจะถูกนับเป็น "รอยแตก" ตอน threshold
    out = cv2.warpPerspective(img, H, (w, h), borderValue=(235, 235, 235))
    return out, 1.0 / px_per_mm


def crack_width_px(mask):
    """ความกว้างรอยแตกเป็น pixel จาก binary mask

    distance transform คืน 'ระยะถึงพิกเซลพื้นหลังที่ใกล้ที่สุด' ไม่ใช่ 'ระยะถึงขอบ'
    แถบกว้าง W พิกเซลจะได้ค่าสูงสุด (W+1)/2  =>  W = 2*maxdist - 1
    ถ้าลืมลบ 1 จะได้ความกว้างเกินจริง 1 px เสมอ (ที่ GSD 0.2 mm/px = เกิน 0.2 mm)
    """
    dist = cv2.distanceTransform((mask > 0).astype(np.uint8), cv2.DIST_L2, 5)
    return 2.0 * float(dist.max()) - 1.0


def crack_width_mm(mask, mm_per_px):
    return crack_width_px(mask) * mm_per_px


# ---------- self-check ด้วยภาพสังเคราะห์ ----------

def _synth(size=900, thickness=6, warp=False):
    """marker 400 px (= 200 mm => 0.5 mm/px) + เส้น 'รอยแตก' หนึ่งเส้น"""
    img = np.full((size, size), 235, np.uint8)
    img[100:500, 100:500] = cv2.aruco.generateImageMarker(DICT, 0, 400)
    cv2.line(img, (660, 60), (660, 860), 40, thickness)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    if warp:
        src = np.float32([[0, 0], [size, 0], [size, size], [0, size]])
        dst = np.float32([[70, 40], [size - 25, 0], [size - 80, size - 30], [15, size - 70]])
        img = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (size, size),
                                  borderValue=(235, 235, 235))
    return img


def _crack_mask(img):
    """threshold หารอยแตก แล้วลบบริเวณ marker ออก (marker ก็ดำเหมือนกัน)"""
    m = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 0, 80)
    c = find_marker(img)
    if c is not None:
        x0, y0 = np.floor(c.min(axis=0)).astype(int) - 12
        x1, y1 = np.ceil(c.max(axis=0)).astype(int) + 12
        m[max(y0, 0):y1, max(x0, 0):x1] = 0
    return m


if __name__ == "__main__":
    flat = _synth()

    # ground truth: นับพิกเซลจริงที่ถูกวาด ไม่ใช่เชื่อค่า thickness ที่สั่ง
    # (cv2.line thickness=6 วาดออกมาจริง 7 px — ค่าที่สั่งไม่ใช่ค่าที่ได้)
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
