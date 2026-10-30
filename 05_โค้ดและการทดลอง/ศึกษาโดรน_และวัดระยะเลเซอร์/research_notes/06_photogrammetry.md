# การเก็บภาพและรวมภาพผิวโครงสร้างแนวดิ่งด้วย UAV (เสา ตอม่อ ท้องสะพาน) สำหรับงานตรวจสอบสภาพด้วย AI

# การเก็บภาพและรวมภาพผิวโครงสร้างแนวดิ่งด้วย UAV
## สำหรับ ku_project_jop — ตรวจสอบสภาพสะพาน/เสาตอม่อด้วย AI (ต่อยอด วช. ปีงบ 68)

> **สรุปคำตอบสั้นที่สุดก่อน** (เผื่ออ่านไม่หมด)
> 1. งานผิวแนวดิ่งต้องใช้ overlap สูงกว่างานแนวราบมาก — **forward 80–90% / side 70–80%** และต้องมี oblique/convergent เสริม ไม่ใช่แค่ strip ขนานผนัง
> 2. **lawnmower จากด้านบนใช้ไม่ได้เลย** กับท้องสะพาน/เสา (กล้องมองไม่เห็นผิว + GSD ไม่คงที่ + ใต้สะพาน GNSS ตาย) → ต้องใช้ **vertical strips / orbit / Slope mission**
> 3. ซอฟต์แวร์ที่คุ้มที่สุดสำหรับ thesis = **Agisoft Metashape Professional Educational $549 USD** (หรือลอง **RealityScan/RealityCapture ฟรี** ก่อน) — เพราะมี **scale bar + planar-projection ortho** ซึ่งเป็นสองอย่างที่จำเป็นและ DJI Terra ทำไม่ได้
> 4. คอนกรีตเรียบสีเดียวทำ SfM ล้มจริง — แก้ด้วย **ติด marker/coded target บนผิว + เพิ่ม overlap + ถ่ายวันฟ้าปิด + เพิ่ม min features** (ไม่ใช่แก้ที่ซอฟต์แวร์)
> 5. **ไม่จำเป็นต้อง stitch เพื่อให้ AI เห็นรอยแตก** — AI ทำงานบน tile 256×256 px อยู่แล้ว การ stitch มีไว้เพื่อ "ระบุตำแหน่ง + ไม่นับซ้ำ + คิดปริมาณเข้าเกณฑ์ T-BHI" ต่างหาก
> 6. **วัดความกว้างรอยแตกบนภาพเดี่ยว ไม่ใช่บน ortho** (ortho มี resampling → error ความกว้างสูงมาก) แต่วัดความยาว/พื้นที่/ตำแหน่งบน ortho

---

# 1. เงื่อนไข overlap สำหรับ facade / vertical surface — ต่างจาก mapping แนวราบยังไง

## 1.1 ทำไมมันต่าง — เหตุผลเชิงเรขาคณิต

งาน mapping แนวราบ (nadir grid) กล้องมองลงตั้งฉากกับพื้น ระยะทางกล้อง→วัตถุคงที่เกือบทั้งภาพ ผลคือ:
- GSD คงที่ทั้งภาพ
- baseline (ระยะระหว่างจุดถ่าย) ตั้งฉากกับแนวมอง → parallax ดี → triangulation แม่น
- ฉากมี texture ธรรมชาติเยอะ (พืช ดิน ยางมะตอย เงา)

งานผิวแนวดิ่งเปลี่ยนทั้ง 3 ข้อ:
- **ระยะไม่คงที่** ถ้าผิวไม่เรียบสนิท (เสาโค้ง, ตอม่อมีบัว, girder มี haunch) → GSD ต่างกันในภาพเดียว → ค่าที่วัดได้ผิดถ้าไม่แก้ perspective
- **มุมตกกระทบเฉียง** ถ้าเก็บด้วย nadir จะกลายเป็น grazing angle → depth error ระเบิด
- **ฉากไม่มี texture** คอนกรีตทาสี/ผิวแบบเรียบเป็นเทาทั้งแผ่น → feature detector หา keypoint ไม่ได้ (ดูหัวข้อ 4)

เพราะฉะนั้น overlap ที่งานราบใช้ได้ (75/65) ใช้กับผิวแนวดิ่งแล้ว **ล้มบ่อยมาก** — ไม่ใช่เพราะ overlap น้อยไปในเชิงพื้นที่ แต่เพราะจำนวน keypoint ที่ match ได้ต่อคู่ภาพต่ำกว่ามาก ต้องชดเชยด้วย redundancy

## 1.2 ตัวเลขที่แนะนำ (มีแหล่งอ้างอิง)

| งาน | Forward overlap | Side overlap | แหล่งอ้างอิง |
|---|---|---|---|
| Mapping แนวราบทั่วไป | 70–80% | 60–70% | [Hammer Missions](https://www.hammermissions.com/post/overlap-in-drone-mapping) |
| Urban + facade (double grid) | 75% | 60% | [T2D2](https://t2d2.ai/blog/harnessing-photogrammetry-revolutionizing-building-facade-inspection-with-drones) |
| **Facade / vertical (แนะนำ)** | **80–90%** | **~80%** | [Pix-Pro Vertical Photogrammetry](https://www.pix-pro.com/blog/vertical-photogrammmetry) |
| Facade inspection ทั่วไป | ≥80% ทั้งสองแกน | ≥80% | [T2D2](https://t2d2.ai/blog/harnessing-photogrammetry-revolutionizing-building-facade-inspection-with-drones) |
| **ขั้นต่ำที่ reconstruct สำเร็จ (สะพานจริง)** | **66%** | — | [Sensors 23(16):7159](https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/) |
| Quay wall + orthophoto + AI crack | ~80% | ~80% | [Sensors 25(14):4325](https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/) |

**ข้อสังเกตสำคัญจากงานวิจัยสะพาน** ([Sensors 23(16):7159](https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/)):
> "conducting multiple flight paths improved local geometric accuracy **better than increasing the overlapping rate**"
> การรวม flight route แบบ overall + partial ให้คุณภาพโมเดลดีกว่า route เดียว **46.7%**

แปลว่า: ถ้าเลือกได้ระหว่าง "เพิ่ม overlap จาก 80→90%" กับ "บินเพิ่มอีก 1 route ที่มุมต่างกัน" — **เลือกบินเพิ่ม route** คุ้มกว่า นี่คือหลักการที่ควรใส่ในบทวิธีดำเนินการวิจัยของ thesis

## 1.3 ความหมายที่แท้จริงของ "forward" กับ "side" บนผนัง

ต้องนิยามใหม่ เพราะโดรนไม่ได้บินแนวราบ:

- **Forward overlap** = ทับซ้อนระหว่างภาพที่ถ่าย "ก่อน-หลัง" ตามทิศที่โดรนเคลื่อน → ถ้าบิน vertical strip (ขึ้น-ลง) forward overlap คือ **ทับซ้อนในแนวดิ่ง**
- **Side overlap** = ทับซ้อนระหว่าง strip ข้างเคียง → คือ **ทับซ้อนในแนวนอน**

[Hammer Missions](https://www.hammermissions.com/post/overlap-in-drone-mapping) ระบุชัดว่างานผนังต้องให้ทุกภาพทับซ้อนกับภาพ **ซ้าย ขวา บน ล่าง** ครบทั้ง 4 ทิศ — ต่างจากงานราบที่สนใจแค่ทับซ้อนตามแนวบิน

## 1.4 การคำนวณระยะห่างจุดถ่ายจริง (ทำเองได้ ตรวจสอบได้)

สูตรจาก footprint:
```
footprint_diag = 2 × D × tan(FOV_diag / 2)
footprint_W    = footprint_diag × (px_W / px_diag)
footprint_H    = footprint_diag × (px_H / px_diag)
ระยะเลื่อนแนวดิ่ง = footprint_H × (1 − forward_overlap)
ระยะห่าง strip    = footprint_W × (1 − side_overlap)
GSD              = footprint_diag / px_diag
```

**ตัวอย่างจริง — Mavic 3E กล้อง wide** (4/3 CMOS, 20 MP, 5280×3956 px, FOV 84°, [DJI specs](https://enterprise.dji.com/mavic-3-enterprise/specs)):
- px_diag = √(5280² + 3956²) = 6597.6 px
- GSD = D × 0.273 mm/m → **ตรวจทานได้**: ที่ D = 100 m ได้ 2.73 cm ตรงกับที่ DJI ประกาศว่า GSD = H/37 ≈ 2.70 cm ที่ 100 m ([DSLRPros](https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series))

| ระยะห่างผนัง D | GSD | footprint W × H | เลื่อนแนวดิ่ง @80% | ห่าง strip @70% |
|---|---|---|---|---|
| 1.5 m | 0.41 mm/px | 2.16 × 1.62 m | 0.32 m | 0.65 m |
| 3.0 m | 0.82 mm/px | 4.32 × 3.24 m | 0.65 m | 1.30 m |
| 5.0 m | 1.36 mm/px | 7.21 × 5.40 m | 1.08 m | 2.16 m |
| 10.0 m | 2.73 mm/px | 14.4 × 10.8 m | 2.16 m | 4.32 m |

**เช็คความเป็นไปได้ทางปฏิบัติ**: ที่ D = 3 m ต้องถ่ายทุก 0.65 m ถ้าไต่ขึ้นที่ 0.3 m/s → ถ่ายทุก 2.2 วินาที Mavic 3E ถ่ายต่อเนื่องได้ที่ interval ต่ำสุด **0.7 วินาที** ([DSLRPros](https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series)) → เหลือเฟือ ไม่ใช่คอขวด

[Pix-Pro](https://www.pix-pro.com/blog/vertical-photogrammmetry) แนะนำความเร็วไต่ **0.2–0.3 m/s** ตรงกับที่คำนวณได้ และแนะนำระยะห่างผนัง **3 m** ว่าเป็นจุดสมดุลระหว่างคุณภาพกับความปลอดภัย

## 1.5 มุมกล้อง — ไม่ใช่ 0° อย่างเดียว

| แหล่ง | คำแนะนำมุมกล้อง |
|---|---|
| [Hammer Missions](https://www.hammermissions.com/post/overlap-in-drone-mapping) | −70° เก็บหลังคา+facade, −45° รอยต่อ, **0° เก็บ facade ล้วน** |
| [Pix4D support](https://support.pix4d.com/hc/en-us/articles/202557459) | ถ้าอยากให้เห็น facade ในเที่ยวบิน mapping ต้องเอียงกล้อง **10°–35°** (0° = มองลง) |
| [Pix-Pro](https://www.pix-pro.com/blog/vertical-photogrammmetry) | nadir ขนานผนัง + oblique รอบขอบ **~45°** ทั้ง 4 ด้าน + แถวกลาง oblique เสริม |

**สรุปเงื่อนไขที่ควรใช้ในโปรเจกต์นี้:**
```
ผิวหลัก (เสา/ตอม่อ/ผนัง):  กล้อง 0° ตั้งฉากผิว, forward 85%, side 75%
ชั้นเสริม convergent:       กล้อง ±20–30° ทั้งซ้าย-ขวา-บน-ล่าง, overlap 70%
ขอบ/มุม/รอยต่อ:            oblique 45° เก็บเพิ่มรอบขอบเขต
```
ชั้น convergent สำคัญมากสำหรับคอนกรีตเรียบ — มันคือสิ่งที่ทำให้ bundle adjustment ไม่ drift และแก้ปัญหา "doming" ในโมเดล

---

# 2. ทำไม lawnmower จากด้านบนใช้ไม่ได้ + flight pattern ที่ถูกต้อง + DJI Pilot 2 มีอะไรบ้าง

## 2.1 เหตุผล 5 ข้อที่ lawnmower/nadir grid ล้มกับท้องสะพานและเสา

**(1) กล้องมองไม่เห็นผิวเลย — occlusion ล้วน ๆ**
Nadir grid มองลง เห็นแค่ผิวบนของพื้นสะพาน ท้องสะพาน (soffit) ถูกบัง 100% โดยตัวพื้นสะพานเอง เสาตอม่อเห็นแค่หน้าตัดบน ไม่ใช่ผิวข้าง ไม่ว่าจะเพิ่ม overlap เท่าไรก็ไม่มีทางเห็น เพราะข้อมูลไม่เคยถูกบันทึก

**(2) gimbal เงยขึ้นไม่ได้พอ**
โดรน DJI ส่วนใหญ่ gimbal เงยขึ้นได้จำกัด (Mavic 3E / M4 series ต้องเช็ค tilt range ที่หน้า [specs](https://enterprise.dji.com/matrice-4-series/specs) — **ยังไม่ยืนยันตัวเลของศาที่แน่นอน หน้า spec ที่ดึงมาไม่ระบุ gimbal tilt range**) ทำให้การถ่าย soffit ตรง ๆ จากใต้สะพานทำได้ยาก ต้องบินเยื้องออกด้านข้างแล้วถ่ายเฉียงขึ้น หรือใช้โดรนที่ mount gimbal ด้านบน (M300/M350 รองรับ upward gimbal — **ยังไม่ยืนยัน** ให้เช็คที่หน้า payload compatibility ของ M350)

**(3) GSD ไม่คงที่บนผิวแนวดิ่ง**
Nadir grid ที่ระดับความสูงคงที่ให้ GSD คงที่บน "พื้นราบ" เท่านั้น สำหรับหน้าเสาสูง 8 m ระยะเฉียงจากกล้องถึงจุดบนเสาต่างกันหลายเท่าระหว่างหัวเสากับตีนเสา → GSD ต่างกันหลายเท่า → รอยแตกเดียวกันวัดได้ค่าต่างกันตามความสูง นี่คือปัญหาที่งานวิจัยเรียกว่า "variable standoff distance hinders valid millimeter-level quantification"

**(4) ใต้สะพาน GNSS/RTK ตาย → mission บินไม่ได้**
DJI Pilot 2 mission ทุกชนิดที่เป็น pre-planned route ต้องพึ่ง GNSS สำหรับ waypoint และ Slope mission ระบุชัดว่า **"Real Time Kinematics (RTK) must be enabled during the planning and operation of slope missions"** ([DJI Enterprise Insights](https://enterprise-insights.dji.com/blog/automated-data-capture-for-slope-surfaces-and-building-facades)) เมื่อบินเข้าไปใต้พื้นสะพาน สัญญาณดาวเทียมถูกบัง → RTK หลุด FIX → mission ถูก abort หรือโดรนเปลี่ยนไป ATTI mode ซึ่งลอยไปตามลม

**(5) Terrain Follow ไม่ช่วย — มันแก้คนละปัญหา**
Terrain Follow ใช้ sensor มองลงหรือ DSM ที่ import เข้ามาเพื่อรักษาความสูงเหนือ "พื้นดิน" ที่ลาดเอียง ([Propeller Aero](https://help.propelleraero.com/hc/en-us/articles/19384883356439-How-to-Plan-a-Terrain-Follow-Mission-with-DJI-Pilot-2)) มันไม่รู้จัก overhang เลย — DSM เป็นฟังก์ชัน 2.5D คือ 1 พิกัด XY มีค่า Z ได้ค่าเดียว ท้องสะพานคือกรณี 2 ค่า Z ที่พิกัดเดียวกัน (ผิวบนพื้นสะพาน + ท้องสะพาน) ซึ่งอยู่นอกความสามารถของโมเดล 2.5D โดยสิ้นเชิง

## 2.2 Flight pattern ที่ถูกต้อง — เลือกตามชิ้นส่วน

| ชิ้นส่วน | Pattern | รายละเอียด |
|---|---|---|
| **เสา/ตอม่อ หน้าตัดกลม** | **Orbit / POI (circular)** | บินวงกลมรัศมีคงที่ กล้อง 0° เล็งเข้าศูนย์กลาง แบ่งวง 360° เป็น interval 4–8° |
| **เสา/ตอม่อ หน้าตัดเหลี่ยม** | **Vertical strips ทีละหน้า (4 หน้า)** + orbit เก็บมุม | แต่ละหน้าทำเป็น facade แยก + วงเก็บมุมโค้ง |
| **ท้องสะพาน (soffit)** | **Parallel strips ตามแนวคาน + กล้องเงย** | บินเยื้องข้าง offset คงที่ ถ่ายเฉียงขึ้น หลาย offset เพื่อ convergence |
| **ผนัง/abutment/wing wall** | **Vertical strips (boustrophedon)** | ขึ้น-ลงสลับ กล้อง 0° ตั้งฉากผนัง |
| **ตัวสะพานทั้งหลัง (context)** | **Linear/Corridor + Oblique 5 ทิศ** | ให้บริบทและยึดโมเดลไม่ให้ drift |
| **คานยาว/girder line** | **Linear (corridor)** | ตามแนวยาว ไม่ต้องทำ grid |

### ตัวเลข orbit ที่ใช้ได้จริง

[Pix4D](https://www.pix4d.com/blog/3d-models-choose-angle-between-images-circular-missions) ทดสอบอาคาร 30×30 m สูง 18 m:

| Angle interval | จำนวนภาพ/วง | เวลาบิน | GSD |
|---|---|---|---|
| 12° | 31 | 4:29 | 3.11 cm |
| 8° | 62 | 5:44 | 2.87 cm |
| 4° | 124 | 9:00 | 2.84 cm |

**แปลงเป็นตอม่อจริง** — ตอม่อกลม Ø1.5 m สูง 8 m, orbit รัศมี 3 m, Mavic 3E wide:
- เส้นรอบวง = 2π × 3 = 18.85 m
- ที่ 8° interval = 45 ภาพ/วง, ระยะระหว่างจุดถ่าย = 0.42 m
- footprint W ที่ D=3 m = 4.32 m → side overlap = 1 − 0.42/4.32 = **90%** (เหลือเฟือ ใช้ 12° ก็ยังได้ 85%)
- footprint H = 3.24 m, forward overlap 80% → ระยะห่างวง = 0.65 m
- จำนวนวง = 8 / 0.65 ≈ **13 วง** → รวม 13 × 45 = **585 ภาพ** ที่ GSD 0.82 mm/px
- ลดเหลือ 12° interval → 30 ภาพ/วง → **390 ภาพ** ยังได้ side overlap ~85%

เพิ่ม 2 วงพิเศษที่กล้องเงย +25° และก้ม −25° เพื่อ convergence และผูกวงเข้าด้วยกัน → **+60 ภาพ**

## 2.3 DJI Pilot 2 — โหมดที่มีจริง และรุ่นไหนมี

| โหมด | ทำอะไร | ใช้กับงานนี้ได้ไหม | รุ่นที่รองรับ |
|---|---|---|---|
| **Waypoint** | กำหนดจุดเอง ตั้ง gimbal/action ต่อจุดได้ | ✅ **ทางออกสากล** ทำ facade/orbit เองได้ทุกแบบ | M3E series, M30 series, M300/M350, M4 series |
| **Area (Mapping / Ortho)** | grid nadir มาตรฐาน | ❌ ไม่เห็นผิวแนวดิ่ง | ทุกรุ่น enterprise |
| **Oblique (3/5-directional)** | เก็บ nadir + เฉียง 4 ทิศ | ⚠️ ได้บริบท แต่ GSD บนผิวดิ่งไม่คงที่ | M3E series, M300/M350, M4 series ([Propeller](https://help.propelleraero.com/hc/en-us/articles/19384415429911-How-to-Plan-a-3D-Oblique-Mission-with-DJI-Pilot-2)) |
| **Smart Oblique** | รวม mapping + oblique ในเที่ยวเดียว | ⚠️ Propeller เตือนตรง ๆ ว่า "produces **less than optimal data**" ใช้เมื่อแบตไม่พอเท่านั้น | M300/M350 RTK, M3E series, M4E |
| **Linear / Corridor** | บินตามแนวยาว | ✅ ดีสำหรับ girder line, ทางเข้าสะพาน | M3E series, M300/M350, M4 series ([Propeller](https://help.propelleraero.com/hc/en-us/articles/19384545634711-How-to-Plan-a-Linear-Mission-Using-DJI-Pilot-2)) |
| **Slope (Facade)** | ⭐ **โหมดที่ตรงงานนี้ที่สุด** | ✅✅ | Mavic 3 Enterprise Series ([DJI](https://enterprise-insights.dji.com/blog/automated-data-capture-for-slope-surfaces-and-building-facades)), M4 series ([Coptrz](https://shop.coptrz.com/blogs/news/dji-enterprise-app-v2-5-3-pilot-2-app-v17-1-5-14-update)) |
| **Terrain Follow** | รักษาความสูงเหนือพื้นลาด | ❌ 2.5D ไม่รู้จัก overhang | ใช้ร่วมกับ Oblique + Linear ได้ ([DJI](https://enterprise-insights.dji.com/blog/march-2023-enterprise-firmware-update)) |
| **POI (orbit)** | บินวงรอบจุดสนใจ | ✅ ดีสำหรับตอม่อกลม | เพิ่มใน firmware update มี.ค. 2023 |
| **Smart 3D Capture** | สแกน 360° → สร้าง rough model บน controller → วางเส้นทางประชิดผิว | ✅✅ อาจเป็นตัวเปลี่ยนเกม | **M4E + Manifold 3 เท่านั้น** ([Heliguy](https://www.heliguy.com/blogs/posts/transform-3d-modelling-with-dji-matrice-4e/)) |
| **Geometric** | route ตามรูปทรงเรขาคณิต | ⚠️ ยังไม่ยืนยันรายละเอียด | M4 series |

### วิธีทำงานของ Slope mission (สำคัญที่สุด — จดไว้ใช้จริง)

จาก [DJI Enterprise Insights](https://enterprise-insights.dji.com/blog/automated-data-capture-for-slope-surfaces-and-building-facades):
1. บินโดรนออกไป กด **C1** เพื่อ "snap" ผิวเป้าหมาย
2. ปรับขอบเขตของ surface ให้ครอบเฉพาะส่วนที่ต้องการตรวจ
3. **แอปแสดงระยะห่างจากเป้าหมาย** ← นี่คือคำตอบตรง ๆ ของคำถาม "อยากรู้ว่าโดรนอยู่ห่างวัตถุเท่าไหร่"
4. ตั้งค่า 3 ตัว: **GSD**, **ระยะห่างสัมพัทธ์จากผิว**, **overlap**
5. ระบบ generate flight path ให้เอง
6. **บังคับเปิด RTK** ทั้งตอนวางแผนและตอนบิน

DJI ระบุว่าออกแบบมาสำหรับ **"millimeter-level GSD acquisition"** และมีตัวอย่างที่ทำได้ GSD 1 cm

### ถ้าอยาก "เขียนโปรแกรมการบินเอง"

3 เส้นทาง:
1. **DJI WPML (KMZ waypoint file)** — DJI มี schema เปิดสำหรับไฟล์ route (`template.kml` + `waylines.wpml` ห่อใน .kmz) เขียน generator เป็น Python แล้ว import เข้า Pilot 2 ได้ — **ยังไม่ยืนยัน schema version ล่าสุด ให้ดูที่ developer.dji.com หมวด Cloud API / Waypoint Mission File**
2. **Third-party GCS ที่มี facade/orbit component สำเร็จรูป**
   - **Dronelink** — มี "Basic Facades (Vertical Mapping)" component โดยตรง ([support.dronelink.com](https://support.dronelink.com/hc/en-us/articles/4411563374099-Basic-Facades-Vertical-Mapping-Facade-Mission-Component))
   - **UgCS (SPH Engineering)** — มี Facade scan + **Circlegrammetry** (กล้องเอียง 45–70° บินวงกลม) ([manuals-ugcs.sphengineering.com](https://manuals-ugcs.sphengineering.com/docs/circlegrammetry-area))
   - **Hammer Missions** — เน้น facade inspection
   - ราคาแต่ละเจ้า **ยังไม่ยืนยัน**
3. **บินมือ + interval shooting** — สำหรับใต้สะพานที่ GNSS ตาย นี่คือทางเดียวที่ทำได้จริงกับโดรน DJI ทั่วไป ตั้ง interval 2 s แล้วไต่ช้า ๆ 0.2–0.3 m/s

## 2.4 การรู้ระยะห่างจากวัตถุ — 4 วิธี เรียงตามความน่าเชื่อถือ

| วิธี | ความแม่น | ใช้ตอนไหน | หมายเหตุ |
|---|---|---|---|
| **1. เป้าความยาวรู้ค่าในเฟรม** | ดีที่สุด — GSD = ความยาวจริง(mm) ÷ พิกเซลที่วัดได้ | หลังบิน (ต่อภาพ) | ทำงานแม้ GPS ตาย ไม่ต้องพึ่ง sensor ใด ๆ |
| **2. camera pose จาก SfM** | ดีมาก ถ้ามี scale bar | หลังประมวลผล | คำนวณระยะจากศูนย์กล้องถึงระนาบที่ fit |
| **3. Laser Rangefinder (LRF)** | ระยะ 1–3 m: system error <0.3 m, random <0.1 m @1σ; ระยะอื่น ±(0.2 + 0.0015D) m | เรียลไทม์ | **blind zone 1 m** — ที่ D=3 m error ±0.20 m = **6.7%** → ไม่ดีพอควบคุม GSD |
| **4. Vision obstacle sensing** | binocular fwd 0.4–22.5 m, lateral 0.5–32 m | เรียลไทม์ (ความปลอดภัย) | ใช้กันชน ไม่ใช่เครื่องมือวัด |

ทั้ง LRF และ vision sensing spec จาก [DJI Matrice 4 Series specs](https://enterprise.dji.com/matrice-4-series/specs)

**ข้อสรุปที่ควรใส่ในเล่ม**: LRF บนโดรนแม่นไม่พอสำหรับ metrology ระยะประชิด (±0.20 m ที่ 3 m = ±6.7% ซึ่งกลายเป็น ±6.7% บนความกว้างรอยแตกทันที) → **ต้องมีเป้าอ้างอิงในเฟรมเสมอ** นี่ไม่ใช่ทางเลือก แต่เป็นข้อบังคับถ้าจะอ้างตัวเลขความกว้าง

---

# 3. เปรียบเทียบซอฟต์แวร์ — ตัวไหนทำ vertical/facade ได้ดี

## 3.1 ตารางเปรียบเทียบหลัก

| ซอฟต์แวร์ | ราคา | Facade/Vertical ortho | GPS-denied | Scale bar (ไม่มีพิกัด) | OS | ข้อจำกัดใหญ่ |
|---|---|---|---|---|---|---|
| **DJI Terra** | Standard/Flagship perpetual (ราคา **ยังไม่ยืนยัน**; แหล่งรอง: Pro $1,299/yr, Electricity $2,599/yr) | รับภาพจาก facade route / gimbal 0° ได้ | ❌ อ่อนมาก (**ยังไม่ยืนยันว่ารับ non-geotagged ได้**) | ❌ มีแต่ GCP ต้องมี ≥4 จุด | Windows 10+ / NVIDIA **เท่านั้น** | ผูก DJI ecosystem, ไม่มี Mac |
| **Pix4Dmapper** | **$332.50/mo** หรือ **$3,990/yr** (official) | ✅ **Orthoplane tool** สร้าง ortho ของ facade ได้โดยตรง | ✅ ได้ (ต้องใส่ manual tie point) | ✅ | Win/Mac | template "3D Models" **ไม่ gen ortho** ต้องใช้ orthoplane |
| **Pix4Dinspect** | **ยังไม่ยืนยันราคา 2026** (แหล่งเก่าปี 2020: $130/mo billed yearly) | ออกแบบมาสำหรับ inspection โดยเฉพาะ | ยังไม่ยืนยัน | ยังไม่ยืนยัน | Cloud | ราคาต้องถาม sales |
| **Agisoft Metashape Pro** | **$3,499** perpetual; **Educational $549** | ✅ **Planar-projection ortho** ตั้งระนาบด้วย marker 3 จุด | ✅ **ดีที่สุด** — align ได้โดยไม่ต้องมีพิกัดเลย | ✅✅ **Scale bar + marker เต็มรูปแบบ** | Win/Mac/Linux | ราคาเต็มแพง |
| **Metashape Standard** | **$179**; **Educational $59** | ⚠️ **ยังไม่ยืนยันว่ามี planar-projection ortho / marker / scale bar** — ต้องเช็คตาราง compare ที่ agisoft.com/features/compare **ก่อนซื้อ** | ⚠️ | ⚠️ | Win/Mac/Linux | อาจไม่มีฟีเจอร์ที่จำเป็น — **อย่าซื้อก่อนเช็ค** |
| **RealityCapture / RealityScan 2.0** | **ฟรี** ถ้ารายได้บริษัท < $1M/ปี (นักศึกษา/การศึกษาฟรี); เกินนั้น $1,250/seat/yr | ✅ ทำได้ | ✅ ได้ | ✅ control point + distance constraint | **Windows + NVIDIA CUDA เท่านั้น** | ผูก GPU NVIDIA |
| **OpenDroneMap / WebODM** | **ฟรี, open source (AGPL)** | ⚠️ ทำได้แต่ต้อง tune เอง; ต้อง `--use-3dmesh`, `--skip-orthophoto` | ⚠️ `--matcher-neighbors 0` → match by triangulation (ใช้เฉพาะ non-georeferenced) | ❌ ไม่มี native scale bar | Win/Mac/Linux/Docker | เอกสาร facade บางมาก ชุมชนเล็ก |
| **COLMAP** | **ฟรี, BSD** | ⚠️ ได้ point cloud/mesh ไม่มี ortho tool | ✅✅ **ออกแบบมาเพื่อสิ่งนี้** | ❌ ต้อง scale เองด้วย script | Win/Mac/Linux | ไม่มี metric scale ในตัว |

## 3.2 ข้อสังเกตรายตัวที่สำคัญ

### DJI Terra
- **รับภาพ facade ได้**: "can import photos captured from a **facade route mission or gimbal camera angle of 0°** for 3D reconstruction" ([DJI FAQ](https://repair.dji.com/help/content?customId=01700005092&spaceId=17&re=US&lang=en&documentType=&paperDocType=ARTICLE))
- **oblique รองรับเฉพาะ 3D reconstruction ไม่รองรับ 2D** ([DJI Terra FAQ](https://enterprise.dji.com/dji-terra/faq))
- **ความแม่นเมื่อ RTK FIX ไม่ใช้ GCP**: Horizontal = 1 cm + 1–2 × GSD; Vertical = 2 cm + 1.5–3 × GSD (oblique) ([DJI Support](https://support.dji.com/help/content?customId=en-us03400004973&spaceId=34&re=US&lang=en&documentType=artical&paperDocType=paper))
- **GCP ต้อง ≥4 จุดกระจายสม่ำเสมอ** ([DJI Terra FAQ](https://enterprise.dji.com/dji-terra/faq))
- **ข้อจำกัด hardware**: ขั้นต่ำ 32 GB RAM + NVIDIA 4 GB VRAM (Shader Model 6.1+); แนะนำ 64 GB + RTX 2070 ขึ้นไป; **ไม่รองรับ macOS และไม่รองรับ GPU ที่ไม่ใช่ NVIDIA**
- **จำนวนภาพ**: RAM ว่างเพิ่มทุก 10 GB ประมวลผลได้เพิ่ม ~4,000 ภาพ
- **จุดตายสำหรับงานนี้**: ไม่มี workflow scale bar → ถ้าใต้สะพาน GNSS ตายและไม่มีพิกัด GCP จริง Terra ใช้ไม่ได้เลย

### Pix4Dmapper
- ต้องใช้ **Orthoplane tool** เพราะ default Pix4D สร้าง ortho ขนานระนาบ (X,Y) เท่านั้น ([Pix4D support](https://support.pix4d.com/hc/en-us/articles/202559889))
- template **"3D Models"** ไม่ gen orthomosaic เลย ต้องรู้ก่อนไม่งั้นงงว่าทำไมไม่มี output ([Pix4D](https://support.pix4d.com/hc/en-us/articles/205319155))
- มี case study ตรวจ facade อิตาลีด้วย orthoplane โดยเฉพาะ ([Pix4D blog](https://www.pix4d.com/blog/facade-inspection-pix4dmapper-orthoplane))

### Agisoft Metashape Pro — **ตัวที่แนะนำสำหรับ thesis นี้**
- **Planar projection orthomosaic**: ต้องเลือก Surface type = **Model** (ไม่ใช่ DEM) แล้วกำหนดระนาบด้วย **marker 3 จุด** พร้อมระบุแกน horizontal/vertical ([Agisoft helpdesk](https://agisoft.freshdesk.com/support/solutions/articles/31000154049-orthomosaic-generation-planar-projection-))
- **Scale bar** ทำงานได้แม้ไม่มี GCP: "Scale bars are ideal when you don't have access to GCPs but need accurate scaling for small and medium projects, such as **architectural documentation or indoor modeling**" ([AgisoftMetashape.com](https://www.agisoftmetashape.com/how-to-set-the-scale-in-agisoft-metashape-complete-guide/))
- **RTK integration**: เปิด `Load camera location accuracy from XMP meta data` + `Load camera orientation angles from XMP meta data` ใน Tools > Preferences > Advanced **ก่อน** import ภาพ ([Agisoft helpdesk](https://agisoft.freshdesk.com/support/solutions/articles/31000161735-dji-with-rtk-coordinates-data-processing))
- งานวิจัย quay wall ที่ทำสำเร็จจริงใช้ **Metashape Professional v2.2.0** + 5 GCP → RMSE ระนาบ 0.89 cm, ดิ่ง 2.74 cm ([Sensors 25(14):4325](https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/))
- **Educational Professional $549** ทำให้เข้าถึงได้จริงสำหรับโปรเจกต์ ม.เกษตร (ต้องมีเอกสารรับรองสถานะนักศึกษา)

### RealityCapture / RealityScan 2.0
- **ฟรีสำหรับนักศึกษา/การศึกษา/บริษัทรายได้ < $1M/ปี** ([RealityScan license](https://www.realityscan.com/license))
- เร็วมาก จัดการภาพจำนวนมากได้ดี
- **ต้อง Windows + NVIDIA CUDA** — เช็ค GPU ที่มีก่อน
- เหมาะทำ baseline เปรียบเทียบใน thesis แบบไม่มีต้นทุน

### OpenDroneMap
Flags ที่จำเป็นสำหรับ facade (จาก [ODM docs](https://docs.opendronemap.org/arguments/) + [ODM community](https://community.opendronemap.org/t/vertical-facade-mapping/16890)):
```bash
--use-3dmesh              # default False → ต้องเปิด (2.5D mesh ใช้กับผนังไม่ได้)
--skip-orthophoto true    # ถ้าเอาแค่ 3D
--min-num-features 20000  # default 10000 → เพิ่มสำหรับผิวคอนกรีต
--feature-quality ultra   # default high
--pc-quality ultra        # default medium
--mesh-octree-depth 12    # default 11 (แนะนำ 8-12)
--mesh-size 500000        # default 200000
--matcher-neighbors 0     # match by triangulation (non-georeferenced เท่านั้น)
--camera-lens brown       # default auto; brown = Brown-Conrady ให้ผลดีกว่า perspective
--gps-accuracy 10         # ถ้า GPS ห่วย
```
**ข้อจำกัดจริง**: ชุมชน ODM ยอมรับว่าเอกสารเรื่อง facade "remains sparse" และไม่มี scale bar native → ถ้าใช้ ODM ต้องเขียน script scale เอง

### COLMAP
- **scale ambiguity คือปัญหาโครงสร้าง**: "COLMAP typically produces sparse 3D reconstructions **without metric scale**"
- ทางแก้: เริ่มจาก known poses — "If rough camera poses are already known by measurements from sensors like GPS, incremental reconstruction **can be started with known poses**, which will be used as prior values for triangulation" และ "sparse reconstruction is **not necessary** to compute a dense model from known camera poses" ([COLMAP FAQ](https://colmap.github.io/faq.html))
- เหมาะสำหรับสาย research ที่จะทดลอง detector-free matcher (LoFTR / [DetectorFreeSfM](https://zju3dv.github.io/DetectorFreeSfM/)) กับผิวคอนกรีตไร้ texture

## 3.3 คำแนะนำเชิงกลยุทธ์สำหรับ thesis

```
ขั้นที่ 1 (ฟรี, ทดลอง):  RealityScan 2.0 (ฟรี) + COLMAP (ฟรี)
                        → พิสูจน์ว่าชุดภาพที่บินมาใช้ได้ก่อน
ขั้นที่ 2 (ลงทุนน้อย):   Metashape Professional Educational $549
                        → ได้ scale bar + planar ortho ครบ ทำเล่มได้จริง
ขั้นที่ 3 (ถ้ามีทุน):    Pix4Dmapper $3,990/yr เป็นตัวเทียบผล
DJI Terra:              ใช้เฉพาะกรณีบินบนสะพาน (RTK FIX) ไม่ใช้ใต้สะพาน
```

**การเปรียบเทียบผลจาก 2–3 ซอฟต์แวร์บนชุดภาพเดียวกัน เป็นเนื้อหาบทที่ 4 ที่ดีมากสำหรับ thesis** และแทบไม่มีต้นทุนเพิ่ม

---

# 4. ปัญหา feature-poor: คอนกรีตเรียบสีเดียว ทำให้ SfM ล้ม — วิธีแก้

## 4.1 ทำไมมันล้ม (กลไกจริง ไม่ใช่คำพูดลอย ๆ)

SfM แบบ detector-based (SIFT ใน COLMAP/Metashape/ODM) ทำงานเป็นลำดับ:
1. หา keypoint ที่เป็น corner/blob จาก gradient ของภาพ
2. สร้าง descriptor จาก local gradient histogram
3. match descriptor ข้ามภาพ
4. RANSAC หา geometry ที่สอดคล้อง
5. bundle adjustment

ผิวคอนกรีตทาสีเรียบทำให้ **ขั้นที่ 1 ตายก่อน** — ไม่มี gradient ให้จับ ถ้าจับได้ก็เป็น sensor noise ซึ่งไม่ repeatable ข้ามภาพ → ขั้นที่ 3 ตาย

งานวิจัยยืนยันตรง ๆ:
> "Textureless scenarios and viewpoint changes in low-textured datasets cause detector-based SfM methods to struggle with poor keypoint detection and **lead to failed reconstruction**" ([DetectorFreeSfM](https://zju3dv.github.io/DetectorFreeSfM/))
> "Classic SfM pipelines such as COLMAP recover scale but **require textured scenes**, extensive feature matches, and pre-calibrated intrinsics"

**อาการที่จะเจอในสนามจริง** (จดไว้ debug):
- Metashape align ได้ 40/500 ภาพ แล้วหยุด
- โมเดลแตกเป็นหลายชิ้น (multiple chunks) ที่ต่อกันไม่ได้
- ผิวเสาโค้งงอเป็นกล้วย (doming / bowl effect)
- dense cloud มีรูโหว่ตรงกลางหน้าเสาที่เรียบที่สุด (ตรงที่อยากได้ที่สุดพอดี)

## 4.2 วิธีแก้ เรียงตามอัตราส่วนผล/ความพยายาม

### ⭐ วิธีที่ 1: ติด marker / coded target บนผิว — **ได้ผลที่สุดและถูกที่สุด**

- ใช้ **Metashape circular coded target** (พิมพ์จาก Tools > Markers > Print Markers, มีแบบ 12-bit/16-bit/20-bit) ติดบนผิวเสา 8–15 จุดกระจาย
- Metashape จะ **auto-detect** ทั้งชุดในทุกภาพ → ได้ tie point ที่แน่นอน 100% ทันที
- **ได้ 2 ต่อ**: แก้ปัญหา feature-poor **และ** สร้าง scale bar ในคราวเดียว (ดูหัวข้อ 5)
- ต้นทุน: กระดาษ A4 + เทปกาว ~50 บาท
- ข้อจำกัด: ต้องเข้าถึงผิวได้ทางกายภาพ — **ท้องสะพานสูงติดไม่ได้** → ใช้กับตอม่อ/ผนัง/abutment ได้ ท้องสะพานต้องใช้วิธีอื่น

งานวิจัยยืนยันว่าการเติม texture เทียมช่วยจริง:
> "optimal artificial textures **significantly enhance accuracy** of 3D models, especially for materials with uniform textures" ([F1000Research 13:1479](https://f1000research.com/articles/13-1479) — **ตัวเลขเชิงปริมาณยังไม่ยืนยัน เว็บ block การดึงเนื้อหา ต้องเข้าไปอ่านเอง**)

### วิธีที่ 2: เพิ่ม overlap + convergent geometry

- forward 85–90%, side 75–80% (สูงกว่างานราบชัดเจน)
- **สำคัญกว่า overlap คือ convergence** — ถ่ายผิวจุดเดียวกันจากหลายมุม ±20–30° ไม่ใช่แค่ strip ขนานกัน
- ยืนยันจากงานสะพานจริง: multiple flight paths ให้ผลดีกว่าเพิ่ม overlap และ fusion ของ overall+partial route ดีขึ้น **46.7%** ([Sensors 23(16):7159](https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/))

### วิธีที่ 3: จัดเฟรมให้มีบริบท — **อย่าให้ผิวเรียบเต็มเฟรม**

นี่คือข้อผิดพลาดที่พบบ่อยที่สุดของมือใหม่: บินประชิดมากจนภาพเป็นเทาทั้งใบ

ต้องให้ในเฟรมมีอย่างน้อย 1–2 อย่างนี้เสมอ:
- ขอบเสา / มุม / รอยต่อ construction joint
- รูเหล็กยึดแบบ (form-tie hole) — มีทุก 60–90 cm บนเสาหล่อในที่
- คราบน้ำ คราบสนิม คราบตะไคร่ — ของขวัญจากธรรมชาติ
- Bearing, expansion joint, ท่อระบายน้ำ
- พื้นหลัง (ท้องฟ้า/พื้นดิน) ตรงขอบเฟรม

**Trade-off ตรง ๆ**: บินไกลขึ้น → SfM สำเร็จง่ายขึ้น แต่ GSD แย่ลง → ต้องหาจุดสมดุล (แนะนำ 2–3 m สำหรับ wide, หรือใช้ tele จากไกลขึ้น ดูหัวข้อ 4.6)

### วิธีที่ 4: RTK / known poses เป็น prior

- **Metashape**: เปิด XMP accuracy loading, ตั้ง camera accuracy ที่ **0.01–0.05 m** (RTK จริง) ไม่ใช่ default 10 m — ค่านี้บอก Metashape ว่าจะเชื่อพิกัดกล้องแค่ไหนตอน bundle adjustment ([Agisoft](https://agisoft.freshdesk.com/support/solutions/articles/31000161735-dji-with-rtk-coordinates-data-processing))
- **COLMAP**: `--Mapper.ba_refine_extrinsics 0` + import known poses → "sparse reconstruction is not necessary to compute a dense model from known camera poses" ([COLMAP FAQ](https://colmap.github.io/faq.html))
- **ODM**: `--gps-accuracy 0.05` + `--sfm-algorithm triangulation` (docs ระบุว่า "For aerial datasets, if camera GPS positions and angles are available, triangulation can generate better results")
- ⚠️ **ข้อควรระวังใหญ่**: ใต้สะพาน RTK หลุด → prior หายไปพอดีตรงที่ต้องการมากที่สุด นี่คือเหตุผลที่ marker (วิธีที่ 1) สำคัญกว่า

### วิธีที่ 5: เพิ่มจำนวน feature ที่ดึงออกมา

| ซอฟต์แวร์ | ค่า default | ค่าแนะนำสำหรับคอนกรีต |
|---|---|---|
| Metashape | Key point limit 40,000 / Tie point limit 4,000 | Key point **80,000–100,000**, Tie point **0** (ไม่จำกัด), เปิด **Generic preselection** ปิด **Reference preselection** ถ้า GPS ห่วย |
| ODM | `--min-num-features 10000` | **20,000–40,000**, `--feature-quality ultra` |
| COLMAP | SiftExtraction.max_num_features 8192 | **20,000+**, `--SiftExtraction.estimate_affine_shape 1`, `--SiftExtraction.domain_size_pooling 1` |

⚠️ ไม่ใช่ยาวิเศษ — ถ้าผิวไม่มี gradient จริง ๆ เพิ่มค่าก็ได้แต่ noise เพิ่ม เวลาประมวลผลเพิ่ม 3–5 เท่า

### วิธีที่ 6: แสง

- **ฟ้าปิด/มีเมฆ = ดีที่สุด** สำหรับผิวคอนกรีต (แสงกระจายสม่ำเสมอ ไม่มีเงาแข็ง)
- **หลีกเลี่ยง**: แดดจัดตอนเที่ยง (เงาแข็งเปลี่ยนตำแหน่งระหว่างบิน → feature ที่ match ได้จริง ๆ คือเงา ไม่ใช่ผิว → โมเดลผิด), ผิวเปียกมันวาว (specular), ย้อนแสง
- **ท้องสะพานมืด** → ต้องใช้ ISO สูง → noise → feature แย่ลงอีก ⚠️ อาจต้องใช้ไฟ LED เสริม (โดรน inspection บางรุ่นมี spotlight เช่น M30 series / M4T)

### วิธีที่ 7: Projected pattern (สำหรับใต้สะพาน / กลางคืน)

ฉายลาย speckle/checkerboard ลงบนผิว → สร้าง texture เทียมชั่วคราว ([Eureka PatSnap](https://eureka.patsnap.com/article/handling-textureless-surfaces-in-photogrammetry-pattern-projection-techniques))

⚠️ **ข้อควรระวังทางทฤษฎีที่คนมักพลาด**: ถ้า projector อยู่บนโดรน ลายจะขยับตามกล้อง → SfM จะ match ลาย ไม่ใช่ match ผิว → ผลลัพธ์ผิดทั้งหมด **projector ต้องอยู่นิ่งกับที่ (ตั้งบนขาตั้งบนพื้น) เท่านั้น** เหมาะกับใต้สะพานที่มีที่ตั้งขาตั้งได้

### วิธีที่ 8: Detector-free matcher (สาย research — น่าใส่ในบท "ข้อเสนอแนะ")

- **LoFTR / DetectorFreeSfM** ([zju3dv](https://zju3dv.github.io/DetectorFreeSfM/)) — ข้ามขั้นตอน keypoint detection ไปเลย ทำ dense matching ตรง ๆ ออกแบบมาแก้ปัญหา textureless โดยเฉพาะ
- **Hybrid features** — ใช้ line segment ช่วย: "In scenarios with weakly textured scenes, **line segments are often abundant** and can offer complementary geometric constraints" ([ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05311.pdf)) — เหมาะกับเสาสี่เหลี่ยมมาก เพราะขอบเสา/รอยต่อแบบเป็นเส้นตรงชัด
- **MP-SfM** (monocular surface priors) ([arXiv 2504.20040](https://arxiv.org/html/2504.20040))

### วิธีที่ 9: เลือกโดรนที่แก้ปัญหาที่ต้นเหตุ

- **DJI M4E + Manifold 3 Smart 3D Capture** — สร้าง rough model แล้วบินตามผิวจริง ทำให้ระยะห่างคงที่ → GSD คงที่ → ลดปัญหา scale drift
- **Flyability Elios 3** — LiDAR-SLAM ไม่พึ่ง visual feature เลย ทำงานใน GPS-denied ได้จริง (มี depth camera + LiDAR 6 ตัว + vision 6 ตัว + RTK) ([Flyability](https://www.flyability.com/blog/gps-denied-drone)) มีกรงคาร์บอนบินใต้สะพาน/ใน box girder ได้ ⚠️ ราคาสูงมาก **ยังไม่ยืนยันตัวเลข**
- **Skydio X10** — autonomy สำหรับ bridge inspection ([Skydio](https://www.skydio.com/solutions/bridge-inspection))

## 4.3 Checklist ก่อนออกสนาม (ปริ้นท์ติดกระเป๋า)

```
[ ] เป้า scale bar 1.000 m (คาร์บอน/อลูมิเนียม) + coded target 2 หัว
[ ] Coded target พิมพ์แล้ว 15 แผ่น + เทปกาวสองหน้า
[ ] เช็คพยากรณ์: ฟ้าปิด/มีเมฆ ไม่ใช่แดดเที่ยง
[ ] แบตเตอรี่ ≥4 ก้อน (facade mission กินแบตกว่า mapping 2-3 เท่า)
[ ] ตั้งกล้อง: mechanical shutter ON, ISO ล็อคต่ำสุดที่ทำได้, shutter ≥1/500
[ ] ตั้ง interval 2 s หรือช้ากว่า (ถ้าบินมือ)
[ ] จดระยะห่างผิวที่ตั้งใจ + GSD ที่คาดหวัง ลงในสมุด (ใช้ตรวจทานทีหลัง)
[ ] ถ่ายภาพ "context" ทั้งสะพานจากไกล 10-20 ภาพ ก่อนเข้าประชิด (ใช้ผูกโมเดล)
```

---

# 5. GCP / scale constraint — ใส่ marker เป็น scale bar ยังไงให้โมเดลมีหน่วยจริง

## 5.1 ทำไมต้องมี — และทำไม GCP ธรรมดาใช้ไม่ได้กับงานนี้

SfM คืนค่าโมเดลที่ถูกต้องเชิงรูปทรง (similarity transform) แต่ **ไม่รู้ขนาดจริง** — โมเดลเสาสูง 8 m กับโมเดลเสาสูง 8 หน่วยไร้มิติ หน้าตาเหมือนกันทุกประการ ต้องมี **constraint ภายนอก** อย่างน้อย 1 อย่างมาตรึงมาตราส่วน

ทางเลือกมี 2 ทาง:
| | GCP (พิกัดสัมบูรณ์) | Scale bar (ระยะสัมพัทธ์) |
|---|---|---|
| ต้องการ | พิกัด X,Y,Z จาก RTK rover / total station | แค่ระยะห่าง 2 จุด (เช่น 1.000 m) |
| ตรึงอะไร | ตำแหน่ง + ทิศทาง + มาตราส่วน (7 DOF) | มาตราส่วนอย่างเดียว (1 DOF) |
| ใช้ใต้สะพาน | ❌ ยิง RTK ไม่ได้ | ✅ ได้ |
| ต้นทุน | rover RTK 100k+ บาท / จ้างช่างสำรวจ | ไม้บรรทัดคาร์บอน + coded target |
| งานนี้ควรใช้ | ถ้าบินบนสะพาน (RTK FIX ได้) | **✅ ใช้ตัวนี้เป็นหลัก** |

Agisoft ระบุตรง ๆ ว่า:
> "Scale bars are often used **when Ground Control Points (GCPs) are not available**... ideal when you don't have access to GCPs but need accurate scaling for small and medium projects, such as **architectural documentation or indoor modeling**" ([AgisoftMetashape.com](https://www.agisoftmetashape.com/how-to-set-the-scale-in-agisoft-metashape-complete-guide/))

**ตอม่อสะพาน = "small/medium project ไม่มี GCP" เป๊ะ ๆ** → scale bar คือคำตอบ ไม่ใช่ GCP

## 5.2 Workflow ใน Metashape — ทีละขั้น

### ขั้นเตรียมของ (ทำก่อนออกสนาม)
1. **สร้างเป้า**: Tools > Markers > **Print Markers** → เลือก 12-bit circular → พิมพ์บน A4 กันน้ำ (หรือ sticker vinyl)
   - ขนาดเป้าต้องใหญ่พอที่ระยะบิน: **เส้นผ่านศูนย์กลางเป้า ≥ 30–50 pixel ในภาพ**
   - ที่ D = 3 m, GSD = 0.82 mm/px → เป้าต้องกว้าง ≥ 0.82 × 40 = **33 mm** → ใช้ A4 (~200 mm) เหลือเฟือ ใช้ได้ถึง D = 15 m
2. **สร้าง scale bar จริง**: ท่อคาร์บอน/อลูมิเนียมยาว ~1.2 m ติด coded target 2 หัว
   - **วัดระยะระหว่างศูนย์กลางเป้า 2 อัน ด้วยเวอร์เนียร์/เทปเหล็กที่สอบเทียบแล้ว** จดค่าละเอียดถึง 0.1 mm เช่น 1.0000 m
   - ⚠️ ความไม่แน่นอนของค่านี้ **ส่งต่อตรง ๆ** ไปทั้งโมเดล: ถ้าวัดผิด 1 mm บนบาร์ 1 m = error 0.1% ทั้งโมเดล = 0.001 mm บนรอยแตก 1 mm (ยอมรับได้) แต่ถ้าวัดผิด 10 mm = 1% (เริ่มมีนัย)

### ขั้นสนาม
3. วางบาร์บนผิว/พิงเสา ในตำแหน่งที่ **เห็นจากอย่างน้อย 3–5 ภาพ**
4. **ใช้อย่างน้อย 3 บาร์** วางในทิศต่างกัน:
   - บาร์ 1: แนวดิ่งบนหน้าเสา
   - บาร์ 2: แนวนอนบนหน้าเสา
   - บาร์ 3: **ไม่ใส่ในการคำนวณ ใช้เป็น check bar** ← สำคัญมากสำหรับ thesis เพราะเป็นหลักฐาน independent validation
5. ถ้าเสาสูง วางบาร์ที่ระดับล่าง กลาง บน อย่างละอัน (ตรึง scale drift ตามความสูง)

### ขั้นประมวลผล
6. Workflow > **Align Photos** (Accuracy: High, Key point 80,000, Tie point 0)
7. Tools > Markers > **Detect Markers** (12-bit, Tolerance 50) → เป้าจะถูก detect อัตโนมัติเป็น `target 1`, `target 2`, ...
8. Reference pane → เลือก marker 2 ตัว → คลิกขวา → **Create Scale Bar**
9. ดับเบิลคลิก scale bar → พิมพ์ระยะจริง เช่น `1.0000` (หน่วยเมตร)
10. ตั้ง **Accuracy (m)** ของ scale bar = ความไม่แน่นอนที่วัดได้จริง เช่น `0.0005`
11. ติ๊ก check box scale bar ที่ใช้คำนวณ, **untick** check bar
12. Tools > **Optimize Cameras** (ติ๊ก f, cx, cy, k1–k3, p1–p2)
13. ดู **Error (m)** ในคอลัมน์ Reference pane → ค่านี้คือ residual ของ scale bar
14. **ตรวจสอบ**: ใช้ Ruler วัด check bar ในโมเดล → เทียบกับค่าจริง → **นี่คือตัวเลขที่ต้องรายงานในบทที่ 4**

15. Workflow > **Build Orthomosaic** → Surface type = **Model** → Projection = **Planar** → กำหนดระนาบด้วย marker 3 จุดบนหน้าเสา + ระบุแกน Horizontal/Vertical ([Agisoft helpdesk](https://agisoft.freshdesk.com/support/solutions/articles/31000154049-orthomosaic-generation-planar-projection-))
    - แนะนำ **mask ส่วนที่ไม่เกี่ยวออกจากภาพต้นฉบับ** (ท้องฟ้า พื้นดิน ต้นไม้) ก่อน build

## 5.3 GCP ใน DJI Terra — ถ้าจะใช้

- ต้องมี **≥4 GCP กระจายสม่ำเสมอ** ในขอบเขตการบิน หลีกเลี่ยงวางนอกพื้นที่บิน ควรอยู่บนพื้นเปิดโล่งราบ ([DJI Terra FAQ](https://enterprise.dji.com/dji-terra/faq))
- ตั้งค่า accuracy ของ GCP ให้ตรงกับความแม่นเครื่องมือที่ใช้วัดจริง: "the smaller the accuracy settings, the stronger the GCP's contribution to the triangulation model" ([DJI Support](https://support.dji.com/help/content?customId=en-us03400004973&spaceId=34&re=US&lang=en&documentType=artical&paperDocType=paper))
- Terra มี automatic GCP marking workflow ([Heliguy](https://www.heliguy.com/blogs/posts/automatic-gcp-marking-workflow-in-dji-terra/))
- **❌ Terra ไม่มี workflow scale-bar-only** — **ยังไม่ยืนยัน 100% ให้เช็คใน [DJI Terra User Manual v4.0](https://dl.djicdn.com/downloads/dji-terra/20240118/DJI_Terra_User_Manual_v4.0__EN.pdf) หมวด GCP Management** แต่จากเอกสารทั้งหมดที่ค้นมา ไม่พบการกล่าวถึง scale bar เลย
- **ข้อสรุปเชิงปฏิบัติ**: Terra เหมาะกับงานที่ RTK FIX ตลอด (บินบนสะพาน) ไม่เหมาะกับใต้สะพาน

## 5.4 ทางเลือกสำรอง: ใช้ของที่มีอยู่แล้วบนโครงสร้างเป็น scale

ถ้าติดเป้าไม่ได้จริง ๆ (ท้องสะพานสูง):
- **ระยะรูเหล็กยึดแบบ (form-tie hole)** — มักเป็นระยะมาตรฐาน แต่ต้องวัดยืนยันในสนาม
- **ความกว้างรอยต่อ expansion joint** — วัดจากพื้นได้
- **ความกว้างหน้าตัดเสา** จากแบบก่อสร้าง ⚠️ ต้องระวัง as-built ต่างจากแบบ
- **ระยะระหว่างศูนย์กลางเสา (span)** จากแบบ / วัดด้วย total station จากพื้น
- **ป้ายจราจร/เสากันตก** ที่มีขนาดมาตรฐาน

⚠️ ทุกวิธีนี้ต้อง **รายงานที่มาและความไม่แน่นอน** ในเล่ม ไม่ใช่แค่ใส่ตัวเลขลอย ๆ

---

# 6. Orthomosaic ของผนัง/เสา แล้ววัดรอยแตกบน ortho — แม่นเทียบกับวัดบนภาพเดี่ยวยังไง

## 6.1 ตัวเลขจริงจากงานวิจัย

### ฝั่ง ortho

[ISPRS Archives XLVIII-2/W11-2025, 139–146](https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/139/2025/isprs-archives-XLVIII-2-W11-2025-139-2025.pdf) — "Exploring the Potential of Super-Resolution for Crack Analysis in UAV Facade Orthomosaics of Small Bridges" (UAV-g 2025, Espoo):
- facade orthomosaic จริง GSD **~0.3 mm**
- **ความกว้าง**: relative error เฉลี่ย **149.11%** (ก่อน super-resolution) → **10.03%** (หลัง SR ด้วย Real-ESRGAN)
- **ความยาว**: **4.80%** → **1.93%**

**อ่านตัวเลขนี้ให้ดี — มันคือหัวใจของคำตอบข้อ 6:**
- error ความยาวบน ortho = **4.80%** → ดีมาก ใช้ได้เลย
- error ความกว้างบน ortho = **149.11%** → **แย่กว่าเดาสุ่ม** ที่ GSD 0.3 mm ซึ่งเป็น GSD ที่ดีมากแล้วสำหรับงาน UAV

**สาเหตุเชิงกลไก**: orthomosaic เกิดจาก resample + blend ภาพหลายใบเข้าระนาบเดียว รอยแตกกว้าง 0.5 mm ที่ GSD 0.3 mm = กว้าง ~1.7 pixel การ interpolate (bilinear/bicubic) ทำให้ขอบรอยแตกเบลอไป 1–2 px ซึ่งเป็น **error ระดับ 100% ของค่าที่วัด** ส่วนความยาว 500 mm = 1,667 px error 1–2 px = 0.1% ไม่มีนัยเลย

→ **error ที่เกิดจาก resampling เป็นค่าคงที่หน่วยพิกเซล แต่ผลกระทบเป็นสัดส่วนกลับกับขนาดของสิ่งที่วัด**

### ฝั่งภาพเดี่ยว

[Sensors 22(12), PMC9227050](https://pmc.ncbi.nlm.nih.gov/articles/PMC9227050/) — UAV + laser ranging module, กล้อง Sony DSC-RX0 (f = 9.346 mm, 4800×3200):

| ระยะถ่าย | Error สูงสุด | Relative error |
|---|---|---|
| 1.0 m | 1 mm | 0.2% |
| 2.0 m | 3 mm | 0.6% |
| 3.0 m | 6 mm | 0.8% |
| 2.5 m (สนามจริง) | — | <0.8% |
| 2.9 m (สนามจริง) | — | 1.8–3.0% |
| 4.6 m (สนามจริง) | — | 6.1% |

- ตรวจพบรอยแตกกว้าง **3.9 mm** ที่ระยะ 2.5 m
- **ผู้วิจัยแนะนำระยะวัด ไม่เกิน 3 m** และพื้นที่เป้าหมายไม่เกิน **1.0 × 1.0 m**
- เกิน 6 m ภาพไม่ชัดพอให้คนแยกแยะได้

**เทียบกันตรง ๆ: 0.8% (ภาพเดี่ยว @2.5 m) vs 149% (ortho @0.3 mm GSD ไม่ทำ SR)** — ห่างกัน ~186 เท่า

## 6.2 กฎ 3 pixel และการเลือก GSD

> "When the average GSD of images was ~1 mm, the thinnest detectable crack width was considered as **3 × GSD = 3 mm**"

**ตารางแปลง GSD → ความกว้างรอยแตกที่ตรวจได้ (คำนวณจากกฎ 3 px)**

| GSD | ตรวจได้ต่ำสุด (3px) | ระยะบิน — Mavic 3E wide | ระยะบิน — Mavic 3E tele | ระยะบิน — M4E tele |
|---|---|---|---|---|
| 0.10 mm | 0.30 mm | 0.37 m ❌ อันตราย | 1.9 m | 3.9 m |
| 0.26 mm | 0.78 mm | 0.95 m ⚠️ | 5.0 m | 10 m ✅ |
| 0.41 mm | 1.23 mm | 1.5 m ⚠️ | 7.8 m | 16 m ✅ |
| 0.82 mm | 2.5 mm | 3.0 m ✅ | 16 m | 32 m |
| 1.36 mm | 4.1 mm | 5.0 m ✅ | 26 m | 53 m |

*(ระยะคำนวณจากสูตรหัวข้อ 1.4 — Mavic 3E wide: GSD = D×0.273 mm/m; Mavic 3E tele (162mm eq, 4000×3000, FOV 15°): GSD = D×0.0527 mm/m; M4E tele (168mm eq, 48MP สมมติ 8000×6000): GSD = D×0.0258 mm/m* — **ตัวเลข M4E tele เป็นการคำนวณเอง ไม่ใช่ค่าที่ DJI ประกาศ; DJI ไม่ระบุ FOV และ max image size ของ tele บนหน้า spec ที่ดึงมา — ควรถ่ายเป้าที่รู้ขนาดจริงมาตรวจสอบก่อนใช้*)

## 6.3 ⚠️ ข้อค้นพบสำคัญที่ควรเขียนตรง ๆ ในเล่ม

**เกณฑ์ ACI 224R-01 tolerable crack width:**
| สภาพแวดล้อม | ความกว้างยอมรับได้ |
|---|---|
| Dry air / protective membrane | 0.016 in = **0.41 mm** |
| Humidity, moist air, soil | 0.012 in = **0.30 mm** |

([ACI 224R-01](https://studylib.net/doc/27964637/aci-224r-01))

**ตอม่อสะพานในไทย = humid/moist/soil → เกณฑ์ 0.30 mm**

จากตาราง 6.2: ต้องการ GSD ≤ 0.10 mm → Mavic 3E wide ต้องบินห่าง **0.37 m** (บินไม่ได้ — blind zone LRF คือ 1 m, obstacle sensing ต่ำสุด 0.4 m) หรือ M4E tele ที่ **3.9 m** (ทำได้ แต่ต้องนิ่งมากและอาจติด min focus distance ของเลนส์ tele — **ยังไม่ยืนยัน min focus distance**)

**→ ข้อสรุปที่ซื่อสัตย์สำหรับ thesis:**
> UAV โดยลำพังที่ระยะปลอดภัย **ไม่สามารถตรวจจับรอยแตกที่เกณฑ์ serviceability (0.3 mm) ได้อย่างน่าเชื่อถือ** สิ่งที่ทำได้จริงคือรอยแตกที่มีนัยสำคัญเชิงโครงสร้าง (**≥ 1 mm** ด้วยกล้อง tele, **≥ 2.5 mm** ด้วยกล้อง wide ที่ 3 m)

นี่ไม่ใช่จุดอ่อนของงาน — เป็น **ผลการวิจัยที่มีค่า** และควรเขียนเป็นข้อจำกัดที่ระบุปริมาณได้ พร้อมข้อเสนอแนะ (tele lens / super-resolution / hybrid manual inspection สำหรับ critical zone)

หมายเหตุ: มีงานที่รายงานว่าตรวจได้ **<0.2 mm** ([ScienceDirect S0926580523001899](https://www.sciencedirect.com/science/article/abs/pii/S0926580523001899)) แต่ต้องอ่านเงื่อนไข standoff/กล้อง/การประมวลผลให้ละเอียดก่อนอ้าง — **ยังไม่ได้ยืนยันเงื่อนไขการทดลอง**

## 6.4 ปัญหาอื่นของการวัดบน ortho ที่ต้องระวัง

1. **สมมติฐานระนาบ** — ortho บังคับให้ผิวเป็นระนาบเดียว เสากลม/ผิวโค้ง/บัวปูน จะถูกยืดผิด → รอยแตกที่พาดข้ามความโค้งวัดความยาวเกินจริง
2. **Blending seam** — จุดที่ ortho เปลี่ยนภาพต้นฉบับ อาจตัดรอยแตกขาดหรือทำให้เห็นซ้อน 2 เส้น
3. **การเลือกภาพต้นฉบับ** — ortho เลือกภาพที่ "ตั้งฉากที่สุด" ต่อพิกเซล ซึ่งอาจไม่ใช่ภาพที่คมที่สุด
4. **Resolution cap** — ในทางกลับกัน ortho ก็อาจตั้ง resolution สูงกว่า GSD จริงได้ ทำให้ดูเหมือนละเอียดกว่าความจริง (ODM มี `--orthophoto-resolution` แต่ docs ระบุว่า "capped by a GSD estimate")
5. **ขนาดไฟล์** — quay wall 100×20 m ที่ 2.28 mm GSD ได้ ortho **63,747 × 36,319 px** ([Sensors 25(14):4325](https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/)) = ~2.3 Gpixel เปิดใน QGIS/Photoshop ไม่ไหว ต้อง tile

## 6.5 ✅ วิธีที่ถูกต้อง — Hybrid (คำตอบสุดท้ายของข้อ 6)

```
ความกว้างรอยแตก  →  วัดบน "ภาพเดี่ยว" ความละเอียดเต็ม native pixel
                     ที่ GSD รู้ค่าแน่นอน + แก้ perspective แล้ว
                     (error ~0.8% ที่ 2.5 m)

ความยาว/พื้นที่/  →  วัดบน ortho หรือ 3D model
รูปแบบรอยแตก        (error ~4.8% ก่อน SR, 1.93% หลัง SR)

ตำแหน่ง/ชิ้นส่วน  →  จาก 3D model + camera pose
                     (บอกได้ว่ารอยแตกอยู่ที่ตอม่อต้นที่ 3 หน้าทิศเหนือ สูง 4.2 m)

การไม่นับซ้ำ      →  back-project detection จากภาพเดี่ยว ลงบน 3D model
                     แล้ว merge ตาม 3D proximity
```

**สำคัญ**: การจะวัดความกว้างบนภาพเดี่ยวได้ ต้องรู้ GSD ของภาพนั้น ซึ่งมาจาก **camera pose ของ SfM** → **ยังต้องทำ photogrammetry อยู่ดี** แค่ไม่ได้วัดบน ortho เท่านั้น

งานวิจัยยืนยัน pattern นี้: "in UAV-based bridge inspection, **the angle between the measured plane and the imaging plane must be corrected** in pixel resolution calculation" — คือต้องแก้มุมเอียงก่อนวัด ซึ่งข้อมูลมุมมาจาก SfM

---

# 7. ถ้าเป้าหมายคือ "ให้ AI เห็นรอยแตกชัด" — จำเป็นต้อง stitch ไหม

## 7.1 คำตอบตรง ๆ: **ไม่จำเป็น สำหรับการ "เห็น" — แต่จำเป็นสำหรับการ "ให้เกรด"**

## 7.2 หลักฐานว่า AI ไม่ได้อยากได้ภาพใหญ่

CNN/segmentation model สำหรับ crack detection **ทำงานบน tile เล็ก** ไม่ใช่ภาพใหญ่:

> "High-resolution orthophotos for crack detection are **too large to process directly** (a 100 × 20 m site reached 63,747 × 36,319 pixels), so they must be divided into appropriately sized tiles. Optimal performance is achieved when the **tile size matches the training data size**, with **256 × 256 pixels commonly adopted**" ([Sensors 25(14):4325](https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/))

**นี่คือ logic ที่ทำลายเหตุผลของการ stitch เพื่อ AI โดยสิ้นเชิง:**
```
ภาพเดี่ยว 5280×3956 → tile 256×256 → ได้ 20×15 = 300 tiles ต่อภาพ
Ortho 63747×36319   → tile 256×256 → ได้ 249×142 = 35,358 tiles
```
ทั้งสองทางจบที่ tile 256×256 เหมือนกัน แต่ทางแรก **ไม่ผ่าน resampling** → คมกว่า

**ยิ่งไปกว่านั้น**: ถ้าใครเอา ortho ไป resize ให้พอดี input ของโมเดล (เช่น 512×512) จะทิ้งข้อมูล 99.99% และรอยแตกหายเกลี้ยง — ข้อผิดพลาดที่พบบ่อยมาก

## 7.3 แต่ stitch มีเหตุผลจริง 5 ข้อ — และตรงกับโจทย์ thesis นี้พอดี

| # | เหตุผล | เกี่ยวกับ BMMS/T-BHI ยังไง |
|---|---|---|
| 1 | **ไม่นับซ้ำ** — overlap 85% แปลว่ารอยแตกเดียวปรากฏใน ~7 ภาพ ถ้าไม่ merge จะรายงาน 7 รอย | จำนวนความเสียหายเข้าสูตร condition rating โดยตรง |
| 2 | **ระบุตำแหน่งบนชิ้นส่วน** — "ตอม่อ P3 หน้าทิศเหนือ ระดับ +4.2 m" | NBI/BMMS ให้เรตติ้ง **ต่อชิ้นส่วน** ไม่ใช่ต่อรูป |
| 3 | **คิดปริมาณ (quantity)** — ความยาวรวม/พื้นที่/สัดส่วน % ของผิวที่เสียหาย | **AASHTO element-level inspection ต้องการปริมาณต่อ Condition State (CS1–CS4)** ไม่ใช่แค่ "มี/ไม่มี" |
| 4 | **ติดตามตามเวลา** — เปรียบเทียบการตรวจปีนี้กับปีหน้าที่พิกัดเดียวกัน | หัวใจของ Bridge Management System |
| 5 | **ส่งมอบที่วิศวกรยอมรับ** — ภาพ 600 ใบไม่มีใครดู แต่ ortho 1 แผ่นมีจุดแดงระบุตำแหน่งใช้งานได้จริง | ความเป็นไปได้ในการนำไปใช้จริง |

## 7.4 เปรียบเทียบ 3 ทางเลือก

| แนวทาง | ข้อดี | ข้อเสีย | ได้ condition rating ไหม |
|---|---|---|---|
| **A. ภาพเดี่ยวล้วน** (ไม่ stitch) | • คมที่สุด ไม่มี resampling<br>• ง่าย เร็ว ไม่ต้องซื้อซอฟต์แวร์<br>• ไม่ล้มเมื่อ SfM fail<br>• ทำงานได้แม้ GPS ตาย | • นับซ้ำ<br>• ไม่รู้ตำแหน่ง<br>• ไม่รู้ปริมาณ<br>• ไม่รู้ GSD → **วัดความกว้างเป็น mm ไม่ได้** | ❌ ได้แค่ "พบ/ไม่พบ" |
| **B. Ortho ล้วน** (detect บน ortho) | • ตำแหน่ง+ปริมาณครบ<br>• ส่งมอบสวย<br>• ไม่นับซ้ำโดยธรรมชาติ | • **error ความกว้าง 149%** ([ISPRS](https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/139/2025/isprs-archives-XLVIII-2-W11-2025-139-2025.pdf))<br>• SfM ล้มบนคอนกรีตเรียบ<br>• เสาโค้งบิดเบี้ยว<br>• ไฟล์ยักษ์ | ⚠️ ได้ แต่ความกว้างเชื่อไม่ได้ |
| **C. ⭐ Hybrid** — detect บนภาพเดี่ยว + back-project ลง 3D model | • คมที่สุด **และ** มีตำแหน่ง/ปริมาณ<br>• error ความกว้างต่ำ (~0.8%)<br>• ถ้า SfM ล้ม ยังเหลือผล detect | • pipeline ซับซ้อนกว่า<br>• ต้องเขียนโค้ด back-projection เอง | ✅ ได้ครบ |

## 7.5 ⭐ Pipeline ที่แนะนำสำหรับ ku_project_jop

```
[1] UAV เก็บภาพ
    ├─ facade strips / orbit, overlap 85/75, GSD ≤0.5 mm
    ├─ scale bar 1.000 m × 3 บาร์ (1 บาร์เป็น check)
    └─ ภาพ context ทั้งสะพาน 10-20 ใบ

[2] SfM (Metashape Pro) — ทำเพื่อ "camera pose + 3D geometry"
    ├─ align + detect markers + scale bars + optimize
    ├─ export camera poses (XML)  ← ของสำคัญ ไม่ใช่ ortho
    ├─ build model (mesh/point cloud)
    └─ [optional] planar-projection ortho ต่อหน้าเสา ← ใช้ทำรูปประกอบเล่ม

[3] คำนวณ GSD ต่อภาพ จาก camera pose + ระนาบผิวที่ fit
    GSD_i = ระยะกล้อง_i→ระนาบ × ค่าคงที่กล้อง / cos(มุมตกกระทบ)

[4] AI detection บนภาพเดี่ยว "ความละเอียดเต็ม"
    ├─ tile 256×256 หรือ 512×512, overlapping tiling
    │   (overlapping tiling ให้ Recall ดีขึ้น ~24% — Sensors 25(14):4325)
    ├─ segmentation model → crack mask ระดับพิกเซล
    └─ วัดความกว้างจาก mask × GSD_i  ← เลข mm จริงเกิดตรงนี้

[5] Back-project detection → 3D model
    ├─ ray-cast จาก camera pose ผ่านพิกเซล → หาจุดตัดบน mesh
    ├─ merge detection ที่อยู่ใกล้กันใน 3D (dedup)
    └─ ได้ crack map 3D: ตำแหน่ง + ความกว้าง(max) + ความยาว + ชิ้นส่วน

[6] MLLM ให้ condition rating
    ├─ input: crop ภาพเดี่ยวรอบรอยแตก (ไม่ใช่ ortho ทั้งแผ่น)
    │        + ตัวเลขที่วัดได้จาก [4][5]
    │        + บริบทชิ้นส่วน (ตอม่อ/คาน/แผ่นพื้น)
    └─ output: condition rating ตาม BMMS / NBI / T-BHI
```

**เหตุผลว่าทำไม [6] ต้องใช้ crop ไม่ใช่ ortho**: MLLM มี input resolution จำกัด (มักย่อภาพลงเหลือ ~1000px ด้านยาว) ป้อน ortho 63,747 px ให้ = ป้อนภาพเบลอ ป้อน crop 512×512 รอบรอยแตกที่ native resolution = MLLM เห็นรอยแตกจริง

งานวิจัยที่ทำ pattern คล้ายกันนี้:
- [Tunnelling & Underground Space Technology (2024)](https://www.sciencedirect.com/science/article/pii/S0886779824005972) — "Photogrammetry-based tunnel crack digitalization and documentation method using deep learning"
- [arXiv 2501.09203](https://arxiv.org/pdf/2501.09203) — "3D Modeling and Automated Measurement of Concrete Cracks via Segment Anything Refinement and Visual Inertial LiDAR Fusion"

## 7.6 เชื่อมกับเป้าหมาย T-BHI / BMMS / NBI ของงานวิจัย

| ระบบ | หน่วยของการให้เรตติ้ง | ต้อง stitch ไหม |
|---|---|---|
| **NBI (US)** | 1 rating (0–9) ต่อ component (deck/superstructure/substructure) | ⚠️ ไม่จำเป็นเชิงบังคับ แต่ต้องรู้ว่ารอยอยู่ component ไหน |
| **AASHTO element-level** | **ปริมาณ (ตร.ม./ม./จำนวน) ต่อ Condition State 1–4 ต่อ element** | ✅ **จำเป็น** — ไม่มีปริมาณ ให้เรตไม่ได้ |
| **BMMS ไทย** | เกณฑ์เฉพาะ — **ยังไม่ยืนยัน ต้องดูคู่มือกรมทางหลวง/ทางหลวงชนบทฉบับจริง** | ต้องตรวจสอบ |
| **T-BHI** | ดัชนีรวมถ่วงน้ำหนักตามชิ้นส่วน — **ยังไม่ยืนยันสูตรและเกณฑ์** | น่าจะต้องการปริมาณต่อชิ้นส่วน |

**→ ถ้า thesis ตั้งเป้า output เป็น condition rating ระดับชิ้นส่วน (ซึ่งเป็นสิ่งที่ T-BHI ต้องการ) การ stitch ไม่ใช่ทางเลือก แต่เป็นข้อบังคับ** เพียงแต่ stitch เพื่อ **เรขาคณิตและปริมาณ** ไม่ใช่เพื่อป้อน AI

## 7.7 แผนสำรองที่ควรมี (สำคัญมาก)

SfM บนคอนกรีตเรียบ **ล้มได้จริง** และล้มบ่อย ต้องออกแบบ pipeline ให้ทนต่อความล้มเหลว:

```
ถ้า SfM สำเร็จ  → ได้ครบ: ความกว้าง(mm) + ตำแหน่ง 3D + ปริมาณ + condition rating
ถ้า SfM ล้ม     → ยังเหลือ: detection บนภาพเดี่ยว + ความกว้างจาก LRF/เป้าในเฟรม
                  (เสียแค่ตำแหน่ง 3D กับปริมาณรวม)
```

การออกแบบให้ **ขั้นที่ 4 (AI detection) ไม่ขึ้นกับขั้นที่ 2 (SfM)** คือการตัดสินใจเชิงสถาปัตยกรรมที่สำคัญที่สุดของทั้งระบบ — ทำให้ผลงานยังมีค่าแม้ photogrammetry ไม่สำเร็จ และเป็นจุดที่กรรมการสอบจะถามแน่นอน

---

# ภาคผนวก A — แผนการบินที่พร้อมใช้ (ตอม่อสะพาน 1 ต้น)

**สมมติฐาน**: ตอม่อสี่เหลี่ยม 1.5 × 1.5 m สูง 8 m, โดรน Mavic 3E (หรือ M4E), มี RTK บนพื้นที่โล่ง

```
### ก่อนบิน
- ติด coded target 12 จุด บนตอม่อ (ระดับ 0.5 / 2.5 / 4.5 / 6.5 m × 4 หน้า)
- วาง scale bar 1.000 m แนวดิ่ง 1 อัน + แนวนอน 1 อัน + check bar 1 อัน
- ตั้งกล้อง: mechanical shutter ON, ISO 100-200, shutter ≥1/500, AF ล็อค

### เที่ยวที่ 1 — Context (ผูกโมเดล)
orbit รัศมี 15 m, ระดับ 5 m, กล้อง -20°, 12° interval → 30 ภาพ
GSD ≈ 15 × 0.273 = 4.1 mm/px

### เที่ยวที่ 2-5 — Facade แต่ละหน้า (4 หน้า)
D = 1.5 m, กล้อง 0° ตั้งฉากหน้าเสา
  footprint = 2.16 W × 1.62 H m, GSD = 0.41 mm/px
  เลื่อนแนวดิ่ง @85% = 0.24 m → 8/0.24 = 34 แถว
  2 คอลัมน์ @60% side → ห่าง 0.86 m
  → 68 ภาพ/หน้า × 4 = 272 ภาพ
ตรวจได้: รอยแตก ≥ 1.2 mm (3×GSD)

### เที่ยวที่ 6 — Convergent (ผูก 4 หน้าเข้าด้วยกัน + แก้ doming)
orbit รัศมี 4 m, 3 ระดับ (2/4/6 m), กล้อง ±25° สลับ, 15° interval
  → 24 ภาพ/ระดับ × 3 = 72 ภาพ

### เที่ยวที่ 7 — Detail (ถ้ามี tele) — เฉพาะบริเวณที่พบรอยแตก
M4E tele, D = 8 m, GSD ≈ 0.21 mm/px → ตรวจได้ ≥0.6 mm
  ถ่ายมือ 20-40 ภาพ ที่จุดสนใจ

รวม ≈ 374-414 ภาพ, ~3 แบตเตอรี่, ~50 นาที
```

**ตรวจสอบก่อนกลับ (สำคัญ — ทำในสนาม อย่ารอกลับบ้าน)**
- [ ] เปิดดูภาพ 5 ใบสุ่ม ซูม 100% เห็นเนื้อคอนกรีตเป็นเกล็ดหรือเบลอ?
- [ ] coded target ทุกอันปรากฏชัดในภาพ ≥3 ใบ?
- [ ] scale bar ทั้ง 3 อันถ่ายติดครบ?
- [ ] มีภาพที่ผิวเรียบเต็มเฟรมไม่มีบริบทเลยกี่ใบ? (ถ้าเยอะ ต้องบินซ้ำห่างขึ้น)

---

# ภาคผนวก B — ข้อจำกัดและสิ่งที่ยังไม่ยืนยัน (อ่านก่อนอ้างอิง)

| หัวข้อ | สถานะ | ต้องไปหาที่ไหน |
|---|---|---|
| Metashape **Standard** ($179/$59 edu) มี marker/scale bar/planar ortho ไหม | ❌ **ยังไม่ยืนยัน — ห้ามซื้อก่อนเช็ค** | agisoft.com/features/compare |
| DJI Terra ราคา 2026 (Standard/Flagship) | ⚠️ แหล่งรองขัดแย้งกัน | ตัวแทนจำหน่าย DJI Enterprise ในไทย |
| DJI Terra รับ non-geotagged images ได้ไหม | ❌ ยังไม่ยืนยัน | DJI Terra User Manual v4.0 |
| DJI Terra มี scale-bar workflow ไหม | ❌ ไม่พบในเอกสารทั้งหมดที่ค้น — น่าจะไม่มี | DJI Terra User Manual v4.0 หมวด GCP Management |
| Pix4Dinspect ราคา 2026 | ❌ ยังไม่ยืนยัน (แหล่งเก่า 2020: $130/mo) | pix4d.com/pricing ติดต่อ sales |
| Gimbal tilt range (เงยขึ้นได้กี่องศา) Mavic 3E / M4E | ❌ ยังไม่ยืนยัน — spec page ไม่ระบุ | enterprise.dji.com specs หมวด Gimbal |
| M350 รองรับ upward gimbal mount ไหม | ❌ ยังไม่ยืนยัน | DJI M350 payload compatibility |
| Mavic 3T LRF ระยะ 200 m หรือ 1200 m | ⚠️ แหล่งขัดแย้ง | enterprise.dji.com/mavic-3-enterprise/specs |
| M4E tele max image size (8000×6000?) และ FOV | ⚠️ คำนวณจาก equiv focal length ไม่ใช่ค่าประกาศ | ต้องถ่ายเป้ารู้ขนาดจริงมาตรวจสอบ |
| Min focus distance ของเลนส์ tele (ถ่ายใกล้ได้แค่ไหน) | ❌ ยังไม่ยืนยัน | ทดสอบเองในสนาม |
| BMMS ไทย เกณฑ์ความกว้างรอยแตก | ❌ **ไม่พบเอกสารออนไลน์** | คู่มือตรวจสอบสะพาน กรมทางหลวง / กรมทางหลวงชนบท (ต้องขอเอกสารตัวจริง) |
| T-BHI สูตรและเกณฑ์ | ❌ ยังไม่ยืนยัน | รายงานวิจัยทุน วช. ปีงบ 68 ต้นทาง |
| ราคา Flyability Elios 3 / Skydio X10 | ❌ ยังไม่ยืนยัน | ตัวแทนจำหน่าย |
| DJI WPML schema version ล่าสุด | ❌ ยังไม่ยืนยัน | developer.dji.com |
| กฎหมายบินโดรนใกล้สะพาน/ทางหลวง ในไทย | ❌ **ไม่ได้ค้น** | CAAT + กสทช. + ขออนุญาตเจ้าของโครงสร้าง |
| ตัวเลขเชิงปริมาณของ artificial texture (F1000Research) | ❌ เว็บ block การดึงข้อมูล | f1000research.com/articles/13-1479 |

---

# ภาคผนวก C — สรุปคำตอบต่อโจทย์เฉพาะหน้าของคุณ

> **"อยากทำโปรแกรมการบินให้โดรนบินใกล้วัตถุมากขึ้น เพื่อให้เห็นรอยแตกชัดขึ้น"**

1. **ใช้ DJI Pilot 2 → Slope mission** เป็นทางลัดที่เร็วที่สุด (ตั้ง GSD/ระยะ/overlap ได้โดยตรง แอปแสดงระยะห่างให้ ต้องมี RTK) — Mavic 3E series และ M4 series รองรับ
2. **สำหรับใต้สะพาน (RTK ตาย) ไม่มี mission ไหนใช้ได้** ต้องบินมือ + interval shooting 2 วินาที + ไต่ 0.2–0.3 m/s
3. **บินใกล้อย่างเดียวไม่พอ** — บินใกล้ ⇒ ฉากเป็นคอนกรีตเรียบเต็มเฟรม ⇒ SfM ล้ม ⇒ ไม่ได้ทั้งโมเดลและ GSD ⇒ วัด mm ไม่ได้ **ต้องติด coded target บนผิวควบคู่ไปเสมอ**
4. **ทางเลือกที่ดีกว่าบินใกล้: ใช้เลนส์ tele บินไกล** — M4E tele ที่ 10 m ได้ GSD 0.26 mm/px ดีกว่า wide ที่ 1 m (0.27 mm/px) แถมปลอดภัยกว่ามาก มีบริบทในเฟรมมากกว่า และ SfM ทำงานได้ดีกว่า

> **"อยากรู้ว่าโดรนอยู่ห่างจากวัตถุเท่าไหร่"**

| ต้องการเพื่อ | ใช้อะไร | ความแม่น |
|---|---|---|
| **ความปลอดภัยขณะบิน** | Vision obstacle sensing (fwd 0.4–22.5 m) + LRF | เพียงพอ |
| **ตั้งค่า mission** | Slope mission แสดงระยะบนหน้าจอ | เพียงพอ |
| **คำนวณ GSD เพื่อวัดรอยแตกเป็น mm** | ❌ LRF ไม่พอ (±0.20 m ที่ 3 m = ±6.7%) <br>✅ **เป้าความยาวรู้ค่าในเฟรม** หรือ **camera pose จาก SfM + scale bar** | ✅ ต้องใช้ตัวนี้ |

**นี่คือประเด็นเดียวที่สำคัญที่สุดของทั้งรายงาน**: ถ้าจะรายงานความกว้างรอยแตกเป็นมิลลิเมตรในเล่ม thesis ตัวเลขนั้นต้องสาวกลับไปถึง **เป้าอ้างอิงที่วัดด้วยเครื่องมือสอบเทียบแล้ว** ไม่ใช่ค่าจาก LRF ของโดรน มิฉะนั้นตัวเลขทุกตัวในบทที่ 4 จะไม่มี traceability และถูกกรรมการถามแน่นอน


## KEY NUMBERS
- Overlap แนะนำสำหรับ facade/vertical: side overlap ~80%, front overlap 80-90%: side 80%, front 80-90%  [high] https://www.pix-pro.com/blog/vertical-photogrammmetry
- Overlap ขั้นต่ำที่ 3D reconstruction ของสะพานสำเร็จ: 66%  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/
- การรวม flight route แบบ overall+partial ให้คุณภาพโมเดลดีกว่า route เดียว: 46.7%  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/
- UAV bridge study: GSD ดีที่สุดที่ระดับบิน 10 m: 3.71 mm/pixel (ที่ 10 m); 18.5 mm/pixel (ที่ 40 m)  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/
- ความหนาแน่นจุดที่ 10 m เทียบ 40 m: 298,474 pts/m³ vs 13,117 pts/m³  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/
- Urban/facade double grid overlap ที่แนะนำ: frontal 75%, side 60%  [medium] https://t2d2.ai/blog/harnessing-photogrammetry-revolutionizing-building-facade-inspection-with-drones
- มุมกล้องที่ facade จะมองเห็นได้ในเที่ยวบิน mapping (Pix4D): 10°–35° (0° = มองลง)  [high] https://support.pix4d.com/hc/en-us/articles/202557459
- Pix4D circular mission: angle interval vs จำนวนภาพ/เวลา/GSD (อาคาร 30×30 m สูง 18 m): 12°→31 ภาพ/4:29/3.11 cm; 8°→62 ภาพ/5:44/2.87 cm; 4°→124 ภาพ/9:00/2.84 cm  [high] https://www.pix4d.com/blog/3d-models-choose-angle-between-images-circular-missions
- Circlegrammetry: มุมกล้องเอียงที่ใช้: 45–70°  [medium] https://manuals-ugcs.sphengineering.com/docs/circlegrammetry-area
- ความเร็วไต่ที่แนะนำสำหรับ vertical facade scan: 0.2–0.3 m/s  [medium] https://www.pix-pro.com/blog/vertical-photogrammmetry
- ระยะห่างผนังที่แนะนำในตัวอย่าง facade scan จริง: 3 m  [medium] https://www.pix-pro.com/blog/vertical-photogrammmetry
- DJI Mavic 3E wide camera: sensor/ความละเอียด/FOV/focal: 4/3 CMOS, 20 MP, 5280×3956 px, FOV 84°, equiv 24mm, f/2.8-f/11  [high] https://enterprise.dji.com/mavic-3-enterprise/specs
- DJI Mavic 3E tele camera: 1/2" CMOS, 12 MP, 4000×3000 px, equiv 162mm, FOV 15°  [high] https://enterprise.dji.com/mavic-3-enterprise/specs
- Mavic 3E GSD ที่ระดับบิน 100 m (DJI ประกาศ): GSD = H/37 ≈ 2.7 cm ที่ 100 m  [medium] https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series
- GSD Mavic 3E wide (คำนวณจาก FOV 84° + 5280×3956) — ตรวจทานกับค่า DJI แล้วตรงกัน: GSD (mm) = D (m) × 0.273 → 3 m = 0.82 mm/px, 1.5 m = 0.41 mm/px  [medium] https://enterprise.dji.com/mavic-3-enterprise/specs
- Mavic 3E interval shooting ต่ำสุด: 0.7 วินาที  [medium] https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series
- Mavic 3E mechanical shutter อายุการใช้งาน: 200,000 ครั้ง  [medium] https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series
- Mavic 3E/3T RTK accuracy: H: 1 cm + 1 ppm; V: 1.5 cm + 1 ppm  [high] https://enterprise.dji.com/mavic-3-enterprise/specs
- DJI Matrice 4E/4T laser rangefinder measurement range: 1800 m (1 Hz) @20% reflectivity; oblique 1:5 = 600 m; blind zone 1 m  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI M4 series LRF accuracy: 1–3 m: system error <0.3 m, random <0.1 m @1σ; ระยะอื่น ±(0.2 + 0.0015D) m  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI M4 series obstacle sensing ranges: Forward/backward binocular 0.4–22.5 m (measurement 0.4–200 m); lateral 0.5–32 m; downward 0.3–18.8 m  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI M4E camera set: Wide 4/3 CMOS 20 MP (24mm, f/2.8-f/11); Medium tele 1/1.3" 48 MP (70mm f/2.8); Tele 1/1.5" 48 MP (168mm f/2.8)  [high] https://enterprise.dji.com/matrice-4-series/specs
- DJI M4 series RTK accuracy / flight time: RTK 1 cm+1 ppm (H), 1.5 cm+1 ppm (V); flight time 49 min (standard props)  [high] https://enterprise.dji.com/matrice-4-series/specs
- GSD M4E tele คำนวณจาก equiv focal 168mm + สมมติ 8000×6000 px (ไม่ใช่ค่าประกาศ DJI): GSD (mm) = D (m) × 0.0258 → 10 m = 0.26 mm/px  [low] https://enterprise.dji.com/matrice-4-series/specs
- DJI Pilot 2 Slope mission: ตั้งค่าอะไรได้ + ข้อบังคับ: ตั้ง GSD, relative distance, overlap; แสดงระยะจากเป้าหมาย; บังคับเปิด RTK; ตัวอย่างทำได้ GSD 1 cm  [high] https://enterprise-insights.dji.com/blog/automated-data-capture-for-slope-surfaces-and-building-facades
- DJI Pilot 2 route types บน M4E: Waypoint, Area (Ortho + Oblique), Linear, Slope, Geometric, Smart 3D Capture  [medium] https://shop.coptrz.com/blogs/news/dji-enterprise-app-v2-5-3-pilot-2-app-v17-1-5-14-update
- Smart Oblique คุณภาพข้อมูล: 'produces less than optimal data' — แนะนำใช้เฉพาะเมื่อเวลา/แบตจำกัด  [high] https://help.propelleraero.com/hc/en-us/articles/19384415429911-How-to-Plan-a-3D-Oblique-Mission-with-DJI-Pilot-2
- DJI Terra reconstruction accuracy เมื่อ RTK FIX ไม่ใช้ GCP: H = 1 cm + 1~2 × GSD; V = 2 cm + 1.5~3 × GSD (oblique)  [high] https://support.dji.com/help/content?customId=en-us03400004973&spaceId=34&re=US&lang=en&documentType=artical&paperDocType=paper
- DJI Terra GCP ขั้นต่ำ: ≥4 GCP กระจายสม่ำเสมอในขอบเขตการบิน  [high] https://enterprise.dji.com/dji-terra/faq
- DJI Terra hardware requirement: ขั้นต่ำ 32 GB RAM + NVIDIA 4 GB VRAM (SM 6.1+); แนะนำ 64 GB + RTX 2070+; Windows 10+ 64-bit เท่านั้น ไม่รองรับ macOS/non-NVIDIA  [high] https://enterprise.dji.com/dji-terra/faq
- DJI Terra ความจุการประมวลผลภาพ: RAM ว่างเพิ่มทุก 10 GB ประมวลผลได้เพิ่ม ~4,000 ภาพ; cluster ~6,000 ภาพต่อ 1 GB idle memory  [high] https://enterprise.dji.com/dji-terra/faq
- DJI Terra รับภาพ facade route / gimbal 0° ได้: รองรับ; oblique รองรับเฉพาะ 3D reconstruction ไม่รองรับ 2D; camera tilt ถึง 35° สำหรับ 2D (v3.1.0+)  [high] https://repair.dji.com/help/content?customId=01700005092&spaceId=17&re=US&lang=en&documentType=&paperDocType=ARTICLE
- DJI Terra versions 2026: Agriculture (1 ปี), Standard (perpetual), Flagship (perpetual), Education (perpetual), Cluster (offline)  [high] https://enterprise.dji.com/dji-terra/faq
- DJI Terra ราคา (แหล่งรอง — ยังไม่ยืนยันกับ DJI โดยตรง): Pro $1,299/yr, Electricity $2,599/yr, Agriculture $999/yr USD  [low] https://www.thefuture3d.com/software/dji-terra/
- PIX4Dmapper ราคาทางการ: $332.50/เดือน หรือ $3,990/ปี USD  [high] https://www.pix4d.com/pricing/pix4dmapper/
- PIX4Dmapper perpetual license (แหล่งรอง): ~$5,990 (ก่อน 5 ม.ค. 2026) → ~$14,990 (หลัง) USD  [low] https://checkthat.ai/brands/pix4d/pricing
- Pix4Dmapper template '3D Models' ไม่สร้าง orthomosaic: No orthomosaic generated; ต้องใช้ Orthoplane tool สำหรับ facade ortho  [high] https://support.pix4d.com/hc/en-us/articles/205319155
- Agisoft Metashape ราคา node-locked (ทางการ): Professional $3,499; Standard $179 USD (perpetual, ไม่จำกัดเวลา)  [high] https://www.agisoft.com/buy/online-store/
- Agisoft Metashape educational license (แหล่งรอง): Standard $59; Professional $549 USD  [medium] https://www.agisoft.com/buy/online-store/educational-license/
- RealityCapture / RealityScan 2.0 ฟรีเมื่อรายได้ต่ำกว่าเกณฑ์: ฟรีสำหรับนักศึกษา/การศึกษา/บริษัทรายได้ <$1M USD/ปี; เกินนั้น $1,250/seat/ปี; Unreal Subscription $1,850/user/ปี  [high] https://www.realityscan.com/license
- ODM default flags ที่ต้องเปลี่ยนสำหรับ facade: use-3dmesh (default False→True), min-num-features (default 10000→20000+), pc-quality (default medium→ultra), mesh-octree-depth (default 11→12), mesh-size (default 200000→500000), camera-lens (auto→brown)  [high] https://docs.opendronemap.org/arguments/
- COLMAP รองรับ dense reconstruction จาก known camera poses โดยไม่ต้องทำ sparse ก่อน: 'sparse reconstruction is not necessary to compute a dense model from known camera poses'  [high] https://colmap.github.io/faq.html
- กฎ pixel ต่อความกว้างรอยแตกขั้นต่ำ: 3 × GSD (ที่ GSD ~1 mm ตรวจได้ต่ำสุด 3 mm)  [medium] https://www.sciencedirect.com/science/article/abs/pii/S0926580517311366
- UAV crack measurement error ตามระยะถ่าย (Sony DSC-RX0, f=9.346mm, 4800×3200): 1.0 m: 1 mm (0.2%); 2.0 m: 3 mm (0.6%); 3.0 m: 6 mm (0.8%); สนามจริง 2.5 m <0.8%, 2.9 m 1.8-3.0%, 4.6 m 6.1%  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC9227050/
- ระยะวัดสูงสุดที่แนะนำสำหรับ UAV crack measurement: ไม่เกิน 3 m; พื้นที่เป้าหมายไม่เกิน 1.0 × 1.0 m; ตรวจพบรอยแตก 3.9 mm ที่ 2.5 m; เกิน 6 m ภาพไม่ชัดพอ  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC9227050/
- Facade orthomosaic crack measurement error (GSD ~0.3 mm) ก่อน/หลัง super-resolution: ความกว้าง: 149.11% → 10.03%; ความยาว: 4.80% → 1.93%  [high] https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/139/2025/isprs-archives-XLVIII-2-W11-2025-139-2025.pdf
- Quay wall AI crack detection: drone/altitude/overlap/GSD/software/GCP: Autel EVO II Pro, 10 m, ~80% overlap, GSD 2.28 mm/px, Metashape Pro v2.2.0, 5 GCP  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- Quay wall study accuracy: Planimetric RMSE 0.89 cm; vertical RMSE 2.74 cm  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- ขนาด orthophoto ของพื้นที่ 100 × 20 m ที่ GSD 2.28 mm: 63,747 × 36,319 pixels  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- ขนาด tile มาตรฐานสำหรับ deep learning crack detection: 256 × 256 pixels (ต้องตรงกับขนาด training data)  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- ผลของ overlapping tiling ต่อ Recall: Recall ดีขึ้น ~24% relative  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- Quay wall AI performance: Precision 81.0%, Recall 62.9%; F1 สูงสุด 88% ที่ '10 m + pseudo 15 m'; เป้าหมายรอยแตก 1 mm (เกณฑ์ตรวจสอบทางการคือ 3 mm)  [high] https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- ACI 224R-01 tolerable crack width: Dry air/protective membrane 0.016 in = 0.41 mm; Humidity/moist air/soil 0.012 in = 0.30 mm  [medium] https://studylib.net/doc/27964637/aci-224r-01
- UAV crack detection ที่รายงานว่าตรวจได้ต่ำกว่า 0.2 mm: <0.2 mm (ยังไม่ได้ตรวจสอบเงื่อนไขการทดลอง)  [low] https://www.sciencedirect.com/science/article/abs/pii/S0926580523001899
- งานที่ตรวจพบรอยแตก 116 จุดจากภาพ 647 ใบ: GSD 0.21 cm/pixel = 2.1 mm/pixel  [medium] https://www.mdpi.com/2072-4292/18/11/1806
- Flyability Elios 3 sensing suite สำหรับ GPS-denied: depth camera + LiDAR distance sensors 6 ตัว + vision-based velocity sensors 6 ตัว + RTK GPS  [medium] https://www.flyability.com/blog/gps-denied-drone
- Metashape RTK: ค่าที่ต้องเปิดก่อน import ภาพ: Tools > Preferences > Advanced: 'Load camera location accuracy from XMP meta data' + 'Load camera orientation angles from XMP meta data'  [high] https://agisoft.freshdesk.com/support/solutions/articles/31000161735-dji-with-rtk-coordinates-data-processing
- Metashape RTK workflow accuracy ที่คาดหวัง: horizontal error <0.03 m, vertical error <0.05 m  [medium] https://www.agisoftmetashape.com/metashape-rtk-ppk-drones-how-to-maximize-accuracy-with-geotagged-photos/
- Metashape planar-projection orthomosaic สำหรับ facade: ต้องเลือก Surface type = Model แล้วกำหนดระนาบด้วย marker 3 จุด + ระบุแกน Horizontal/Vertical  [high] https://agisoft.freshdesk.com/support/solutions/articles/31000154049-orthomosaic-generation-planar-projection-

## SOURCES
- https://www.pix-pro.com/blog/vertical-photogrammmetry
- https://www.hammermissions.com/post/overlap-in-drone-mapping
- https://t2d2.ai/blog/harnessing-photogrammetry-revolutionizing-building-facade-inspection-with-drones
- https://help.dronedeploy.com/hc/en-us/articles/1500004861241-Vertical-Facade-Flight
- https://support.dronelink.com/hc/en-us/articles/4411563374099-Basic-Facades-Vertical-Mapping-Facade-Mission-Component
- https://www.propelleraero.com/blog/quality-drone-data-part-3-walls-faces-overhangs/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10459964/
- https://www.mdpi.com/1424-8220/23/16/7159
- https://www.sciencedirect.com/science/article/pii/S0924271624002065
- https://www.skydio.com/solutions/bridge-inspection
- https://enterprise-insights.dji.com/blog/automated-data-capture-for-slope-surfaces-and-building-facades
- https://enterprise.dji.com/matrice-4-series/specs
- https://enterprise.dji.com/mavic-3-enterprise/specs
- https://help.propelleraero.com/hc/en-us/articles/19384415429911-How-to-Plan-a-3D-Oblique-Mission-with-DJI-Pilot-2
- https://help.propelleraero.com/hc/en-us/articles/19384883356439-How-to-Plan-a-Terrain-Follow-Mission-with-DJI-Pilot-2
- https://help.propelleraero.com/hc/en-us/articles/19384545634711-How-to-Plan-a-Linear-Mission-Using-DJI-Pilot-2
- https://enterprise-insights.dji.com/blog/march-2023-enterprise-firmware-update
- https://shop.coptrz.com/blogs/news/dji-enterprise-app-v2-5-3-pilot-2-app-v17-1-5-14-update
- https://www.heliguy.com/blogs/posts/transform-3d-modelling-with-dji-matrice-4e/
- https://enterprise-insights.dji.com/blog/top-features-of-the-matrice-4-series
- https://www.dslrpros.com/blogs/drone-trends/all-about-the-dji-mavic-3-enterprise-series
- https://www.pix4d.com/blog/3d-models-choose-angle-between-images-circular-missions
- https://manuals-ugcs.sphengineering.com/docs/circlegrammetry-area
- https://dronelife.com/2024/10/15/sph-engineering-unveils-circlegrammetry-a-new-approach-to-drone-photogrammetry/
- https://enterprise.dji.com/dji-terra/faq
- https://repair.dji.com/help/content?customId=01700005092&spaceId=17&re=US&lang=en&documentType=&paperDocType=ARTICLE
- https://support.dji.com/help/content?customId=en-us03400004973&spaceId=34&re=US&lang=en&documentType=artical&paperDocType=paper
- https://www.heliguy.com/blogs/posts/automatic-gcp-marking-workflow-in-dji-terra/
- https://dl.djicdn.com/downloads/dji-terra/20240118/DJI_Terra_User_Manual_v4.0__EN.pdf
- https://www.thefuture3d.com/software/dji-terra/
- https://www.terrestrialimaging.com/blogs/news/dji-terra-in-2026-versions-pricing-and-whats-new
- https://www.pix4d.com/pricing/pix4dmapper/
- https://checkthat.ai/brands/pix4d/pricing
- https://support.pix4d.com/hc/en-us/articles/202557459
- https://support.pix4d.com/hc/en-us/articles/205319155
- https://support.pix4d.com/hc/en-us/articles/202559889
- https://www.pix4d.com/blog/facade-inspection-pix4dmapper-orthoplane
- https://www.agisoft.com/buy/online-store/
- https://www.agisoft.com/buy/online-store/educational-license/
- https://agisoft.freshdesk.com/support/solutions/articles/31000154049-orthomosaic-generation-planar-projection-
- https://agisoft.freshdesk.com/support/solutions/articles/31000161735-dji-with-rtk-coordinates-data-processing
- https://www.agisoftmetashape.com/how-to-set-the-scale-in-agisoft-metashape-complete-guide/
- https://www.agisoftmetashape.com/how-to-add-a-scale-bar-in-agisoft-metashape-step-by-step-guide/
- https://www.agisoftmetashape.com/how-to-place-markers-in-agisoft-metashape-a-step-by-step-guide/
- https://www.agisoftmetashape.com/metashape-rtk-ppk-drones-how-to-maximize-accuracy-with-geotagged-photos/
- https://unisvalbard.github.io/Geo-SfM/content/lessons/georeferencing/markers.html
- https://www.realityscan.com/license
- https://www.unrealengine.com/en-US/blog/we-are-updating-unreal-engine-twinmotion-and-realitycapture-pricing-in-late-april
- https://docs.opendronemap.org/arguments/
- https://community.opendronemap.org/t/vertical-facade-mapping/16890
- https://colmap.github.io/faq.html
- https://github.com/colmap/colmap/issues/1653
- https://zju3dv.github.io/DetectorFreeSfM/
- https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/05311.pdf
- https://arxiv.org/html/2504.20040
- https://eureka.patsnap.com/article/handling-textureless-surfaces-in-photogrammetry-pattern-projection-techniques
- https://f1000research.com/articles/13-1479
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9227050/
- https://isprs-archives.copernicus.org/articles/XLVIII-2-W11-2025/139/2025/isprs-archives-XLVIII-2-W11-2025-139-2025.pdf
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12300741/
- https://www.mdpi.com/1424-8220/25/14/4325
- https://www.sciencedirect.com/science/article/abs/pii/S0926580517311366
- https://www.sciencedirect.com/science/article/abs/pii/S0926580523001899
- https://www.mdpi.com/2072-4292/18/11/1806
- https://www.sciencedirect.com/science/article/pii/S0886779824005972
- https://arxiv.org/pdf/2501.09203
- https://studylib.net/doc/27964637/aci-224r-01
- https://www.flyability.com/blog/gps-denied-drone
- https://www.flyability.com/blog/autonomous-indoor-drone
- https://uavcoach.com/bridge-drone/
- https://www.mdpi.com/2504-446X/7/6/342
- https://enterprise-insights.dji.com/blog/ground-sample-distance

## OPEN QUESTIONS
- Metashape Standard ($179 / $59 educational) มี marker, scale bar และ planar-projection orthomosaic หรือไม่ — ต้องเช็คตาราง feature comparison ที่ agisoft.com/features/compare ก่อนตัดสินใจซื้อ เพราะเป็นตัวชี้ขาดว่าจะต้องจ่าย $549 (Pro edu) หรือ $59 (Standard edu)
- ราคา DJI Terra Standard/Flagship ปี 2026 ที่แท้จริง — แหล่งที่ค้นได้ขัดแย้งกัน (thefuture3d ให้ Pro $1,299/yr แต่ terrestrialimaging บอกว่าเปลี่ยนชื่อเป็น Standard/Flagship แล้วไม่ระบุราคา) ต้องถามตัวแทน DJI Enterprise โดยตรง
- DJI Terra รับภาพที่ไม่มี geotag (non-geotagged) มาทำ reconstruction ได้หรือไม่ และมี workflow scale-bar-only (ไม่มี GCP พิกัด) หรือไม่ — ไม่พบการกล่าวถึงในเอกสารทั้งหมดที่ค้น ต้องดู DJI Terra User Manual v4.0 หมวด GCP Management
- Gimbal tilt range (เงยขึ้นได้กี่องศา) ของ Mavic 3E และ Matrice 4E — หน้า spec ที่ดึงมาไม่ระบุ ตัวเลขนี้ตัดสินว่าถ่ายท้องสะพานตรง ๆ ได้หรือไม่
- DJI Matrice 350 RTK รองรับการติด gimbal แบบหงายขึ้น (upward mount) หรือไม่ และมี payload ใดบ้างที่ใช้ได้ — สำคัญมากสำหรับงานท้องสะพาน
- Laser rangefinder ของ Mavic 3T มีระยะ 200 m หรือ 1,200 m — แหล่งข้อมูลขัดแย้งกัน
- Max image size และ FOV ที่แท้จริงของกล้อง tele บน Matrice 4E (สมมติ 8000×6000 ในการคำนวณ GSD) และ minimum focus distance ของเลนส์ tele — ต้องทดสอบด้วยการถ่ายเป้าที่รู้ขนาดจริงในสนาม
- เกณฑ์ความกว้างรอยแตกร้าวและ condition rating ที่ BMMS ของกรมทางหลวง/กรมทางหลวงชนบทใช้จริง — ไม่พบเอกสารออนไลน์ ต้องขอคู่มือตรวจสอบสะพานฉบับจริง
- สูตรและเกณฑ์ของ T-BHI (Thailand Bridge Health Index) — ต้องอ้างอิงจากรายงานวิจัยทุน วช. ปีงบ 68 ต้นทางโดยตรง เพื่อกำหนดว่าต้องการปริมาณความเสียหายต่อชิ้นส่วนในรูปแบบใด (ซึ่งเป็นตัวชี้ว่าต้อง stitch หรือไม่)
- ราคาและความเป็นไปได้ในการเข้าถึง Flyability Elios 3 / Skydio X10 สำหรับงานใต้สะพาน (GPS-denied) — น่าจะเกินงบโปรเจกต์ ป.ตรี แต่ควรอ้างอิงเป็นข้อเสนอแนะในเล่ม
- DJI WPML (KMZ waypoint file) schema เวอร์ชันล่าสุด ถ้าจะเขียน generator เส้นทางบินเอง — ดูที่ developer.dji.com
- ราคาและความสามารถของ Dronelink / UgCS / Hammer Missions สำหรับ facade mission — ยังไม่ได้ค้นราคา
- ข้อกำหนดทางกฎหมายในการบินโดรนใกล้สะพาน/เหนือทางหลวงในไทย (CAAT, กสทช., การขออนุญาตจากกรมทางหลวง) — ยังไม่ได้ค้นเลย ต้องทำก่อนออกสนามจริง
- เงื่อนไขการทดลองของงานที่รายงานว่าตรวจจับรอยแตก <0.2 mm ได้ (ScienceDirect S0926580523001899) — ระยะถ่าย กล้อง และการประมวลผลคืออะไร ก่อนจะอ้างตัวเลขนี้ในเล่ม
- ตัวเลขเชิงปริมาณของผลการเติม artificial texture ต่อความแม่นของโมเดล (F1000Research 13:1479) — เว็บบล็อกการดึงเนื้อหา ต้องเข้าไปอ่านเอง
