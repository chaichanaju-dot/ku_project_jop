# G1 — เกณฑ์ประเมิน (T-BHI) และมาตรฐานรองรับ: ไฟล์ 03, 04, 08, 10, 06, 11

หมายเหตุการอ้างหน้า: p.N = เลข "=== PAGE n ===" ในไฟล์ txt (ไฟล์ 03 ไม่มีเลขหน้าพิมพ์ในตัวเอง ใช้เลขหน้า PDF; ไฟล์ 11 ตรงกับเลข "Page N" ท้ายหน้า; ไฟล์ 06 และ 10 ใส่เลขหน้าวารสารในวงเล็บ). ตัวเลขทั้งหมดคัดจากข้อความที่ถอดมา; ที่ยืนยันไม่ได้ระบุไว้ตรงๆ.

---

## [03] "เกณฑ์ประเมิน T-BHI (สังเคราะห์ล่าสุด)" — ผู้เขียนไม่ปรากฏในไฟล์ (ไม่มีหน้าปก/บรรณานุกรม) — เนื้อหาคือ "บทที่ 3 ระเบียบวิธีวิจัย" (p.1-30) + "บทที่ 4 ผลการวิจัย" (p.31-59) ของงานเปรียบเทียบมาตรฐานสะพาน

- ชนิด: ร่างบท 3-4 ของงานวิจัย/รายงาน (งานของทีมเรา ไม่ใช่เปเปอร์ที่ตีพิมพ์) ; อายุ: ไม่ระบุปี. ไฟล์ **ไม่มีรายการอ้างอิง** ทุกที่มาของเกณฑ์ต้องอนุมานจากชื่อตาราง/ข้อความประกอบ (ดูตาราง "แหล่งที่มารายเกณฑ์" ด้านล่าง)
- OCR: ตารางอ่านได้ครบ; สมการ 4.1/4.2/3.1 ถอดเป็นตัวอักษรกระจัดกระจายแต่ประกอบกลับได้ (ตรวจแล้วตรงกับรูปแบบมาตรฐาน)

### ภาพรวมโครงสร้างเอกสาร
- 3.2 เลือก 5 มาตรฐาน/งานวิจัยมาเปรียบเทียบ (ตาราง 3.1 p.1): AASHTO MBE+MBEI / NBI-SNBI (FHWA) / BMMS (กรมทางหลวง) / JSCE Maintenance / Pellegrino, Pipinato & Modena (2011)
- 3.3 เปรียบเทียบ 5 มิติ: จำนวนระดับ, แยกวัสดุ RC/PC, เกณฑ์เชิงปริมาณ, การถ่วงน้ำหนัก, ความเหมาะสมกับ AI (p.2-30)
- ตาราง 4.1 สรุป (p.31): จำนวนระดับ AASHTO 4 (CS1-4) / NBI 10 (0-9) / BMMS 6 (0-5) / JSCE 4 (I-IV) / Pellegrino 6 (CV0-5); เกณฑ์เชิงปริมาณ: AASHTO มี, NBI ไม่มี, BMMS มี, JSCE "มีบางส่วน", Pellegrino "มีบางส่วน"; แยก RC/PC: AASHTO และ BMMS แยก ส่วนอื่นไม่แยก; ถ่วงน้ำหนัก: AASHTO และ Pellegrino มี, NBI/BMMS "ใช้ค่าต่ำสุด", JSCE ไม่มี; เหมาะกับ AI: AASHTO, BMMS เหมาะ / NBI, JSCE ไม่เหมาะ / Pellegrino "กลางๆ"
- 4.2.2 (p.32) ข้อเสนอแบบผสม 5 ข้อ: (1) แกนเกณฑ์ระดับ = BMMS 0-5 + คอลัมน์ AASHTO CS คู่ขนาน + Multi-Path Distress (เอาระดับแย่สุด) (2) ดัชนี = T-BHI ขยายจาก AASHTO MBEI ด้วย EHI + T-BHI, CHI 6 ค่า (1.00/0.83/0.67/0.33/0.17/0.00) "ได้จากการ interpolate ระหว่างค่า AASHTO CEI" (3) น้ำหนัก W ตาม Pellegrino แทน Failure Cost ของ AASHTO (4) BPS ด้วย Permanent Factor ของ Pellegrino (5) แปลง T-BHI เป็นสถานะ 6 ระดับ (Reporting Threshold)

### สูตรและค่าที่ใช้ (คัดตรงตัว)
- **EHI** (สมการ 4.1, p.56): EHI = Σ_{i=1..6} (Chi_ei × y_ei) × 100 ; Chi = ตาราง 4.12 ; y_ei = "สัดส่วนของ Element (e) ในแต่ละระดับ BMMS (i)"
- **T-BHI** (สมการ 4.2, p.57): T_BHI = Σ(q_e · W_e · EHI_e) / Σ(q_e · W_e) ; q_e = "quantity ของแต่ละ Element (e)" ; W_e = ตาราง 4.9 ; "ค่าเต็ม 100"
- **ชั้นที่ 0** (p.56): Primitive Metrics = ค่าที่ AI วัดจากภาพ ไม่ผูกมาตรฐาน (ให้ audit trail) ; **ชั้นที่ 1**: แปลงเป็นระดับ BMMS ด้วยตาราง 4.3.1-4.8.7, element ที่มีหลายความเสียหาย → ใช้ระดับแย่สุด (Multi-Path Distress ของ AASHTO), บันทึกการกระจายเป็นสัดส่วนต่อระดับ ; **ชั้นที่ 2** Confidence Flag: เรขาคณิต (Spalling, Scaling, Distortion) = High; วัดได้บางส่วน (เช่น Crack Width ที่ระบุไม่ได้ต่ำกว่า 1 มม.) = Medium; ต้องใช้ Proxy Indicator = Low
- ชั้นที่ 5 (p.57): ตาราง 4.10 ; "ค่าแบ่งที่ 90 และ 70 อ้างอิงตามแนวปฏิบัติของ FHWA ในขณะที่ค่าแบ่งที่ 50 และ 30 ปรับเพิ่มเพื่อให้รองรับการแยกระดับ ชำรุด/วิกฤติ/วิบัติ"
- ชั้นที่ 6 (p.57): **PF = RT × TI × NBI × AF** (4.3) ; **BPS = T_BHI × PF** (4.4) ; PF ประมาณ 0.67-1.00 ; สะพานสำคัญสูง → PF ต่ำ → BPS ต่ำ → ต้องดูแลก่อน
- ตาราง 4.13-4.16 (p.58): RT: Highway 0.80 / National 0.90 / Provincial 0.95 / Secondary 1.00 ; TI: High (>20,000 vpd) 0.90 / Middle (6,000-20,000) 0.95 / Low (<6,000) 1.00 ; NBI: Situation 1 0.96 / 2 0.98 / 3 1.00 ; AF (ปีสร้าง): ก่อน ค.ศ.1900 0.97 / 1900-1945 0.98 / 1946-1970 0.99 / 1971+ 1.00
- ขั้นตอนประเมิน 6 ขั้น (p.59): วัดค่า+ระบุระดับ+น้ำหนัก → EHI → T-BHI → สถานะตาราง 4.10 + ตรวจกฎบังคับตาราง 4.11 → BPS → เรียงลำดับ (สถานะต่ำกว่าก่อน แล้วค่อย BPS ต่ำกว่าก่อน)

### ตาราง 4.12 CHI (p.55)
| ระดับ BMMS | ความหมาย | AASHTO CS equiv | Chi |
|---|---|---|---|
| 5 | ดีมาก | CS1 (ดี) | 1.00 |
| 4 | ดีพอใช้ | CS1.5 (ดี-พอใช้) | 0.83 |
| 3 | พอใช้ | CS2 (พอใช้) | 0.67 |
| 2 | ชำรุด | CS3 (แย่) | 0.33 |
| 1 | วิกฤติ | CS3.5 (แย่-รุนแรง) | 0.17 |
| 0 | วิบัติ | CS4 (รุนแรง) | 0.00 |
ข้อความ p.55: AASHTO CS1-CS4 = 1.00, 0.67, 0.33, 0.00 ; T-BHI "ขยายจากสี่ค่าเป็นหกค่า" ด้วย Linear Interpolation "โดยอาศัยตารางอ้างอิงคู่ขนานระหว่างระดับ BMMS และ AASHTO CS ตามตารางที่ 4.10" (อ้างผิดตาราง ควรเป็น 4.2 — ดูข้อสังเกต)

### ตาราง 4.2 ระดับสภาพ (p.33)
5 ดีมาก=CS1 "ดีเหมือนใหม่ ไม่มีความเสียหาย ซ่อมบำรุงตามปกติ" ; 4 ดีพอใช้=CS1.5 "เสียหายเล็กน้อย ซ่อมตามกำหนดเวลา" ; 3 พอใช้=CS2 "เสียหายปานกลาง ต้องพิจารณาซ่อมตามกำหนดเวลา" ; 2 ชำรุด=CS3 "โครงสร้างหลักชำรุด ต้องพิจารณาซ่อมแซมหรือบำรุงพิเศษ" ; 1 วิกฤติ=CS3.5 "ชำรุดเสียหายมาก ต้องซ่อมเร่งด่วนหรือบูรณะ" ; 0 วิบัติ=CS4 "ต้องทุบทิ้งและก่อสร้างใหม่"

### ตาราง 4.10 Reporting Threshold (p.53)
| สถานะ | ช่วง T-BHI | คำอธิบาย |
|---|---|---|
| ดีมาก | = 100 | ซ่อมบำรุงตามปกติ |
| ดีพอใช้ | 90 ≤ T-BHI < 100 | ซ่อมบำรุงเชิงป้องกัน |
| พอใช้ | 70 ≤ T-BHI < 90 | ซ่อมบำรุงตามกำหนดเวลา |
| ชำรุด | 50 ≤ T-BHI < 70 | ซ่อมบำรุงพิเศษ |
| วิกฤติ | 30 ≤ T-BHI < 50 | ซ่อมบำรุงเร่งด่วนหรือบูรณะ |
| วิบัติ | < 30 | ปิดสะพาน หรือทุบทิ้งแล้วก่อสร้างใหม่ |
(ตาราง 3.4 p.3: BHI ตาม FHWA: ดี ≥90 / พอใช้ 70≤BHI<90 / แย่ <70)

### ตาราง 4.11 กฎบังคับสถานะโดยรวม (p.53) — เฉพาะชิ้นส่วน Primary
- ไม่พบระดับ ≤2 → ตามตาราง 4.10
- พบระดับ 2 แต่ไม่พบ ≤1 → min(ชำรุด, ตามตาราง 4.10) (บังคับเป็นระดับ 2 อย่างน้อย)
- พบระดับ 1 แต่ไม่พบ 0 → min(วิกฤติ, ตาม 4.10)
- พบระดับ 0 → min(วิบัติ, ตาม 4.10) (บังคับเป็นระดับ 0)

### ตาราง 4.9 น้ำหนัก W (p.52-53) — map AASHTO Element ID → Pellegrino
| Element ID | ชิ้นส่วน | BMMS | กลุ่ม Pellegrino | W |
|---|---|---|---|---|
| 12,13,15,28,38,60 | Decks (RC,PC,Steel) | Primary | Transversal/Slab | 9 |
| 102,104,105,106,107,109,110,111 | Girders/Beams (Box, Open) | Primary | Principal Element | 10 |
| 113,115,116 | Stringers | Primary | Transversal | 9 |
| 120,135 | Trusses | Primary | Principal | 10 |
| 141-145 | Arches | Primary | Principal | 10 |
| 146 | "Steel Cable" | Primary | Transversal | 9 |
| 152,154,155 | Floor Beams | Primary | Transversal | 9 |
| 161 | Steel Pin & Pin/Hanger | Primary | Transversal | 9 |
| 202,204,205,206 | Columns | Primary | Principal | 10 |
| 207,208 | Towers, Trestles | Primary | Principal | 10 |
| 210,211 | Pier Walls | Primary | Principal | 10 |
| 215-219 | Abutments | Primary | Abutments | 8 |
| 220,225-228 | Pile Caps, Piles | Primary | Foundation | 7 |
| 231,233,234,235 | Pier Caps | Primary | Transversal | 9 |
| 300-306 | Joints | Secondary | Non-structural | 6 |
| 310-316 | Bearings | Secondary | Bearings | 9 |
| 320,321 | Approach Slabs | Secondary | Approach | 8 |
| 330-334 | Bridge Railings | Secondary | Non-structural | 5 |
| 510,522 | Wearing Surfaces, Deck Membrane | Secondary | Non-structural | 6 |
| 515,521 | Protective Coatings/Systems | Secondary | Non-structural | 5 |
ต้นทางค่า W = ตาราง 3.22 (p.30) ซึ่งคัดจาก Pellegrino Table 3 (ตรวจตรงแล้ว ดูไฟล์ 10): Principal (beams, arches, piers) LF5/W10 ; Transversal, bearings, non-seismic devices, slabs LF6/W9 ; Abutments, approach embankment, wingwalls LF7/W8 ; Abutment and pier foundations LF8/W7 ; Waterproofing, road pavement, guard-rails, expansion joints LF9/W6 ; Pavements, parapets, drainage systems, accessories LF10/W5

### เกณฑ์ความเสียหายคอนกรีต (หัวข้อ 4.3.1 RC, 4.3.2 PC) — ถอดครบ
(ทุกตารางมีคอลัมน์: ระดับ | AASHTO CS | เงื่อนไข | ตัวบ่งชี้เพิ่มเติม ; ระดับ 0 ทุกตารางเขียนเหมือนกันว่า "CS4 โครงสร้างชำรุดเสียหายมาก จำเป็นต้องวิเคราะห์โครงสร้าง")

**ตาราง 4.3.1 RC Cracking (p.33)**
- 5/CS1: ไม่พบ
- 4/CS1.5: ความกว้าง <1.6 มม. ; ระยะห่างรอยร้าว >0.9 ม.
- 3/CS2: ความกว้าง 1.6-3.2 มม. ; ระยะห่าง 0.3-0.9 ม., รอยร้าวที่พบร่วมกับคราบเกลือ/น้ำ/สนิม
- 2/CS3: ความกว้าง 3.2-4.8 มม. ; ระยะห่าง <0.3 ม., รอยร้าวที่เกิดจากเหล็กเสริมเป็นสนิม
- 1/CS3.5: ความกว้าง >4.8 มม. ; พบรอยร้าวที่บ่งชี้ปัญหาเชิงโครงสร้าง เช่น รอยร้าวเฉือนแนวทแยง หรือรอยร้าวที่บริเวณรับแรงดึงของหน้าตัด

**ตาราง 4.3.2 RC Scaling/Abrasion/Wears (p.34)**
- 5: ไม่พบ ; 4/CS1.5: ปูนทรายผิวหลุดล่อน ลึก <5 มม. ยังมองไม่เห็นมวลรวมหยาบ ; 3/CS2: ลึก 5-10 มม. มองเห็นมวลรวมหยาบในเนื้อคอนกรีตแต่ยังอยู่ในสภาพดี บางแห่งเห็นเม็ดหินบางส่วนหลุดล่อน ; 2/CS3: ปูนทรายและมวลรวมหลุดล่อน ลึก 10-20 มม. เม็ดหินหลุดชัดเจนจากการขัดสี แต่ยังไม่ลึกถึงเหล็กเสริม ; 1/CS3.5: ลึก >20 มม. เม็ดหินหลุดเป็นหลุมลึก

**ตาราง 4.3.3 Spalling/Delamination/Patched Area (p.34)**
- 5: ไม่พบ
- 4/CS1.5: กะเทาะหลุดล่อนเล็กน้อย ลึกไม่ถึงผิวเหล็กเสริม
- 3/CS2: กะเทาะหลายจุดหรือเป็นบริเวณกว้าง แต่ลึกไม่ถึงเหล็กเสริม ; ลึกไม่เกิน 2.5 ซม. และ เส้นผ่านศูนย์กลางไม่เกิน 15 ซม.
- 2/CS3: กะเทาะถึงผิวเหล็กเสริม ; ลึกเกิน 2.5 ซม. หรือ เส้นผ่านศูนย์กลางเกิน 15 ซม.
- 1/CS3.5: กะเทาะถึงผิวเหล็กเสริมหลายจุดหรือบริเวณกว้าง

**ตาราง 4.3.4 RC Honeycomb (p.35)**
- 5: ไม่พบ ; 4/CS1.5: โพรงขนาดเล็ก ลึกไม่ถึงผิวเหล็กเสริม ; 3/CS2: โพรงขนาดเล็กหลายจุด หรือโพรงขนาดใหญ่ ลึกไม่ถึงผิวเหล็กเสริม ; **ระดับ 2 และ 1: ว่าง ("-")** → Honeycomb ต่ำสุดได้แค่ระดับ 3 (Chi 0.67) ยกเว้นระดับ 0

**ตาราง 4.3.5 RC Exposed Rebar (p.35)**
- 5: ไม่พบ ; 4: ว่าง ; 3/CS2: พบเหล็กเสริมโผล่ในจุดที่ไม่มีผลต่อกำลังโครงสร้าง ; ไม่มีการสูญเสียหน้าตัดที่วัดได้ อาจมีคราบสนิมที่ผิวเหล็ก
- 2/CS3: กะเทาะถึงเหล็กเสริม ; เหล็กมีการสูญเสียหน้าตัดที่วัดได้ ("สังเกตจาก Proxy Indicators เช่น คราบสนิมขนาดใหญ่ การกะเทาะรอบเหล็กเสริม")
- 1/CS3.5: กะเทาะถึงเหล็กเสริม หลายจุดหรือบริเวณกว้าง

**ตาราง 4.3.6 RC Rebar Corrosion (p.36)**: 5 ไม่พบ ; 4,3 ว่าง ; 2/CS3 เหล็กเสริมเป็นสนิม ; 1/CS3.5 เป็นสนิมรุนแรงหรือเสียหายอย่างมาก (ตัวบ่งชี้: รอยร้าวขนาดใหญ่ที่เกิดจากเหล็กสนิม)

**ตาราง 4.3.7 RC Water Staining/Efflorescence/Rust Staining (p.36)**: 5 ไม่พบ ; 4/CS1.5 คราบน้ำเล็กน้อย ไม่พบคราบเกลือและสนิม ; 3/CS2 คราบน้ำปริมาณมากและพบคราบเกลือ (อาจปรากฏร่วมกับคราบสนิมที่ผิวคอนกรีต) ; **ระดับ 2 และ 1 ว่าง** → ต่ำสุดระดับ 3

**ตาราง 4.3.8 RC Excessive Deflection/End Displacement (p.37)**: 5 ไม่พบ ; 4,3 ว่าง ; 2/CS3 เห็นการแอ่นตัว/เลื่อนด้วยตาเปล่า (ปลายเลื่อนจากตำแหน่งหรือพื้นที่วางบนฐานรองรับน้อยผิดปกติ) ; 1/CS3.5 แอ่นหรือเลื่อนมากผิดปกติ

**หัวข้อ 4.3.2 PC (p.37-38)**: Scaling, Spalling, Honeycomb, Exposed Rebar "ให้ใช้ตามตาราง 4.3.2-4.3.5"
- **ตาราง 4.4.1 PC Cracking (p.37)**: 5 ไม่พบ ; 4/CS1.5 กว้าง <0.1 มม., ห่าง >0.9 ม. ; 3/CS2 กว้าง 0.1-0.23 มม., ห่าง 0.3-0.9 ม., รอยร้าวพร้อมคราบเกลือ/น้ำ/สนิม ; 2/CS3 กว้าง 0.23-0.76 มม., ห่าง <0.3 ม., รอยร้าวจากเหล็กเสริมสนิม ; 1/CS3.5 กว้าง >0.76 มม., รอยร้าวบ่งชี้ปัญหาเชิงโครงสร้าง (เฉือนแนวทแยง/บริเวณรับแรงดึง)
- **ตาราง 4.4.2 PC Exposed Prestressing (p.38)**: 5 ไม่พบ ; 4,3 ว่าง ; 2/CS3 เห็นลวดอัดแรงบางส่วน ; มีการสูญเสียหน้าตัดที่วัดได้ (สังเกตจาก Proxy Indicators เช่น คราบสนิมขนาดใหญ่ การกะเทาะรอบลวด) ; 1/CS3.5 เห็นลวดอัดแรงเป็นจำนวนมาก

(ตาราง 4.5.x เหล็ก, 4.6.x รอยต่อ, 4.7.x แผ่นรองรับ, 4.8.x ผิวทาง — มีใน p.38-51 อ่านแล้ว ไม่ถอดทั้งหมดเพราะนอกขอบเขตความเสียหายคอนกรีต 6 คลาสของเรา; เรื่องที่เกี่ยวคือแผ่นรองรับ/รอยต่อ/ผิวทางจะเข้า T-BHI ก็ต่อเมื่อขยายขอบเขตเกินคานหลัก)

### แหล่งที่มารายเกณฑ์ (ตามที่ไฟล์ระบุ/อนุมานได้จากชื่อตาราง)
| เกณฑ์ใน 03 | แหล่งที่ไฟล์ระบุหรืออนุมานได้ | ที่มาไม่ชัด/ผู้เขียนเพิ่มเอง |
|---|---|---|
| 4.3.1 RC Cracking ความกว้าง 1.6/3.2/4.8 มม. | BMMS (ตาราง 3.14 p.16) | — |
| 4.3.1 ระยะห่าง 0.9/0.3 ม. | AASHTO RC (ตาราง 3.8 p.5; ต้นฉบับหน่วยฟุต ดูไฟล์ 04 p.8) | ตัวบ่งชี้ "ร่วมกับคราบเกลือ/น้ำ/สนิม", "เกิดจากเหล็กสนิม", "เฉือนแนวทแยง/ที่รับแรงดึง" ไม่อยู่ใน 3.8 หรือ 3.14 (เฉือนแนวทแยงมีใน NBI ระดับ 3 ตาราง 3.3 p.3) → ผู้เขียนผสมเอง |
| 4.3.2 Scaling | BMMS 3.14 (5-10/10-20/>20 มม.) | "<5 มม." ของระดับ 4 ไม่อยู่ใน 3.14 (BMMS ระดับ 4 ไม่ระบุความลึก) ; คอลัมน์ AASHTO อิง Abrasion/Wear ตาราง 3.8 |
| 4.3.3 Spalling | BMMS 3.14 + AASHTO 2.5 ซม./15 ซม. (3.8) | — |
| 4.3.4 Honeycomb | BMMS 3.14 เท่านั้น | **AASHTO ไม่มีความเสียหายชนิด Honeycomb** (ตรวจแล้วใน 08 p.2 และ 11 p.15) → คอลัมน์ "AASHTO CS" ของตารางนี้เป็นการจับคู่ของผู้เขียน |
| 4.3.5 Exposed Rebar | BMMS 3.14 + AASHTO 3.8 | "Proxy Indicators" ผู้เขียนเพิ่ม |
| 4.3.6 Rebar Corrosion | BMMS 3.14 เท่านั้น | AASHTO ไม่มีรายการนี้ (มีแค่ Exposed Rebar และ Efflorescence/Rust Staining) |
| 4.3.7 Water/Efflorescence/Rust | BMMS 3.14 (p.17) + AASHTO Efflorescence/Rust 3.8 | การเอาระดับ "สนิม" ไว้ระดับ 3 ขัดกับ AASHTO (ดูข้อสังเกต) |
| 4.3.8 Deflection | BMMS 3.14 | — |
| 4.4.1 PC Cracking | BMMS 3.15 (p.18) + AASHTO PC 3.9 | 3.15 ระบุ 0.1-0.23 และ 0.25-0.76 (ช่องว่าง 0.23-0.25) → 4.4.1 ปิดช่องเป็น 0.23-0.76 เอง |
| 4.4.2 Exposed Prestressing | BMMS 3.15 + AASHTO 3.9 | Proxy ผู้เขียนเพิ่ม |
| CS1.5 / CS3.5 | — | ไม่ใช่ condition state ของ AASHTO จริง (AASHTO มีแค่ CS1-4, ตาราง 3.2) เป็นค่ากลางที่ผู้เขียนตั้ง |
| ตาราง 4.10 ค่าแบ่ง 90/70 | "อ้างอิงแนวปฏิบัติ FHWA" (p.57, ตาราง 3.4) | ไม่มีเอกสารต้นทางในไฟล์ใด 04/06/08/10/11 ที่มีค่า 90/70 → ยืนยันไม่ได้ ; 50/30 "ปรับเพิ่ม" โดยผู้เขียน |
| ตาราง 4.11 กฎบังคับ | ไม่ระบุแหล่ง (เป็นการแก้ข้อจำกัดกฎค่าต่ำสุดของ BMMS ตาม 4.2.1 p.32) | ผู้เขียนออกแบบเอง |
| Chi 6 ค่า | interpolate จาก AASHTO 1.00/0.67/0.33/0.00 (p.55) | ไฟล์ไม่อ้างที่มาของค่า AASHTO ; ค่า 1.00/0.67/0.33/0.00 ไม่อยู่ในไฟล์ 04/08/11 → ยืนยันไม่ได้ |
| สมการ EHI/T-BHI | "กระบวนทัศน์การรวมเชิงปริมาณของ AASHTO MBEI" | ไฟล์ไม่ยกสมการต้นฉบับ → ยืนยันไม่ได้จากกลุ่มนี้ |
| W (ตาราง 4.9) | Pellegrino Table 3 (ตรงตัว) | การ map Element ID → กลุ่ม Pellegrino และการแบ่ง Primary/Secondary ของ BMMS เป็นของผู้เขียน |
| PF = RT×TI×NBI×AF และ RT/TI/NBI/AF | Pellegrino (ตรง Table 5-8) | BPS = T-BHI × PF เป็นของผู้เขียน (Pellegrino ใช้ TSR = 10·PF·ΣCF·W/ΣW) |
| Confidence Flag | ไม่ระบุแหล่ง | ผู้เขียนออกแบบเอง ไม่เข้าสูตรใดๆ |
| ลำดับชั้น 0-6 | — | ผู้เขียนออกแบบเอง |

### ตารางต้นทางที่ 03 ถอดมาในบท 3 (ใช้เทียบ)
- BMMS RC (ตาราง 3.14 p.16-17): Cracking ไม่มี/<1.6/1.6-3.2/3.2-4.8/>4.8 มม./ระดับ 0 ; Scaling สึกกร่อน "เล็กน้อย / 5-10 มม. / 10-20 มม. / >20 มม." ; Spalling ระดับ 4 กะเทาะเล็กน้อยไม่ถึงเหล็ก, 3 หลายจุดไม่ถึงเหล็ก, 2 ถึงเหล็ก, 1 ถึงเหล็กหลายจุด ; Honeycomb ระดับ 4,3 ; Exposed Rebar ระดับ 3 (จุดไม่มีผลต่อกำลัง อาจมีสนิม), 2 (กะเทาะถึงเหล็ก), 1 (หลายจุด/กว้าง) ; Rebar Corrosion ระดับ 2 (เป็นสนิม), 1 (สนิมรุนแรง) ; Water Staining/Efflorescence ระดับ 4 (คราบน้ำเล็กน้อย), 3 (คราบมาก/คราบเกลือ) ; Deflection/End Displacement ระดับ 2 (เห็นด้วยตาเปล่า), 1 (มากผิดปกติ)
- BMMS PC (3.15 p.18-19): Cracking ไม่มี/<0.1/0.1-0.23/0.25-0.76/>0.76 มม. ; Exposed Prestressing ระดับ 2 (เห็นลวดบางส่วน), 1 (จำนวนมาก) ; Rebar Corrosion ระดับ 2 (เหล็กเสริม/ลวดสนิม), 1 (รุนแรง) ; หมายเหตุ: ตาราง 3.15 (BMMS PC, p.18-19) มีแถวแค่ Cracking, Scaling, Spalling, Honeycomb, Exposed Prestressing, Exposed Rebar, Rebar Corrosion — ไม่มี Water Staining/Efflorescence/Excessive Deflection สำหรับ PC ; แต่ตาราง 4.4.x ไม่ได้ทำ PC Rebar Corrosion ตามมา (ดูข้อสังเกตข้อ 7)
- AASHTO RC (3.8 p.5-6) : Cracking CS1 <0.3 มม. หรือห่าง >0.9 ม. / CS2 0.3-1.3 มม. หรือห่าง 0.3-0.9 ม. / CS3 >1.3 มม. และห่าง <0.3 ม. ; Spall CS2 ≤2.5 ซม. หรือ ≤15 ซม. / CS3 >2.5 ซม. หรือ >15 ซม. ; Exposed Rebar CS2 ไม่สูญเสียหน้าตัด / CS3 สูญเสีย ; Efflorescence/Rust CS2 "พบคราบเกลือแต่ไม่พบคราบสนิม" / CS3 "พบคราบเกลือและพบคราบสนิม" ; AASHTO PC (3.9 p.7): Cracking CS1 <0.1 / CS2 0.1-0.2 / CS3 >0.2 มม.

### ข้อสังเกตความสอดคล้อง (เทียบกับไฟล์บริบทและภายในเอกสาร)

**ก. ตรงกับไฟล์บริบท**
1. Chi 5=1.00, 4=0.83, 3=0.67, 2=0.33, 1=0.17, 0=0 ตรงตาราง 4.12 (p.55)
2. W คานหลัก/เสา = 10, ราวกันตก = 5 ตรงตาราง 4.9 (p.52-53)
3. EHI = Σ(Chi × สัดส่วน)×100 และ T-BHI = Σ(qWEHI)/Σ(qW) ตรงสมการ 4.1/4.2 ; กฎบังคับสถานะ = ตาราง 4.11 ; Confidence Flag 3 ระดับ = ชั้นที่ 2 (p.56) ; ระดับ 0-5 = BMMS
4. ตรวจเลขคูณ PF ต่ำสุด 0.80×0.90×0.96×0.97 = 0.6705 ตรงที่เอกสารว่า "ประมาณ 0.67" (p.57)

**ข. จุดที่ไม่ตรง/ที่มาไม่ชัด (เรียงตามความสำคัญต่อโครงงาน)**
1. **นิยาม q ไม่ตรงกัน**: ไฟล์บริบทว่า q = "สัดส่วนพื้นที่ชิ้นส่วนที่ตรวจพบ" แต่ 03 p.57 เขียน q_e = "quantity ของแต่ละ Element" (ไม่มีหน่วย ไม่มีการทำให้เป็นสัดส่วน). ใน AASHTO หน่วย quantity ต่างกันตามชนิด: Girder = LF (ความยาวสะพาน × จำนวนคาน), Deck = SF, Column = EA, Bearing = EA (11 p.51, p.8; 08 p.1) → การถ่วง q·W ข้ามชนิดจึงปนหน่วย. ถ้าใช้ "สัดส่วนพื้นที่ที่ตรวจพบ" (0-1) ของเรา ต้องเขียนในบท 3.7 ให้ชัดว่านี่คือการดัดแปลงจาก AASHTO ไม่ใช่ตามต้นฉบับ
2. **สถานะ (ตาราง 4.10) เลื่อนลงหนึ่งขั้นจากระดับองค์ประกอบ**: ถ้าทุกองค์ประกอบอยู่ระดับเดียวกันหมด EHI = Chi×100 → ระดับ 5=100 "ดีมาก" ; ระดับ 4=83 → "พอใช้" (70-90) ทั้งที่ระดับ 4 ชื่อ "ดีพอใช้" ; ระดับ 3=67 → "ชำรุด" (50-70) ทั้งที่ชื่อ "พอใช้" ; ระดับ 2=33 → "วิกฤติ" (30-50) ทั้งที่ชื่อ "ชำรุด" ; ระดับ 1=17 → "วิบัติ" (<30) ทั้งที่ชื่อ "วิกฤติ". แปลว่า "ดีพอใช้" (90-100) ต้องมีระดับ 5 เป็นส่วนใหญ่เท่านั้น ; ชื่อสถานะ T-BHI กับชื่อระดับ BMMS ไม่เทียบกันตรงๆ ควรชี้แจงหรือปรับ threshold. นอกจากนี้ "ดีมาก" ต้องได้ T-BHI = 100 เป๊ะ (ทุกพิกเซลระดับ 5) ซึ่งในงานภาพถ่ายแทบเป็นไปไม่ได้
3. **ตาราง 4.3.1 RC: คอลัมน์ "AASHTO CS" ไม่เทียบกับเกณฑ์ AASHTO จริง**: ความกว้างใช้ของ BMMS (1.6/3.2/4.8 มม.) แต่ AASHTO RC แบ่งที่ 0.3/1.3 มม. (3.8 p.5; 04 p.8; 08 p.2 footnote 0.012/0.05 in) → รอยกว้าง 1.0 มม. ตกเป็นระดับ 4 (CS1.5) ทั้งที่ AASHTO เป็น CS2 ; กว้าง 2 มม. ตกระดับ 3 (CS2) ทั้งที่ AASHTO เป็น CS3. (สำหรับ PC ตรงกันค่อนข้างดี: BMMS 0.1/0.23 ≈ AASHTO 0.1/0.2) — ถ้างานของเราเป็น PC girder ใช้ตาราง 4.4.1 ซึ่งเข้ากันดีกว่า
4. **ตาราง 4.3.7: Rust staining ถูกจัดระดับต่ำเกิน**: AASHTO CS3 = คราบเกลือ+คราบสนิม (3.8 p.5; 08 p.2 "Heavy build-up with rust staining"; 11 p.15 "Efflorescence with rust staining" = CS3) แต่ 4.3.7 (p.36) ให้ "พบคราบเกลือ ... อาจปรากฏร่วมกับคราบสนิม" เป็นระดับ 3/CS2 และเว้นระดับ 2,1 ว่าง → Rust_Stain และ Efflorescence ถูกรวมเป็นตารางเดียวและเพดานสูงสุดแย่แค่ระดับ 3 (Chi 0.67) ; คลาสทั้งสองของเราจึงแยกไม่ออกในตาราง T-BHI. (BMMS 3.14 มีแต่ Water Staining/Efflorescence ไม่มี Rust Staining — ไฟล์ 03 p.17)
5. **Honeycomb ไม่มีคู่ AASHTO**: คอลัมน์ AASHTO CS ของ 4.3.4 เป็นการ assign เอง และเพดานแย่สุดระดับ 3 ; เช่นเดียวกับ Scaling "<5 มม." และ Rebar Corrosion/Deflection ที่เป็น BMMS ล้วน → ข้อความ p.32 ที่ว่า T-BHI "มีความเทียบเท่าทางคณิตศาสตร์กับ AASHTO BHI" (และ 4.4.3) ควรถ่อมลง: เทียบเท่าเฉพาะสมการ ไม่ใช่เกณฑ์ระดับรายความเสียหาย
6. **ระดับ 0 ≠ CS4**: AASHTO CS4 = "ต้องทำการวิเคราะห์โครงสร้าง" (08 p.2) แต่ BMMS ระดับ 0 = "ต้องทุบทิ้งและก่อสร้างใหม่" (3.5 p.4); ตาราง 4.3.x ระดับ 0 ใช้ข้อความ CS4 ปนกับ Chi = 0.00. และทุกตารางไม่มีเกณฑ์ที่ภาพถ่ายตัดสินระดับ 0 ได้ (เป็นดุลยพินิจวิศวกร)
7. **PC Rebar Corrosion หาย**: หัวข้อ 4.3.2 บอกให้ PC ใช้ 4.3.2-4.3.5 + 4.4.1-4.4.2 (p.37) ข้ามตาราง 4.3.6 (Rebar Corrosion ซึ่ง BMMS PC ตาราง 3.15 มีแถวนี้ p.19) ; ส่วน 4.3.7/4.3.8 ที่ข้ามไปสอดคล้องกับ 3.15 ที่ไม่มีแถว Water Staining/Deflection สำหรับ PC ; ไม่ชัดว่าการข้าม 4.3.6 จงใจหรือตกหล่น (ถ้าจงใจควรเขียนเหตุผล)
8. **Confidence Flag ไม่ได้เข้าสูตร**: ชั้นที่ 2 กำหนด High/Medium/Low แต่ไม่ปรากฏในสมการ 4.1-4.4 หรือตาราง 4.11 → ระดับที่มาจาก proxy (Low) บังคับสถานะรวมได้เหมือนระดับที่วัดได้จริง. และตัวอย่างใน p.56 ("Crack Width ระบุไม่ได้ต่ำกว่า 1 มม.") ขัดกับตาราง 4.4.1 ที่เกณฑ์ PC อยู่ที่ 0.1-0.76 มม. → ตาม p.56 งานภาพจึงตัดสินระดับรอยร้าว PC ได้ในระดับ Low/Medium เท่านั้น ไม่ใช่ High ; ควรบอกในบท 3.7 ให้ตรงกับผลทดสอบเลเซอร์/GSD ของโครงงาน
9. **องค์ประกอบที่โดรนไม่เห็นถูกตัดออกจากตัวหารเงียบๆ**: สมการ 4.2 หารด้วย Σ q·W ของ element ที่ประเมิน → ฐานราก/แผ่นรองรับ (ที่ภาพโดรนเห็นไม่ครบ) ไม่มีผลต่อดัชนี ทำให้ T-BHI มองโลกในแง่ดีกว่าจริง ; Pellegrino มีกลไกรับมือ (CoF, TSR_min ให้ CV=5 กับ element ที่ไม่ได้ประเมิน และ CV=3 กับฐานราก — ไฟล์ 10 p.9-10) แต่ 03 ไม่ได้นำมาใช้
10. **"สังเคราะห์จาก 5 มาตรฐาน" เกินจริงเล็กน้อย**: ตาราง 4.3.x ใช้จริงแค่ BMMS (ระดับ+ความกว้าง/ความลึก) + AASHTO (CS คู่ขนาน, 2.5/15 ซม., ระยะห่าง) ; NBI (0-9) และ JSCE (I-IV, ตาราง 3.6 และ 3.21) อยู่ในบท 3 เพื่อเปรียบเทียบเท่านั้น ไม่มีค่าใดจาก NBI/JSCE เข้ามาในตาราง 4.2-4.12 (ยกเว้นข้อความ "รอยร้าวเฉือน" ที่ใกล้กับ NBI ระดับ 3) ; Pellegrino ให้ W และ PF. ไฟล์บริบทเขียนว่า "เกณฑ์สังเคราะห์จาก BMMS, AASHTO MBE, FHWA NBI, JSCE, Pellegrino" — ถ้าเขียนในเล่มต้องระบุบทบาทรายมาตรฐานให้ตรง
11. **ค่าแบ่ง 90/70/50/30 และกฎ 4.11**: 90/70 อ้าง FHWA แต่ยืนยันไม่ได้ในกลุ่มไฟล์นี้ ; 50/30 และตาราง 4.11 เป็นของผู้เขียน ไม่มีเอกสารรองรับ → ในเล่มต้องเขียนว่าเป็น "เกณฑ์ที่ผู้วิจัยกำหนด" ไม่ใช่ "ตามมาตรฐาน"
12. **Pellegrino ถูกบรรยายคลาดเคลื่อน (p.55)**: 03 ว่า Pellegrino ใช้ "ระบบ Condition Value 0-5 ของประเทศอิตาลี" และ "คล้าย BMMS หกระดับ" ; ตัวเปเปอร์ (10 p.4) ว่า CV "Inspired by UK Local Authority experience", ค่าเลือกจาก BRIME (2001), Ryall (2001), UK Local Authority ; CV 1-5 เป็น 5 ระดับ (+0 = "No judgement"/ไม่ประเมิน) ; **ทิศทางกลับกับ BMMS** (CV 5 = แย่สุด, BMMS 5 = ดีสุด) ; และหน่วยงานอิตาลี "ใช้โค้ดที่พัฒนาเอง" (10 p.3) ไม่มีมาตรฐานชาติ. การที่วารสารเป็น Q1 ยืนยันไม่ได้จากไฟล์
13. **ตาราง 3.7 (p.4) ถอด CV 0 ผิด**: เขียน CV 0 = "ไม่มี/ไม่พบความเสียหาย" แต่เปเปอร์ Table 1 (10 p.4) CV 0 = "No judgement" (ไม่ได้ประเมิน) ; "no meaningful defect" คือ CV 1 (CF 10) ส่วน CV 2-5 และค่า CF 10/7/4/2/1 ถูกต้อง
14. **ตาราง 4.15 (NBI) ถอดสถานการณ์ไม่ตรงต้นฉบับ**: 03: Situation 1 "สะพานแทนที่ไม่ได้", 3 "มีทางเลี่ยงหลายเส้น" ; Pellegrino Table 7 (10 p.7): Sit.1 = long deviation on unsuitable alternative road 0.96 ; Sit.2 = short deviation on unsuitable หรือ long deviation on suitable 0.98 ; Sit.3 = short deviation on suitable alternative road 1.00. นิยาม long = อัตราส่วนความยาวทางอ้อม/ทางเดิม >2, short = ≤2 ตัวอักษรบางตัวใน OCR เพี้ยน ("42", "2") (10 p.8) ; นอกจากนี้ตาราง 4.15 ของ 03 ตั้งหัวคอลัมน์ผิดเป็น "ปริมาณจราจร" (ควรเป็นสถานการณ์/ทางเลี่ยง)
15. **ข้ออ้างตารางผิด/ชื่อตารางซ้ำ**: สมการ 3.1 (p.29) อ้าง "ตารางที่ 3.17" ที่จริงคือ 3.22 ; 4.2.2 ข้อ 2 (p.32) และ 4.4.3 (p.55) อ้าง "ตารางที่ 4.10" สำหรับตารางเทียบ BMMS-CS ที่จริงคือตาราง 4.2 ; ตาราง 4.16 (ปีที่สร้าง/AF) ตั้งชื่อ "Road Type (RT)" ซ้ำกับ 4.13 ; ตาราง 3.15 ชื่อ "คอนกรีตเสริมเหล็ก (PC)" ควรเป็นอัดแรง ; BMMS PC ช่วงความกว้าง 0.1-0.23 กับ 0.25-0.76 (3.15 p.18) มีช่องว่าง 0.23-0.25 ซึ่ง 4.4.1 ปิดเป็น 0.23-0.76 โดยไม่บอก
16. **ตาราง 4.9 map รหัสองค์ประกอบ**: "146 Steel Cable" — ใน handout FHWA (08 p.1) 146 = Timber Arch ส่วน Steel Main Cables = 147, Secondary = 148 ; "522 Deck Membrane" ไม่อยู่ในรายการของ 08 p.1 (มี 510, 515, 520, 521) และ VDOT p.9 (510, 515, 521) → ยืนยัน 522 ไม่ได้ ; Bridge Railing ถูกให้ W=5 (กลุ่ม parapets) แต่ Pellegrino ใส่ guard-rails W=6 กับ parapets W=5 และ "road pavement"/"Pavements" ซ้ำสองแถวคนละ W (6 และ 5) (10 p.5) ; ไฟล์บริบทกำหนด ราวกันตก=5 ซึ่งตรงตาราง 4.9 แต่เป็นการเลือกตีความ ; Stringers (ตามยาว) ถูกจัดเป็น "Transversal" W=9 ตั้งใจหรือไม่ไม่ชัด ; Bearings/Joints เป็น "Secondary" ในคอลัมน์ BMMS ทั้งที่ Bearings W=9 (สูงเท่าพื้น) และกฎ 4.11 ใช้เฉพาะ Primary → แผ่นรองรับระดับ ≤2 ไม่บังคับสถานะ
17. **ความเสี่ยงในการอ้างตัวเลข BMMS**: ช่วง 1.6/3.2/4.8 มม. ≈ 1/16, 1/8, 3/16 นิ้ว และ PC 0.1/0.23-0.25/0.76 มม. ≈ 0.004/0.01/0.03 นิ้ว (การแปลงของเราเอง ไม่ได้อยู่ในไฟล์ ใช้เป็นข้อสังเกตเท่านั้น) — ต้นฉบับ BMMS เป็นไฟล์ 05 (ไม่อยู่ในงานนี้) ให้ตรวจแหล่งก่อนอ้าง

### ความเกี่ยวข้องกับงานเรา: **ใช้แน่** (เป็นไฟล์หลักของ 3.7 และตัวกำหนดคลาส/เกณฑ์ของ 3.5; ต้องแก้ข้อสังเกตด้านบนก่อนยกลงเล่ม โดยเฉพาะข้อ 1, 2, 4, 8, 9, 11, 12, 13)

---

## [04] มาตรฐาน NBI และ AASHTO — รายงานที่ปรึกษา (ผู้เขียน/ชื่อเรื่องไม่ระบุ มีหัว "มหาวิทยาลัยเกษตรศาสตร"), 17 หน้า — ปีไม่ระบุ

- ชนิด: รายงานโครงการที่ปรึกษา (แหล่งรอง เรียบเรียงจากมาตรฐาน) ; อายุ: ไม่ระบุ ; ภาษาอ่านได้ (วรรณยุกต์/สระบางตัวหายจาก OCR เช่น "ํา" ไม่กระทบเนื้อหา)
- วัตถุประสงค์/วิธี (p.1, 3): ตรวจสะพานบนเส้นทางยานพาหนะน้ำหนักเกินด้วยสายตา ก่อน-หลังรถบรรทุกวิ่งผ่าน ; ใช้เกณฑ์ NBI และ AASHTO ; **ใช้อากาศยานไร้คนขับเก็บภาพรวมของโครงสร้างและจุดที่เข้าถึงยาก** (p.1) ; ตั้งรหัสชิ้นส่วนเช่น FLB-001-N และบันทึกปริมาณความเสียหายเป็นพื้นที่หรือความยาว (p.1)
- NBI Condition Rating (p.3-4, ตาราง 1.1): "แบ่งสภาพความเสียหายของสะพานโดยรวมเป็น 10 ระดับ 0-9" ; 9 ดีเยี่ยม(ใหม่) / 8 ดีมาก(ไม่พบความเสียหาย) / 7 ดี(พบเล็กน้อย) / 6 น่าพอใจ(ชิ้นส่วนด้านโครงสร้างเสื่อมเล็กน้อย) / 5 ปานกลาง(โครงสร้างหลักมีเสถียรภาพ อาจสูญเสียหน้าตัดเล็กน้อย กะเทาะ รอยร้าวเล็กน้อย) / 4 แย่(สูญเสียหน้าตัด เสื่อมสภาพ กะเทาะปานกลาง) / 3 แย่อย่างรุนแรง(สูญเสียหน้าตัดมาก กะเทาะ รอยร้าวใหญ่ กระทบกำลังรับน้ำหนัก อาจพบรอยร้าวล้า/เฉือน) / 2 วิกฤติ(ตรวจระยะใกล้ไม่ได้เพราะอันตราย อาจต้องปิดสะพาน) / 1 ใกล้วิบัติ(โครงสร้างไม่เสถียร ต้องปิด) / 0 วิบัติ
- AASHTO CS (p.5): 4 ระดับ CS1 Good / CS2 Fair / CS3 Poor / CS4 Severe (ไฟล์ใช้ "ปกติ/พอใช้/ชำรุด/วิกฤต") แยกตามวัสดุ: คอนกรีต, คอนกรีตอัดแรง, เหล็ก, แผ่นรองรับ, รอยต่อ ; อ้างถึง "Manual For Bridge Element Inspection 2nd Edition, 2011" (**ปีผิด**: VDOT 2026 ระบุ MBEI 2nd Edition = 2019, 11 p.3,6 — อย่าลอกปี 2011 ตามไฟล์นี้)
- เกณฑ์คอนกรีต RC (ตาราง 1.2 p.6; ตาราง 1.5 p.8): Spall CS2 ลึก <1 นิ้ว (2.5 ซม.) หรือ ⌀ <6 นิ้ว (15 ซม.) ; CS3 เกิน ; Exposed Rebar CS2 ไม่สูญเสียหน้าตัด / CS3 สูญเสีย ; Cracking CS1 <0.012 นิ้ว (0.3 มม.) ห่าง >3 ฟุต (90 ซม.) ; CS2 0.012-0.05 นิ้ว (0.3-1.3 มม.) ห่าง 1.0-3.0 ฟุต (30-90 ซม.) ; CS3 >0.05 นิ้ว (1.3 มม.) และถี่ <1 ฟุต (30 ซม.) ; Abrasion CS2 เห็นมวลรวมหยาบยังดี / CS3 มวลรวมหลวม-หลุด ; Settlement แยกตามที่ยอมรับได้
- PC (p.9-10, ตาราง 1.7-1.8): เพิ่ม Exposed Prestressing (CS2 โผล่ไม่สูญเสียหน้าตัด / CS3 สูญเสีย) ; Cracking CS1 <0.004 นิ้ว (0.1 มม.) ; CS2 0.004-0.009 นิ้ว (0.1-0.2 มม.) ; CS3 >0.009 นิ้ว (0.2 มม.) และถี่ <1 ฟุต
- เหล็ก/แผ่นรองรับ/รอยต่อ: p.11-17 (ตาราง 1.9-1.18) ; แผ่นรองรับ ปูดบวม <15% ของความหนา(CS2), สูญเสียพื้นที่ <10%(CS2) ; รอยต่อ Seal adhesion CS2 ">50% ของความสูงข้อต่อ", CS3 "น้อยกว่า 50%" (p.16) (ต้นฉบับ AASHTO: CS3 = 50% หรือน้อยกว่า, 08 p.3)
- **ความเกี่ยวข้อง: ใช้เสริม** — แหล่งภาษาไทยสะดวกที่สรุป NBI/AASHTO สำหรับ 2.2 และเป็นตัวอย่างงานไทยที่ใช้ UAV ตรวจสะพาน ; แต่เป็นแหล่งรอง ต้องอ้างต้นฉบับ AASHTO MBEI/FHWA ถ้าจะใช้เป็นเกณฑ์ ; ไม่มีสมการ BHI และไม่มี weighting
- ข้อจำกัด: ตารางไม่มีแถว Efflorescence/Rust Staining (ทั้งที่ข้อความ p.5 ระบุรายการนี้) ; ไม่ได้ระบุว่า NBI ให้คะแนนรายส่วนประกอบ (deck/superstructure/substructure) — "โดยรวม" ตาม p.3 ยืนยันความหมายที่แน่นอนไม่ได้จากไฟล์ ; ตารางความเสียหายทุกแถว CS4 = "ระดับชำรุดมากกว่า CS3 จำเป็นต้องตรวจสอบความแข็งแรง..." (ไม่มีตัวเลข)

---

## [08] AASHTO Elements, Defects, and Condition States (2015 Interims) — FHWA handout, 5 หน้า

- ชนิด: handout อ้างอิงมาตรฐาน (ข้อความ footer "02/24/2015", ส่วน RC/PC มีตราวันที่ "04/13/2018") ; อายุ: ~8-11 ปี และเก่ากว่า MBEI 2nd Ed. 2019 + interim 2022/2024/2025 (ดูไฟล์ 11)
- เนื้อหา: p.1 รายการ Element + หน่วย (Deck/Slab = AREA sq ft ; Girder/Joint/Rail/Pier cap = LENGTH ft ; Column/Bearing/Pile = EACH) เช่น 104 PC Closed Web/Box Girder, 109 PC Open Girder/Beam, 110 RC Open Girder/Beam, 204/205 PC/RC Column, 234 RC Pier Cap, 310 Elastomeric Bearing, 331 RC Bridge Railing, 510 Wearing Surfaces, 520 Concrete Reinforcing Steel Protective System, 521 Concrete Protective Coating ; **146 = Timber Arch, 147 = Steel Main Cables** ; ไม่มี 522
- ตาราง CS ของ RC (p.2): Delam/Spall/Patched (1080) CS2 "Delaminated. Spall 1 in. or less deep or 6 in. or less in diameter. Patched area that is sound." CS3 ">1 in. deep or >6 in. diameter ... does not warrant structural review" CS4 "warrants a structural review ... OR a structural review has been completed and the defects impact strength or serviceability" ; Exposed Rebar (1090) CS2 without measurable section loss / CS3 with ; Efflorescence/Rust Staining (1120) CS2 "Surface white without build-up or leaching without rust staining" / CS3 "Heavy build-up with rust staining" ; Cracking (1130) CS1 "Insignificant cracks or moderate width cracks that have been sealed" / CS2 "Unsealed moderate width cracks or unsealed moderate pattern (map) cracking" / CS3 "Wide cracks or heavy pattern (map) cracking" ; Abrasion/Wear (1190) CS2 exposed coarse aggregate secure / CS3 loose or popped out ; Distortion, Settlement, Scour, Damage (7000)
- PC (p.2): เช่นเดียวกัน + Exposed Prestressing (1100) CS2 present without section loss / CS3 with section loss ; Cracking in PC = รหัส 1110
- **เชิงปริมาณ (footnote p.2)**: "The inspector should use judgment ... especially for concrete cracking ... consider width, spacing, location, orientation, and structural or nonstructural nature" ; RC: <0.012 in = insignificant, 0.012-0.05 in = moderate, >0.05 in = wide ; PC: <0.004 in insignificant, 0.004-0.009 in moderate, >0.009 in wide ; Pattern (map) cracking: "Without further guidance, moderate is 1 ft. to 3 ft. spacing and heavy is less than 1 ft. spacing"
- Bearing (p.3): ปูดบวม <15% ความหนา (CS2) ; Loss of bearing area <10% (CS2), ≥10% (CS3) ; Joint Seal adhesion CS2 ">50% ของความสูงข้อต่อ", CS3 "50% หรือน้อยกว่า" ; Wearing surface crack width <0.012 in หรือห่าง >3.0 ft (CS1)
- **ความเกี่ยวข้อง: ใช้แน่** สำหรับ 2.2 (นิยาม CS และชนิดความเสียหาย) และ 3.7 (อ้างต้นฉบับของ CS1-CS4, 6 คลาสความเสียหายที่ตรงกับ Delam/Spall, Exposed Rebar, Efflorescence/Rust Staining, Cracking) — และเป็นหลักฐานว่า AASHTO ไม่มี Honeycomb
- ข้อเท็จจริงที่หยิบไปเขียนได้: ตัวเลขความกว้างรอยร้าวของ AASHTO เป็น "แนวทางทั่วไป" ใน footnote ไม่ใช่เกณฑ์ตายตัว ; Cracking CS1 รวมรอยร้าวขนาดกลางที่อุดแล้ว ; CS3 ของ Cracking เป็น "wide cracks OR heavy pattern" (ใช้ "หรือ") — ต่างจาก 03 ตาราง 3.8 ที่เขียน "ใหญ่กว่า 1.3 มม. **และ** ห่าง <0.3 ม."
- ข้อจำกัด/ยืนยันไม่ได้: ไม่มีค่า BHI/CEI หรือค่าถ่วงน้ำหนักใดๆ ; ไม่มี Honeycomb ; Efflorescence CS2 ในฉบับนี้ไม่ระบุ "ไม่มี Rust" ต่างจาก VDOT 2026 ที่เขียน "without rust staining" ตรงๆ

---

## [10] Pellegrino, C., Pipinato, A., Modena, C. (2011) "A simplified management procedure for bridge network maintenance" — Structure and Infrastructure Engineering 7(5): 341-351 (online 22 Jan 2009), DOI 10.1080/15732470802659084

- ชนิด: เปเปอร์วิจัย ; อายุ: 2011 (online 2009) ≈ 15 ปี → **เกินกรอบ 5-10 ปี** (อ้างได้ถ้าเป็นต้นทาง W/PF โดยตรง แต่ต้องแจ้งเหตุผล/มีงานใหม่ประกอบ)
- วัตถุประสงค์ (p.2): ขั้นตอนใหม่แบบง่ายประเมินสภาพสะพานจากการตรวจด้วยสายตา เพื่อวางแผนบำรุงรักษาในกรอบ BMS ; ใช้กับสะพานราว 200 แห่ง (197 โครงสร้าง, 19 ถนนภูมิภาค) ในภูมิภาค Veneto อิตาลี (p.2, p.11)
- วิธีการ (p.4-9): ตรวจสอบ 2 ระดับ project level / network level (p.4) ; CV รายองค์ประกอบ → CF → ESR → TSR
  - CV (Table 1, p.4): 0 No judgement ; 1 No meaningful defect ; 2 Minor defects that do not cause damage ; 3 Moderate defects that could cause damage ; 4 Severe defects that cause damage ; 5 Non-functional or non-existent element. "when it is not possible to express an evaluation, CV = 0"
  - CF (Table 2, p.4): CV 0→0, 1→10, 2→7, 3→4, 4→2, 5→1
  - Weight W 10 (สำคัญสุด) ถึง 5 + Location Factor LF (Table 3, p.5) — "LF and weights are defined according to Blakelock et al. (1998) and Ryall (2001)" (p.5) [ต้นทางจริงคือ UK Bridge Condition Index]
  - ESR = CF × LF × RF × NBI × AF, RF = RT × TI (Eq.1, p.7) ; ตาราง RT/TI/NBI/AF (Table 5-8, p.7) ; Table 9 ESR→ระดับเร่งด่วน: 1-10 สูงสุด / 11-20 ระยะสั้น / 21-30 ระยะกลาง / 31-100 ระยะยาว
  - TSR_real = 10·PF·(ΣCF_i·W_i / ΣW_i), PF = RF×NBI×AF (Eq.2, p.9) ; Confidence factor CoF = 100·ΣW_i(evaluated)/ΣW_i(all) (Eq.3) ; TSR_min = สมมติ CV=5 ให้ element ที่ไม่ได้ประเมิน ยกเว้นฐานราก CV=3 "since the foundations are usually not visible" (p.9-10) ; **TSR = (100·TSR_real + TSR_min·CoF)/(100 + CoF)** (Eq.4, p.10) ; Table 10 TSR→ความเร่งด่วน: 1-30 / 31-40 / 41-60 / 61-100 (p.8)
- Table 4 (p.6) ตัวอย่าง datasheet CV เสาคอนกรีต: CV2 ตาข่ายรอยร้าวบาง w ≤0.3 mm (อักขระใน OCR เป็น "5"); CV3 รอยร้าวกว้างลึก w >0.3 mm ("4"), มีคราบสนิม, เกลือ, efflorescence ; CV4 เหล็กโผล่สนิม สูญเสียหน้าตัด ≤20% ; CV5 เหล็กโผล่ สูญเสียหน้าตัด >20% (เครื่องหมาย ≤/> เป็น OCR เพี้ยน ตีความตามบริบท — ยืนยันไม่ได้ 100%)
- ผลที่สำคัญ: นำไปจัดลำดับ 197 สะพาน (Fig.9-10, p.10) ; พบองค์ประกอบรอง (joints 46 จาก 125 มี ESR 1-10, แผ่นรองรับ, ระบายน้ำ) เป็นจุดอ่อนทั่วไป (p.11)
- **ความเกี่ยวข้อง: ใช้แน่** (ต้นทาง W และ PF/RT/TI/NBI/AF ที่ 3.7 ใช้; รองรับ 2.2 เรื่องการถ่วงน้ำหนักชิ้นส่วนและจัดลำดับระดับโครงข่าย)
- ข้อเท็จจริงที่หยิบไปเขียนได้: ค่า W/PF ตรงกับตาราง 3.22, 4.13-4.16 ใน 03 (ตรวจตรงตัวเลขทุกค่า) ; "bridge structure has been divided into structural/non-structural elements" (p.4) ; กรอบคิด project level vs network level (p.4)
- ข้อจำกัด/ห้ามอ้างเกิน: (1) สรุปเอง p.12: "The calibration of the coefficients was developed on the basis of the current standards of maintenance practice of most of the regional authorities in Italy, and could be improved by means of reliability-based methods" และ p.11 "approach may be considered as a first step" → ค่า RT/TI/AF/NBI/W ปรับตามอิตาลี/Veneto ไม่ได้ปรับกับไทย ; TI อิงข้อมูลจราจรทั่วไปของ Regional Authority (p.7-8) (2) **ทิศทาง CV กลับกับ BMMS** และเป็น 5 ระดับ + 0 (3) ESR/TSR: ค่าน้อย = เร่งด่วน (ตรงข้ามกับ T-BHI ที่ค่ามาก = ดี) แต่ผลคูณ PF<1 ทำให้ทิศทางสอดคล้อง (4) ไม่มีตัวเลขเกณฑ์ความเสียหายแบบวัดได้ครบ มีเฉพาะตัวอย่าง Table 4 (5) ไม่มี AI/ภาพถ่าย — ตรวจด้วยสายตาโดยเจ้าหน้าที่ (p.4)
- ข้อสังเกตต่อแผนเรา: เปเปอร์ไม่ได้ให้ "ดัชนี 0-100 ต่อชิ้นส่วนจากสัดส่วนพื้นที่"; T-BHI ของเราเป็นการผสม EHI(AASHTO-style) กับ W(Pellegrino) ไม่ใช่ของเปเปอร์ฉบับนี้ ; กลไก CoF/TSR_min ของเปเปอร์ตอบปัญหา "element ที่ไม่ได้ประเมิน" ได้ตรงกว่า Confidence Flag ใน 03

---

## [06] Frangopol, D.M. & Liu, M. (2007) "Maintenance and management of civil infrastructure based on condition, safety, optimization, and life-cycle cost" — Structure and Infrastructure Engineering 3(1): 29-41, DOI 10.1080/15732470500253164

- ชนิด: บทความทบทวน (keynote) ; อายุ: 2007 (≈19 ปี) → **เกินกรอบ 5-10 ปี**
- วัตถุประสงค์ (p.2): ทบทวนการวางแผนบำรุงรักษาตลอดอายุการใช้งานสำหรับสะพาน โดย optimization หลายวัตถุประสงค์ (สภาพ ความปลอดภัย ต้นทุนตลอดอายุ)
- วิธีการ: ตัวชี้วัดสมรรถนะ (condition/safety/reliability index) (p.4) ; แบบจำลองเสื่อมสภาพ Markov และแบบต่อเนื่อง + Monte Carlo (p.5) ; Genetic Algorithm หา Pareto (p.6) ; ตัวอย่าง RC crosshead ระดับโครงการ (p.8-9) และโครงข่าย 13 สะพาน Denver (p.10-11) ; SHM+SMS (p.11-12)
- ผลสำคัญที่คัดมา: "27.1% of the 590,750 existing bridges ... structurally deficient or functionally obsolete" (p.2, อ้าง ASCE 2005) ; visual-inspection-based condition states "mostly used" แต่ "actual infrastructure safety level has not been explicitly or adequately accounted for ... a reinforced concrete structure with satisfactory visual condition states could actually be structurally unsafe when invisible flaws such as corrosion of the embedded reinforcement exist" (p.3) ; condition index "As a subjective measure ... may not faithfully reflect the true load-carrying capacity" (p.4) ; Denton (2002) แบ่งสภาพ RC ใน UK เป็น 4 ระดับ 0-3 (ไม่มี chloride / เริ่มกัดกร่อน / เริ่มแตกร้าว / คอนกรีตหลวม-delamination) (p.4) ; safety index = ratio of available to required live load capacity, ไม่ยอมรับถ้า <0.91 (p.4) ; Pontis/BRIDGIT สร้างบน visual condition state + Markov (p.7) ; ผู้เขียนเสนอให้ SHM เชื่อมกับ SMS เพื่อ "revolutionize the traditional visual-inspection based SMS" (p.12)
- **ความเกี่ยวข้อง: ใช้เสริม** — ใช้เป็นข้อจำกัดของแนวทางดัชนีจากสภาพภายนอก (T-BHI Tier 1 = คัดกรองด้วยภาพ ไม่ใช่ความปลอดภัยเชิงโครงสร้าง) ในหัวข้อ 2.2/2.6 ; ไม่รองรับวิธีเลขใดในบท 3 โดยตรง
- ข้อจำกัด: ไม่มีเกณฑ์ความเสียหาย/น้ำหนักชิ้นส่วน/ภาพถ่าย ; ไม่ใช่งานวิจัยด้านภาพ ; ตัวเลข 27.1% เป็นสถิติสหรัฐฯ ปี 2005 ; ห้ามอ้างว่าเปเปอร์ฉบับนี้เสนอ "ดัชนีสุขภาพ 0-100"

---

## [11] VDOT Supplement to the AASHTO Manual for Bridge Element Inspection — Structure and Bridge Division, Virginia DOT, January 2026 (77 หน้า)

- ชนิด: คู่มือหน่วยงาน (ภาคผนวกของ AASHTO MBEI) ; อายุ: ม.ค. 2026 (ปัจจุบัน) อ้างอิง MBEI 2nd Ed. (2019) + interim 2022, 2024, 2025 (p.3, p.6) ; FHWA เปลี่ยนไปใช้ SNBI ตั้งแต่ 1 ม.ค. 2026 (p.6)
- อ่านละเอียดแล้ว: p.1-9, 14-18, 42-59 ; ที่เหลือ (p.10-13 รายชื่อ ADE, p.19-41 เหล็ก/ไม้/ก่ออิฐ/ADE ต่างๆ เช่น ท่อระบายน้ำ MSE wall ลาดดิน, p.60-77 ตัวอย่างการนับปริมาณเสา/ตอม่อ/ท่อ/ทรัส/โค้ง/ผิวทาง) ไล่ดูหัวข้อ ไม่เกี่ยวกับคอนกรีตคานหลัก
- **ใช้ได้ (เกี่ยวกับคอนกรีต/คานหลัก):**
  1. ตาราง defect คอนกรีต RC และ PC (p.15-18) เท่ากับ AASHTO MBEI ฉบับปัจจุบัน — ยืนยัน CS1-4 ของ Delam/Spall (CS2 ≤1 in. deep หรือ ≤6 in. dia.; CS3 เกิน), Exposed Rebar (CS2 ไม่มี measurable section loss / CS3 มี), Exposed Prestressing (CS2 without section loss / CS3 with), Cracking (CS1 insignificant หรือ moderate ที่อุดแล้ว; CS2 unsealed moderate width หรือ unsealed moderate pattern; CS3 wide cracks หรือ heavy pattern), Efflorescence/Rust Staining (CS2 "Efflorescence without rust staining" ; CS3 "Efflorescence with rust staining" (p.15, 17)), Abrasion/Wear, Distortion, Settlement, Scour, Damage (7000), CS4 = warrants structural review
  2. **กฎ Overlapping Defects (p.43-44)**: ที่ซ้อนกันให้รายงานได้เพียงหนึ่ง defect ต่อพื้นที่ — ตัวที่ condition state แย่สุดชนะ ; "We can't count this one foot area twice" ; ถ้าเสมอกันใช้ลำดับ Defect Hierarchy (เป็นแนวทาง ไม่ใช่กฎตายตัว, p.43) ; Elements หน่วย "Each" (เช่น เสา) แบ่งไม่ได้ — แต่ละต้นอยู่ CS เดียว (p.43-44) ; 7000-Damage ไม่ roll-up (p.45)
  3. **ลำดับความสำคัญเมื่อเสมอกัน — PC superstructure (p.46)**: 1900 Distortion > 1100 Exposed Prestressing > 1090 Exposed Rebar > 1080 Delam/Spall/Patched > 1120 Efflorescence/Rust Staining > 1110 Cracking ; RC superstructure (p.45): Distortion > Exposed Rebar > Delam/Spall > Efflorescence/Rust > Cracking ; (RC deck: Exposed Rebar > Spall > Efflorescence/Rust > Cracking > Damage > Abrasion)
  4. **การนับ quantity (p.51-58)**: Girder/Beam/Box girder = ความยาวสะพาน × จำนวนคาน (LF) "NOT dependent on the number of visible pairs of girder faces" (เช่น PC tee beam 4 ตัว ยาว 25 ft = 100 LF, p.55) ; Deck = SF (กว้างรวม × ยาว) ; Column = EA ; Bridge Rail = LF ; หน่วยตาราง p.8-9 : Deck SF, Girder LF, Column EA, Pier Cap LF, Bearing EA, Joint LF
  5. VDOT กำหนดให้ทุก element อยู่ "low environment" (Environment 2) (p.7)
- **ใช้ไม่ได้/ไม่เกี่ยว**: Agency-defined elements ของ VDOT (deck drains, MSE wall, roadway over fill, link slab, slab extension, ลาดดิน, ช่องน้ำ, joint effectiveness p.10-41), defect ของเหล็ก/ไม้/ก่ออิฐ, ตัวอย่างการนับปริมาณของทรัส/โค้ง/ท่อ
- **ไม่มีในไฟล์นี้**: ตัวเลขความกว้างรอยร้าว (ไม่มี 0.3/1.3/0.1/0.2 มม. ใดๆ — grep ไม่พบหน่วย mm/in. ของรอยร้าว), Honeycomb/Scaling (ไม่มีเป็น defect), ค่า BHI/CEI/น้ำหนัก, การใช้โดรน/ภาพถ่าย → ตัวเลขเชิงปริมาณของ AASHTO ต้องอ้างจาก 08 footnote หรือ MBEI ต้นฉบับ
- **ความเกี่ยวข้อง: ใช้เสริม** — (ก) หลักฐานปัจจุบัน (2026) ว่าตาราง CS ของ MBEI ที่ T-BHI อ้างยังเหมือนเดิม และ Rust staining = CS3 (ใช้แก้ข้อสังเกตข้อ 4 ของ 03) (ข) รองรับกฎ "ตัดการนับซ้ำเมื่อ mask ความเสียหายซ้อนกัน/เลือกระดับแย่สุดต่อพื้นที่" และ "q ของ girder = ความยาว" ใน 3.7 (ค) ลำดับความสำคัญของ defect ใช้เป็นตัวตัดสินเมื่อ mask ต่างคลาสทับกัน ถ้าจะ implement
- ข้อจำกัด: เป็นคู่มือรัฐเวอร์จิเนียเพื่อการตรวจโดยคน ไม่ใช่มาตรฐานชาติ/สากล ; ยืนยันไม่ได้ว่า hierarchy ใช้กับการแยกส่วนด้วยภาพได้ (ไฟล์เองบอกเป็น "guideline ... inspectors must use their own judgment", p.43)

---

## สรุปกลุ่ม G1

- **เข้า proposal แน่**: 03 (แกนเกณฑ์ 3.7 ต้องแก้ข้อสังเกต 1, 2, 4, 8, 9, 11-13 ก่อน), 10 Pellegrino (ต้นทาง W/PF — แจ้งว่าอายุเกิน 10 ปีและค่าปรับกับอิตาลี), 08 FHWA/AASHTO CS (ต้นฉบับเกณฑ์คอนกรีต 4 CS, footnote ความกว้างรอยร้าว)
- **เข้าเป็นตัวเสริม**: 04 (แหล่งไทยสรุป NBI/AASHTO + มีตัวอย่าง UAV ตรวจสะพานในไทย; ระวังปี MBEI ผิด), 11 VDOT 2026 (ความเป็นปัจจุบันของตาราง CS, กฎ overlap/นับปริมาณ), 06 Frangopol & Liu (ข้อจำกัดของดัชนีจากสายตา ใช้ใน 2.6 ได้ย่อหน้าเดียว; เก่า 19 ปี)
- **ตัด/ไม่ต้องอ้างเพิ่ม**: ไม่มีไฟล์ในกลุ่มที่ควรตัดทั้งฉบับ ; ส่วนของ 11 ที่เกี่ยวกับ ADE/เหล็ก/ไม้/ก่ออิฐ ตัด
- **ช่องว่าง (หัวข้อที่กลุ่มนี้ยังไม่รองรับ)**: (ก) ที่มาของ AASHTO BHI/CEI (1.00/0.67/0.33/0.00) และสมการ BHI ต้นฉบับ — ไม่อยู่ในไฟล์ใดของกลุ่มนี้ ต้องหา MBEI/ AASHTO ต้นฉบับ ; (ข) ที่มาของ FHWA 90/70 ; (ค) BMMS ต้นฉบับ (ไฟล์ 05 อยู่นอกการมอบหมาย) เพื่อตรวจ 1.6/3.2/4.8 มม., PC 0.1/0.23-0.25/0.76 มม. และชนิด Honeycomb/Rebar Corrosion ; (ง) ไม่มีเอกสารรองรับ Honeycomb/Rust_Stain แยกจาก Efflorescence ; (จ) ไม่มีงานในกลุ่มที่ทดสอบว่า "ระดับจากภาพ" ตรงกับวิศวกร (อยู่กลุ่มอื่น)
- **คำเตือนเรื่อง 03**: ถ้าจะบอกว่า "เกณฑ์สังเคราะห์จาก BMMS, AASHTO, NBI, JSCE, Pellegrino" ต้องชี้ให้เห็นว่าแต่ละมาตรฐานเข้ามาที่ส่วนไหนจริง (ข้อ 10) ; ค่า 50/30 และตาราง 4.11 และ Confidence Flag เป็นของผู้วิจัย ไม่ใช่ของมาตรฐาน
