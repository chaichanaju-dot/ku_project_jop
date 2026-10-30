"""laser_scale.py — หามาตราส่วน mm/pixel จากจุดเลเซอร์ (4 จุดปกติ, ถอยเป็น 3 จุดอัตโนมัติถ้าตัวใดตัวหนึ่งเสีย)
เหมือน crack_scale.py (ArUco) ทุกประการ ต่างแค่แหล่ง scale reference:
จุดเลเซอร์ (สี+ความสว่าง) แทนมุม marker พิมพ์กระดาษ

ข้อกำหนดฮาร์ดแวร์ที่ทำให้วิธีนี้ใช้ได้: เลเซอร์ทุกตัวต้องยิง "ขนานกัน"
(ไม่ใช่ลู่เข้า/บานออกแบบ laser rangefinder) ระยะจริงระหว่างจุดบนผิวจึงคงที่
ทุกระยะห่างจากผิว ไม่ต้องรู้ระยะ/focal length/calibration เหมือน ArUco

โหมด 3 จุด (เลเซอร์เสียไป 1 ตัวจาก 4 — เกิดขึ้นจริง 2026-09-15): มี 2 รูปแบบที่รองรับ
เดาจากมุมของสามเหลี่ยมที่เจอเอง ไม่ต้องบอกโค้ดว่าใช้แบบไหน —
  1) 'right_angle'  — เลเซอร์ 3 ตัวยังอยู่ตำแหน่งเดิมของสี่เหลี่ยมจัตุรัส (แค่ตัวที่ 4 ดับ)
     3 มุมที่เหลือมี "มุมกึ่งกลาง" หนึ่งมุมเป็นมุมฉากเสมอ (เรขาคณิตล้วน) ใช้ 2 ด้านที่ติดมุมนั้น
  2) 'equilateral'  — ย้าย/ตั้งเลเซอร์ 3 ตัวใหม่เป็นรูปสามเหลี่ยมด้านเท่าโดยตรง (2026-09-15:
     ทางเลือกนี้ทนต่อความคลาดเคลื่อนตอนประกอบมากกว่า เพราะไม่ต้องเล็งให้ได้มุมฉากเป๊ะ แค่ 3 ด้าน
     ยาวเท่ากันก็พอ) ใช้ทั้ง 3 ด้านเฉลี่ยกัน
ถ้ามุมที่เจอไม่เข้าเค้าทั้งสองแบบ (คลาดเคลื่อนเกิน ~12°) ถือว่า 'unknown' แล้วคืน None แทนการเดา
ข้อจำกัดที่ตามมา: `rectify()` โหมด 3 จุดใช้ affine transform (แก้ได้แค่ หมุน/เลื่อน/เอียงเฉือน/
สเกลไม่เท่ากันสองแกน) ไม่ใช่ perspective transform เหมือนโหมด 4 จุด — แก้ perspective
(keystone) จากมุมกล้องเอียงจริงไม่ได้ แม่นยำพอเฉพาะกล้องเกือบตั้งฉากกับผิว (ไม่เกิน ~15 องศา
เหมือนเดิม) มุมที่เอียงมากกว่านี้ scale จะยังคลาดเคลื่อนอยู่บ้างแม้ rectify แล้ว

รันไฟล์นี้ตรง ๆ (python laser_scale.py) จะรัน self-check ด้วยภาพสังเคราะห์ ทั้งโหมด 4 จุด, 3 จุด
มุมฉาก, และ 3 จุดด้านเท่า
ทดสอบกับ OpenCV 4.10.0 / numpy 2.3.5 / Python 3.13
"""
import math
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


RIGHT_ANGLE_TOL_DEG = 12.0  # มุมหนึ่งใกล้ 90° ในช่วงนี้ = ตีความเป็นโหมด right_angle
EQUILATERAL_TOL_DEG = 12.0  # ทั้ง 3 มุมใกล้ 60° ในช่วงนี้ = ตีความเป็นโหมด equilateral


def _triangle_angles_deg(pts):
    """คืนมุมภายในที่จุดยอดแต่ละจุด (องศา) เรียงลำดับตรงกับ pts ที่ส่งเข้ามา"""
    angs = []
    for i in range(3):
        p, a, b = pts[i], pts[(i + 1) % 3], pts[(i + 2) % 3]
        va, vb = a - p, b - p
        cosv = np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-9)
        angs.append(math.degrees(math.acos(max(-1.0, min(1.0, cosv)))))
    return angs


def _order_three_points_equilateral(pts):
    """เรียง 3 จุดของสามเหลี่ยมด้านเท่า: จุดบนสุด (y น้อยสุดในภาพ) ก่อน แล้วอีก 2 จุดเรียงให้
    ทิศทวนเข็มนาฬิกาคงที่เสมอ (บังคับด้วยเครื่องหมาย cross product) — ถ้าไม่ทำขั้นนี้ rectify()
    จะสุ่มจับคู่จุดกับมุมปลายทางผิดทิศ ได้ affine ที่หมุน/กลับด้านภาพทั้งใบ (บั๊กเดียวกับที่เจอ
    ตอนแก้โหมด right_angle — ดูคอมเมนต์ใน rectify())"""
    top_i = int(np.argmin(pts[:, 1]))
    top = pts[top_i]
    rest = [pts[i] for i in range(3) if i != top_i]
    v, w = rest[0] - top, rest[1] - top
    if (v[0] * w[1] - v[1] * w[0]) < 0:
        rest = [rest[1], rest[0]]
    return np.array([top, rest[0], rest[1]], dtype=np.float32)


def _classify_three_dots(pts):
    """ตัดสินจากมุมของสามเหลี่ยมว่า 3 จุดที่เจอควรตีความแบบไหน — ไม่ต้องบอกโค้ดว่ารูปแบบไหน
    คืน (mode, ordered_pts): mode ∈ {'right_angle','equilateral','unknown'}
    'right_angle'  -> ordered_pts = (corner, armA, armB)
    'equilateral'  -> ordered_pts = (top, left, right) จาก _order_three_points_equilateral
    'unknown'      -> ordered_pts = pts เดิม (ไม่มีความหมายอะไรเป็นพิเศษ ห้ามใช้คำนวณต่อ)"""
    angs = _triangle_angles_deg(pts)
    i90 = int(np.argmin([abs(a - 90) for a in angs]))
    if abs(angs[i90] - 90) <= RIGHT_ANGLE_TOL_DEG:
        corner = pts[i90]
        a, b = pts[(i90 + 1) % 3], pts[(i90 + 2) % 3]
        return 'right_angle', np.array([corner, a, b], dtype=np.float32)
    if max(abs(a - 60) for a in angs) <= EQUILATERAL_TOL_DEG:
        return 'equilateral', _order_three_points_equilateral(pts)
    return 'unknown', pts


def find_laser_dots(img, hsv_lo=HSV_LO, hsv_hi=HSV_HI, min_area=MIN_DOT_AREA_PX):
    """คืน {'n':4,'pts':(TL,TR,BR,BL)} ถ้าเจอครบ 4 จุด
    หรือ {'n':3,'mode':...,'pts':...} ถ้าเจอแค่ 3 (เลเซอร์เสียไป 1 ตัว — ดู _classify_three_dots)
    หรือ None ถ้าเจอน้อยกว่า 3
    ตัด blob เล็กกว่า min_area ทิ้งก่อน แล้วเอา blob ที่ใหญ่สุดเท่าที่มี (4 หรือ 3)"""
    mask = cv2.inRange(cv2.cvtColor(img, cv2.COLOR_BGR2HSV), hsv_lo, hsv_hi)
    n, _, stats, centroids = cv2.connectedComponentsWithStats(mask)
    areas = stats[1:, cv2.CC_STAT_AREA]
    pts = centroids[1:][areas >= min_area]
    areas = areas[areas >= min_area]
    if len(pts) < 3:
        return None
    if len(pts) >= 4:
        top4 = pts[np.argsort(-areas)[:4]]
        return {'n': 4, 'pts': _order_points(top4.astype(np.float32))}
    top3 = pts[np.argsort(-areas)[:3]].astype(np.float32)
    mode, ordered = _classify_three_dots(top3)
    return {'n': 3, 'mode': mode, 'pts': ordered}


def scale_mm_per_px(img, dot_spacing_mm=DOT_SPACING_MM, hsv_lo=HSV_LO, hsv_hi=HSV_HI):
    """มาตราส่วนเฉลี่ยจากด้านของจุดเลเซอร์ — 4 ด้านถ้าเจอครบ 4 จุด, ถ้าเหลือ 3 ใช้ตามโหมดที่
    _classify_three_dots ตัดสิน (2 ด้านจากมุมฉาก / 3 ด้านของสามเหลี่ยมด้านเท่า)
    คืน None ถ้าเจอ 3 จุดแต่มุมไม่เข้าเค้าทั้งสองแบบ ('unknown') — ไม่เดามาตราส่วนจากเรขาคณิตที่ไม่รู้จัก
    ใช้ได้เมื่อกล้องเกือบตั้งฉากกับผิว (เอียงไม่เกิน ~15 องศา) — เหมือน crack_scale.scale_mm_per_px"""
    found = find_laser_dots(img, hsv_lo, hsv_hi)
    if found is None:
        return None
    if found['n'] == 4:
        c = found['pts']
        side = np.mean([np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)])
    elif found['mode'] == 'right_angle':
        corner, a, b = found['pts']
        side = np.mean([np.linalg.norm(a - corner), np.linalg.norm(b - corner)])
    elif found['mode'] == 'equilateral':
        p0, p1, p2 = found['pts']
        side = np.mean([np.linalg.norm(p1 - p0), np.linalg.norm(p2 - p1), np.linalg.norm(p0 - p2)])
    else:
        return None
    return dot_spacing_mm / side


def rectify(img, dot_spacing_mm=DOT_SPACING_MM, px_per_mm=2.0, margin_mm=20.0,
            hsv_lo=HSV_LO, hsv_hi=HSV_HI):
    """แก้ภาพเอียงให้กลับเป็นระนาบตรง (fronto-parallel) โดยใช้จุดเลเซอร์แทนมุม ArUco
    4 จุด -> perspective transform (แก้ keystone ได้เต็มที่); 3 จุด -> affine transform
    (แก้ไม่ได้เฉพาะ perspective/keystone จริง ๆ — ดู caveat ที่หัวไฟล์)
    คืน (ภาพที่แก้แล้ว, mm/px ซึ่งคงที่เท่ากันทั้งภาพ) — เหมือน crack_scale.rectify"""
    found = find_laser_dots(img, hsv_lo, hsv_hi)
    if found is None:
        return None, None
    s = dot_spacing_mm * px_per_mm
    m = margin_mm * px_per_mm
    h, w = img.shape[:2]
    if found['n'] == 4:
        c = found['pts']
        dst = np.float32([[m, m], [m + s, m], [m + s, m + s], [m, m + s]])
        H = cv2.getPerspectiveTransform(c, dst)
        out = cv2.warpPerspective(img, H, (w, h), borderValue=(235, 235, 235))
    elif found['mode'] == 'right_angle':
        corner, p, q = found['pts']
        # (armA,armB) ไม่มีความหมายเรื่องซ้าย/ขวา-บน/ล่าง — ถ้าตั้งปลายทางแบบตายตัว
        # (armA=+x เสมอ, armB=+y เสมอ) affine ที่ fit ได้จะหมุนภาพทั้งใบไป 90/180/270 องศา
        # แบบสุ่ม (ขึ้นกับว่ามุมไหนรอด) ซึ่งพังทั้งการดูภาพด้วยตาและการสแกนหารอยแตกที่กำกับ
        # ทิศไว้ล่วงหน้า จึงต้องดูทิศทางจริงในภาพ แล้ววางปลายทางให้ซ้าย/ขวา-บน/ล่างตรงของเดิม
        # (rectify แก้แค่มุมเอียงเล็กน้อยของกล้อง ไม่ใช่หมุนภาพใหม่)
        vp, vq = p - corner, q - corner
        x_arm, y_arm = (p, q) if abs(vp[0]) >= abs(vq[0]) else (q, p)
        sx = 1.0 if (x_arm[0] - corner[0]) >= 0 else -1.0
        sy = 1.0 if (y_arm[1] - corner[1]) >= 0 else -1.0
        cx, cy = (m if sx > 0 else m + s), (m if sy > 0 else m + s)
        src = np.float32([corner, x_arm, y_arm])
        dst = np.float32([[cx, cy], [cx + sx * s, cy], [cx, cy + sy * s]])
        H = cv2.getAffineTransform(src, dst)
        out = cv2.warpAffine(img, H, (w, h), borderValue=(235, 235, 235))
    elif found['mode'] == 'equilateral':
        top, p, q = found['pts']
        # ปลายทาง = สามเหลี่ยมด้านเท่าหัวชี้ขึ้นจริง ๆ (จุดยอดบนตรงกลาง, อีก 2 จุดล่างซ้าย-ขวา)
        # จับคู่ "จุดที่อยู่บนสุดในภาพจริง" กับ "จุดยอดบนของสามเหลี่ยมปลายทาง" (เหมือนโหมด right_angle)
        # (p,q) มาจาก _order_three_points_equilateral ที่บังคับ cross(p-top,q-top)>=0 เสมอ —
        # ปลายทางต้องมี cross เดียวกัน (ทดสอบแล้วคือ p->จุดขวา, q->จุดซ้าย) ไม่งั้น affine ที่ fit
        # ได้จะกลับด้านภาพ (บั๊กเดียวกับโหมด right_angle ตอนแรก — เจอจาก self-check ตรงนี้เอง)
        h_tri = s * math.sqrt(3) / 2
        src = np.float32([top, p, q])
        dst = np.float32([[m + s / 2, m], [m + s, m + h_tri], [m, m + h_tri]])
        H = cv2.getAffineTransform(src, dst)
        out = cv2.warpAffine(img, H, (w, h), borderValue=(235, 235, 235))
    else:
        return None, None
    return out, 1.0 / px_per_mm


# ---------- self-check ด้วยภาพสังเคราะห์ ----------

def _synth(size=900, thickness=6, dot_radius=15, warp=False, drop_dot=None):
    """4 จุดเลเซอร์เขียว เป็นสี่เหลี่ยม 400x400 px (=200 mm ที่ 2 px/mm) + เส้น 'รอยแตก' หนึ่งเส้น
    drop_dot=index (0-3) จำลองเลเซอร์ตัวนั้นเสีย เหลือ 3 จุด"""
    img = np.full((size, size, 3), 235, np.uint8)
    dots = [(100, 100), (500, 100), (500, 500), (100, 500)]
    if drop_dot is not None:
        dots = [d for i, d in enumerate(dots) if i != drop_dot]
    for x, y in dots:
        cv2.circle(img, (x, y), dot_radius, (0, 255, 0), -1)  # BGR เขียว
    cv2.line(img, (660, 60), (660, 860), (40, 40, 40), thickness)
    if warp:
        src = np.float32([[0, 0], [size, 0], [size, size], [0, size]])
        dst = np.float32([[70, 40], [size - 25, 0], [size - 80, size - 30], [15, size - 70]])
        img = cv2.warpPerspective(img, cv2.getPerspectiveTransform(src, dst), (size, size),
                                  borderValue=(235, 235, 235))
    return img


def _synth_equilateral(size=900, thickness=6, dot_radius=15, warp=False):
    """3 จุดเลเซอร์เขียว เป็นสามเหลี่ยมด้านเท่า ด้านยาว 400px (=200 mm ที่ 2 px/mm) — เหมือน _synth
    แต่จำลอง rig ที่ตั้งเลเซอร์ 3 ตัวเป็นด้านเท่าโดยตรง (ไม่ใช่เหลือ 3 มุมจากสี่เหลี่ยมเดิม)"""
    img = np.full((size, size, 3), 235, np.uint8)
    for x, y in [(300, 130), (100, 476), (500, 476)]:
        cv2.circle(img, (x, y), dot_radius, (0, 255, 0), -1)
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

    # โหมด 3 จุด (เลเซอร์เสียไป 1 ตัว) — ทำซ้ำ [1]-[4] ด้วยจุดที่ (100,500) หายไป
    flat3 = _synth(drop_dot=3)
    s3 = scale_mm_per_px(flat3)
    print(f"[5] มาตราส่วน 3 จุด ตั้งฉาก : {s3:.4f} mm/px   (จริง 0.5000)")
    assert abs(s3 - 0.5) < 0.005, s3

    w3 = crack_width_mm(_crack_mask(flat3), s3)
    print(f"[6] ความกว้างรอยแตก 3 จุด  : {w3:.2f} mm      (จริง {gt_mm:.2f} mm)")
    assert abs(w3 - gt_mm) < 0.1, (w3, gt_mm)

    tilted3 = _synth(warp=True, drop_dot=3)
    rect3, s_rect3 = rectify(tilted3)
    w4 = crack_width_mm(_crack_mask(rect3), s_rect3)
    print(f"[7] 3 จุด หลัง rectify (affine): {s_rect3:.4f} mm/px, ความกว้าง {w4:.2f} mm (จริง {gt_mm:.2f} mm)")
    assert abs(w4 - gt_mm) < 0.6, (w4, gt_mm)

    # โหมด 3 จุดด้านเท่า (ตั้งเลเซอร์ 3 ตัวใหม่เป็นสามเหลี่ยมด้านเท่า — 2026-09-15)
    flat_eq = _synth_equilateral()
    s_eq = scale_mm_per_px(flat_eq)
    print(f"[8] มาตราส่วน 3 จุดด้านเท่า ตั้งฉาก : {s_eq:.4f} mm/px   (จริง 0.5000)")
    assert abs(s_eq - 0.5) < 0.005, s_eq

    w_eq = crack_width_mm(_crack_mask(flat_eq), s_eq)
    print(f"[9] ความกว้างรอยแตก 3 จุดด้านเท่า  : {w_eq:.2f} mm      (จริง {gt_mm:.2f} mm)")
    assert abs(w_eq - gt_mm) < 0.1, (w_eq, gt_mm)

    tilted_eq = _synth_equilateral(warp=True)
    rect_eq, s_rect_eq = rectify(tilted_eq)
    w_eq2 = crack_width_mm(_crack_mask(rect_eq), s_rect_eq)
    print(f"[10] 3 จุดด้านเท่า หลัง rectify   : {s_rect_eq:.4f} mm/px, ความกว้าง {w_eq2:.2f} mm (จริง {gt_mm:.2f} mm)")
    assert abs(w_eq2 - gt_mm) < 0.6, (w_eq2, gt_mm)

    print("OK — ผ่านทุกข้อ (รวมโหมด 3 จุด มุมฉาก + ด้านเท่า)")
