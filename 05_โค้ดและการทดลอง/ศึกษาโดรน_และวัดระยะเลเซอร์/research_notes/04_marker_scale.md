# การทำ Scale (mm/pixel) ที่เชื่อถือได้ให้ภาพ UAV สำหรับตรวจรอยแตกคอนกรีต — คู่มือเชิงลึกแบบ fiducial marker

> **สถานะข้อมูล:** ค้นเว็บจริง 20+ query (ส.ค. 2026) — งบ WebSearch หมดกลางทาง จึงมี 4 จุดที่ยัง "ยังไม่ยืนยัน" และระบุไว้ชัดว่าต้องไปดูที่ไหน
> **โค้ดในรายงานนี้รันจริงแล้ว** บน OpenCV 4.13.0 (Windows) พร้อม self-check — ผลอยู่ท้าย §2

---

# §0 สรุปสำหรับตัดสินใจ (อ่านอันเดียวจบ)

| คำถาม | คำตอบสั้น | เหตุผลเชิงตัวเลข |
|---|---|---|
| ใช้ marker แบบไหน | **ArUco `DICT_4X4_50` หรือ AprilTag `tag36h11`** พิมพ์ **10×10 cm** | ที่ระยะ 2 m กล้อง wide ของ M4T marker กิน ~290 px → scale uncertainty ~0.15% |
| ต้องใหญ่แค่ไหน | ด้าน marker ต้องกิน **≥ 30 px** ถึงจะ detect เสถียร แต่ต้อง **≥ 300 px** ถึงจะได้ scale 0.1% | 20 px = ขีดต่ำสุด, 30 px = optimal ([OpenDroneMap Find-GCP](https://opendronemap.org/findgcp/)) |
| calibrate กล้องไหม | **จำเป็น ถ้าใช้ solvePnP หาระยะ / ถ้า marker อยู่ขอบภาพ** — ถ้า marker อยู่กลางภาพและอยู่ระนาบเดียวกับรอยแตก **homography เอาอยู่โดยไม่ต้อง calibrate** | ดู §4 |
| **error ตัวใหญ่ที่สุด** | **มุมเอียง (ถ้าไม่ rectify) และ marker ไม่ร่วมระนาบกับรอยแตก** | เอียง 28.6° → ผิด **6.9%** (วัดจาก self-check §2); marker หนา 50 mm ที่ระยะ 2 m → ผิด **2.5%** |
| จะรู้ระยะโดรน→วัตถุยังไง | **ใช้ marker เอง (solvePnP) ไม่ใช่ laser rangefinder** | laser M4T ที่ 1–3 m มี system error **<0.3 m** = ผิดได้ถึง **15%** ที่ระยะ 2 m ([DJI](https://enterprise.dji.com/matrice-4-series/specs)) |
| บินใกล้ได้แค่ไหน | **1.0 m** (ขีดจำกัด min focus ของเลนส์ wide ไม่ใช่ขีดจำกัดการบิน) | M4T wide focus 1 m–∞, medium tele/tele 3 m–∞ ([DJI](https://enterprise.dji.com/matrice-4-series/specs)) |

**สิ่งที่ต้องทำ 3 อย่างเท่านั้น ถ้าจะเริ่มพรุ่งนี้:**
1. พิมพ์ ArUco 10×10 cm บนกระดาษ matte → **วัดด้านจริงด้วยเวอร์เนียร์** (เครื่องพิมพ์เพี้ยน 4–6% ได้ง่าย ๆ)
2. ติดให้ **แนบและร่วมระนาบ** กับผิวที่มีรอยแตก อย่าติดบนแผ่นหนา อย่าติดคนละหน้าตัด
3. ประมวลผลด้วย `getPerspectiveTransform` + `warpPerspective` **เสมอ** — ห้ามหาร `MARKER_MM / ด้าน_pixel` ตรง ๆ

---

# §1 เปรียบเทียบ marker: อันไหนเหมาะกับคอนกรีตภาคสนาม

## 1.1 ตารางเปรียบเทียบ

| ระบบ | detection rate | เวลา detect | ทนบัง (occlusion) | ให้ scale ได้เอง | จุดตายในภาคสนาม |
|---|---|---|---|---|---|
| **ArUco** (`DICT_4X4_50`) | >90% ถึงมุม 80° | **17 ms** | ต้องเห็น **100%** โดยเฉพาะมุมทั้ง 4 | ✅ (4 มุม + ด้านที่รู้) | เปื้อน/บิ่นที่มุม = หายทั้งตัว |
| **AprilTag** (`tag36h11`) | >90% | ช้ากว่า ArUco | ทนกว่า ArUco ในงาน occlusion | ✅ | ประมวลผลหนักกว่า |
| **STag** | >90% (มี outlier ที่ 80°) | **35 ms** | — | ✅ | σ ของมุมสูงกว่า ArUco/AprilTag มาก |
| **ARTag** | **~45–49%** | — | — | ✅ | **ตกรอบ** — detection rate ต่ำเกินใช้งาน |
| **ChArUco** | สูงที่สุด (มุม chessboard sub-pixel) | ช้าที่สุด | **ทนบางส่วนได้** — จุดแข็งสูงสุด | ✅ แม่นสุด | ต้องใหญ่กว่า marker เดี่ยวมาก |
| **checkerboard** | ต้องเห็นครบทั้งกระดาน | เร็ว | **0%** — บังนิดเดียวพัง | ✅ | ไม่มี ID → สับสนถ้ามีหลายตัว |
| **scale bar / ไม้บรรทัด** | ต้อง detect ด้วยตา/มือ | — | — | ✅ แต่ manual | ไม่ auto, ไม่ให้ pose, ไม่แก้ perspective |

ที่มา: [Kalaitzakis et al., J. Intell. Robot. Syst. 101(4), 2021](https://link.springer.com/article/10.1007/s10846-020-01307-9) (detection rate, มุม 80°, ARTag 45–49%), [Robotics Knowledgebase](https://roboticsknowledgebase.com/wiki/sensing/fiducial-markers/) (17 ms / 35 ms, ArUco ต้องเห็น 100%), [OpenCV ChArUco calibration tutorial](https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html) ("ChArUco corners are much more accurate in comparison to marker corners", "allows occlusions or partial views")

## 1.2 ประเด็นเฉพาะเงื่อนไขภาคสนามบนคอนกรีต

**มุมเอียง (oblique)** — ทั้ง ArUco/AprilTag/STag ยัง >90% ที่มุมสูงถึง **80°** ในการทดลองของ Kalaitzakis ([source](https://link.springer.com/article/10.1007/s10846-020-01307-9)) แต่ **"detect ได้" ≠ "วัดแม่น"** — perspective distortion ลดความแม่นของ pose ([arXiv:2509.17345](https://arxiv.org/abs/2509.17345)) และในการทดลอง AoA ที่ระยะ 2 m error พุ่งชัดที่มุมเฉียงมาก ([arXiv:2506.05195](https://arxiv.org/pdf/2506.05195)). **สรุปเชิงปฏิบัติ: ต้องแก้ perspective ด้วย homography เสมอ ไม่ว่ามุมเท่าไร (ดู §5.4)**

**แสงจ้า/เงา** — ตัวชี้ขาดคือ `adaptiveThreshWinSizeMin/Max/Step` ของ OpenCV (default 3 / 23 / 10) ซึ่งไล่ window size 3→13→23 px. เงาคมพาดกลาง marker ทำให้ threshold ที่ window เล็กแตกเป็นสองก้อน. **ถ้า marker กิน 300 px แต่ window สูงสุดแค่ 23 px จะพัง** → ต้องดัน `adaptiveThreshWinSizeMax` ขึ้นให้สัมพันธ์กับขนาด marker บนภาพ ([DetectorParameters](https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html))

**ผิวเปียก / คอนกรีตสะท้อน** — specular highlight ทำให้ `minOtsuStdDev` (default **5.0**) ไม่ผ่าน → marker ถูกทิ้งในขั้น decode. แก้ที่วัสดุ ไม่ใช่ที่พารามิเตอร์: **ใช้พื้นผิว matte / laminate ด้าน ห้ามใช้ glossy**

**ระยะไกล** — AprilTag `tag25h9` detect ได้ไกลกว่า `tag36h11` ที่ขนาดพิมพ์เท่ากัน เพราะ bit น้อยกว่า → ต้องการ resolution น้อยกว่า **แต่แลกกับ false positive**: `tag36h11` (no error correction) เจอ false positive **0 ครั้ง** ใน LabelMe 266,995 ภาพ ขณะที่ `tag25h9` เจอ **3 ครั้ง** ([AprilTag Identifiers PDF](http://www.aerialroboticscompetition.org/assets/downloads/AprilTag_Identifiers.pdf)). สำหรับงานตรวจสะพานที่ต้องเชื่อถือได้ → **เลือก 36h11 / DICT_4X4 แล้วขยายขนาดพิมพ์แทนการลด bit**

## 1.3 คำแนะนำสำหรับ ku_project_jop

| งาน | เลือก |
|---|---|
| **วัด scale รอยแตกทั่วไป (งานหลัก)** | **ArUco `DICT_4X4_50` 10×10 cm** — เร็วที่สุด, OpenCV รองรับใน core (`objdetect`) ไม่ต้อง dependency นอก, ID พอสำหรับสะพานหนึ่งตัว |
| **มุมมืดใต้สะพาน / marker ถูกบังบางส่วน** | **AprilTag `tag36h11`** |
| **calibrate กล้องโดรน (ทำบนพื้นก่อนบิน)** | **ChArUco** ไม่ใช่ checkerboard — ทนภาพที่กระดานล้นเฟรม ซึ่งเกิดตลอดเวลาเวลาถือกระดานหน้าโดรน |
| **benchmark ถาวรสำหรับ monitoring หลายปี** | **ArUco บนแผ่นอลูมิเนียม + ID ไม่ซ้ำต่อจุด** (ดู §6) |
| **ไม่ควรใช้** | ARTag (detection rate ~45–49%), checkerboard ในภาคสนาม (ไม่มี ID + ไม่ทน occlusion), scale bar เดี่ยว ๆ (ไม่ auto) |

---

# §2 OpenCV API ปัจจุบัน — เขียนให้ถูกกับของใหม่

## 2.1 อะไร deprecated แล้วบ้าง (ยืนยันจาก OpenCV Deprecated List)

| ของเก่า | ของใหม่ที่ต้องใช้ |
|---|---|
| `cv::aruco::estimatePoseSingleMarkers()` | **`cv::solvePnP()`** |
| `cv::aruco::detectMarkers()` (free function) | **`ArucoDetector::detectMarkers()`** |
| `cv::aruco::interpolateCornersCharuco()` | **`CharucoDetector::detectBoard()`** |
| `cv::aruco::calibrateCameraCharuco()` | **`CharucoBoard::matchImagePoints()` + `cv::solvePnP()`** |

ที่มา: [OpenCV Deprecated List](https://docs.opencv.org/4.x/da/d58/deprecated.html) — ข้อความ deprecation ระบุตรง ๆ ว่า "Use cv::solvePnP"

**เวอร์ชัน (ส.ค. 2026):** สาย 4.x ล่าสุด **4.14.0**, และ **OpenCV 5.0** ออกแล้วกลางปี 2026 (ประกาศ ~10 มิ.ย. 2026, ตรงกับ CVPR 2026) — [opencv.org/opencv-5](https://opencv.org/opencv-5/), [CNX Software](https://www.cnx-software.com/2026/06/10/opencv-5-release-new-dnn-engine-with-enhanced-onnx-and-llm-vlm-support-intel-arm-and-risc-v-hardware-optimizations/). โมดูล aruco ย้ายจาก `opencv_contrib` เข้า **`objdetect` ใน core ตั้งแต่ 4.7** — ติดตั้งแค่ `pip install opencv-python` พอ ไม่ต้อง `opencv-contrib-python`
> **ยังไม่ยืนยัน:** วันที่ release ที่ดึงจาก GitHub Releases ขัดแย้งกันเอง (ระบุ 4.14.0 = ก.ค. 2024 ซึ่งไม่สมเหตุผล) → ให้เช็คที่ [github.com/opencv/opencv/releases](https://github.com/opencv/opencv/releases) ตรง ๆ ก่อน pin เวอร์ชันใน `requirements.txt`

## 2.2 กฎเหล็ก 3 ข้อที่คนเขียนผิดบ่อยที่สุด

1. **`cornerRefinementMethod` default = `CORNER_REFINE_NONE`** — ต้องเปิดเอง ไม่งั้นได้มุมความละเอียดระดับ pixel เต็ม ๆ (OpenCV เขียนไว้เองว่า "usually a time-consuming step and therefore is disabled by default") → **สำหรับงานวัด ต้องเปิด `CORNER_REFINE_SUBPIX` เสมอ**
2. **ลำดับมุมคือ TL → TR → BR → BL** (top-left, top-right, bottom-right, bottom-left) — สลับแล้ว homography พลิก
3. **`solvePnP` กับ marker สี่เหลี่ยม ต้องใส่ `flags=cv2.SOLVEPNP_IPPE_SQUARE`** — เป็นอัลกอริทึมเดียวกับที่ `estimatePoseSingleMarkers` เรียกภายใน ถ้าใช้ default (ITERATIVE) จะเจอ pose ambiguity กระโดดไปมา

ที่มา: [OpenCV ArUco detection tutorial](https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html)

## 2.3 objPoints ที่ถูกต้องสำหรับ solvePnP (จาก tutorial ทางการ)

```cpp
objPoints[0] = Vec3f(-markerLength/2.f,  markerLength/2.f, 0);   // TL
objPoints[1] = Vec3f( markerLength/2.f,  markerLength/2.f, 0);   // TR
objPoints[2] = Vec3f( markerLength/2.f, -markerLength/2.f, 0);   // BR
objPoints[3] = Vec3f(-markerLength/2.f, -markerLength/2.f, 0);   // BL
```

## 2.4 โค้ดใช้งานจริง (รันผ่านแล้ว)

```python
"""UAV crack-scale จาก ArUco marker — OpenCV 4.7+ API"""
import cv2, numpy as np

MARKER_MM = 100.0      # ***วัดด้วยเวอร์เนียร์*** อย่าเชื่อค่าที่สั่งพิมพ์
MM_PER_PX = 0.05       # ความละเอียดที่ต้องการบนภาพ rectified
PAD_MM    = 300.0      # กินพื้นที่รอบ marker กี่ มม.

def make_detector():
    p = cv2.aruco.DetectorParameters()
    p.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX  # default NONE ต้องเปิดเอง
    p.cornerRefinementWinSize = 5
    p.minMarkerPerimeterRate = 0.01        # ยอมให้ marker เล็กลง (default 0.03)
    return cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50), p)

def rectify(img, corners_px, marker_mm=MARKER_MM, mm_per_px=MM_PER_PX, pad_mm=PAD_MM):
    """warp ให้ทุก pixel = mm_per_px มม. บนระนาบ marker (แก้ perspective ไปในตัว)"""
    s, o = marker_mm / mm_per_px, pad_mm / mm_per_px
    dst = np.float32([[o,o],[o+s,o],[o+s,o+s],[o,o+s]])          # TL,TR,BR,BL
    H = cv2.getPerspectiveTransform(np.float32(corners_px), dst)
    size = int(s + 2*o)
    return cv2.warpPerspective(img, H, (size, size)), mm_per_px

def pose(corners_px, K, dist, marker_mm=MARKER_MM):
    """ระยะกล้อง->marker (ม.) และมุมเอียงระนาบ (องศา)"""
    L = marker_mm / 1000.0
    obj = np.float32([[-L/2,L/2,0],[L/2,L/2,0],[L/2,-L/2,0],[-L/2,-L/2,0]])
    ok, rvec, tvec = cv2.solvePnP(obj, np.float32(corners_px), K, dist,
                                  flags=cv2.SOLVEPNP_IPPE_SQUARE)   # ***สำคัญ***
    if not ok: return None
    R, _ = cv2.Rodrigues(rvec)
    tilt = np.degrees(np.arccos(min(1.0, abs(R[2,2]))))
    return float(np.linalg.norm(tvec)), float(tilt)

def scale_uncertainty(side_px, sigma_corner_px=0.3):
    """ความไม่แน่นอนเชิงสัมพัทธ์ของ mm/px จาก corner noise (~1 sigma)"""
    return np.sqrt(2) * sigma_corner_px / side_px
```

**ผล self-check (รันจริง OpenCV 4.13.0, ภาพสังเคราะห์บิด perspective ให้ระนาบเอียง 28.6°):**

```
OK  rectified scale err=0.032%  naive err=6.9%  D=0.264 m  tilt=28.6 deg
    scale_1sigma@400px=0.106%
```

**อ่านตัวเลขนี้ให้ดี** — นี่คือหลักฐานตัวเลขของ §5.4: การหา mm/px จากด้าน marker ตรง ๆ ที่มุมเอียง 28.6° **ผิด 6.9%** ส่วนการ warp ก่อนแล้ววัด **ผิด 0.032%** = ดีขึ้น **215 เท่า** ด้วยโค้ด 3 บรรทัด

ไฟล์เต็มพร้อม `_demo()` ที่ assert ทุกข้อ: `D:\Temp\claude\d--00mk-steel-project------------Constistant\54be0d19-54c1-4c13-b62a-b3ab7efa041f\scratchpad\uav_scale.py`

## 2.5 DetectorParameters ที่ต้องปรับสำหรับงาน UAV (ค่า default จาก OpenCV 4.13.0)

| พารามิเตอร์ | default | ปรับเป็น | ทำไม |
|---|---|---|---|
| `cornerRefinementMethod` | `CORNER_REFINE_NONE` | **`CORNER_REFINE_SUBPIX`** | ได้มุมระดับ sub-pixel — จุดชี้ขาดความแม่น |
| `minMarkerPerimeterRate` | **0.03** | **0.01** | ภาพ 8064 px: 0.03 → marker ต้อง ≥60 px/ด้าน; 0.01 → ≥20 px |
| `adaptiveThreshWinSizeMax` | **23** | 53–103 (marker ใหญ่บนภาพ) | เงาคม/แสงไม่สม่ำเสมอบนคอนกรีต |
| `errorCorrectionRate` | **0.6** | ลดเหลือ 0.3 ถ้ากลัว false positive | สะพานจริง มี pattern สี่เหลี่ยมเยอะ |
| `useAruco3Detection` | **False** | True ถ้าต้องการเร็ว | multi-scale strategy จาก [Romero-Ramirez et al. 2018](https://www.sciencedirect.com/science/article/abs/pii/S0262885618300799) |
| `minOtsuStdDev` | **5.0** | คงไว้ | ถ้าไม่ผ่านบ่อย = ปัญหาที่วัสดุ (glossy) ไม่ใช่ที่ค่านี้ |

ทุกค่า default ยืนยันจาก [OpenCV DetectorParameters](https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html)

**สูตรแปลง `minMarkerPerimeterRate` → ขนาด marker ต่ำสุดบนภาพ (จาก OpenDroneMap):**
```
marker_side_px_min = (image_width_px × minrate) / 4
```
เช่น ภาพกว้าง 5472 px, minrate 0.01 → perimeter ต่ำสุด 54.7 px → ด้านต่ำสุด **13.7 px** ([Find-GCP](https://opendronemap.org/findgcp/))

---

# §3 การเลือกขนาด marker — กฎ pixel และสูตรคำนวณ

## 3.1 กฎ pixel (มีตัวเลขจริง)

| เกณฑ์ | ค่า | ที่มา |
|---|---|---|
| **ต่ำสุดที่ detect ได้** (3×3 / 4×4 ArUco) | **20 × 20 px** | [OpenDroneMap Find-GCP](https://opendronemap.org/findgcp/) |
| **optimal สำหรับ detect** | **30 × 30 px** | เดียวกัน |
| ตัวอย่างจริง: DJI Phantom 4P บิน 50 m AGL | marker **30 × 30 cm เพียงพอ** | เดียวกัน |
| coded target ของ Agisoft Metashape | ต้อง **รัศมี ≥ 30 px** (เส้นผ่านศูนย์กลาง 60 px) | [Agisoft Helpdesk](https://agisoft.freshdesk.com/support/solutions/articles/31000148855-coded-targets-and-scale-bars) |

**⚠️ กับดักสำคัญ: 30 px คือเกณฑ์ "ตรวจเจอ" ไม่ใช่เกณฑ์ "วัดแม่น"**

## 3.2 สูตรความไม่แน่นอนของ scale (สิ่งที่ควรใช้ตัดสินขนาดจริง ๆ)

Corner localization error σ_c (หน่วย px) แพร่เข้า scale โดยตรง:

```
σ_scale / scale  ≈  √2 · σ_c / L_px
```

โดย L_px = ด้าน marker บนภาพเป็น pixel. ค่า σ_c ≈ 0.3 px เมื่อเปิด `CORNER_REFINE_SUBPIX`

| L_px | σ_scale (%) | แปลว่า ถ้าวัดรอยแตก 0.2 mm |
|---|---|---|
| 30 | **1.41%** | ±0.003 mm จาก scale (ยังโอเค) แต่ detect เฉียดฉิว |
| 100 | **0.42%** | |
| **300** | **0.14%** | ← **จุดที่แนะนำ** |
| 500 | 0.085% | เกินความจำเป็น |

ยืนยันเชิงตัวเลขจาก self-check §2.4: `scale_1sigma@400px = 0.106%` ตรงกับสูตร (√2×0.3/400 = 0.106%)

**กฎง่าย ๆ: ตั้งเป้าให้ marker กิน 200–400 px บนภาพ** ต่ำกว่า 100 px = scale error เริ่มใหญ่กว่า error ตัวอื่น ๆ

## 3.3 สูตรคำนวณขนาด marker จากระยะ + เลนส์

**ขั้นที่ 1 — หา GSD:**
```
GSD (mm/px) = sensor_width_mm × D_mm / (focal_mm × image_width_px)
```
หรือถ้ารู้แค่ FOV (กรณีโดรน DJI ที่ไม่ประกาศขนาด sensor แน่ชัด):
```
GSD (mm/px) = 2 × D_mm × tan(FOV/2) / image_diag_px
```
ที่มา: [Skyebrowse GSD Calculator](https://www.skyebrowse.com/news/posts/gsd-calculator) — ตัวอย่างที่ตรวจสอบได้: Mavic 3E, sensor 17.3 mm, f 12.3 mm, 5280 px, บิน 100 m → GSD = **2.66 cm/px**

**ขั้นที่ 2 — ขนาดพิมพ์:**
```
marker_side_mm = L_px_target × GSD
```

## 3.4 ตาราง GSD ของ DJI Matrice 4T (คำนวณเอง)

จาก spec ทางการ ([DJI Matrice 4 Series](https://enterprise.dji.com/matrice-4-series/specs)): wide 8064×6048 (diag 10080 px) FOV 82°, medium tele 8064×6048 FOV 35°, tele 8192×6144 (diag 10240 px) FOV 15°

| เลนส์ | min focus | D = 1 m | D = 2 m | D = 3 m | D = 5 m | D = 10 m |
|---|---|---|---|---|---|---|
| **Wide** (24 mm eq.) | 1 m | **0.173** | **0.345** | 0.517 | 0.862 | 1.725 |
| **Medium tele** (70 mm eq.) | 3 m | — | — | **0.188** | 0.313 | 0.626 |
| **Tele** (168 mm eq.) | 3 m | — | — | **0.077** | 0.129 | **0.257** |

*(หน่วย mm/pixel)*
> **ยังไม่ยืนยัน:** DJI ระบุแค่ "82° FOV" ไม่บอกว่าเป็น DFOV หรือ HFOV — ผมคำนวณโดยสมมติเป็น **DFOV** ถ้าจริงเป็น HFOV ค่า GSD จะใหญ่กว่านี้ ~25%. **วิธีตรวจ: ถ่ายไม้บรรทัดที่ระยะวัดจริง 2.00 m แล้วนับ pixel** — 5 นาทีจบ และแม่นกว่าการเดา spec

## 3.5 ขนาด marker ที่แนะนำสำหรับ ku_project_jop

| สถานการณ์ | GSD | marker เพื่อได้ 300 px | **พิมพ์จริง** |
|---|---|---|---|
| Wide @ 2 m (ถ่ายภาพรวมเสาตอม่อ) | 0.345 | 104 mm | **10 × 10 cm** |
| Tele @ 10 m (ถ่ายจากที่ปลอดภัย) | 0.257 | 77 mm | **10 × 10 cm** |
| Tele @ 3 m (ซูมสุดใกล้สุด — GSD ดีที่สุด) | 0.077 | 23 mm | 10 × 10 cm (จะกิน 1,300 px, เกินพอ) |

**ข้อสรุปที่สวยงาม: marker 10 × 10 cm ใบเดียว ครอบคลุมทุกสถานการณ์** — ไม่ต้องทำหลายขนาด

## 3.6 GSD ต้องละเอียดแค่ไหนถึงวัดรอยแตกได้

| เกณฑ์ | ตัวคูณ | ที่มา |
|---|---|---|
| **แบบอนุรักษ์นิยม** | crack ต่ำสุด ≈ **3 × GSD** (GSD 1 mm → วัดได้ที่ 3 mm) | [MDPI Drones 7(6) 342](https://www.mdpi.com/2504-446X/7/6/342) |
| **มีอัลกอริทึม sub-pixel** | crack ต่ำสุด ≈ **0.5 × GSD** | [Kim et al., Sensors 18(6) 1881](https://pmc.ncbi.nlm.nih.gov/articles/PMC6022134/) — GSD 1.0 mm/px วัดรอยแตก 0.53 mm ได้ |

**เทียบกับเกณฑ์วิศวกรรม** ([ACI 224R-01 tolerable crack width](https://wiki.opensourceecology.org/images/8/8c/ACI_224R-01_Control_of_Cracking_in_Concrete_Structures_f224R(01)Chap3.pdf)):

| สภาพแวดล้อม | crack width ยอมรับได้ | GSD ที่ต้องการ (3× rule) | ทำได้ด้วย M4T? |
|---|---|---|---|
| อากาศแห้ง | 0.41 mm | 0.137 mm/px | ✅ Tele @ 5 m (0.129) |
| ชื้น/ดิน | 0.30 mm | 0.100 mm/px | ✅ Tele @ 3–4 m |
| สารละลายน้ำแข็ง | 0.18 mm | 0.060 mm/px | ⚠️ ต้อง Tele @ <2.3 m แต่ **min focus = 3 m** → **ทำไม่ได้** |
| น้ำทะเล/ละอองเค็ม | 0.15 mm | 0.050 mm/px | ❌ |
| โครงสร้างกักน้ำ | 0.10 mm | 0.033 mm/px | ❌ |

**นี่คือข้อค้นพบสำคัญที่สุดสำหรับโจทย์ "บินใกล้ขึ้น" ของคุณ:** ที่ tele + min focus 3 m คุณได้ GSD 0.077 mm/px → วัดรอยแตกได้ต่ำสุด ~**0.23 mm** (3× rule) หรือ ~**0.04 mm** (sub-pixel rule). **การบินใกล้กว่า 3 m ด้วยเลนส์ tele ไม่ช่วยอะไรเพราะโฟกัสไม่เข้า** — ทางแก้คือใช้ sub-pixel algorithm ไม่ใช่บินใกล้ขึ้น

---

# §4 Camera calibration — จำเป็นแค่ไหน

## 4.1 ตอบตรง ๆ: ขึ้นกับว่าคุณใช้ marker ทำอะไร

| ใช้ทำอะไร | ต้อง calibrate? | เหตุผล |
|---|---|---|
| **หา mm/px ด้วย homography** (marker ร่วมระนาบกับรอยแตก, อยู่กลางภาพ) | **ไม่ต้อง** (แต่ควร) | homography ดูดซับ perspective ได้เอง; distortion ที่กลางภาพ ≈ 0 |
| **หา mm/px เมื่อ marker อยู่ขอบภาพ** | **ต้อง** | radial distortion แรงสุดที่ขอบ |
| **หาระยะโดรน→วัตถุด้วย `solvePnP`** | **ต้อง** — ไม่มี K ก็คำนวณไม่ได้ | ต้องมี focal length เป็น pixel |
| **stitching / photogrammetry (Metashape, Pix4D)** | ซอฟต์แวร์ทำ self-calibration ให้ | แต่ต้องมี scale bar / GCP |

## 4.2 เลือก ChArUco ไม่ใช่ checkerboard

| | ChArUco | checkerboard |
|---|---|---|
| ต้องเห็นทั้งกระดาน | **ไม่ต้อง** | ต้อง |
| ความแม่นของมุม | สูงกว่า (chessboard corner + ArUco ID) | สูง |
| ใช้กับกล้องมุมกว้าง (มุมภาพล้นเฟรม) | ✅ | ❌ |

OpenCV เขียนไว้เองว่า ChArUco corners "much more accurate in comparison to marker corners" และ "allows occlusions or partial views" ([OpenCV](https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html))

> **ตัวเลขที่พบแต่ confidence ต่ำ:** repeatability ±0.03 mm (ChArUco) vs ±0.08 mm (checkerboard) และ "ChArUco ใช้ภาพน้อยกว่า ~50%" — มาจาก [calibvision.com](https://calibvision.com/blog/charuco-camera-calibration-boards-complete-guide-best-practices-for-2025/) ซึ่งเป็น **blog ของผู้ขายกระดาน calibration** ไม่ใช่ peer-reviewed → **อย่าอ้างในเล่มจบ** ถ้าอยากได้ตัวเลขนี้ต้องทดลองเอง

## 4.3 โค้ด calibrate ด้วย API ปัจจุบัน

```python
board = cv2.aruco.CharucoBoard((7, 5), 0.04, 0.02,          # 7x5 ช่อง, 40mm, marker 20mm
        cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50))
det = cv2.aruco.CharucoDetector(board)

allObj, allImg = [], []
for img in images:
    ch_corners, ch_ids, _, _ = det.detectBoard(img)          # แทน interpolateCornersCharuco
    if ch_ids is None or len(ch_ids) < 6: continue
    obj, imgp = board.matchImagePoints(ch_corners, ch_ids)   # แทน calibrateCameraCharuco
    allObj.append(obj); allImg.append(imgp)

rep_err, K, dist, _, _ = cv2.calibrateCamera(allObj, allImg, img.shape[::-1], None, None)
```
API ยืนยันจาก [OpenCV ChArUco calibration tutorial](https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html)

## 4.4 ปัญหาใหญ่: กล้องโดรนที่ซูมได้

**นี่คือจุดที่ต้องระวังที่สุดสำหรับ M4T**

1. **K และ dist เปลี่ยนตามระดับซูม** — hybrid zoom 56× ของ Mavic 3E/M4T หมายถึงมี optical zoom หลายจุด + digital zoom. **calibrate ครั้งเดียวใช้ไม่ได้กับทุก zoom**
2. **โฟกัสก็เปลี่ยน distortion** — งานวิจัยยืนยันว่า depth of field มีอิทธิพลมากต่อ lens distortion ในงาน close-range และเป็นสาเหตุหลักของ measurement error ([Sensors, PMC7588988](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7588988/)) — error ระดับ "dozens to hundreds of microns" ในงานระยะใกล้
3. **ทางแก้ที่ lazy และถูกต้อง:** **ล็อกเลนส์ + ล็อกซูม ไว้ที่ค่าเดียวตลอดภารกิจ** แล้ว calibrate เฉพาะค่านั้น. ถ้าจำเป็นต้องใช้หลาย config → calibrate แยกเป็นตาราง (เช่น wide@1×, tele@1×) ไม่ใช่ interpolate

**ทางเลือกที่ lazy ที่สุด:** ถ้าคุณติด marker ร่วมระนาบกับรอยแตกและวางไว้ **กลางภาพ** — คุณ **ไม่ต้อง calibrate เลย** เพราะ homography จาก 4 มุม marker แก้ทั้ง scale และ perspective ให้พร้อมกัน. **ใช้ calibration เฉพาะตอนต้องการรู้ระยะ (solvePnP)**

## 4.5 lens distortion กระทบเท่าไร

| ตำแหน่งในภาพ | ผลกระทบต่อ scale (ถ้าไม่แก้) |
|---|---|
| กลางภาพ (< 20% ของรัศมี) | **< 0.1%** — ตัดทิ้งได้ |
| 50% ของรัศมี | ~0.5–2% (ขึ้นกับเลนส์) |
| มุมภาพ | สำหรับเลนส์ 24 mm eq. ทั่วไป **2–5%** |
> **ยังไม่ยืนยัน (ตัวเลข 2 แถวล่าง)** — เป็นตัวเลขทั่วไปของเลนส์ประเภทนี้ ไม่มีแหล่งอ้างอิงเฉพาะสำหรับ M4T. **วิธีวัดเอง: calibrate แล้วดูค่า k1 — คำนวณ r_dist/r ที่ขอบภาพตรง ๆ** งานวิจัยยืนยันว่าการชดเชย distortion ปรับปรุงความแม่นได้ถึง **84.0%** ในงาน stereo close-range ([arXiv:2404.19242](https://arxiv.org/pdf/2404.19242))

**กฎง่าย ๆ: วาง marker ให้อยู่ในกรอบกลาง 60% ของภาพ แล้ว distortion แทบไม่มีผล**

---

# §5 แหล่ง error — แต่ละอันผิดกี่ %

**ตารางสรุป เรียงตามขนาดผลกระทบ (สำคัญที่สุดในรายงานนี้):**

| # | แหล่ง error | ผลต่อ scale | ประเภทตัวเลข | วิธีกำจัด |
|---|---|---|---|---|
| 1 | **มุมเอียง ไม่ rectify** | **6.9%** @ 28.6° | **วัดจริง** (self-check §2.4) | `warpPerspective` — 3 บรรทัด |
| 2 | **marker ไม่ร่วมระนาบกับรอยแตก** | **= d/D** เช่น d=50mm @ D=2m → **2.5%** | เรขาคณิตแท้ | ติดให้ร่วมระนาบ / ใช้แผ่นบาง |
| 3 | **พิมพ์ผิดสเกล** | **1:1 กับ error การพิมพ์** — "Fit to Page" เปลี่ยนสเกลเป็น **94–96%** → ผิด **4–6%** | เชิงเส้นแท้ | **วัดด้วยเวอร์เนียร์หลังพิมพ์** |
| 4 | **marker ไม่แนบผิว (โก่ง/นูน)** | ผลเหมือน #2, d = ระยะโก่ง | เรขาคณิตแท้ | แผ่นแข็ง (อลูมิเนียม) |
| 5 | **corner noise** | **√2·σ_c/L_px** → 1.4% @30px, **0.14%** @300px | สูตร + ยืนยัน self-check | marker ใหญ่ + subpix refine |
| 6 | **motion blur** | ทำให้ detect fail มากกว่าทำให้ scale ผิด | — | shutter เร็ว (§5.6) |
| 7 | **lens distortion** | <0.1% กลางภาพ, 2–5% ที่ขอบ | ประมาณ (ยังไม่ยืนยัน) | วาง marker กลางภาพ |

## 5.1 พิมพ์ marker ผิดสเกล — error ที่โง่ที่สุดและใหญ่ที่สุด

**คณิตศาสตร์:** ถ้าคุณสมมติว่า marker = 100.0 mm แต่จริง ๆ พิมพ์ออกมาได้ 96.0 mm
```
s_ที่คำนวณ = 100.0 / L_px      แต่     s_จริง = 96.0 / L_px
→ ทุกค่าที่วัด ใหญ่เกินไป 4.17%
```
**เป็นความสัมพันธ์ 1:1 ไม่มีการหักล้าง ไม่มีการเฉลี่ยออก** — รอยแตก 0.30 mm จะถูกรายงานเป็น 0.3125 mm ตลอดไป

**ทำไมถึงเกิดบ่อย:** PDF viewer มักตั้ง "Fit to Page" เป็น default ซึ่งย่อเป็น **94% หรือ 96%** โดยไม่บอก ([Toolivance](https://www.toolivance.com/guides/how-to-print-actual-size)) — และ driver บางตัวย่อลงเล็กน้อยเงียบ ๆ เพื่อกันเนื้อหาล้นขอบกระดาษ

**การป้องกัน (บังคับทำ):**
1. ตั้ง scaling = **100% / Actual Size / 1:1** และปิด Fit to Page / Shrink to Printable Area
2. **วัดด้าน marker ที่พิมพ์แล้วด้วยเวอร์เนียร์** แล้วเอาค่านั้นใส่ `MARKER_MM` — ไม่ใช่ค่าที่สั่งพิมพ์
3. กระดาษยืด/หดตามความชื้น — อีกเหตุผลที่ต้องใช้ **แผ่นอลูมิเนียม/พลาสติก** สำหรับ benchmark ถาวร (§6)

## 5.2 marker ไม่แนบผิว

marker โก่งขึ้นจากผิว d มิลลิเมตร ที่ระยะกล้อง D:
```
scale_error = d / D
```
| d (mm) | D = 1 m | D = 2 m | D = 5 m | D = 10 m |
|---|---|---|---|---|
| 5 | 0.50% | 0.25% | 0.10% | 0.05% |
| 20 | 2.0% | 1.0% | 0.40% | 0.20% |
| 50 | **5.0%** | **2.5%** | 1.0% | 0.50% |

**สังเกต: ยิ่งบินใกล้ error นี้ยิ่งใหญ่** — ขัดกับ intuition และเป็นเหตุผลว่าทำไม "บินใกล้ขึ้น" ไม่ใช่ยาครอบจักรวาล

## 5.3 marker ไม่ร่วมระนาบกับรอยแตก — **error ที่อันตรายที่สุดเพราะมองไม่เห็น**

เหมือน §5.2 แต่ d คือ **ระยะออฟเซ็ตของระนาบ** — และเกิดง่ายมากบนโครงสร้างจริง:

| กรณีจริงบนตอม่อสะพาน | d โดยประมาณ | error @ D=2m |
|---|---|---|
| ติด marker บนหน้าเสา วัดรอยแตกหน้าเดียวกัน | 0 | **0%** ✅ |
| ติดบนหน้าเสา วัดรอยแตกที่มุมเสา (ลึกเข้าไป) | ~50 mm | **2.5%** |
| ติดบนตอม่อ วัดรอยแตกบนคานที่ยื่นออกมา | 200–500 mm | **10–25%** ❌ |
| ติดบน pier cap วัดรอยแตกบนเสาที่อยู่ล่างลงไป | > 500 mm | **>25%** ❌❌ |

**นี่คือเหตุผลว่าทำไม Germanese et al. ถึงติด marker "ตามแนวรอยแตก ณ จุดที่วิกฤตที่สุด"** ไม่ใช่ติดไว้มุมเดียวแล้วใช้กับทั้งภาพ ([J. Imaging 4(8), 99, 2018](https://www.mdpi.com/2313-433X/4/8/99))

**กฎ: 1 marker = 1 ระนาบ ห้ามข้ามหน้าตัด**

## 5.4 มุมเอียง — **ยืนยันด้วยตัวเลขที่วัดเองแล้ว**

**ถ้าไม่แก้ perspective**: ผิวเอียง θ จะถูก foreshorten ตาม cos θ
```
scale_error = 1/cos(θ) − 1
```
| θ | error ตามทฤษฎี |
|---|---|
| 10° | 1.5% |
| 20° | 6.4% |
| **28.6°** | **13.9%** (ทฤษฎี) / **6.9%** (วัดจริงจาก self-check) |
| 30° | 15.5% |
| 45° | 41.4% |

> ค่าที่วัดจริง (6.9%) ต่ำกว่าทฤษฎี (13.9%) เพราะการเฉลี่ยด้านทั้ง 4 หักล้างกันบางส่วน — **แต่นี่ไม่ใช่เรื่องดี** เพราะมันแปลว่า error ซ่อนตัวอยู่และไม่แสดงตัวชัดเจน

**ถ้า rectify ด้วย homography: error → 0.032%** (วัดจริง) = **ลดลง 215 เท่า**

**สรุปเด็ดขาด: `getPerspectiveTransform` + `warpPerspective` ไม่ใช่ optional เป็นข้อบังคับ**

หมายเหตุ: การ rectify ถูกต้องเฉพาะบน **ระนาบของ marker** เท่านั้น — ผิวโค้ง (เสาตอม่อกลม!) ต้องแบ่งเป็นแถบ ๆ หรือใช้หลาย marker

## 5.5 มุมเอียงกับ detection (คนละเรื่องกับความแม่น)

- ArUco/AprilTag/STag ยัง detect ได้ >90% ถึงมุม **80°** ([Kalaitzakis 2021](https://link.springer.com/article/10.1007/s10846-020-01307-9))
- แต่ pose error โตขึ้นชัด: ArUco มี rotation std เฉลี่ย **11.70°** จาก pose ambiguity ([STag paper, arXiv:1707.06292](https://arxiv.org/pdf/1707.06292))
- ระยะ detect สูงสุดลดลงเมื่อมุมเพิ่ม ([arXiv:2509.17345](https://arxiv.org/abs/2509.17345))

**ข้อเสนอ: บินให้ตั้งฉากกับผิวมากที่สุด (θ < 20°) แล้วยัง rectify อยู่ดี**

## 5.6 Motion blur

**สูตร:**
```
blur_px = v (m/s) × t_exposure (s) / GSD (m/px)
```
**เกณฑ์:** blur ต้อง **≤ 1 × GSD** (บางที่ใช้ 2× GSD เป็นขีดสูงสุด) — [Hammer Missions](https://www.hammermissions.com/post/preventing-motion-blur-in-drone-photogrammetry-flights), [GeoCue](https://support.geocue.com/determine-shutter-interval/)

ตัวอย่างที่ตรวจสอบได้: exposure 1/100 s + ความเร็ว 10 m/s → smear **10 cm** ([Drones Made Easy](https://support.dronesmadeeasy.com/hc/en-us/articles/208235483-Motion-Blur-and-Automatic-Light-based-Speed-Adjustment))

**คำนวณสำหรับงานคุณ (Tele @ 10 m, GSD 0.257 mm/px):**

| ความเร็ว | shutter ที่ต้องการ (blur ≤ 1 px) |
|---|---|
| 1.0 m/s | 1/3,900 s |
| 0.5 m/s | 1/1,950 s |
| **0 m/s (hover)** | **จำกัดด้วย gimbal jitter เท่านั้น** |

**สรุป: สำหรับการวัดรอยแตกด้วย tele ต้องบิน hover แล้วถ่าย ไม่ใช่บินผ่านแล้วถ่าย** (ค่าแนะนำทั่วไปสำหรับ mapping คือ 1/800 s ซึ่ง**ไม่พอ**สำหรับงานนี้ — [GeoCue](https://support.geocue.com/determine-shutter-interval/))

**ผลของ blur ต่อ scale:** blur ไม่ทำให้ scale ผิดเป็นระบบ (ไม่มี bias) แต่ทำให้ σ_c โตขึ้น → ตาม §3.2 error โตตาม และในกรณีหนัก **detect ไม่ได้เลย** — `tag36h11` ออกแบบมาให้ทน motion blur ด้วย Hamming distance 11 ([AprilTag](http://www.aerialroboticscompetition.org/assets/downloads/AprilTag_Identifiers.pdf))

## 5.7 Error budget รวม (ตัวอย่างสำหรับงานคุณ)

สมมติ: marker 10 cm พิมพ์แล้ววัดด้วยเวอร์เนียร์, tele @ 5 m, rectify แล้ว, hover ถ่าย

| แหล่ง | 1σ |
|---|---|
| ขนาด marker (วัดด้วยเวอร์เนียร์ ±0.1 mm) | 0.10% |
| corner noise (L_px ≈ 780) | 0.05% |
| perspective residual หลัง rectify | 0.03% |
| coplanarity (d ≈ 5 mm) | 0.10% |
| distortion (กลางภาพ) | 0.10% |
| **RSS รวม** | **≈ 0.19%** |

**แปลว่า: รอยแตก 0.30 mm → 0.30 ± 0.0006 mm จาก scale error** — scale ไม่ใช่คอขวดอีกต่อไป **คอขวดคือ segmentation algorithm และ GSD**

---

# §6 การติดตั้งภาคสนามบนเสาคอนกรีต / ตอม่อสะพาน

## 6.1 วัสดุ marker (เรียงตามอายุการใช้งาน)

| วัสดุ | อายุกลางแจ้ง | ความเรียบ | ต้นทุน | ใช้เมื่อ |
|---|---|---|---|---|
| กระดาษ + laminate matte | สัปดาห์–เดือน | ปานกลาง (โก่งได้) | ต่ำสุด | **ตรวจครั้งเดียว / งานทดลอง** |
| สติ๊กเกอร์ vinyl matte บนแผ่นพลาสติก | 1–2 ปี | ดี | ต่ำ | ตรวจซ้ำรายปี |
| **สติ๊กเกอร์ vinyl บนแผ่นอลูมิเนียม 2–3 mm** | **หลายปี** | **ดีที่สุด (ไม่โก่ง)** | ปานกลาง | **benchmark ถาวร** |
| แผ่นอลูมิเนียม anodized/etched | 10+ ปี | ดีที่สุด | สูง | โครงสร้างสำคัญ |
| Reflective survey target (สำหรับ total station) | ระบุ **−20°C ถึง +70°C**, UV-stable | ดี | ต่ำ | **ใช้คู่กับ ArUco เป็นจุดอ้างอิงร่วม** |

ที่มา reflective target: [Metricop](https://metricop.com/collections/reflective-survey-targets) — ระบุว่าใช้สำหรับ long-term monitoring ของสะพานและอาคาร, ยึดติดคอนกรีต/เหล็ก/ไม้ได้, มี crosshair พิมพ์บน backplate เพื่อ**รักษาตำแหน่งจุดวัดถาวร — ถ้า target เสียหายเปลี่ยนใหม่แล้วกลับมาที่จุดเดิมได้**

**⚠️ ห้ามใช้ผิว glossy เด็ดขาด** — specular reflection บนคอนกรีตกลางแดดจะทำให้ `minOtsuStdDev` (5.0) ไม่ผ่านและ decode พัง

## 6.2 กาว/การยึด

| วิธี | ทนกลางแจ้ง | เจาะคอนกรีต? | หมายเหตุ |
|---|---|---|---|
| **3M VHB tape** | **UV stable, ทน −? ถึง +93°C ระยะยาว, +149°C ระยะสั้น**, ทนสารเคมี/ความชื้น/temperature cycling | ไม่ | **⚠️ ออกแบบสำหรับผิวไม่มีรูพรุน** — คอนกรีตมีรูพรุน 3M แนะนำให้**ทา primer ก่อน** |
| Epoxy 2 ส่วน (โครงสร้าง) | สูงมาก | ไม่ | ถาวรจริง แต่แกะยาก |
| Anchor bolt + แผ่นอลูมิเนียม | สูงสุด | **ใช่** | **ต้องขออนุญาตเจ้าของโครงสร้าง** — เจาะตอม่อสะพานคือการทำลายโครงสร้าง |
| Magnet (บนเหล็ก) | สูง | ไม่ | ใช้ไม่ได้กับคอนกรีต ยกเว้นติดบนแผ่นเหล็กที่ยึดไว้แล้ว |

ที่มา 3M: [3M VHB Tapes](https://www.3m.com/3M/en_US/vhb-tapes-us/), [3M 5915 (primer note)](https://www.flexfireleds.com/other-accessories/3m-vhb-adhesive-mounting-tape-for-aluminum-3m-brand-5915)

**ลำดับขั้นตอนติดตั้งที่แนะนำ:**
1. ทำความสะอาดผิวคอนกรีต (แปรงลวด + แอลกอฮอล์) — ฝุ่นคือศัตรูอันดับ 1 ของ VHB
2. **ทา 3M primer** (เพราะคอนกรีตมีรูพรุน)
3. ติด VHB → แผ่นอลูมิเนียมที่มี ArUco → กดค้าง 15 วินาที
4. **วัดด้าน marker ด้วยเวอร์เนียร์ตรงจุดติดตั้ง แล้วจดลง log** ไม่ใช่วัดตอนพิมพ์
5. ถ่ายภาพ reference วันแรก (baseline)

## 6.3 Permanent benchmark สำหรับ monitoring ระยะยาว

**นี่คือส่วนที่ทำให้โปรเจกต์คุณต่างจากงาน "ตรวจครั้งเดียว" ทั่วไป**

Germanese et al. ทำสิ่งนี้กับโครงสร้างประวัติศาสตร์: ติด marker **ตามแนวรอยแตก ณ จุดที่เค้นมากที่สุด** แล้ววัด **ระยะระหว่าง barycenter ของ marker แต่ละคู่ + การเปลี่ยนแปลงของมุมระหว่าง reference frame ของแต่ละ marker** ตามเวลา ([J. Imaging 4(8), 99, 2018](https://www.mdpi.com/2313-433X/4/8/99))

**วิธีนี้ฉลาดตรงที่: ไม่ต้องพึ่ง absolute scale เลย** — คุณวัด **การเปลี่ยนแปลง** ระหว่าง marker ที่เห็นในภาพเดียวกัน ทำให้ error เชิงระบบ (พิมพ์ผิดสเกล, calibration) หักล้างออก

**ออกแบบสำหรับ ku_project_jop:**

| องค์ประกอบ | ข้อกำหนด |
|---|---|
| **จำนวน marker/จุดตรวจ** | **≥ 2 คร่อมรอยแตก** (หนึ่งฝั่ง หนึ่งฝั่ง) + 1 ตัวควบคุมบนพื้นที่ไม่แตก |
| **ID** | **ไม่ซ้ำทั้งสะพาน** — บันทึก ID ↔ พิกัด GPS ↔ element ID ตาม BMMS ลงฐานข้อมูล |
| **วัสดุ** | อลูมิเนียม 2–3 mm + vinyl matte |
| **ขนาด** | 10×10 cm (ครอบคลุมทุกระยะบิน — §3.5) |
| **จดบันทึกวันติดตั้ง** | ขนาดที่วัดจริง, วันติด, ภาพ baseline, สภาพอากาศ |
| **ตรวจสภาพ marker ทุกรอบบิน** | ถ้า ArUco decode ไม่ได้ = marker เสื่อม ต้องเปลี่ยน (และ re-baseline) |

**ประโยชน์ต่อ T-BHI ที่ควรเขียนในเล่ม:** marker ถาวรทำให้ condition rating เปลี่ยนจาก "ค่า ณ เวลาหนึ่ง" เป็น **"อัตราการเสื่อมสภาพ (deterioration rate)"** — ซึ่งเป็นสิ่งที่ BMMS ปัจจุบันของ ทล. **ยังไม่ได้นำมาคิด** ("deterioration due to increasing traffic and severe environments like cracks and corrosion are not taken into account" — [AUN/SEED-Net JICA project](https://seed-net.org/development-of-upgrading-systems-for-structural-performances-of-existing-concrete-bridges-in-thailand/))

## 6.4 ประเด็นกฎหมาย/การอนุญาต

**ก่อนติดอะไรบนสะพานจริง ต้องขออนุญาตกรมทางหลวง/ทางหลวงชนบท** — และ "คู่มือการสำรวจและตรวจสอบสะพาน" ที่ใช้อยู่จริงจัดทำโดย **มหาวิทยาลัยเกษตรศาสตร์** ในโครงการศึกษาและพัฒนาระบบการบริหารงานบำรุงรักษาสะพาน ([YOTATHAI](https://www.yotathai.com/yotanews/check-bridge55), 382 หน้า) — **คุณอยู่ ม.เกษตร คู่มือนี้ควรเป็น baseline ของเล่มจบคุณ**
> **ยังไม่ยืนยัน:** ผมเข้าไปโหลด PDF ไม่ได้ (หน้าเว็บมีแต่ปกกับลิงก์) → **ต้องไปโหลดเองแล้วดูว่าเกณฑ์ crack width เป็นตัวเลข mm เท่าไร และ condition rating มีกี่ระดับ** นี่คือช่องว่างที่ใหญ่ที่สุดในรายงานนี้สำหรับบริบทไทย

---

# §7 ทางเลือกเมื่อติด marker ไม่ได้

**สถานการณ์จริงที่ติด marker ไม่ได้:** สะพานข้ามแม่น้ำ, ตอม่อกลางน้ำ, ใต้สะพานที่คนเข้าไม่ถึง, โครงสร้างที่เจ้าของห้ามแตะ

| วิธี | ความแม่นของ scale | ข้อดี | ข้อเสีย |
|---|---|---|---|
| **A. มิติจากแบบ as-built** | **1–5%** (ขึ้นกับความตรงของแบบกับของจริง) | ฟรี, ไม่ต้องเข้าถึง | **แบบมักไม่ตรงกับของจริง** (ก่อสร้างคลาดเคลื่อน, ซ่อมแซม); ต้องเห็นขอบชัด |
| **B. Laser rangefinder + GSD** | **~2–15%** (ดูตาราง §7.2) | มีในตัวโดรนแล้ว, auto | **แม่นไม่พอสำหรับวัดรอยแตก** |
| **C. Four-point laser dot projector** | ระดับ sub-mm | ให้ scale ทุกเฟรม, ไม่ต้องแตะโครงสร้าง | ต้องสร้าง payload เอง / ยังเป็นงานวิจัย |
| **D. Crack comparator card (คนถือ)** | **0.1 mm resolution** | ราคาถูกมาก, มีมาตรฐาน ACI | **ต้องเข้าถึงด้วยมือ** — ขัดกับเหตุผลที่ใช้โดรน |
| **E. Total station วัดพิกัดจุดเด่นบนผิว** | สูงสุด (mm) | ไม่ต้องแตะโครงสร้าง | ต้องมีเครื่อง + ตั้งกล้อง |
| **F. Stereo camera / photogrammetry แบบมี baseline รู้ค่า** | ดี | scale จาก baseline | ต้อง rig สองกล้อง |

## 7.1 A — มิติจากแบบ as-built

ใช้ **ขอบที่วัดได้แน่นอนบนภาพ** เป็น scale reference แทน marker เช่น ความกว้างเสาตอม่อ, ระยะระหว่าง bearing, ความสูงราวสะพาน

**วิธีทำ (ใช้โค้ดเดิม §2.4 ได้เลย):** แทนที่จะเอา 4 มุม marker ไปเข้า `getPerspectiveTransform` ให้เอา **4 มุมของหน้าเสา** (ที่รู้ขนาดจากแบบ) แทน — เหมือนกันเป๊ะ

**เทคนิคเพิ่มความน่าเชื่อถือ:** ใช้ **≥ 3 มิติอิสระ** แล้วเช็คว่าสอดคล้องกันไหม ถ้าไม่ = แบบไม่ตรงของจริง — เป็นหลักการเดียวกับที่ photogrammetry แนะนำให้ใช้ **scale bar อย่างน้อย 3 อัน** ("two providing a basic check and three or more adding confidence and statistical reassurance" — [Cultural Heritage Imaging](https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf))

## 7.2 B — Laser rangefinder (ตัวเลขจริงจาก DJI M4T)

| ระยะ | spec | error สัมพัทธ์ |
|---|---|---|
| **1–3 m** | system error **< 0.3 m**, random error **< 0.1 m @1σ** | **10–30%** ❌ |
| 5 m | ±(0.2 + 0.0015×5) = ±0.208 m | 4.2% |
| 10 m | ±0.215 m | 2.2% |
| 50 m | ±0.275 m | 0.55% |
| ระยะวัดสูงสุด | 1,800 m @ reflectivity 20%; blind zone **1 m** | |

ที่มา: [DJI Matrice 4 Series specs](https://enterprise.dji.com/matrice-4-series/specs)

**ข้อสรุปสำคัญ: laser rangefinder ของ M4T ที่ระยะทำงานจริง (2–10 m) ให้ scale error 2–15% ซึ่ง แย่กว่า marker 10–100 เท่า** → **ใช้มันสำหรับควบคุมการบิน (รักษา standoff) ไม่ใช่สำหรับ scale**

## 7.3 C — Four-point laser projector (งานวิจัยล่าสุด)

มีงานตีพิมพ์ที่ใช้ **four-point laser metric calibration** ติดบน UAV เพื่อสร้าง scale ให้ทุกเฟรม แล้วรวมกับ homography เพื่อลด scale drift ข้ามมุมมอง — [Automation in Construction, S0926580526000154](https://www.sciencedirect.com/science/article/abs/pii/S0926580526000154)
> **ยังไม่ยืนยันรายละเอียด:** ScienceDirect ให้ 403 ผมเข้าไม่ถึง abstract เต็ม → **ต้องไปหาผ่าน library ของ ม.เกษตร** ตัวเลขความแม่นที่แน่นอนยังไม่ทราบ

**หลักการที่คุณทำเองได้:** ติด laser pointer 4 ตัวขนานกัน ระยะห่างระหว่างจุดรู้ค่า (เช่น 100 mm) → จุดสี่จุดบนผิวคือ "marker เสมือน" ที่ฉายไปได้โดยไม่ต้องแตะโครงสร้าง **ข้อควรระวัง: ถ้าลำแสงขนานกันจริง ระยะระหว่างจุดคงที่ไม่ว่าระยะเท่าไร → ใช้เป็น scale ได้แต่ใช้หาระยะไม่ได้; ถ้าเอียงเข้าหากันเล็กน้อย → ได้ทั้งสองอย่าง**

## 7.4 D — Crack comparator card

- ช่วงวัด **0.1–7.0 mm** (0.004–0.26 นิ้ว) ขนาดเท่าบัตรเครดิต
- CRACKMON 224R **สอดคล้อง ACI 224R-01**, ทำจาก polycarbonate ใส ทนน้ำชั่วคราว
- ที่มา: [Certified MTP](https://certifiedmtp.com/crack-comparator-card/), [Buildera CRACKMON 224R](https://www.buildera.com/crackmon-224r-crack-width-comparator)

**บทบาทที่ถูกต้องในโปรเจกต์คุณ: ไม่ใช่ทางเลือกแทน marker แต่เป็น ground truth สำหรับ validate ระบบ AI** — วัดด้วยมือที่จุดที่เข้าถึงได้ 20–30 จุด แล้วเทียบกับค่าที่ระบบวัดจากภาพโดรน → นี่คือ validation table ที่ committee เล่มจบจะถาม

## 7.5 ลำดับความสำคัญที่แนะนำ

```
1. marker (ถ้าติดได้)                    → 0.2%
2. total station วัดจุดเด่นบนผิว          → <1%
3. มิติ as-built ≥3 ค่า ที่สอดคล้องกัน     → 1-5%
4. laser rangefinder + GSD                → 2-15%  ← ใช้เป็น fallback เท่านั้น
```

---

# §8 งานวิจัยที่ใช้ marker-based scale กับ UAV crack inspection (อ้างอิงจริง)

## 8.1 งานที่ตรวจสอบตัวเลขได้แล้ว

### [1] Kim, Cho & Ahn (2018) — งานที่ควรอ้างเป็นหลัก
**"Application of Crack Identification Techniques for an Aging Concrete Bridge Inspection Using an Unmanned Aerial Vehicle"**, *Sensors* 18(6), 1881 — [PMC6022134](https://pmc.ncbi.nlm.nih.gov/articles/PMC6022134/) | DOI: [10.3390/s18061881](https://doi.org/10.3390/s18061881)

| รายการ | ค่า |
|---|---|
| UAV | DJI **Inspire 2** |
| กล้อง | **Zenmuse X5S**, 5280 × 2970 px |
| ระยะบินจากผิวสะพาน | **~2 m** |
| GSD | **0.10 cm/px = 1.0 mm/px** |
| **marker** | **planar marker สี่เหลี่ยม 70 × 70 mm** |
| รอยแตกที่วัดได้ | **0.53 – 2.47 mm** กว้าง, 6.60 – 78.43 mm ยาว |
| **relative error (lab validation)** | **1–2%** |
| training data | 384 ภาพ 256×256 RGB |

**ทำไมสำคัญ:** ใกล้เคียงโจทย์คุณที่สุด — สะพานคอนกรีตเก่า + UAV + planar marker + deep learning + validation จริง. **สังเกต: วัดรอยแตก 0.53 mm ได้ทั้งที่ GSD = 1.0 mm/px** = พิสูจน์ว่า sub-pixel algorithm ทำงานได้จริง (≈0.5×GSD)

### [2] Germanese, Leone, Moroni, Pascali & Tampucci (2018) — งานที่ควรอ้างสำหรับ long-term monitoring
**"Long-Term Monitoring of Crack Patterns in Historic Structures Using UAVs and Planar Markers: A Preliminary Study"**, *Journal of Imaging* 4(8), 99 — DOI: [10.3390/jimaging4080099](https://doi.org/10.3390/jimaging4080099)

- ใช้ **ArUco fiducial markers วางตามแนวรอยแตก ณ จุดที่วิกฤตที่สุด**
- ได้ scale factor pixel→physical **จากเรขาคณิตของ marker ในภาพ UAV**
- วัด: **ระยะระหว่าง barycenter ของ marker แต่ละคู่** + **การเปลี่ยนแปลงมุมระหว่าง reference frame ของแต่ละ marker**
- ออกแบบสำหรับรอยแตกที่ "wide, large, and often non-planar" ในโครงสร้างเก่า
> **ยังไม่ยืนยัน:** MDPI ให้ 403 ตอน fetch → ขนาด marker เป็น mm, รุ่น UAV, และตัวเลข error **ยังไม่ทราบ** — paper เป็น open access ให้โหลด PDF จาก mdpi.com โดยตรง

### [3] Yoon, Shin & Spencer (ประมาณ 2021) — งานที่ตอบคำถาม "ต้องกี่ pixel"
**"Feasibility Study for the Fine Crack Width Estimation of Concrete Structures Based on Fiducial Markers"** — [IEEE Xplore doc 9583237](https://ieeexplore.ieee.org/document/9583237/)

- ใช้ **Harris corner detector** ดึงพิกัดมุม fiducial marker
- ประมาณรอยแตกละเอียด **≈ 0.3 mm หรือต่ำกว่า**
- **ข้อค้นพบหลัก (สำคัญมากสำหรับ §3): "จำนวน pixel เป็นปัจจัยชี้ขาดความแม่น มากกว่า GSD"** — ปรับปรุงความแม่นได้โดยเพิ่มจำนวน pixel, เพิ่ม focal length, และควบคุม effective object distance
> **ยังไม่ยืนยัน:** ตัวเลข error เป็น % ยังไม่ทราบ (paywall) — เข้าผ่าน IEEE ของ ม.เกษตร

### [4] Kang, Kim, Spencer et al. — marker-based UAV navigation + crack SHM
**"Deep learning-based obstacle-avoiding autonomous UAVs with fiducial marker-based localization for structural health monitoring"** — [PMC10881319](https://pmc.ncbi.nlm.nih.gov/articles/PMC10881319/)

| รายการ | ค่า |
|---|---|
| **marker** | **ArUco 4 × 4 cm ติดที่ waypoint** |
| UAV | Parrot Bebop 2 Power / Parrot Anafi + Hawkeye Firefly Micro Cam 160 |
| ความสูง waypoint | ~7 m |
| **path-following error (RMSD)** | **0.114 m** (vs **0.48 m** ด้วย ultrasonic beacon) = **ดีขึ้น 67.29%** |
| yaw control error | ดีขึ้น **60.45%** |
| obstacle avoidance threshold | ปรับได้ **1–2 m** |
| crack segmentation (STRNet) | **92.5% mIoU** (ภาพพื้น) / **91.8% mIoU** (ภาพ UAV) |

**ทำไมสำคัญสำหรับโจทย์เฉพาะหน้าของคุณ:** นี่คือหลักฐานว่า **ArUco ใช้เป็น navigation reference ในสภาพ GPS-denied ได้จริง** — ตอบโจทย์ "อยากรู้ว่าโดรนอยู่ห่างวัตถุเท่าไร" ด้วยของที่คุณติดอยู่แล้วเพื่อ scale

## 8.2 งานอื่นที่พบชื่อแต่ยังไม่ได้ตรวจตัวเลข

| งาน | ประเด็น | สถานะ |
|---|---|---|
| **Woo et al.** | ใช้ relative position ระหว่าง reference object — error **24–84 mm (x)** และ **8–48 mm (y)** | ตัวเลขจาก secondary source ยังไม่ยืนยัน |
| **UAV + four-point laser metric calibration + Mamba segmentation** (2026) | [Automation in Construction](https://www.sciencedirect.com/science/article/abs/pii/S0926580526000154) | 403, ต้องเข้าผ่าน library |
| **MSDA-Net sub-millimetre bridge crack** | สะพาน Kaijiang No.5 เมือง Deyang เสฉวน — **max error 0.1 mm** ในความกว้าง, **<1%** ในความยาว | [IOPscience](https://iopscience.iop.org/article/10.1088/1361-6501/ae65c2) — ยังไม่ได้ตรวจ full text |
| **UAS in Bridge Inspection: Comprehensive Review** (2026) | [MDPI Drones 10(2), 144](https://www.mdpi.com/2504-446X/10/2/144) | **แนะนำให้อ่าน** — เป็น review ล่าสุด เหมาะเป็นบทที่ 2 ของเล่มจบ |
| **Design of a Small UAS for Bridge Inspections** | position-hold ใต้สะพาน GPS-denied: **แนวดิ่ง ±12.8 cm, แนวราบ ±435 cm** | [Sensors 20(18), 5358](https://doi.org/10.3390/s20185358) |

**สังเกตตัวเลขสุดท้าย: horizontal hold ±435 cm ใต้สะพาน** = **4.35 เมตร!** นี่คือเหตุผลว่าทำไม marker-based scale จำเป็น — คุณ**ไม่มีทางรู้ระยะจาก GPS ใต้สะพาน**

## 8.3 ช่องว่างงานวิจัยที่โปรเจกต์คุณเติมได้

จากที่ค้นมาทั้งหมด **ยังไม่พบงานที่:**
1. เชื่อม marker-based mm/px เข้ากับ **condition rating ตามมาตรฐานเฉพาะประเทศ** (BMMS ไทย / T-BHI)
2. ใช้ **MLLM** (ไม่ใช่แค่ CNN segmentation) ให้ condition rating จากภาพที่มี scale กำกับ
3. ทำ **permanent marker benchmark เพื่อวัด deterioration rate** บนสะพานทางหลวงไทย

**ข้อ 1 และ 3 คือ novelty ที่ป้องได้จริงในเล่มจบ** — และ marker คือสิ่งที่ทำให้มันเป็นไปได้ เพราะ AI ที่ไม่รู้ scale ให้ condition rating ตาม ACI/AASHTO ไม่ได้เลย (เกณฑ์เป็น mm ทั้งหมด)

---

# §9 ตอบโจทย์เฉพาะหน้า: บินใกล้ขึ้น + รู้ระยะ + stitching

## 9.1 "บินใกล้แค่ไหนได้" — ขีดจำกัดจริงไม่ใช่การบิน แต่คือเลนส์

| ขีดจำกัด | ค่า (M4T) | ที่มา |
|---|---|---|
| **min focus wide** | **1 m** | [DJI](https://enterprise.dji.com/matrice-4-series/specs) |
| **min focus medium tele / tele** | **3 m** | เดียวกัน |
| obstacle sensing หน้า/หลัง | 0.4–200 m | เดียวกัน |
| obstacle sensing ข้าง | 0.5–200 m | เดียวกัน |
| laser rangefinder blind zone | **1 m** | เดียวกัน |
| hovering accuracy (vision) | **±0.1 m** | เดียวกัน |
| hovering accuracy (GNSS) | ±0.5 m | เดียวกัน |

**สรุป: บินใกล้กว่า 1 m ไม่มีประโยชน์ (โฟกัสไม่เข้า + ระบบหลบสิ่งกีดขวางเริ่มดัน) และใกล้กว่า 0.4 m ระบบจะไม่ยอม**

**ทางเลือกที่ดีกว่าการบินใกล้ (เรียงตามที่แนะนำ):**

| วิธี | GSD ที่ได้ | ความเสี่ยงชน |
|---|---|---|
| **Tele @ 5 m** | **0.129 mm/px** | ต่ำ |
| Tele @ 3 m (min focus) | **0.077 mm/px** | ปานกลาง |
| Medium tele @ 3 m | 0.188 mm/px | ปานกลาง |
| Wide @ 1 m | 0.173 mm/px | **สูง** |

**ข้อสรุปที่สวนความรู้สึก แต่ตัวเลขชี้ชัด: Tele ที่ 5 m ให้ GSD ดีกว่า Wide ที่ 1 m (0.129 vs 0.173 mm/px) โดยห่างจากโครงสร้าง 5 เท่า** → **อย่าบินใกล้ ให้ซูมแทน** ปลอดภัยกว่า, hover นิ่งกว่า (ลม turbulence ใกล้ผิวโครงสร้างน้อยลง), และภาพดีกว่า

**ข้อแลกเปลี่ยนของ tele ที่ต้องรู้:** DOF ตื้นมาก → marker กับรอยแตกที่ต่างระนาบกันจะเบลอทีละอัน; และ jitter ของ gimbal ถูกขยาย 7 เท่า → **บังคับ hover + shutter เร็ว (§5.6)**

## 9.2 "รู้ว่าโดรนห่างวัตถุเท่าไร" — 3 วิธี เรียงตามความแม่น

| วิธี | error ที่ D = 5 m | ต้องมีอะไร |
|---|---|---|
| **1. marker + solvePnP** | **~0.2%** (= 1 cm) | marker + calibrated K |
| 2. marker + สูตรง่าย ๆ (ไม่ต้อง calibrate ครบ) | ~0.5% | รู้ f_px อย่างเดียว |
| 3. laser rangefinder M4T | **4.2%** (= 21 cm) | ไม่ต้องมีอะไร |

**สูตรวิธีที่ 2 (lazy ที่สุด):**
```
D = f_px × L_real_mm / L_px        โดย f_px = (image_width_px/2) / tan(HFOV/2)
```

**โค้ดวิธีที่ 1 อยู่ใน `pose()` §2.4 แล้ว** — คืนทั้งระยะ **และมุมเอียงของระนาบ** ซึ่งเป็นข้อมูลที่ rangefinder ให้ไม่ได้ และเป็นสิ่งที่คุณต้องใช้ควบคุมให้บินตั้งฉาก

**ข้อเสนอสำหรับ flight program:**
```
loop:
  1. detect ArUco ใน video feed
  2. solvePnP → (D, tilt)
  3. ถ้า D > target: เข้าใกล้ | ถ้า D < target: ถอย  (deadband ±0.1 m = hovering accuracy)
  4. ถ้า tilt > 15°: หมุน yaw / ปรับ gimbal
  5. เมื่อ D และ tilt เข้าเป้า และ velocity ≈ 0 → ถ่าย
```
> **ยังไม่ยืนยัน — ต้องเช็คก่อนเขียนโค้ด:** Waypoint 3.0 ผ่าน MSDK v5 ระบุรองรับ **Matrice 30 Series, Mavic 3 Enterprise Series, Matrice 3D/3TD** — **ยังไม่พบการยืนยันว่ารองรับ Matrice 4 Series** ([DJI MSDK](https://developer.dji.com/mobile-sdk/), [Waypoint Mission docs](https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/waypoint.html)). DJI ระบุว่า M4 Series รองรับ PSDK / MSDK / Cloud API แต่ **ต้องเข้าไปเช็ค supported-aircraft list ที่ developer.dji.com ก่อนเลือกโดรน** — ถ้า M4 ยังไม่รองรับ **Mavic 3E เป็นตัวเลือกที่ปลอดภัยกว่าสำหรับงานที่ต้องเขียนโปรแกรมบินเอง**

## 9.3 Stitching / photogrammetry — marker ช่วยยังไง

**ปัญหาของ stitching ภาพระยะใกล้:** scale drift สะสมข้ามภาพ — ภาพที่ 1 กับภาพที่ 50 อาจมี scale ต่างกันหลาย % โดยไม่มีอะไรบอก

**marker แก้ปัญหานี้ 3 ทาง:**

| บทบาท | วิธีทำ |
|---|---|
| **1. Scale constraint** | ใส่ marker เป็น **scale bar** ใน Metashape/Pix4D — Metashape แนะนำตั้ง scale bar accuracy = **0.0001 m** (default 0.001) เมื่อใช้ scale bar คุณภาพสูง ([CHI](https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf)) |
| **2. Tie point ที่เชื่อถือได้** | คอนกรีตเรียบมี texture น้อย → SfM หา feature ไม่เจอ. marker เป็น high-contrast feature ที่มี **ID** → matching ไม่มีทางผิด |
| **3. Ground control** | marker ที่รู้พิกัดจริง = GCP ตรึงทั้ง model |

**ข้อกำหนดเชิงตัวเลขสำหรับ stitching:**
- **overlap ≥ 80% forward / 60% side** สำหรับงาน close-range (มาตรฐานทั่วไป — ยังไม่ยืนยันแหล่งเฉพาะ)
- **ใช้ scale bar / marker อย่างน้อย 3 ชุด** เพื่อ cross-check ([CHI](https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf))
- **motion blur ≤ 1 × GSD** ([Hammer Missions](https://www.hammermissions.com/post/preventing-motion-blur-in-drone-photogrammetry-flights))
- ถ้าใช้ Metashape coded target: ต้องกิน **รัศมี ≥ 30 px** ([Agisoft](https://agisoft.freshdesk.com/support/solutions/articles/31000148855-coded-targets-and-scale-bars))

**ทางลัดที่แนะนำ (ponytail):** สำหรับ **การวัดรอยแตกทีละรอย คุณไม่ต้อง stitch เลย** — ถ่าย 1 ภาพที่มี marker + รอยแตกอยู่ในเฟรมเดียวกัน → rectify → วัด. จบ. **stitching จำเป็นเฉพาะเมื่อต้องการแผนที่ความเสียหายทั้งเสา** ซึ่งเป็นคนละ deliverable

---

# §10 แผนปฏิบัติที่แนะนำ (สำหรับ ku_project_jop)

**Phase 1 — พิสูจน์บนพื้น (1 สัปดาห์, ไม่ต้องบิน)**
1. พิมพ์ ArUco `DICT_4X4_50` id 0-9 ขนาด 10×10 cm บนกระดาษ matte → **วัดด้วยเวอร์เนียร์**
2. ทำรอยแตกจำลองบนแผ่นคอนกรีต (หรือหาผนังจริง) วัดด้วย crack comparator card เป็น ground truth
3. ถ่ายด้วยโดรน hover ที่ 2 m, 5 m, 10 m ทั้ง wide/medium/tele
4. รันโค้ด §2.4 → เทียบกับ ground truth → **ได้ตาราง validation จริงสำหรับเล่มจบ**

**Phase 2 — calibration (2-3 วัน)**
5. พิมพ์ ChArUco board → calibrate แต่ละเลนส์แยกกัน, ล็อกซูม
6. เทียบ GSD ที่วัดจริงกับตาราง §3.4 → แก้ค่าที่ผมคำนวณไว้ให้ตรงกับกล้องคุณ

**Phase 3 — ภาคสนาม**
7. ขออนุญาต ทล./ทช. ติด benchmark marker บนอลูมิเนียม
8. บันทึก ID ↔ element ID ตาม BMMS
9. บิน hover ที่ **tele @ 5 m** เป็น default (GSD 0.129 mm/px) ไม่ใช่บินใกล้

**Phase 4 — เชื่อมกับ MLLM**
10. ส่งภาพ **rectified** (ทุก pixel = 0.05 mm) เข้า model พร้อม metadata `mm_per_px` → model ตอบเป็น mm ได้ตรง ๆ ไม่ต้องเดา scale
11. map ค่า mm → condition rating ตาม T-BHI / ACI 224R

---

# ภาคผนวก: สิ่งที่ยังไม่ยืนยัน (ต้องไปตรวจเอง)

| # | ประเด็น | ไปดูที่ไหน |
|---|---|---|
| 1 | **เกณฑ์ crack width เป็น mm ในคู่มือ ทล. / T-BHI** — ช่องว่างใหญ่ที่สุด | โหลด "คู่มือการสำรวจและตรวจสอบสะพาน" (382 หน้า) จาก [yotathai.com](https://www.yotathai.com/yotanews/check-bridge55) — จัดทำโดย ม.เกษตร |
| 2 | **FOV ของ M4T เป็น DFOV หรือ HFOV** (กระทบตาราง GSD §3.4 ~25%) | **ถ่ายไม้บรรทัดที่ระยะ 2.00 m แล้วนับ pixel** — 5 นาที |
| 3 | **Matrice 4 Series รองรับ Waypoint 3.0 ผ่าน MSDK v5 หรือไม่** | [developer.dji.com/mobile-sdk](https://developer.dji.com/mobile-sdk/) supported-aircraft list |
| 4 | ตัวเลข ChArUco ±0.03 mm vs checkerboard ±0.08 mm | มาจาก vendor blog — **อย่าอ้างในเล่มจบ** ต้องทดลองเอง |
| 5 | ตัวเลขจาก [arXiv:2509.17345](https://arxiv.org/abs/2509.17345) (marker 100mm→3.5m ฯลฯ) | สกัดจาก PDF 9MB ด้วย model เล็ก — **abstract ไม่ยืนยัน** ให้เปิด PDF อ่านเอง |
| 6 | รายละเอียด Germanese et al. (ขนาด marker, UAV, error) | MDPI ให้ 403 — โหลด PDF จาก [doi.org/10.3390/jimaging4080099](https://doi.org/10.3390/jimaging4080099) |
| 7 | ตัวเลข error ของ Yoon et al. (IEEE 9583237) | ผ่าน IEEE Xplore ของ ม.เกษตร |
| 8 | lens distortion ที่ขอบภาพ M4T (ผมประมาณ 2–5%) | calibrate เองแล้วดูค่า k1/k2 |


## KEY NUMBERS
- ArUco marker ขนาดต่ำสุดบนภาพที่ detect ได้ (3x3/4x4 dictionary): 20 x 20 pixels  [high] https://opendronemap.org/findgcp/
- ArUco marker ขนาด optimal บนภาพ: 30 x 30 pixels  [high] https://opendronemap.org/findgcp/
- ขนาด marker พิมพ์ที่พอสำหรับ DJI Phantom 4P บิน 50 m AGL: 30 x 30 cm  [high] https://opendronemap.org/findgcp/
- สูตรขนาด marker ต่ำสุดบนภาพจาก minMarkerPerimeterRate: marker_side_px = image_width_px x minrate / 4 (เช่น 5472 x 0.01 / 4 = 13.7 px)  [high] https://opendronemap.org/findgcp/
- cv::aruco::estimatePoseSingleMarkers สถานะ: deprecated — 'Use cv::solvePnP'  [high] https://docs.opencv.org/4.x/da/d58/deprecated.html
- cv::aruco::detectMarkers (free function) สถานะ: deprecated — 'Use class ArucoDetector::detectMarkers'  [high] https://docs.opencv.org/4.x/da/d58/deprecated.html
- cv::aruco::interpolateCornersCharuco / calibrateCameraCharuco สถานะ: deprecated — ใช้ CharucoDetector::detectBoard และ CharucoBoard::matchImagePoints + cv::solvePnP  [high] https://docs.opencv.org/4.x/da/d58/deprecated.html
- DetectorParameters.cornerRefinementMethod ค่า default: CORNER_REFINE_NONE (ต้องเปิด SUBPIX เองสำหรับงานวัด)  [high] https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- DetectorParameters.minMarkerPerimeterRate ค่า default: 0.03  [high] https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- DetectorParameters.adaptiveThreshWinSizeMin / Max / Step ค่า default: 3 / 23 / 10  [high] https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- DetectorParameters.minOtsuStdDev / errorCorrectionRate / cornerRefinementWinSize ค่า default: 5.0 / 0.6 / 5  [high] https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- ลำดับมุม marker ที่ detectMarkers คืนค่า: top-left, top-right, bottom-right, bottom-left  [high] https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- scale error เมื่อหา mm/px จากด้าน marker ตรง ๆ ที่ระนาบเอียง 28.6 องศา (ไม่ rectify): 6.9%  [high] https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- scale error เมื่อ rectify ด้วย getPerspectiveTransform+warpPerspective ที่มุมเดียวกัน: 0.032% (ดีขึ้น 215 เท่า)  [high] https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- scale uncertainty จาก corner noise (sigma_c=0.3px, marker 400px) วัดจาก self-check: 0.106% (= sqrt(2)*0.3/400)  [high] https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- detection rate ของ ArUco / AprilTag / STag ที่มุมมองสูงถึง 80 องศา: >90%  [high] https://link.springer.com/article/10.1007/s10846-020-01307-9
- detection rate ของ ARTag (ต่ำเกินใช้งาน): ~45% (Logitech cam) / ~49% (piCam)  [high] https://link.springer.com/article/10.1007/s10846-020-01307-9
- เวลา detect เฉลี่ย ArUco vs STag vs WhyCon: 17 ms / 35 ms / 7 ms  [medium] https://roboticsknowledgebase.com/wiki/sensing/fiducial-markers/
- ArUco ต้องเห็นส่วนใดของ marker: 100% โดยเฉพาะมุมทั้ง 4 (WhyCon ต้องการ 90%)  [medium] https://roboticsknowledgebase.com/wiki/sensing/fiducial-markers/
- AprilTag tag36h11 false positive ใน LabelMe 266,995 ภาพ (no error correction): 0 ครั้ง (tag25h9 = 3 ครั้ง)  [medium] http://www.aerialroboticscompetition.org/assets/downloads/AprilTag_Identifiers.pdf
- DJI Matrice 4T min focus distance — เลนส์ wide / medium tele / tele: 1 m / 3 m / 3 m (ถึง infinity)  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T ความละเอียดภาพ wide / tele: 8064 x 6048 px / 8192 x 6144 px  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T FOV — wide / medium tele / tele: 82 / 35 / 15 องศา (24 / 70 / 168 mm equivalent)  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T laser rangefinder ความแม่นที่ระยะ 1-3 m: system error <0.3 m, random error <0.1 m @1sigma (= ผิดได้ 10-30% ที่ระยะทำงาน)  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T laser rangefinder ความแม่นที่ระยะอื่น: +/-(0.2 + 0.0015 x D) m; blind zone 1 m; range 1800 m @20% reflectivity  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T obstacle sensing range หน้า/หลัง และ ข้าง: 0.4-200 m และ 0.5-200 m  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI Matrice 4T hovering accuracy (vision / GNSS / RTK): +/-0.1 m / +/-0.5 m / +/-0.1 m  [high] https://enterprise.dji.com/matrice-4-series/specs
- GSD ของ M4T เลนส์ tele ที่ระยะ 3 / 5 / 10 m (คำนวณเองจาก DFOV 15 องศา, diag 10240 px): 0.077 / 0.129 / 0.257 mm/px  [medium] https://enterprise.dji.com/matrice-4-series/specs
- GSD ของ M4T เลนส์ wide ที่ระยะ 1 / 2 m (คำนวณเองจาก DFOV 82 องศา, diag 10080 px): 0.173 / 0.345 mm/px  [medium] https://enterprise.dji.com/matrice-4-series/specs
- สูตร GSD จาก sensor/focal (ตัวอย่างตรวจสอบได้: Mavic 3E sensor 17.3mm, f 12.3mm, 5280px, 100m AGL): GSD = sensor_w x D / (f x img_w) = 2.66 cm/px  [high] https://www.skyebrowse.com/news/posts/gsd-calculator
- Kim et al. 2018 — UAV bridge crack: ระยะบิน, GSD, marker: Inspire 2 + Zenmuse X5S (5280x2970), บิน ~2 m, GSD 1.0 mm/px, planar marker 70x70 mm  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC6022134/
- Kim et al. 2018 — ช่วงความกว้างรอยแตกที่วัดได้ และ relative error: 0.53-2.47 mm, relative error 1-2%  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC6022134/
- Kang et al. — ArUco marker-based UAV localization สำหรับ SHM: ขนาด marker และ path-following error: ArUco 4x4 cm; RMSD 0.114 m (เทียบ 0.48 m ด้วย ultrasonic beacon) = ดีขึ้น 67.29%  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10881319/
- Kang et al. — crack segmentation (STRNet) บนภาพ UAV: 91.8% mIoU (ภาพพื้น 92.5% mIoU); obstacle threshold ปรับได้ 1-2 m  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10881319/
- ACI 224R-01 tolerable crack width — อากาศแห้ง / ชื้น-ดิน / สารละลายน้ำแข็ง / น้ำทะเล / โครงสร้างกักน้ำ: 0.41 / 0.30 / 0.18 / 0.15 / 0.10 mm  [high] https://wiki.opensourceecology.org/images/8/8c/ACI_224R-01_Control_of_Cracking_in_Concrete_Structures_f224R(01)Chap3.pdf
- เกณฑ์ความกว้างรอยแตกต่ำสุดที่ตรวจได้แบบอนุรักษ์นิยม (เทียบกับ GSD): 3 x GSD (GSD ~1mm -> วัดได้ที่ 3 mm)  [medium] https://www.mdpi.com/2504-446X/7/6/342
- crack comparator card ช่วงวัดและมาตรฐาน: 0.1-7.0 mm (0.004-0.26 in), CRACKMON 224R สอดคล้อง ACI 224R-01, polycarbonate ใส  [high] https://certifiedmtp.com/crack-comparator-card/
- เกณฑ์ motion blur สำหรับ photogrammetry: blur <= 1 x GSD (บางระบบใช้ 2 x GSD เป็นขีดสูงสุด); blur_px = v x t_exposure / GSD  [high] https://www.hammermissions.com/post/preventing-motion-blur-in-drone-photogrammetry-flights
- ตัวอย่าง motion blur ที่ตรวจสอบได้: exposure 1/100 s + 10 m/s = ground smear 10 cm  [high] https://support.dronesmadeeasy.com/hc/en-us/articles/208235483-Motion-Blur-and-Automatic-Light-based-Speed-Adjustment
- shutter interval แนะนำทั่วไปสำหรับ drone mapping (ไม่พอสำหรับ tele close-range): 1/800 s  [medium] https://support.geocue.com/determine-shutter-interval/
- PDF viewer 'Fit to Page' ย่อสเกลเป็น (ทำให้ marker พิมพ์ผิดขนาด -> scale error 1:1): 94% หรือ 96% (= error 4-6%)  [medium] https://www.toolivance.com/guides/how-to-print-actual-size
- Agisoft Metashape coded target ขนาดต่ำสุดบนภาพ: รัศมี 30 px (เส้นผ่านศูนย์กลาง 60 px)  [high] https://agisoft.freshdesk.com/support/solutions/articles/31000148855-coded-targets-and-scale-bars
- scale bar ความแม่นและค่า accuracy ที่ตั้งใน Metashape: calibrated 1/10 mm (scribed 1/100 mm); ตั้ง scale bar accuracy = 0.0001 m (default 0.001)  [high] https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf
- จำนวน scale bar ที่แนะนำในงาน photogrammetry: อย่างน้อย 3 อัน (2 อันได้แค่ basic check)  [high] https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf
- 3M VHB tape ช่วงอุณหภูมิใช้งานและ UV: ระยะยาวถึง 93C (200F), ระยะสั้น 149C (300F); UV/temperature stable; คอนกรีตมีรูพรุนต้องทา primer  [high] https://www.3m.com/3M/en_US/vhb-tapes-us/
- reflective survey target สำหรับ long-term monitoring — ช่วงอุณหภูมิ: -20C ถึง +70C, UV-stable, มี crosshair บน backplate เพื่อกู้จุดวัดเดิมได้  [medium] https://metricop.com/collections/reflective-survey-targets
- UAS position-hold ใต้สะพานในสภาพ GPS-denied: แนวดิ่ง +/-12.8 cm, แนวราบ +/-435 cm  [medium] https://doi.org/10.3390/s20185358
- เวอร์ชัน OpenCV ปัจจุบัน (ส.ค. 2026): 4.14.0 (สาย 4.x) และ 5.0 ออกกลางปี 2026; aruco อยู่ใน objdetect ตั้งแต่ 4.7  [medium] https://opencv.org/opencv-5/
- DJI Waypoint 3.0 ผ่าน MSDK v5 รองรับเครื่องรุ่นใด: Matrice 30 Series, Mavic 3 Enterprise Series, Matrice 3D/3TD (ยังไม่พบการยืนยันว่ารองรับ Matrice 4 Series)  [low] https://developer.dji.com/mobile-sdk/
- การชดเชย lens distortion ปรับปรุงความแม่นในงาน close-range stereo: 84.0%  [medium] https://arxiv.org/pdf/2404.19242

## SOURCES
- https://docs.opencv.org/4.x/da/d58/deprecated.html
- https://docs.opencv.org/4.x/d1/dcd/structcv_1_1aruco_1_1DetectorParameters.html
- https://docs.opencv.org/4.x/d2/d1a/classcv_1_1aruco_1_1ArucoDetector.html
- https://docs.opencv.org/4.x/d5/dae/tutorial_aruco_detection.html
- https://docs.opencv.org/4.13.0/da/d13/tutorial_aruco_calibration.html
- https://docs.opencv.org/4.x/d9/d6a/group__aruco.html
- https://opencv.org/opencv-5/
- https://www.cnx-software.com/2026/06/10/opencv-5-release-new-dnn-engine-with-enhanced-onnx-and-llm-vlm-support-intel-arm-and-risc-v-hardware-optimizations/
- https://github.com/opencv/opencv/releases
- https://opendronemap.org/findgcp/
- https://github.com/zsiki/Find-GCP
- https://link.springer.com/article/10.1007/s10846-020-01307-9
- https://dl.acm.org/doi/10.1007/s10846-020-01307-9
- https://roboticsknowledgebase.com/wiki/sensing/fiducial-markers/
- https://arxiv.org/pdf/1707.06292
- https://arxiv.org/abs/2509.17345
- https://arxiv.org/pdf/2506.05195
- https://www.sciencedirect.com/science/article/abs/pii/S0262885618300799
- http://www.aerialroboticscompetition.org/assets/downloads/AprilTag_Identifiers.pdf
- https://enterprise.dji.com/matrice-4-series/specs
- https://enterprise.dji.com/mavic-3-enterprise/specs
- https://developer.dji.com/mobile-sdk/
- https://developer.dji.com/doc/mobile-sdk-tutorial/en/tutorials/waypoint.html
- https://www.skyebrowse.com/news/posts/gsd-calculator
- https://www.hammermissions.com/post/preventing-motion-blur-in-drone-photogrammetry-flights
- https://support.geocue.com/determine-shutter-interval/
- https://support.dronesmadeeasy.com/hc/en-us/articles/208235483-Motion-Blur-and-Automatic-Light-based-Speed-Adjustment
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6022134/
- https://doi.org/10.3390/s18061881
- https://doi.org/10.3390/jimaging4080099
- https://www.mdpi.com/2313-433X/4/8/99
- https://ieeexplore.ieee.org/document/9583237/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10881319/
- https://www.mdpi.com/2504-446X/7/6/342
- https://www.mdpi.com/2504-446X/10/2/144
- https://doi.org/10.3390/s20185358
- https://www.sciencedirect.com/science/article/abs/pii/S0926580526000154
- https://iopscience.iop.org/article/10.1088/1361-6501/ae65c2
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10007411/
- https://wiki.opensourceecology.org/images/8/8c/ACI_224R-01_Control_of_Cracking_in_Concrete_Structures_f224R(01)Chap3.pdf
- https://certifiedmtp.com/crack-comparator-card/
- https://www.buildera.com/crackmon-224r-crack-width-comparator
- https://culturalheritageimaging.org/What_We_Offer/Gear/Scale_Bars/ScaleBars_UG_v3.pdf
- https://agisoft.freshdesk.com/support/solutions/articles/31000148855-coded-targets-and-scale-bars
- https://www.3m.com/3M/en_US/vhb-tapes-us/
- https://www.flexfireleds.com/other-accessories/3m-vhb-adhesive-mounting-tape-for-aluminum-3m-brand-5915
- https://metricop.com/collections/reflective-survey-targets
- https://www.toolivance.com/guides/how-to-print-actual-size
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7588988/
- https://arxiv.org/pdf/2404.19242
- https://calibvision.com/blog/charuco-camera-calibration-boards-complete-guide-best-practices-for-2025/
- https://www.yotathai.com/yotanews/check-bridge55
- https://seed-net.org/development-of-upgrading-systems-for-structural-performances-of-existing-concrete-bridges-in-thailand/
- https://doh.go.th/uploads/tinymce/service/bid/doc_bid/bridge&box.pdf

## OPEN QUESTIONS
- เกณฑ์ความกว้างรอยแตก (mm) และจำนวนระดับ condition rating ใน 'คู่มือการสำรวจและตรวจสอบสะพาน' ของกรมทางหลวง (382 หน้า จัดทำโดย ม.เกษตรศาสตร์) — โหลดไม่ได้ผ่านเว็บ ต้องดาวน์โหลด PDF เอง นี่คือช่องว่างใหญ่ที่สุดสำหรับบริบทไทย และจำเป็นต่อการ map ค่า mm ที่วัดได้ -> T-BHI
- DJI ระบุ FOV ของ Matrice 4T แค่ '82 องศา' โดยไม่บอกว่าเป็น DFOV หรือ HFOV — ตาราง GSD ใน §3.4 คำนวณโดยสมมติเป็น DFOV ถ้าเป็น HFOV ค่าจะผิด ~25% วิธีตรวจ: ถ่ายไม้บรรทัดที่ระยะวัดจริง 2.00 m แล้วนับ pixel
- Matrice 4 Series รองรับ Waypoint 3.0 ผ่าน Mobile SDK v5 หรือไม่ — เอกสาร DJI ที่ค้นเจอระบุรองรับเฉพาะ Matrice 30 Series / Mavic 3 Enterprise Series / Matrice 3D-3TD ถ้า M4 ยังไม่รองรับ ต้องพิจารณา Mavic 3E แทนสำหรับงานเขียนโปรแกรมบินเอง
- รายละเอียดตัวเลขของ Germanese et al. 2018 (J. Imaging 4(8) 99) — ขนาด marker เป็น mm, รุ่น UAV, ระยะบิน, และ error ที่รายงาน — MDPI คืน HTTP 403 ตอน fetch ต้องโหลด PDF open-access เอง
- ตัวเลข error เป็น % ของ Yoon et al. 'Feasibility Study for the Fine Crack Width Estimation of Concrete Structures Based on Fiducial Markers' (IEEE 9583237) — paywall ต้องเข้าผ่าน IEEE Xplore ของ ม.เกษตร งานนี้สำคัญเพราะสรุปว่า 'จำนวน pixel สำคัญกว่า GSD'
- ตัวเลขเปรียบเทียบ ChArUco vs checkerboard (repeatability +/-0.03 mm vs +/-0.08 mm, ใช้ภาพน้อยกว่า 50%) มาจาก blog ของผู้ขายกระดาน calibration ไม่ใช่ peer-reviewed — อย่าอ้างในเล่มจบโดยไม่ทดลองเอง
- ตัวเลขจาก arXiv:2509.17345 (marker 100mm -> detect ได้ 3.5 m ฯลฯ) สกัดจาก PDF 9MB ด้วยโมเดลเล็ก และ abstract ไม่ยืนยัน — ต้องเปิด PDF อ่านตารางจริงก่อนอ้าง
- lens distortion ที่ขอบภาพของ Matrice 4T (ประมาณไว้ 2-5%) ไม่มีแหล่งอ้างอิงเฉพาะรุ่น — ต้อง calibrate เองแล้วคำนวณ r_distorted/r ที่ขอบภาพจากค่า k1/k2
- รายละเอียด four-point laser metric calibration (Automation in Construction S0926580526000154) — ScienceDirect คืน 403 ยังไม่ทราบความแม่นที่รายงาน ทั้งที่เป็นทางเลือกโดยตรงของ marker เมื่อติด marker ไม่ได้
- overlap ที่เหมาะสมสำหรับ stitching ระยะใกล้บนผิวคอนกรีต (ผมใช้ค่าทั่วไป 80% forward / 60% side) ยังไม่มีแหล่งอ้างอิงเฉพาะงาน crack inspection — งบ WebSearch หมดก่อนค้นได้
