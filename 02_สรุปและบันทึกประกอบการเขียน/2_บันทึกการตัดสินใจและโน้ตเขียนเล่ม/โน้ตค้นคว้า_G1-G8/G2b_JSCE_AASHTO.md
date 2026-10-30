# G2b — JSCE (09) และ AASHTO MBE 2018 (07)

หมายเหตุเลขหน้า: "PDF p.N" = ตัวคั่น `=== PAGE N ===` ในไฟล์ txt (ตรงกับหน้าที่ N ของ PDF) ; ในวงเล็บคือเลขหน้าที่พิมพ์ในเล่ม
- JSCE: เลขพิมพ์ = PDF − 31 (เช่น PDF p.140 = พิมพ์ p.109)
- AASHTO: Section 3 เลขพิมพ์ 3-n = PDF (n+23) ; Section 4 เลขพิมพ์ 4-n = PDF (n+44) ; Section 6 เลขพิมพ์ 6-n = PDF (n+134)
ข้อความ txt ของทั้งสองเล่มอ่านได้ดี ไม่ต้องเปิด PDF ซ้ำ (OCR เพี้ยนเฉพาะหน้าปก AASHTO และสมการ 3.3.1.3-1 ที่ตัวห้อยซ้อน แต่ตัวแปรยังอ่านออก)

ส่วนที่อ่านจริง: สารบัญทั้งสองเล่ม, JSCE ข้อ 1.3, 2.2, 3.2.2, 3.3, 4.1, 4.3, 4.4, 4.5, 4.7.3.3-4.7.3.4, 6.3-6.5 และตารางระดับสภาพของบท 9/10/11/12/14 ; AASHTO Section 2.2.2, Section 3 (3.3.1), Section 4 ข้อ 4.2.3-4.2.5, 4.3.5.1-4.3.5.6, 4.3.6.5, Section 5 สารบัญ/5.2.1, และตาราง φc ใน Section 6
**ส่วนที่ข้าม (ไม่เกี่ยว):** JSCE บท 5, 7-8 (วิธีซ่อม/บันทึก), บท 9-13 ส่วนสมการทำนายการคาร์บอเนชัน/คลอไรด์/น้ำค้างแข็ง/สารเคมี/ASR, บท 14-16 (พื้น/คานรับความล้า, การขัดสึก), บท 17 (seismic retrofit), ภาคผนวก ; AASHTO Section 6 (load rating) ยกเว้นตาราง φc, Section 7 (fatigue เหล็ก), Section 8 (load test), Appendix A (ตัวอย่างคำนวณ load rating), Section 4 ส่วนเหล็ก/ไม้/สะพานขนาดซับซ้อน/underwater/scour

---

### [09] JSCE Standard Specifications for Concrete Structures — 2007 "Maintenance" (JSCE Guidelines for Concrete No.17) — Japan Society of Civil Engineers (2007; ฉบับภาษาอังกฤษ ธ.ค. 2010) — ISBN 978-4-8106-0754-3 (PDF p.3)
- ชนิด: มาตรฐาน/แนวปฏิบัติ (model code ที่ไม่มีผลทางกฎหมาย PDF p.19) ; อายุ: พิมพ์ครั้งแรก 2007 (อังกฤษ 2010) = เกิน 10 ปี (ประมาณ 16-19 ปีนับถึง 2026) ใช้เป็นมาตรฐานอ้างอิง ไม่ใช่งานวิจัยย้อนหลัง 5-10 ปี
- ตัวเล่มเป็นแนวทางบำรุงรักษาโครงสร้างคอนกรีตทั่วไป (RC/PC) ไม่ใช่เฉพาะสะพาน และ **ไม่ได้กล่าวถึงโดรน/UAV เลย** (ค้น drone/UAV/unmanned ไม่พบ ; พูดถึงแค่ naked eye, photographs, binoculars, digital camera, laser reflection)

**วัตถุประสงค์ / วิธีการ / ผลที่สำคัญ**
- วัตถุประสงค์: กำหนดกรอบ "ประเมิน (assessment) → ทำนายการเสื่อม → ประเมินสมรรถนะ → ตัดสินมาตรการแก้ไข → บันทึก" (PDF p.43 Fig. C3.1.1)
- สมรรถนะที่ต้องรักษา 5 ด้าน: safety, serviceability, hazards for third party, esthetic appearance and landscape, durability (ข้อ 2.2, PDF p.39 / พิมพ์ p.11)
- วิธี: แยกการตรวจเป็น initial / periodic (routine + regular) / extraordinary (+ emergency) (PDF p.35 / พิมพ์ p.7 และ PDF p.56)
- ผล: เมื่อคำนวณเชิงปริมาณไม่ได้ ให้ประเมินแบบกึ่งปริมาณด้วย "เกรดรูปลักษณ์ภายนอก (grade of appearance)" โยงกับระยะการเสื่อม (PDF p.105 พิมพ์ p.77)

#### (1) เกณฑ์ความกว้างรอยร้าวคอนกรีตอัดแรง 0.1 / 0.23 / 0.76 มม.
**ไม่มีในเล่มนี้** — ค้นรูปแบบ "x mm" ทั้งไฟล์ ไม่พบตัวเลขความกว้างรอยร้าวสำหรับตัดสินระดับสภาพเลย (ค่า mm เดียวที่เจอคือ "initial crack length 0.05-0.5 mm" ของรอยร้าวล้า ซึ่งเป็น *ความยาว* ในบทความล้า PDF p.278 ไม่เกี่ยวกับ PC สะพานและไม่ใช่เกณฑ์ตัดสิน)
สิ่งที่ JSCE ให้แทน:
- ให้หน่วยงานกำหนดเกณฑ์เอง: จัดระดับความเสียหายเป็น (i) allowable (ii) ไม่แน่ใจว่ายอมรับได้หรือไม่ (iii) not allowable โดย "Criteria should be specified by the authority considering the service conditions and required performances" (PDF p.99 พิมพ์ p.71) — พร้อมรายการที่ควรให้เกรด: ตำแหน่ง/รูปแบบ/ปริมาณ/ความยาว/ความกว้างของรอยร้าว ฯลฯ
- ประโยค "If the crack width is below an allowable value, there will be no problem. Excessive cracking... likely to greatly accelerate deterioration" (PDF p.138 พิมพ์ p.107) — ไม่ระบุค่า
- ถ้าคาร์บอเนชันถึงเหล็กที่รอยร้าว "corrosion occurs even if the crack width is small" (PDF p.144 พิมพ์ p.113)
- ต้องวัดความกว้าง/ความยาวรอยร้าวด้วยสเกลหรือเทปวัด (PDF p.76 พิมพ์ p.48 ; PDF p.65 พิมพ์ p.37) และการตรวจ regular ต้อง "measured using scales to quantitatively determine" ความกว้าง/ความยาวรอยร้าว พื้นที่ delamination (PDF p.65)
→ เกณฑ์ 0.1/0.23/0.76 ต้องอ้างจากแหล่งอื่นในกลุ่ม (น่าจะ BMMS/เอกสาร 03-05) ห้ามอ้างว่ามาจาก JSCE/AASHTO

#### (2) นิยามระดับสภาพของ JSCE (grade of appearance) — เทียบ 0-5 แบบไทย
JSCE ไม่มีสเกลตัวเลขเดียวใช้ทุกกรณี แต่ให้ "ตารางเกรดรูปลักษณ์ + ระยะการเสื่อม" แยกตามกลไก (ตัวเลขเกรดไม่เท่ากันทุกบท) ตัวที่ตรงกับสะพาน PC/RC ที่สุดคือบท 9 คาร์บอเนชัน และบท 10 คลอไรด์ (เหล็กเสริม/เหล็กอัดแรงสนิม):

บท 9 Table C9.3.4 (PDF p.140 พิมพ์ p.109) — 5 เกรด:
- I-1 initiation: ไม่มีความเสียหายที่ผิว คาร์บอเนชันเหลืออยู่ ≥ ค่าจำกัดการเกิดสนิม
- I-2 propagation: ผิวปกติ แต่คาร์บอเนชันต่ำกว่าค่าจำกัด สนิมเริ่ม
- II-1 acceleration ช่วงแรก: เกิดรอยร้าวจากสนิม
- II-2 acceleration ช่วงหลัง: รอยร้าวจากสนิมลุกลาม พบ peeling/spalling ยังไม่เสียหน้าตัดเหล็ก
- III deterioration: peeling/spalling + รอยร้าวจากสนิม + เหล็กเสียหน้าตัด
บท 10 Table C10.3.4 (PDF p.163 พิมพ์ p.132) — I-1, I-2 ไม่มีความเสียหายที่ผิว (ต่างกันที่คลอไรด์เกินค่าวิกฤตหรือไม่) ; II-1 รอยร้าว + rust leaching ; II-2 รอยร้าวหลายเส้น + rust leaching + partial peeling/spalling ; III รอยร้าวหลายเส้น "Crack width is large" + rust leaching + peeling/spalling + displacement/deflection มาก (คำว่า "large" ไม่มีตัวเลข)
บท 11 น้ำค้างแข็งใช้ State I-IV (PDF p.191), บท 12 สารเคมีใช้ I-IV (PDF p.207), บท 14 พื้นรับความล้า State I-IV ตามรูปแบบรอยร้าว 1 ทิศ → 2 ทิศ → ร่างแหละมุมหลุด → พื้นยุบ (PDF p.257 Fig. C14.3.1)
เกรดสนิมของเหล็ก (Table C9.3.3, PDF p.139 พิมพ์ p.108): I = mill scale/สนิมบางแน่น ไม่เกาะผิวคอนกรีต ; II = สนิมพองเป็นจุดเล็ก ; III = สนิมพองรอบเหล็กหรือตลอดความยาว ยังไม่เห็นเสียหน้าตัด ; IV = เหล็กเสียหน้าตัด — และเอกสารระบุเองว่า "Grades I through IV roughly correspond to grades I-1, I-2, II and III" (PDF p.139)
ตารางผลต่อสมรรถนะ (Table C9.3.5, PDF p.148): II-1 กระทบแค่ความสวยงาม (cracking, rust leaching, exposure of steel) ; II-2 เพิ่มความแข็งเกร็งลด + อันตรายต่อบุคคลที่สาม (peeling, spalling) ; III กำลังรับน้ำหนัก/ความเหนียวลด
ตารางมาตรการ (Table C9.4.1 PDF p.149 ; C10.4.1 PDF p.172): I-1/I-2 = investigate/ป้องกัน ; II-1, II-2 = repair เป็นมาตรการมาตรฐาน ; III = จำกัดการใช้/รื้อถอน

**เทียบกับ 0-5 แบบไทย (C_hi 5=1.00 … 0=0) — เป็นข้อเสนอเชิงตีความของเรา ไม่ใช่ข้อความในต้นฉบับ:**
| JSCE (บท 9/10) | ลักษณะสำคัญ | ระดับไทยที่น่าจะเทียบ |
|---|---|---|
| I-1 | ไม่มีความเสียหายที่ผิว (ยังไม่เริ่มกัดกร่อน) | 5 |
| I-2 | ผิวยังปกติ แต่สนิมเริ่มภายใน | 5 หรือ 4 (ภาพถ่ายมองไม่เห็น → ตรวจด้วยภาพไม่ได้) |
| II-1 | รอยร้าวจากสนิม + rust stain | 3 (ถึง 4 ถ้ารอยร้าวเล็ก) |
| II-2 | รอยร้าวมาก + spalling บางส่วน | 2 |
| III | spalling + เหล็กเสียหน้าตัด/crack กว้าง/ขยับ-แอ่น | 1 หรือ 0 |
ข้อควรระวัง: (ก) I-1 กับ I-2 แยกกันด้วยค่าคาร์บอเนชัน/คลอไรด์ ซึ่งภาพถ่ายโดรนบอกไม่ได้ — เกรดตามภาพที่ตรวจได้จริงเริ่มที่ II-1 ; (ข) เกรดของ JSCE ออกแบบตามกลไกเสื่อมเดียว ไม่ใช่เกรดรวมของชิ้นส่วน ; (ค) ข้อความ JSCE ไม่ได้กำหนดน้ำหนัก C_hi ; (ง) ตารางบท 14 รอยร้าวพื้นสะพานรับความล้า เป็นตัวอย่างว่าเกรดตัดสินจาก "รูปแบบรอยร้าว" ไม่ใช่ความกว้าง

#### ประเภทและความถี่การตรวจ (JSCE)
- Routine: ทุก "several days through once a week" เน้นตาเปล่า ภาพถ่าย กล้องส่องทางไกล ; ข้อ 3.3.3 commentary บอก "approximately several days to one month" (PDF p.35 พิมพ์ p.7 ; PDF p.51 พิมพ์ p.23 ; PDF p.63 ข้อ 4.3)
- Regular: ทุก "once in several years" ; ค่าที่พบบ่อย "one to five years for marine structures, five to ten years for plant structures, five years for road bridges and two years for railroad" (PDF p.66 พิมพ์ p.38)
- Extraordinary (หลังแผ่นดินไหว/พายุ/ไฟ/ชน) และ Emergency (เมื่อโครงสร้างคล้ายกันเกิดอุบัติเหตุ) (PDF p.35, 52-54 ข้อ 3.3.4)
- Initial: ตรวจสภาพตั้งต้น รวมถึง initial defects เช่น cracks, cold joints, honeycombs (PDF p.50 พิมพ์ p.22 ; PDF p.47 นิยาม initial defect: crack, honeycombing, cold joints, sand streaking)
- หมวดการบำรุงรักษา A preventive / B corrective / C observational เลือกตามความสำคัญ อันตรายต่อบุคคลที่สาม อายุใช้งาน สภาพแวดล้อม (ข้อ 3.2.2, PDF p.46-47 พิมพ์ p.18-19)
- มาตรฐานเอกสารตรวจ NDIS 3418 "Visual testing methods for concrete structures" ถูกอ้างถึง (PDF p.76) ไม่ได้อ่านเนื้อหา — ยืนยันไม่ได้ว่าในนั้นกำหนดอะไร

#### ชนิดความเสียหายที่ JSCE ให้ตรวจด้วยตา (ข้อ 4.7.3.3, PDF p.76 พิมพ์ p.48) — ตรงกับ 6 คลาสของเรา
(i) discoloring/staining, white gel, **efflorescence**, free lime, water leakage (ii) **cracks** (ทิศ รูปแบบ ปริมาณ ความกว้าง/ยาวทั่วไป และมี rust stain ออกจากรอยหรือไม่) (iii) scaling (iv) delamination (v) peeling และ **spalling** (vi) **exposure/corrosion/fracture of steel** (cover, จำนวนจุดที่เหล็กโผล่, ความยาว, ระดับสนิม) (vii) displacement/deformation
- **Honeycomb** อยู่ในกลุ่ม initial defect ไม่ใช่การเสื่อม (PDF p.47, 50)
- **Rust stain:** ปรากฏเป็น "stain of rust"/"rust leaching" (PDF p.76, 99, 163) — JSCE ใช้เป็นสัญญาณว่าเหล็กเสริมสนิมแล้วและต้องทำ detailed investigation ทันที ("corrosion cracks or stain of rust... reinforcement has already corroded... acceleration stage... detailed investigations should be conducted immediately", PDF p.66 พิมพ์ p.38)
- ผลของ efflorescence/สิ่งบัง: ไม่ใช่ใน JSCE (อยู่ใน AASHTO ข้อ 4.3.5.2)

#### การตรวจด้วยภาพ/โดรน
- ไม่มีโดรน แต่รับรองการวิเคราะห์ภาพดิจิทัลโดยตรง: "For quantitatively assessing the position and size of defect, analyzing the images recorded by digital cameras is effective. In addition to visual observation, data may be extracted from the intensity of laser beam reflected by the concrete surface" (PDF p.76 พิมพ์ p.48)
- กล้องส่องทางไกลใช้เมื่อเข้าถึงผิวคอนกรีตไม่ได้ (PDF p.76) ; ข้อ 4.3 routine ระบุ "visual observations using the naked eye, photographs and binoculars" (PDF p.63)
- แนวทาง PC (post-tensioned): grouting ในท่อไม่เต็มทำให้ลวดอัดแรงสนิม; สัญญาณ = รอยร้าวตามท่อ, free lime, น้ำรั่ว ; ให้ตรวจด้วย X-ray/อัลตราโซนิก/เจาะบางส่วน และดู cracks ใกล้ anchorage, delamination ของ backfill concrete, rust stain (PDF p.62 พิมพ์ p.34) ; อัลตราโซนิก/ความร้อน/radar ใช้หา grout in sheath (PDF p.77 ข้อ 4.7.3.4)

#### น้ำหนัก/ความสำคัญของชิ้นส่วน (JSCE)
ไม่มีตัวเลขน้ำหนัก มีแค่หลักการ: เลือก maintenance category, ความถี่ตรวจ และการตัดสินแก้ไข โดยพิจารณา "importance of the structure, region or member" (PDF p.46, 66, 100) — ยืนยันไม่ได้ว่ามีค่าน้ำหนักเชิงตัวเลข ไม่มี

#### (3) ที่อ้างในหัวข้อ 2.2 ได้ทันที (JSCE)
- ใช้สนับสนุน 2.2: กรอบประเมิน→ตัดสิน (Fig. C3.1.1, PDF p.43); สมรรถนะ 5 ด้าน (PDF p.39); ประเภท/ความถี่การตรวจ (PDF p.35, 51, 66); การให้เกรดกึ่งปริมาณเมื่อไม่มีสมการ (PDF p.105); ตาราง I-1…III และ Table C9.3.4/C10.3.4 (PDF p.140, 163); ตาราง grade of corrosion (PDF p.139)
- ใช้สนับสนุน 3.7: เกณฑ์ไม่ต้องคำนวณเชิงปริมาณทุกกรณี — "semi-quantitative evaluation by the grading of the appearance" ถูกต้องตามมาตรฐาน (PDF p.103, 105) และ JSCE ให้ผู้เป็นเจ้าของกำหนดเกณฑ์ allowable/uncertain/not allowable เอง (PDF p.99) → เป็นเหตุผลรองรับการ "สังเคราะห์เกณฑ์" ของเรา
- ใช้สนับสนุน 3.5/3.6: การวัดความกว้างรอยด้วยสเกล และการวิเคราะห์ภาพดิจิทัลเป็นวิธีที่มาตรฐานยอมรับ (PDF p.65, 76)

**ข้อจำกัด/ห้ามอ้างเกินจริง (JSCE):** ไม่มีเกณฑ์ความกว้างรอยร้าวเป็นตัวเลข ; ไม่ใช่มาตรฐานสะพานโดยเฉพาะ (ไม่มีนิยามชิ้นส่วนสะพาน) ; ไม่มีน้ำหนักชิ้นส่วน ; เกรดอิงกลไกการเสื่อม ไม่ใช่สเกลรวม ; ไม่ได้อ่านเล่มภาษาญี่ปุ่นที่อ้าง (NDIS 3418) ; **ความเกี่ยวข้องกับงานเรา: ใช้เสริม** (2.2 เกรดรูปลักษณ์/ประเภทการตรวจ และรองรับแนวคิดการจัดระดับกึ่งปริมาณ + การตรวจด้วยภาพดิจิทัล)

---

### [07] AASHTO The Manual for Bridge Evaluation (MBE), 3rd Edition — American Association of State Highway and Transportation Officials (2018) — ISBN 978-1-56051-683-5, Pub Code MBE-3 (PDF p.2)
- ชนิด: มาตรฐาน/คู่มือ (อ้างเป็นกฎหมายผ่าน NBIS 23 CFR 650 Subpart C, PDF p.6) ; อายุ: 2018 = 8 ปี อยู่ในช่วง 5-10 ปี ใช้ได้ ; **ไม่มีเรื่องโดรน/UAV** (ค้าง drone/UAS/UAV ไม่พบ ; มีแค่ GPR, infrared thermography สำหรับ deck PDF p.68, 112-113)
- MBE ไม่นิยามระดับสภาพละเอียด: ระบุเพียงว่าใช้ NBI rating 0 (failed) ถึง 9 (excellent) PDF p.26 (พิมพ์ 3-3) และ element Condition State CS1-CS4 (Good/Fair/Poor/Severe) PDF p.27 (พิมพ์ 3-4) แต่ **ข้อความนิยามแต่ละระดับอยู่ในเอกสารอื่น** (Manual for Bridge Element Inspection (MBEI) และ FHWA Coding Guide, PDF p.27, 66) — ไม่อยู่ในเล่มนี้ ใช้ไฟล์ 08/11 ของกลุ่มแทน

**วัตถุประสงค์ / วิธีการ / ผลที่สำคัญ**
- วัตถุประสงค์: เป็นแหล่งอ้างอิงเพื่อพัฒนานโยบายตรวจและประเมินสะพานทางหลวง (PDF p.6 ข้อ 1.1)
- วิธีการ: 8 Section (ไฟล์เอกสาร, BMS, inspection, material testing, load rating, fatigue, load test, ตัวอย่าง)
- ผลหลักที่เกี่ยวกับเรา: Health Index 0-100 (ข้อ 3.3.1.2 ในไฟล์ PDF p.28-29) ; ประเภท/ความถี่การตรวจ (PDF p.47-52) ; แนวตรวจ PC girder (PDF p.75-76)

#### Health Index ของ AASHTO — ตรงกับสูตร EHI / T-BHI ของเรามาก (ใช้ได้ทันที)
- ระดับ element: HI_e = C_e1·y_e1 + C_e2·y_e2 + C_e3·y_e3 + C_e4·y_e4 (Eq. 3.3.1.3-1) โดย C_ei = ค่าสัมประสิทธิ์ถ่วงของ condition state i, y_ei = เปอร์เซ็นต์ของ element ใน state i (PDF p.28 พิมพ์ 3-5)
- "Index values range from 0 ... to 100" ; CS1 ใช้ C=1 เต็ม, CS4 ใช้ C=0 ; CS2/CS3 เจ้าของปรับน้ำหนักเองได้ ("Allowing for variable weights in the CS2 and CS3 categories") (PDF p.28) — ตัวเลข C ที่แนะนำ **ไม่มีในเล่มนี้** (ยืนยันไม่ได้ว่า C_e2, C_e3 ควรเป็นเท่าไร)
- ระดับสะพาน: HI = Σ(q_e · w_e · HI_e) / Σ(q_e · w_e) (Eq. 3.3.1.3-2) โดย q_e = ปริมาณรวมขององค์ประกอบ w_e = "weight or importance factor" ขององค์ประกอบ (PDF p.29 พิมพ์ 3-6) — รูปสมการเดียวกับ T-BHI = Σ(q·W·EHI)/Σ(q·W) ในแผนเรา
- ข้อสังเกตด้านเลขท้ายสมการ: ข้อความในเล่มโยงว่า "AASHTOWare BrM software provides a bridge Health Index" (PDF p.28) — ใช้เป็นแหล่งอ้างว่า Health Index 0-100 มีใช้จริงในมาตรฐานอเมริกัน
- **ไม่มีค่า w_e เป็นตัวเลขใน MBE** (ค้นทั้ง Section 3 แล้ว) — น้ำหนักคานหลัก/เสา = 10 ... ราวกันตก = 5 ของเราไม่ได้มาจากเล่มนี้ ต้องอ้างแหล่งอื่นหรือระบุเป็นการสังเคราะห์ ; MBE บอกแค่ว่า "impact of an element on the bridge health index is related to its condition, total quantity, and the weight or importance factor" (PDF p.29)
- ต่างจากของเรา: AASHTO ใช้ 4 states (CS1-4) ของเรา 6 ระดับ (0-5) ; AASHTO ใช้เปอร์เซ็นต์ปริมาณของ element ในแต่ละ state ซึ่งเทียบได้กับ "สัดส่วนพื้นที่ในแต่ละระดับ" ของเรา

#### (2) นิยามระดับสภาพของ AASHTO เทียบ 0-5 แบบไทย
- NBI 0-9 (PDF p.26): 0 = failed, 9 = excellent เท่านั้นที่ระบุในเล่ม ; ระดับกลางไม่ได้นิยามใน MBE ; ยืนยันได้เพียงว่า: rating ≤5 ต้องมีคำบรรยายประกอบ (PDF p.18 พิมพ์ 2-3 "justify a condition rating of 5 or less for NBI items and Condition State 3 or more for elements")
- ตาราง Table C6A.4.2.3-1 (PDF p.153 พิมพ์ 6-19): แปลง NBI Item 59 → สภาพชิ้นส่วน: ≥6 = Good/Satisfactory ; 5 = Fair ; ≤4 = Poor → φc 1.00 / 0.95 / 0.85 (Table 6A.4.2.3-1 PDF p.152 พิมพ์ 6-18) — ใช้คำนวณ load rating ไม่ใช่เกณฑ์ตรวจ แต่ใช้เป็นหลักฐานว่าอเมริกาจัดกลุ่ม 3 ระดับ (Good/Fair/Poor) ที่ NBI 6/5/4 เป็นรอยต่อ
- CS1 Good, CS2 Fair, CS3 Poor, CS4 Severe (PDF p.27) ; ตัวอย่างกฎเงื่อนไขในมาตรฐาน: "Replace seals ... when quantity in CS2 exceeds 20 percent, or quantity in CS3 is greater than 0 percent" (PDF p.34 พิมพ์ 3-11) — แสดงว่าการตัดสินใช้สัดส่วนปริมาณต่อ state
- ข้อเสนอการเทียบ (ตีความของเรา ไม่ใช่ในต้นฉบับ): CS1 ≈ 5-4, CS2 ≈ 3, CS3 ≈ 2-1, CS4 ≈ 0-1 ; NBI 9-7 ≈ 5, 6 ≈ 4, 5 ≈ 3, 4 ≈ 2, 3-2 ≈ 1, 1-0 ≈ 0 — ต้องตรวจกับเอกสาร 08 (FHWA CS handout) ก่อนเขียนเป็นข้อเท็จจริง

#### ประเภทและความถี่การตรวจ (AASHTO ข้อ 4.2.3-4.2.4)
- 7 ชนิด: Initial, Routine, In-Depth, Fracture-Critical Member, Underwater, Special, Damage (PDF p.47-50 พิมพ์ 4-3…4-6)
- ความถี่ขั้นต่ำตาม NBIS: Initial ต้องเสร็จภายใน 90 วัน (รัฐ/รัฐบาลกลาง) หรือ 180 วัน (อื่น ๆ) หลังเปิดใช้ ; **Routine ≤ 24 เดือน** (ถึง 48 เดือนได้หากมีเกณฑ์เขียนและ FHWA อนุมัติ) ; FCM ≤ 24 เดือน ; Underwater ≤ 60 เดือน (ถึง 72) ; In-depth/Special ไม่มีขั้นต่ำ ; Damage ตามเหตุการณ์ (PDF p.51-52 พิมพ์ 4-7, 4-8)
- Routine: สังเกตทุก element + วัดที่จำเป็น เพื่อเทียบกับ initial และยืนยันความปลอดภัย (PDF p.47) ; ทำจากดาดฟ้า/พื้นดิน/ระดับน้ำ ใช้ under-bridge equipment เฉพาะที่เป็นทางเดียวที่เข้าถึง (PDF p.47)
- In-depth: ตรวจใกล้ ด้วยวิธีตาหรือ NDT เพื่อหาความเสียหายที่ routine ไม่เห็น (PDF p.48)
- Routine + ข้อกำหนดภาพถ่าย: ต้องมีคำบรรยายสนับสนุนทุก condition rating, ระบุข้อบกพร่องสำคัญพร้อมภาพถ่าย (ใช้ภาพตัวแทนได้ถ้าซ้ำกัน), ภาพถ่าย baseline ใน initial (PDF p.53-54 พิมพ์ 4-9, 4-10)
- Critical Inspection Finding (CIF): ต้องนิยามและมีขั้นตอนแจ้งเตือนทันที (PDF p.54, 67)

#### ชนิดความเสียหาย/แนวตรวจคอนกรีตอัดแรง (AASHTO)
- ข้อ 4.3.5.6.3 Prestressed concrete beams/girders (PDF p.75-76 พิมพ์ 4-31, 4-32): ตรวจ alignment, cracking, deterioration ; cracking/spalling รอบ bearing และ cast-in-place diaphragm ; "Carefully note the location of any cracks and their sizes for future reference" ; **"Evidence of rust staining at cracks can mean possible damage to prestressing steel, and should warrant additional investigation"** ; sound ผิวคอนกรีตหุ้มเส้นลวด และจด delamination เพราะ "Delamination may indicate prestressed strands have begun to corrode" ; ตรวจผิวด้านนอกและ soffit ของ girder ทุกชนิด จด spalling/cracking/damage ต่อลวดอัดแรง
- ข้อ 4.3.5.6.2 RC girders (PDF p.74-75): รอยเฉียงจาก bearing เข้าหากลางช่วง = shear ; รอยตั้งขึ้นจาก soffit กลางช่วง = tension ; high edge pressure ที่ bearing ทำให้ spall
- ข้อ 4.3.5.2 Cleaning (PDF p.65-66 พิมพ์ 4-21, 4-22): "On concrete structures, efflorescence and debris may cover heavily corroded reinforcing, cracks, or other deterioration" ; delaminated concrete อาจปิดเหล็กที่สนิม — ควรเอาส่วนที่หลุดร่อนออกเพื่อดูเหล็กด้านใน (เป็นข้อจำกัดของการตรวจด้วยภาพถ่ายที่ควรอ้างถึง)
- ข้อ 4.3.5.1 Field measurements (PDF p.65 พิมพ์ 4-21): วัดและบันทึกขนาดรอยร้าวเพื่อติดตามการเปลี่ยนแปลง เก็บเป็น log ต่อรอบการตรวจ ทำเครื่องหมายถาวรบนชิ้นส่วนได้ ; วัด spall เป็น ยาว × กว้าง × ลึก ; สำหรับเหล็กเสริม/ลวดอัดแรงที่โผล่ ให้ระบุหน้าตัดที่เหลือจริง ไม่ใช่ประเมินเปอร์เซ็นต์ด้วยสายตา
- ข้อ 4.3.6.5 Prestressed segmental bridges (PDF p.100-101 พิมพ์ 4-56, 4-57): รอยร้าวตามยาวที่ขอบ web ของ girder นอก, ดูโปรไฟล์ด้านบนว่ามี hump/sag (ผลของ creep ของ tendon), ท่อ tendon ที่มีน้ำขังกัดกร่อน
- **ไม่มีเกณฑ์ความกว้างรอยร้าวเป็นตัวเลข** (ค้นตัวเลขนิ้ว/มม. ไม่พบ ; ที่เจอคือ "crack size" แบบไม่มีเกณฑ์ PDF p.65, 74 และเรื่อง crack-width control เป็นเกณฑ์ออกแบบ RC ที่ MBE บอกชัดว่า "not relevant to evaluation" PDF p.173)

#### (1) เกณฑ์ความกว้างรอยร้าว PC 0.1/0.23/0.76 มม. ใน AASHTO MBE
**ไม่มี** (ตรวจแล้ว) — MBE ให้เพียงแนวตรวจและหลักการบันทึก เกณฑ์ที่เป็นตัวเลขอยู่ในเอกสาร/คู่มืออื่น (เช่น NCHRP Report 280, MBEI) ซึ่งไม่ได้อยู่ในไฟล์นี้ ; ในรายการอ้างอิงมี "NCHRP. Guidelines for Evaluation and Repair of Prestressed Concrete Bridge Members, NCHRP Report 280" (PDF p.126) — ชื่อเรื่องเดียวที่อาจมีเกณฑ์ แต่ยืนยันไม่ได้จากเล่มนี้

#### การตรวจด้วย NDT/ภาพ (AASHTO)
- Section 5 ข้อ 5.2.1: sonic, ultrasonic, magnetic, electrical, nuclear, thermography, radar, radiography, endoscope (PDF p.107-108) ; hammer sounding/chain drag หา delamination (PDF p.110) ; infrared thermography ใช้ได้กับ element ที่โดนแดดโดยตรง (PDF p.112) ; GPR (PDF p.113) — ไม่มีโดรน ไม่มี photogrammetry
- กล้อง/ภาพถ่ายเป็น "basic inspection equipment" (PDF p.62) ; แนวภาพถ่ายประกอบสเก็ตช์เพื่อกำหนดขอบเขตความเสียหาย (PDF p.63)

#### น้ำหนัก/ความสำคัญของชิ้นส่วน (AASHTO)
- มีแค่สัญลักษณ์ w_e "weight or importance factor" (PDF p.29) — ไม่กำหนดค่า
- มีการแยกชิ้นส่วน fracture-critical (เหล็ก) และ system factor φs ของ load rating (PDF p.153) ซึ่งเกี่ยวกับ redundancy ไม่ใช่น้ำหนักของ Health Index จึงไม่ควรเอามาปนกับ W ของเรา

#### (3) ที่อ้างในหัวข้อ 2.2 ได้ทันที (AASHTO)
- นิยาม Condition rating: "assessment of the functional capability and the physical condition of bridge components by considering the extent of deterioration and other defects" (PDF p.10 พิมพ์ 1-5)
- Health Index 0-100 และสูตรถ่วงน้ำหนักระดับ element/สะพาน (PDF p.28-29 พิมพ์ 3-5, 3-6) — **หลักฐานหลักว่า T-BHI มีรากในมาตรฐานจริง** ใช้ทั้ง 2.2 และ 3.7
- สเกลสภาพ NBI 0-9 และ element CS1-4 (PDF p.26-27)
- ชนิดการตรวจและความถี่ขั้นต่ำ routine ≤24 เดือน (PDF p.47-52)
- คำแนะนำตรวจ PC girder (rust stain ที่รอยร้าว = อาจเสียหายต่อลวดอัดแรง, delamination = ลวดเริ่มสนิม) (PDF p.75)
- ข้อจำกัดของการตรวจด้วยตา efflorescence/เศษซากบังรอยร้าวและเหล็กสนิม (PDF p.66) และให้บันทึกรอยร้าวด้วยภาพ + สเก็ตช์ + วัดขนาดเพื่อเปรียบเทียบรอบถัดไป (PDF p.62-63, 65) — รองรับการเก็บภาพแยกตามชิ้นส่วนและการเก็บ confidence flag

**ข้อจำกัด/ห้ามอ้างเกินจริง (AASHTO):** ไม่ได้กำหนดเกณฑ์ความกว้างรอยร้าวเป็นตัวเลข ; ไม่ได้นิยามระดับ NBI ระหว่าง 1-8 หรือเนื้อหา CS1-4 ใน MBE (ไปอยู่ MBEI/FHWA) ; ไม่ได้ให้ค่า C_e2/C_e3 หรือ w_e ที่ใช้จริง ; ไม่ครอบคลุมโดรน ; สเกลของ AASHTO เป็น 4 states (ไม่ใช่ 6 ระดับ) ; **ความเกี่ยวข้องกับงานเรา: ใช้แน่** สำหรับ 2.2 (Health Index, สูตรถ่วงน้ำหนักตามปริมาณ/ความสำคัญ, ชนิดและความถี่การตรวจ, แนวตรวจ PC girder) และรองรับ 3.7 (วิธีคำนวณ EHI → T-BHI)

---

## สรุปกลุ่ม (G2b)
1. **AASHTO MBE 2018 ควรเข้า proposal** (ใช้แน่): ให้ Health Index 0-100 สูตรถ่วงน้ำหนักด้วยสัดส่วนปริมาณของแต่ละ condition state (Eq. 3.3.1.3-1) และถ่วงน้ำหนักชิ้นส่วนด้วย q·w (Eq. 3.3.1.3-2) PDF p.28-29 เป็นฐานรองรับสูตร EHI/T-BHI ของเราโดยตรง ; อายุ 2018 อยู่ในช่วง 5-10 ปี ; ใช้ใน 2.2 และ 3.7
2. **JSCE 2007 ใช้เสริม**: รองรับเกรดรูปลักษณ์กึ่งปริมาณ (Table C9.3.4 / C10.3.4 / C9.3.3), ประเภท/ความถี่การตรวจ, และการวิเคราะห์ภาพดิจิทัลวัดตำแหน่ง/ขนาดความเสียหาย (PDF p.76) ; อายุเกิน 10 ปี จึงควรอ้างเป็นมาตรฐานประกอบไม่ใช่งานวิจัยหลัก
3. **เกณฑ์รอยร้าว PC 0.1/0.23/0.76 มม. ไม่อยู่ในทั้ง 07 และ 09** (ตรวจครบทั้งสองเล่ม) ต้องไปหาที่ BMMS/เอกสารอื่นของกลุ่ม ห้ามอ้างทั้งสองเล่มสำหรับตัวเลขนี้
4. **น้ำหนัก W ของแต่ละชิ้นส่วน (10 ... 5) ไม่ได้มาจาก 07/09**: MBE มีแค่ตัวแปร w_e แบบไม่กำหนดค่า ; JSCE ไม่มีเลย → ตัวเลข 10…5 ต้องเขียนเป็นการสังเคราะห์/กำหนดโดยผู้ทำ หรืออ้างแหล่งอื่น
5. **ไม่มีเนื้อหาโดรน/ภาพถ่ายทางอากาศ** ทั้งสองเล่ม → 2.4 ต้องหาแหล่งอื่น (กลุ่มเปเปอร์) ; ที่ได้จาก 07/09 คือข้อรองรับการตรวจด้วยภาพ (JSCE p.76: image analysis จากกล้องดิจิทัล; AASHTO p.62-63: ภาพถ่ายประกอบรายงาน; AASHTO p.66: ข้อจำกัด efflorescence บังรอย)
6. **ข้อสังเกตขัดแผน:** (ก) JSCE I-1 กับ I-2 แยกด้วยค่าคาร์บอเนชัน/คลอไรด์ ซึ่งภาพโดรนบอกไม่ได้ ; (ข) AASHTO ใช้ 4 states ส่วนของเรา 6 ระดับ ต้องอธิบายการแปลง ; (ค) AASHTO ให้ CS2/CS3 ปรับน้ำหนักได้เอง (PDF p.28) เป็นเหตุผลรองรับการกำหนด C_hi = 0.83/0.67/0.33/0.17 ของเราเอง แต่ไม่ได้รับรองตัวเลขเหล่านี้ ; (ค) ความถี่ตรวจ routine ของ AASHTO 24 เดือน กับ JSCE regular ของสะพานถนน 5 ปี (PDF p.66) ต่างกัน ต้องเลือกแหล่งตามบริบทไทย
7. **ช่องว่างหัวข้อที่กลุ่มนี้ยังไม่รองรับ:** เกณฑ์รอยร้าวเป็นตัวเลข (2.2 / 3.7) ; นิยามข้อความ CS1-4 ของ element คอนกรีตอัดแรง (ต้องใช้ 08/11) ; ค่าน้ำหนักชิ้นส่วน (W) ; โดรน/โฟโตแกรมเมตรี (2.4) ; การวัดขนาดรอยร้าวด้วยเลเซอร์/GSD (2.5) ; deep learning (2.3)
