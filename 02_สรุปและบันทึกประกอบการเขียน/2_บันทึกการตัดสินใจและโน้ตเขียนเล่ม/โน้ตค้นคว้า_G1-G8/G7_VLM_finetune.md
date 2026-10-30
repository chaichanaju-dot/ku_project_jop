# G7 — VLM / fine-tuning (เอกสาร 23, 24, 25, 37) — หลักฐานรองรับหัวข้อ 2.3 และ 3.5

ผู้อ่าน: อ่านเนื้อหาทั้งฉบับของ 23 และ 24; 37 อ่านทุกส่วนยกเว้นตารางผลลัพธ์ classification ละเอียดและรายการอ้างอิง; 25 อ่านสารบัญ + ทุกส่วนที่เกี่ยวกับ prompt/adapter/fine-tuning/LoRA/pre-trained models/datasets-challenges/evaluation/future (ข้ามตารางชุดข้อมูลหน้า 22-28 ส่วนใหญ่ และรายการอ้างอิง).
เลขหน้า (p.N) = เลข "=== PAGE n ===" ในไฟล์ txt (ตรงกับหน้า PDF). เกี่ยวกับ "Qwen 3.6 35B": ไม่มีในเอกสารใดเลย (ดูข้อ 6).

## คำตอบสั้นก่อน (สิ่งที่ผู้เขียน proposal ควรรู้)
1. **เอกสารทั้ง 4 ฉบับไม่มีตัวเลขวัดความสามารถ "ให้ bounding box/จุด" ของ generative MLLM (แบบ Qwen-VL) เลย** — ไม่มีฉบับไหนทดสอบ VLM หา box แล้ววัด IoU/AP. สิ่งที่มีใกล้สุด: (ก) ตัวเลข zero-shot detection ของ VLM สายแบบ CLIP/GLIP ใน 37 (p.15) ซึ่งไม่ใช่ MLLM, (ข) งานสะพานสองฉบับ (23, 24) ที่ **ให้ VLM เขียนข้อความเท่านั้น ไม่ให้หาตำแหน่ง** — ตัวหาตำแหน่งใน 24 คือ YOLO11-seg. ดังนั้น 3.5 ส่วน "Qwen หา box/จุดแล้วส่ง SAM" **ต้องหาเปเปอร์รองรับจากนอกกลุ่มนี้** (เช่นรายงานเทคนิค Qwen-VL / Qwen2.5-VL ที่อยู่ในรายการอ้างอิงของ 25 เป็น [225], [231] p.39 — แต่ไฟล์ของเรามีเฉพาะชื่อเรื่อง ไม่ใช่เนื้อหา).
2. **Fine-tune VLM 7B-11B ด้วย QLoRA/LoRA ทำได้บน GPU เครื่องเดียว** และข้อมูลระดับ 2,000 คู่ภาพ-ข้อความก็พอถึงจุดคุ้ม (23) หรือ 700 ภาพ (24) — แต่ทั้งคู่ fine-tune เพื่อ "เขียนคำอธิบาย" ไม่ใช่เพื่อ "ให้พิกัด" จึงใช้อ้างเรื่องข้อมูล/ทรัพยากรสำหรับ grounding โดยตรงไม่ได้.
3. **คำเตือนที่มีหลักฐานตรงที่สุด**: 23 วัดเองพบ mode collapse (ทุกเอาต์พุต 100% พูดถึง Main Girder, 99.6% rebar exposure, 98.6% spalling; คะแนนความเร่งด่วนทุกตัวเท่ากัน) และข้อมูลมากขึ้น (4k) ผลแย่ลง.
4. ไม่มีเปเปอร์ใน 4 ฉบับที่ใช้ SAM ต่อจาก VLM; SAM/Grounding DINO ถูกกล่าวถึงแค่ประโยคเดียวใน 23 (p.2, อ้างอิงมือสอง).

---

### [23] Fine-Tuning Vision-Language Models for Understanding Current Damage and Scoring Priority with Quality Guard Agent — Takato Yasuno (2026) — arXiv:2605.27452v1 [cs.CV], 24 พ.ค. 2026 (p.1)
- ชนิด: เปเปอร์วิจัย (preprint arXiv v1; ในไฟล์ไม่มีข้อมูล peer review → ถือเป็น preprint) ; อายุ: <1 ปี (อยู่ในช่วง 5-10 ปี)
- **วัตถุประสงค์**: ทำให้การประเมินความเสียหายสะพาน (ระดับ a–e ของญี่ปุ่น) สม่ำเสมอขึ้น โดย fine-tune VLM ให้เขียนคำบรรยายความเสียหายจากภาพเดียว แล้วใช้กฎ (rule engine) แปลงเป็นดัชนีความเร่งด่วนซ่อม 5 ระดับ (p.1-2)
- **วิธีการ**: LLaVA-1.5-7B (CLIP ViT-L/14 + Vicuna-1.5-7B ต่อด้วย MLP 2 ชั้น, p.6) + QLoRA 4-bit NF4 double-quant, rank r=32, alpha=64, dropout 0.05, target q/k/v/o/gate/up/down_proj; lr 2e-4, 3 epochs, effective batch 16, FP16 (Table 2, p.6-7); GPU RTX 4060 Ti 16GB (p.7). ข้อมูล: pool 10,789 คู่ภาพ-"shoken" ภาษาญี่ปุ่นจากการตรวจสะพานตามกฎหมายถนน (p.5) → กรองคุณภาพ → test คงที่ 800 (798 ภาพใช้ได้) + train 1k/2k/3k/4k แบ่ง 80/20 (Table 1, p.6). ประเมินด้วย cosine similarity ของ Sentence-BERT ภาษาญี่ปุ่น (p.11). เพิ่ม "Quality Guard" 2 ชั้น (กฎ + SLM judge Swallow-8B) กรองเอาต์พุตคุณภาพต่ำก่อนให้คะแนน (p.9-10).
- **ผลที่สำคัญ (คัดตรงตัว)**:
  - เวลาเทรน/val loss (Table 3, p.7): 1k = 3.135 / 1:22:57; 2k = 3.073 / 2:55:37; 3k = 3.073 / 4:31:44; 4k = 3.067 / 6:19:10. บทคัดย่อ (p.1): "2k ... near-optimal validation loss (3.073) in only 2.9 hours ... beyond 2k, validation loss improves by no more than 0.2% per doubling".
  - Cosine similarity (Table 11, p.11): 1k 0.6491±0.0875; 2k 0.6850±0.0814; 3k 0.6909±0.0784 (สูงสุด); 4k 0.6739±0.0795 (ตก) — ทุกโมเดลอยู่ระดับ "Acceptable"; Good ขึ้นไป 2k = 46.9% (Table 12, p.12), 4k = 15.9% (p.12). ข้อความ (p.12): "quality-curated mid-scale data outperforms larger but noisier corpora" (บทคัดย่อ p.1).
  - Inference (Table 4, p.7): 33.79 s/ภาพ (baseline) → 10.06 s/ภาพ (torch.compile + batch 8) = ลด 70.2%; batch 16 VRAM 98% เสี่ยง OOM.
  - Quality Guard (Table 8-9, p.9-10): ใน 800 ภาพ ผ่าน 727 (90.9%), ตก 73 (9.1%); รูปแบบ output คุณภาพต่ำรวม 12.5% (สั้นเกิน 4.4%, ยาวเกิน 3.4%, ข้อความวน 3.0%, ภาพสกปรก/noisy 1.5%, "ไม่รู้จากภาพ" 0.2%) (p.9).
  - **Mode collapse** (p.14-15, Fig.10 p.17): Main Girder ถูกพูดถึง 727/727 = 100%; Rebar Exposure 724/727 = 99.6%; Spalling 717/727 = 98.6%; คะแนนความเร่งด่วนของทั้ง 727 ตัว = 0.54 (Level 3) เท่ากันหมด (p.14, 16).
- **ความเกี่ยวข้องกับงานเรา**: **ใช้เสริม** — 2.3 (ตัวอย่าง fine-tune VLM ด้วย QLoRA ในโดเมนสะพานจริง + ตัวเลขข้อมูล/เวลา/GPU) และ 3.5 (เหตุผลเรื่อง "เครื่องรันไหว" และ "ข้อมูลเท่าไรพอ") ; **ไม่รองรับ** ประเด็นการหาตำแหน่ง/ส่งต่อ SAM เพราะ VLM ตัวนี้ไม่ให้พิกัดเลย.
- **ข้อเท็จจริงที่หยิบไปเขียนได้เลย**:
  - QLoRA ทำให้ fine-tune VLM 7B ได้ในเครื่อง GPU 16GB (p.6 "enables fine-tuning a 7B-parameter model within 16GB VRAM"; p.7 RTX 4060 Ti 16GB).
  - ข้อมูล 2,000 คู่ภาพ-ข้อความ เทรน ~2.9 ชม. ให้ผลใกล้จุดคุ้มสุด; เพิ่มเป็น 4,000 คู่ ผลทดสอบตกลง (p.7, p.11-12).
  - ใช้ VLM เป็นส่วนอ่านแล้วให้กฎที่ตรวจสอบได้ตัดสินคะแนนต่อ (p.2 "transparent, auditable rule engine"; p.3-4 VLM เป็น "semantic front-end" ให้ rule engine) — แนวคิดคล้ายท่อของเรา (VLM → Python คำนวณระดับ/EHI) เหมือนกันเชิงสถาปัตยกรรม.
  - ตัวอย่างการใช้ VLM ของงานก่อสร้างอ้างมือสอง: Pu et al. (ISARC 2024) MLLM + Set-of-Mark prompting สร้างรายงานตรวจจากภาพหน้างาน, Hsu et al. VL-Con dataset, Núñez Varillas et al. (ISARC 2024) โฟโตแกรมเมตรี UAV + CNN จำแนกความเสียหายบนแบบจำลอง 3 มิติของสะพาน (p.4) — **ต้องเปิดต้นฉบับก่อนอ้าง**.
- **ข้อจำกัด/ห้ามอ้างเกิน**:
  - ไม่ใช่ grounding: ผลลัพธ์เป็นข้อความ; แยกชัดว่า pixel-level detection เป็นสายอื่น และชี้ช่องว่าระหว่าง pixel detection กับรายงานภาษา (p.2, อ้าง Spencer et al.).
  - ตัวชี้วัดคือ cosine similarity ของข้อความ ไม่ใช่ความถูกต้องของ "ชิ้นส่วน/ชนิดความเสียหาย" รายตัว — ผู้เขียนยอมรับเอง (p.17) ; ทั้งหมดอยู่ระดับ Acceptable ไม่ถึง Good.
  - **ความไม่สอดคล้องภายใน (ต้องระวังถ้าจะอ้างตัวเลข)**: เกณฑ์ tier ใน Table 10 (Good ≥0.75, Acceptable ≥0.65, p.11) ไม่ตรงกับคำบรรยาย Table 11 (Good ≥0.70, Acceptable ≥0.60, p.11) และข้อความ p.12 ("Acceptable tier ρ∈[0.60,0.70)"); จำนวน token เฉลี่ยของโมเดล 3k = 135.2 (Fig.2, p.9) แต่ Table 5 (p.8) ให้ mean 266.4 — ไฟล์ไม่อธิบายความต่าง (ยืนยันไม่ได้ว่าเกิดจากอะไร).
  - เป็น preprint ฉบับแรก (v1) ข้อมูลเป็นภาษาญี่ปุ่นเฉพาะกฎหมายญี่ปุ่น (p.17); เทรนบน GPU รุ่นเดียว ไม่ได้ตรวจกับ GPU อื่น (p.18).
  - ไม่มีตัวเลข zero-shot baseline ของ LLaVA-1.5 ในฉบับนี้ (baseline คือโมเดล 1k) — การเทียบ zero-shot อยู่ในงานก่อนหน้า [6] arXiv:2603.26770 ที่เขาอ้าง (p.2) แต่ตัวเลขไม่อยู่ในไฟล์ → **ยืนยันไม่ได้**.

---

### [24] (ไฟล์ชื่อ LiuFinetune) Metaheuristic-optimized vision–language framework for quantitative assessment of concrete bridge deterioration — Jui-Sheng Chou, Chia-Hsiang Chang, Chi-Yun Liu (2026) — Engineering Structures 363 (2026) 122898, doi:10.1016/j.engstruct.2026.122898 (รับ 24 ธ.ค. 2025 ปรับปรุง 25 เม.ย. 2026 ตอบรับ 30 เม.ย. 2026; p.1)
- หมายเหตุชื่อไฟล์: ชื่อไฟล์ "LiuFinetune" แต่ผู้เขียนคนแรกคือ **Chou** (Liu เป็นผู้เขียนคนที่ 3) — ตอนอ้างอิงให้ใช้ "Chou et al. (2026)".
- ชนิด: เปเปอร์วิจัย (วารสาร peer-reviewed) ; อายุ: <1 ปี
- **วัตถุประสงค์**: ตรวจหา วัดปริมาณ และเขียนรายงานความเสียหายคอนกรีตสะพานอัตโนมัติ โดยประกอบ instance segmentation กับ MLLM (p.1)
- **วิธีการ**: สถาปัตยกรรม "dual-stream" (p.1, p.4): (1) **YOLO11-seg** หาตำแหน่ง+mask ความเสียหาย 5 ชนิด: cracking, spalling, honeycombing, exposed/corroded rebar, vegetation (p.7) → ใช้ polygon นับพื้นที่พิกเซลด้วย shapely แล้วแปลงเป็น m² ด้วยตัวคูณสเกล s = d/D = h/H จากวัตถุอ้างอิง/ไม้บรรทัดในภาพ (area_m² = area_px × s², Eq.7-8, p.12; ค่าตั้งต้น magnification = 1) (2) **Llama 3.2 Vision 11B** (Unsloth, 4-bit, **LoRA**, SFT; p.7) เขียนคำบรรยาย/วิธีซ่อมตามชิ้นส่วน + RAG อิงคู่มือ/ข้อกำหนด (p.12) ; ทั้งสองสายต่อกันที่ระดับ "record" ไม่ใช่ระดับ feature (decision-level fusion, p.11). ปรับ hyperparameter ด้วย Pilgrimage Walk Optimization (PWO, metaheuristic) เทียบ GA (p.10-11).
- **ข้อมูล**: 700 ภาพ = 650 ภาพชำรุด + 50 ภาพส่วนที่ปกติ (p.7) จากรายงานตรวจเทศบาลไทเป, สำรวจภาคสนาม, CODEBRIM และภาพใหม่ (p.7); ชิ้นส่วน 10 ชนิด; ผู้ label คนเดียว (นักศึกษาปริญญาโท) ตรวจโดยอาจารย์ 2 ท่าน (p.7).
- **ผลที่สำคัญ (คัดตรงตัว)**:
  - **Fine-tune vs ก่อน fine-tune (ข้อความ)** BERTScore F1 (Table 1, p.8): val 0.6025 → 0.8137 (+35.08%); test 0.5929 → 0.7945 (+34.01%). ก่อน fine-tune Llama 3.2 ตอบ "NA" ทั้งชิ้นส่วนและชนิดความเสียหาย (Table 2, p.8) และตอบซ่อมแบบสั้น/ไม่ตรงประเด็น (Table 3, p.9). หลัง PWO: val 0.8523 (+4.74%), test 0.8384 (+5.53%) เทียบ fine-tune ปกติ; GA +2.77%/+3.56% (Table 7, p.10).
  - **ฝั่ง segmentation (Table 5, p.9)**: mAP50 เฉลี่ย 50.5% (val) / 52.1% (test); รายคลาส val/test: honeycombing 50.8/49.3, spalling 50.3/48.4, **cracking 38.0/55.6**, **exposed & rusted rebar 42.0/36.3**, vegetation 71.4/71.0. หลังปรับ PWO (Table 9, p.11): เฉลี่ย 53.6 (val) / 54.0 (test); cracking 41.9/58.1; exposed rebar 44.9/38.3.
  - ผู้เขียนระบุ (p.9) ว่ารอยร้าวและเหล็กโผล่ "exhibit fine textures and irregular patterns that are easily obscured ... reducing segmentation accuracy" และ mAP50 รวมต่ำกว่างาน crack-only เดี่ยวๆ (Assad et al.: YOLOv9 87.8%, YOLO11 87.1%, Mask R-CNN 75.5%; dacl10k baseline mIoU ≈0.414 val/0.424 test) (p.11) — เป็นหลักฐานว่า **multi-class defect segmentation ยากกว่า single-class crack มาก**.
  - เทียบ GPT-4o (คนตอบแบบสอบถาม n=16 ตอบแบบ blind, Table 10, p.15): ความแม่นยำระบุชิ้นส่วน/ฉากความเสียหาย 3.92 vs 3.71 (p=0.281 ไม่มีนัยสำคัญ); ความเป็นมืออาชีพของวิธีซ่อม 4.03 vs 3.70 (p=0.039); ความชัดเจนทางเทคนิค 4.12 vs 3.61 (p=0.003); ความครบถ้วน 4.08 vs 3.61 (p=0.011); เฉลี่ย 4.037 vs 3.658 (p=0.0165).
  - เวลา: ค้นหา hyperparameter ของ LLM ~180 ชม., ของ YOLO11-seg ~130 ชม. (p.10); ทั้งระบบ 30–50 วินาที/ภาพบน RTX A6000 (p.12).
- **ความเกี่ยวข้องกับงานเรา**: **ใช้แน่** สำหรับ 2.3 (VLM คู่กับ segmentation ในงานสะพานคอนกรีต ปี 2026 ใกล้งานเรามาก 4 จาก 6 คลาสตรงกัน: Crack, Spalling, Exposed_Rebar, Honeycomb — คลาสของเรา Efflorescence/Rust_Stain ไม่มีในงานนี้ ส่วน vegetation ของเขาไม่มีในเรา) และ 2.6 (ตารางเปรียบเทียบ/ช่องว่าง); สำหรับ 3.5 **รองรับ "แบ่งบทบาท: โมเดล segmentation หา mask, VLM ทำงานภาษา"** และวิธีแปลง mask→พื้นที่จริง (เชื่อม 3.6) แต่ **ไม่รองรับ** แผนให้ VLM หาตำแหน่ง→SAM.
- **ข้อเท็จจริงที่หยิบไปเขียนได้เลย**:
  - เลือกแยกโมเดล (YOLO11-seg + Llama 3.2 Vision) แทน end-to-end (Florence-2, PaliGemma, Vitron) เพราะ "flexibility for domain-specific fine-tuning and local deployment — a critical factor for infrastructure data security" (p.4); เหตุผลคือ openness, fine-tuning flexibility, ตรวจ subtle defect, ทำซ้ำได้ (p.3) — เป็นตัวอย่างเหตุผลเลือกโมเดลเปิดรันในเครื่อง (ใช้เป็นแนวคิดสำหรับ "ทำไมเลือก Qwen" ได้เฉพาะเชิงหลักการ ไม่ใช่เอ่ยชื่อ Qwen).
  - LoRA + 4-bit บน GPU เดียวพอสำหรับ VLM 11B (p.7 "single-GPU system ... significant benefits by reducing computational cost and training time"); early stopping เมื่อ val loss ไม่ดีขึ้น 10 ครั้ง หยุดที่ step 850 (p.8).
  - การวัดพื้นที่ใช้ mask จากโมเดล segmentation ไม่ใช่จาก VLM; สเกลจากวัตถุอ้างอิงในภาพ (Eq.7-8, p.12) — แนวเดียวกับ "ไม้บรรทัดในภาพ" ของเรา.
  - งานก่อนหน้าที่อ้าง (มือสอง): Kunlamai et al. ใช้ VQA กับรายงานตรวจสะพาน, Chun et al. image captioning CNN+LSTM, Chou et al. [16] ViT + YOLOv8 วัดพื้นที่ polygon ต่อด้วยต้นทุนซ่อม, Pu et al. MiniGPT4-7B ทำรายงานก่อสร้าง (p.2-3).
- **ข้อจำกัด/ห้ามอ้างเกินจริง**:
  - **VLM ในงานนี้ไม่ได้ทำ localization/grounding** (ผู้เขียนใช้ YOLO ทำ) และ **BERTScore วัดความคล้ายของข้อความ ไม่ใช่ความถูกต้องของตำแหน่ง/ชนิด**; ส่วนวิธีวิจัย (p.7) บอกว่าใช้ confusion matrix จำแนกชิ้นส่วน/ความเสียหาย แต่ในผลลัพธ์ที่อ่านไม่พบตัวเลขความแม่นยำการจำแนกชิ้นส่วนรายชนิดเลย (ยืนยันไม่ได้ว่าเป็นเท่าไร).
  - ข้อมูลเล็ก (700 ภาพ) และส่วนใหญ่จากไต้หวัน; ผู้เขียนยอมรับว่ายังไม่ทดสอบการอนุมานข้ามภูมิภาค/ข้ามโครงสร้าง (p.15).
  - mAP50 ≈ 50–54% ถือว่าไม่สูง; ผู้เขียนใช้ augmentation ที่ PWO จูนเอง และกำชับว่าผลดีขึ้นไม่ได้แปลว่า augmentation แก้ปัญหาข้อมูลน้อยได้ (p.10).
  - คำกล่าวว่า RAG ช่วยลด hallucination (p.4) เป็นการอ้างเชิงออกแบบ — **ไม่มีการวัดอัตรา hallucination ในไฟล์**.
  - Fine-tuned Llama ตอบไม่คงที่เท่า GPT-4o (Table 4, p.9: "Generated sentences vary significantly between each response"; มี typo/ซ้ำซ้อนบางครั้ง).
  - ตัวอย่างคนตอบแบบสอบถามเล็ก (16 คน) (p.12) ; รายละเอียด GPU ที่ใช้เทรน อยู่ใน Appendix E ซึ่งไม่อยู่ในข้อความที่ถอด → ยืนยันไม่ได้ว่า GPU รุ่นอะไร (รู้แค่ RTX A6000 ตอนวัดเวลา, p.12).

---

### [25] A comprehensive survey of Vision–Language Models: Pretrained models, fine-tuning, prompt engineering, adapters, and benchmark datasets — Sufyan Danish, Abolghasem Sadeghi-Niaraki, Samee Ullah Khan, L. Minh Dang, Lilia Tightiz, Hyeonjoon Moon (2026) — Information Fusion 126 (2026) 103623, doi:10.1016/j.inffus.2025.103623 (รับ 25 มี.ค. 2025; ตอบรับ 7 ส.ค. 2025; p.1)
- ชนิด: รีวิว/survey (วารสาร Information Fusion; ควอร์ไทล์/อันดับวารสารไม่มีในไฟล์ — ยืนยันไม่ได้) ; อายุ: ตีพิมพ์ 2025-2026 (อยู่ในช่วง) ; รีวิว 115 เปเปอร์ ช่วง 2018–2025 (บทคัดย่อ p.1; คัดจาก 600→305→200→115, p.4)
- สารบัญ (p.4): 2 Foundation model paradigms; 3 VLM optimization (3.1 Prompt engineering, 3.2 Pretraining, 3.3 Adapter, 3.4 Fine tuning); 4 Pre-trained VLM models (Gemini, PaLI-Gemma2, XGen-7B, Qwen-VL, ChatGPT-4, innovations post-2023); 5 Datasets + benchmarking; 6 Evaluation metrics; 7 Challenges; 8 Discussion; 9 Conclusion
- **วัตถุประสงค์**: รวมเทคนิคการปรับ VLM (fine-tuning, prompt, adapter, pre-trained model, dataset) ไว้ในเปเปอร์เดียว (p.1-3)
- **วิธีการ**: systematic review ค้นฐาน ScienceDirect/Springer/Scopus/Web of Science + arXiv ที่ผ่านการรับตีพิมพ์ (p.4); จัด taxonomy + ตารางเปรียบเทียบ.
- **ผลที่สำคัญ (คัดตรงตัว)**:
  - **Adapter/LoRA (Table 5, p.17)**: LoRA แทรกที่ attention layers, trainable params "~0.5% to 2%", "Efficient, scalable, strong for both generation and understanding", ข้อเสีย "May underperform when high-rank adaptation is required"; BitFit ~0.03%; Houlsby ~1–3%; Compacter ~0.5–1.5%; Prefix tuning ~0.1–0.5%; Prompt tuning ~0.01–0.1%; LLaMA-Adapter v2 ~5%+.
  - ข้อสรุป (p.33): "adapter-based methods can reduce trainable parameters by up to 98% while preserving 80 to 95% of the full model performance"; soft/hybrid prompts ดีกว่า hard prompts 4–7% ใน few/zero-shot.
  - DARA ใช้ trainable params เพียง 2.13% เทียบ full fine-tuning (p.16, [213] ซึ่งชื่ออ้างอิงคือ adapter สำหรับ **visual grounding**, p.39).
  - Full vs partial fine-tuning (p.17-18): full fine-tuning ยืดหยุ่นสุดแต่ "computationally intensive"; partial/adapters ถูกกว่าแต่ "may not consistently achieve the same performance level as full fine tuning, especially for tasks that are extremely complex or specialized".
  - Table A.1 (p.34): LLaVA 1.5/1.6 batch 16–128, lr 2e-5, 1–3 epochs, **8× A100 (40/80GB)**, two-stage instruction tuning "uses LoRA"; CLIP ViT-L/14 batch 32k–65k, 256–600+ V100/A100 (เทียบกับ 37 p.15: 256 V100, 288 ชม.). ตัวเลขเหล่านี้เป็น "ช่วงโดยประมาณ" ในตาราง survey ไม่ใช่ค่าจากต้นฉบับตรวจแล้ว.
  - Post-2023 VLMs (p.20): โมเดลใหม่ "emphasize parameter-efficient fine-tuning ... adapters, LoRA, and tool-calling interfaces" (IDEFICS, Gemini, DeepSeek Janus).
- **ความเกี่ยวข้องกับงานเรา**: **ใช้เสริม** — รองรับ 2.3 (นิยาม VLM/MLLM, เส้นเวลา CLIP→Flamingo→BLIP→LLaVA/Qwen, ศัพท์ LoRA/adapter/prompt/fine-tuning, ตาราง LoRA %) และ 3.5 ส่วนเหตุผล "ใช้ parameter-efficient fine-tuning เมื่อทรัพยากรจำกัด". ไม่เกี่ยวกับ grounding/ความเสียหายสะพาน/SAM.
- **ข้อเท็จจริงที่หยิบไปเขียนได้เลย**:
  - นิยาม VLM: ระบบที่ "understand and simultaneously process visual and textual information", บูรณาการ CV กับ NLP; งานหลัก captioning, VQA, retrieval, visual reasoning (p.4).
  - ลำดับพัฒนาการ: VSE → RNN/LSTM → CLIP (contrastive, zero-shot) → Flamingo (parameter-efficient) → BLIP/อื่นๆ (p.5); สถาปัตยกรรมแกน Transformer + ViT, encoder–decoder (p.6).
  - ข้อดี/ข้อจำกัดของ prompt tuning/adapters/LoRA ตามข้างบน; ข้อจำกัด fine-tuning: ใช้ทรัพยากรมาก, overfit เมื่อข้อมูลน้อย, transfer ข้ามงานได้จำกัด, อาจขยายอคติของโมเดลเดิม (p.18).
  - Qwen: ดูข้อ 6.
- **ข้อจำกัด/ห้ามอ้างเกินจริง**:
  - **ไม่มีส่วน grounding/localization/hallucination เป็นเรื่องหลัก**; คำว่า hallucination ปรากฏเพียงคำอธิบาย benchmark ("entangled language hallucination", p.30) และชื่ออ้างอิง [316] "Evaluating object hallucination in large vision-language models" (p.41) — ส่วนตาราง Table 12 (p.30) อธิบายรายการ POPE [316] ว่า "Post-OCR performance evaluation with reasoning tasks" ซึ่ง **ขัดกับชื่อเรื่องของอ้างอิงที่ตัวเองระบุ** → อย่าอ้างคำอธิบาย POPE จาก survey นี้ (ให้ไปเปิดเปเปอร์ต้นฉบับ [316]).
  - คำบรรยาย Qwen-VL ใน 4.4 (p.19) เป็นภาพรวมกว้างๆ (hybrid attention, hierarchical encoders, contrastive + masked LM) และไม่พูดถึง localization/grounding เลย ทั้งที่ชื่ออ้างอิง [225] ระบุ "understanding, localization, text reading" — ผู้อ่านเทียบกับต้นฉบับไม่ได้ (ไม่มีต้นฉบับในมือ) จึง **ยืนยันไม่ได้** ว่าคำบรรยายถูกต้อง → อย่าใช้บรรยายสถาปัตยกรรม Qwen จาก survey นี้ ให้ใช้รายงานเทคนิคต้นฉบับ.
  - ตัวเลขใน Table 5, A.1 เป็นช่วงประมาณจาก survey; "98%/80–95%" ในข้อสรุป (p.33) เป็นการสรุปรวม ไม่ได้ระบุเปเปอร์ต้นทาง (หาที่มาในไฟล์ไม่เจอ) → ถ้าจะอ้างเป็นตัวเลขต้องบอกว่า "ตาม Danish et al. (2026)" ไม่ใช่ข้อเท็จจริงทั่วไป.
  - ไม่มีงานสะพาน/โยธา/ความเสียหาย: คำว่า bridge/damage/structural/civil/SAM ไม่ปรากฏในเนื้อหา (ค้นแล้ว); โดเมนที่กล่าวคือการแพทย์, ขับขี่อัตโนมัติ, ภูมิสารสนเทศ (GeoBench-VLM, RS5M), CityLLaVA (เมือง, p.18).

---

### [37] Vision-Language Models for Vision Tasks: A Survey — Jingyi Zhang, Jiaxing Huang, Sheng Jin, Shijian Lu (NTU) — arXiv:2304.00685v2, 16 ก.พ. 2024 (p.1); ตีพิมพ์ IEEE TPAMI 2024 ตามที่ 25 อ้างใน [7] (p.34) — ตัวไฟล์ที่เรามีคือฉบับ arXiv ("JOURNAL OF LATEX CLASS FILES, MARCH 2023")
- ชนิด: รีวิว/survey ; อายุ: 2023-2024 (อยู่ในช่วง)
- **วัตถุประสงค์**: ทบทวน VLM สำหรับ "visual recognition" (classification, detection, segmentation) ในกระบวนทัศน์ pre-train → zero-shot (p.1-3)
- **วิธีการ**: จัดหมวด (1) pre-training (contrastive / generative / alignment objectives), (2) transfer learning (prompt tuning, feature adapter), (3) knowledge distillation (ไป detection/segmentation), พร้อม benchmark ตาราง 6–11 (p.4-17).
- **ผลที่สำคัญ (คัดตรงตัว)**:
  - **กระบวนทัศน์ 5 ขั้น** (p.3): traditional ML → deep learning from scratch → supervised pre-train+fine-tune → unsupervised pre-train+fine-tune → **VLM pre-training + zero-shot prediction** (ไม่ต้อง fine-tune ต่องาน).
  - **สาเหตุที่ VLM ทั่วไปดี** (p.15): "Big data, Big model, Task-agnostic learning"; **ข้อจำกัด** (p.15): "(1) ... performance saturates and further scaling up won't improve performance; (2) ... extensive computation resources, e.g., 256 V100 GPUs, 288 training hours in CLIP ViT-L; (3) large models introduces excessive computation and memory overheads".
  - **Zero-shot detection/segmentation (Table 7-8, p.15)**: GLIP (Swin-L+BERT, 27.43M ข้อมูล) COCO 49.8 / LVIS 26.9 / LVIS Minival 34.3; FIBER COCO 49.3 / Minival 32.2; RegionCLIP COCO 29.6 / LVIS 11.3; DetCLIP LVIS 35.9. Segmentation zero-shot: GroupViT VOC 52.3 / PASCAL-Context 22.4; SegCLIP 52.6 / 24.7 / COCO 26.5.
  - **หลัง distillation (Table 10-11, p.16-17)**: เช่น open-vocabulary segmentation OVSeg: A-847 = 9.0, PC-459 = 12.4, A-150 = 29.6, PC-59 = 55.7, PAS-20 = 94.5 → **ผลต่างกันมากตามจำนวนคลาส/ความยากของชุดข้อมูล**; detection: BARON APnovel (COCO) 42.7, VLDet LVIS APr 26.3 ฯลฯ.
  - **ข้อสรุป** (p.16-17): "VLM pre-training achieves remarkable zero-shot prediction on a wide range of image classification tasks ... Nevertheless, the development of VLM pre-training for dense visual recognition tasks (on region or pixel-level detection and segmentation) lag far behind."
  - Transfer (p.16): บน ImageNet supervised Wise-FT +10.9%, few-shot CoOp +1.7%, unsupervised TPT +0.8%; few-shot transfer "lag far behind that of supervised transfer (e.g., 87.1% in WiseFT and 76.6% in CuPL)" เพราะ "VLMs may overfit to few-shot labelled samples with degraded generalization"; unsupervised ใกล้เคียง few-shot.
  - ทิศทางอนาคต (p.17): fine-grained vision-language correlation (region-word, dense prediction) ยังมีงานน้อย; unsupervised/test-time transfer; ใช้ LLM ช่วยสร้าง prompt/caption.
- **ความเกี่ยวข้องกับงานเรา**: **ใช้เสริม** สำหรับ 2.3 (ประวัติ/ทฤษฎีพื้นฐาน VLM สาย CLIP: contrastive pre-training, zero-shot, prompt tuning, adapter, KD; อธิบายคำว่า "zero-shot vs fine-tuned"; อ้างว่า dense prediction ยังอ่อน) ; **ไม่ครอบคลุม MLLM แบบ instruction-following (LLaVA/Qwen-VL)** — ค้นแล้วไม่มีคำว่า LLaVA/GPT-4/MLLM ในเนื้อหา (มีแต่ "large language models" ในบริบท LLM ช่วยสร้าง prompt) จึง **ห้ามใช้เป็นหลักฐานความสามารถของ Qwen**.
- **ข้อเท็จจริงที่หยิบไปเขียนได้เลย**:
  - นิยาม: VLM pre-train ด้วยคู่ภาพ-ข้อความจากเว็บ แล้วทำนาย zero-shot โดยจับคู่ embedding ภาพ-ข้อความ (p.1-3); CLIP ใช้ image-text contrastive (InfoNCE สมมาตร, p.5).
  - ประเภท objective: contrastive / generative / alignment (region-word matching ทำให้ทำ detection ได้ เช่น GLIP) (p.5-10).
  - Knowledge distillation ถ่ายความรู้ VLM ไปโมเดลเฉพาะ detection/segmentation โดยไม่ผูกกับสถาปัตยกรรมเดิม (p.13) — สนับสนุนแนวคิด "VLM เป็นตัวช่วย + โมเดลเฉพาะ (YOLO/SAM) ทำงานหลัก".
  - ข้อมูล: LAION-5B 5 พันล้านคู่ (Table 1, p.7); CLIP 400M, ALIGN 1.8B (p.7).
- **ข้อจำกัด/ห้ามอ้างเกินจริง**: เป็นภาพรวมสาย CLIP ถึงต้นปี 2023; ตัวเลข benchmark เป็นของโมเดลสาย CLIP/GLIP ไม่ใช่ MLLM; ผู้เขียนเตือนเองว่าผลตาราง 7-8 "may not be aligned" เพราะวิจัยด้านนี้ยังน้อย (p.15) และการเทียบ pre-training ยุติธรรมได้ยากเพราะข้อมูล/โมเดลต่างกัน (p.17); ไม่มีงานสะพาน/โยธาเลย (ค้น bridge/civil/crack/defect/infrastructure ไม่พบในเนื้อหา).

---

## ตอบคำถามที่ได้รับมอบ

### 1) VLM ทำ grounding/localization ให้ bounding box/จุดได้ดีแค่ไหน — ตามเปเปอร์
- **ไม่มีหลักฐานตรงในทั้ง 4 ฉบับ** สำหรับ generative MLLM ที่ตอบพิกัด (ไม่มีการวัด IoU/AP ของ Qwen-VL หรือโมเดลคู่แข่ง). ใครเขียน 3.5 ว่า "Qwen หา box ได้แม่น" ต้องอ้างเปเปอร์อื่น.
- หลักฐานทางอ้อม (เรียงตามความใกล้เคียง):
  1. 37 p.15: VLM สายเรียนรู้ region-word ทำ **zero-shot detection** ได้ — GLIP COCO 49.8 (LVIS 26.9), FIBER COCO 49.3 — แต่ 37 สรุป p.16-17 ว่า dense prediction (region/pixel) "lag far behind" classification และโมเดลสายนี้ไม่ใช่ MLLM.
  2. 37 p.17 (Table 11): open-vocabulary segmentation แกว่งมาก ตามจำนวนคลาส/ความยาก (OVSeg A-847 = 9.0 mIoU เทียบ PAS-20 = 94.5) → ชี้ว่าความสามารถ localize ขึ้นกับชุดคลาส; ไม่มีข้อมูลสำหรับความเสียหายคอนกรีต.
  3. 23 p.3 (อ้างมือสอง Cao et al.): GPT-4V มีผล zero-/one-shot น่าสนใจกับ anomaly detection แต่ "limitations in fine-grained localisation of subtle defects" — ข้อความรองต่อรอง ต้องเปิดต้นฉบับ [26] ก่อนอ้าง. และ 23 p.2 ระบุ Grounding DINO ว่าเป็นตัวตรวจจับแบบ language grounding "complementary to the language-generation focus of generative VLMs" ([14]) และ SAM ว่าเป็น promptable model ที่ train ด้วยมากกว่า 1 พันล้าน mask transfer zero-shot ([13]) — **เป็นเพียงคำอธิบายในบทที่ 2 ของ 23 ไม่มีการทดลอง**.
  4. 24 p.3-4: ผู้เขียนเลือกให้ YOLO11-seg ทำ localization และ MLLM ทำข้อความ โดยอ้างว่าโมเดล end-to-end อย่าง Florence-2/PaliGemma/Vitron "lack fine-grained defect mapping and standardized reporting" (p.3) — เป็นเหตุผลเชิงออกแบบของผู้เขียนเอง ไม่ใช่ผลการเทียบ.
  5. 25: PaliGemma 2 ระบุ "multilingual generation + grounding" (Table 7 p.21) แต่ไม่มีตัวเลข; "Llava-grounding" ถูกยกเป็นตัวอย่างโมเดลที่ฝึก/fine-tune ต้องใช้ทรัพยากรมาก (p.32, [330]); DARA ปรับ adapter สำหรับ visual grounding ด้วยพารามิเตอร์ 2.13% (p.16, [213] p.39).
- **สิ่งที่ควรเตือนใน proposal**: ผลความเสียหายคอนกรีตที่ละเอียด (รอยร้าว, เหล็กโผล่) แม้ใช้โมเดล detection/segmentation เฉพาะทางยังได้ mAP50 เพียง ≈ 36–58% ต่อคลาส (24 p.9, p.11) และ multi-class ยากกว่า single-class crack มาก (24 p.11: 87.8% vs ≈50% mAP50, dacl10k mIoU ≈ 0.41–0.42) ดังนั้นการให้ VLM ตอบ box ของความเสียหายหลายคลาสในภาพสะพานจริงจึงควรถูกเขียนเป็น **สมมติฐานที่ต้องทดสอบ** ไม่ใช่ข้อเท็จจริงที่รองรับด้วยเปเปอร์.
- เรื่อง "ส่งต่อเป็นกรอบหรือจุด": **ไม่มีเอกสารใดใน 4 ฉบับเทียบ box prompt vs point prompt ให้ SAM** (SAM ถูกกล่าวถึงเพียง 23 p.2). ต้องหาจากเปเปอร์ SAM ที่มีใน index (รหัส 28_SAM_Tengetal, 29_YOLOandSAM — อยู่นอกขอบเขตที่ได้รับมอบ ฉันไม่ได้อ่าน).

### 2) Fine-tune (LoRA/QLoRA/full) ใช้ข้อมูลและทรัพยากรเท่าไร
| แหล่ง | โมเดล/วิธี | ข้อมูล | ฮาร์ดแวร์/เวลา | ผล |
|---|---|---|---|---|
| 23 p.6-8, 11-12 | LLaVA-1.5-7B, QLoRA 4-bit NF4, r=32, α=64 | train 1k/2k/3k/4k (pool 10,789); test 800 | RTX 4060 Ti 16GB; 1:23 / 2:56 / 4:32 / 6:19 ชม.; อนุมาน 10.06 s/ภาพ (batch 8 + compile) | 2k ≈ จุดคุ้ม; 3k สูงสุด (0.6909); 4k แย่ลง (0.6739) |
| 24 p.7-8, 10 | Llama 3.2 11B Vision, 4-bit LoRA, Unsloth (+YOLO11-seg แยก) | 700 ภาพ (650 ชำรุด + 50 ปกติ), label โดยนักศึกษา+ผู้เชี่ยวชาญตรวจ 2 คน | GPU เดียว (รุ่นเทรนอยู่ Appendix E ไม่มีในข้อความ); วัดระบบรวมบน RTX A6000 30–50 s/ภาพ; ค้น hyperparameter ~180 ชม. (LLM) / ~130 ชม. (YOLO) | BERTScore 0.5929 → 0.7945 (test) |
| 25 p.17, 33, 34 | LoRA, adapters ทั่วไป | – | LoRA trainable ~0.5–2%; adapter ลดพารามิเตอร์สูงสุด 98% คงผล 80–95% ของ full FT; LLaVA 1.5/1.6 instruction tuning 8× A100 40/80GB (Table A.1) | สรุปจาก survey ไม่ใช่การทดลองใหม่ |
| 37 p.15-16 | CLIP ViT-L pre-train (ไม่ใช่ fine-tune) | 400M คู่ | 256 V100 × 288 ชม. | few-shot transfer overfit; supervised transfer ดีสุด |
- **ข้อสังเกต**: ตัวเลขใน 23 และ 24 เป็นการ fine-tune เพื่อ **สร้างข้อความ**; ไม่ใช่ fine-tune ให้ตอบพิกัด/box → ขนาดข้อมูลสำหรับ grounding **ยืนยันไม่ได้จากกลุ่มนี้**. ตัวเลข 23 บอกว่า "คัดข้อมูลคุณภาพ 2–3 พันคู่ดีกว่าเพิ่มจำนวนแบบไม่กรอง" (p.15 "curating a high-quality 2k–3k dataset is preferable to indiscriminately expanding to 4k with potentially noisier labels") — ข้อสรุปจากโดเมน/งานเดียว.

### 3) Zero-shot vs fine-tuned
- **ข้อความ (24 p.8-9)**: ก่อน fine-tune Llama 3.2 Vision ตอบ "NA" สำหรับชิ้นส่วน/ชนิดความเสียหาย และตอบซ่อมไม่ตรง (Tables 2-3); BERTScore 0.5929 → 0.7945 (test). **เทียบ GPT-4o** (ไม่ fine-tune) ด้านระบุชิ้นส่วน/ความเสียหายใกล้เคียงกัน (3.92 vs 3.71, p=0.281, p.15) โดยผู้ตอบบางคนบอกว่า GPT-4o ระบุชิ้นส่วนแม่นกว่าเล็กน้อย แต่ Llama fine-tuned พรรณนารายละเอียดดีกว่า (p.15).
- **ฉบับ 23 p.1**: ให้เหตุผลเริ่มต้นว่า LLaVA/InstructBLIP/GPT-4V ทั่วไป "have no exposure to specialised Japanese inspection vocabulary and cannot produce the structured output required by inspection standards" — คำกล่าวของผู้เขียน ไม่มีการวัด zero-shot ในฉบับนี้ (ยืนยันไม่ได้).
- **สาย CLIP (37 p.16)**: zero-shot → supervised transfer ดีขึ้นมาก (Wise-FT +10.9% บน ImageNet), few-shot ดีขึ้นน้อยกว่าเพราะ overfit; zero-shot ดีมากกับ classification แต่ dense prediction "lag far behind" (p.16-17).
- **ฝั่ง segmentation (24 p.11)**: ปรับ hyperparameter (ไม่ใช่เปลี่ยนโมเดล) ทำ mAP50 รวม 50.5 → 53.6 (val), 52.1 → 54.0 (test).
- **Adapter vs full FT (25 p.16)**: "full fine-tuning might be superior ... for tasks that significantly deviate from the pretraining data" — งานภาพสะพานจากโดรนต่างจากข้อมูล pre-train ทั่วไป แต่ไม่มีการทดลองยืนยันในไฟล์.

### 4) Hallucination / ข้อจำกัดที่ต้องเตือนใน proposal
- **Mode collapse / เอาต์พุตเป็นแม่แบบเดียวกัน** (23 p.14-17) — ความเสี่ยงสำคัญของ VLM ที่ fine-tune บนข้อมูลชิ้นส่วนเดียวถูกเน้น (คานหลัก + เหล็กโผล่ + ร่อน ปรากฏ 98.6–100% ของเอาต์พุต; คะแนนไม่แยกแยะ). วิธีบรรเทาที่ผู้เขียนเสนอ (p.16): คัดสมดุลชิ้นส่วน, prompt จำกัดการสร้าง, เพิ่ม diversity metric.
- **เอาต์พุตคุณภาพต่ำ 12.5%** ใน 800 ภาพ (สั้น/ยาว/วน/ภาพไม่ชัด) และ **ข้อความวนซ้ำ** ต้องใช้ repetition_penalty=1.2 (23 p.8-9); ค่าต่ำสุดของ similarity <0.20 ในทุกโมเดล (23 p.13).
- **ข้อมูลมากไม่ได้ดีกว่า**: 4k แย่กว่า 3k แม้ val loss ดีขึ้น → "loss-based early stopping alone is insufficient" (23 p.16).
- **ใช้กฎ/ตัวตรวจสอบรอบ VLM**: 23 เสนอ Quality Guard (กฎ + LLM judge) และอ้าง Chain-of-Verification, Self-RAG, NeMo Guardrails (p.4-5); 24 เสนอ RAG อิงข้อกำหนดเพื่อลดโอกาส hallucination (p.4) แต่ไม่ได้วัด.
- **ความไม่คงเส้นคงวา**: Llama fine-tuned ตอบแต่ละครั้งต่างกันมาก (24 Table 4, p.9).
- **ข้อมูลเล็ก/จำกัดภูมิภาค/ยังไม่ทดสอบข้ามโดเมน** (24 p.15; 23 p.17).
- **ข้อจำกัดทั่วไปของ fine-tuning** (25 p.18): overfit เมื่อข้อมูลน้อย, transfer ได้จำกัด, ขยายอคติ; adapter อาจด้อยเมื่อต้องการ reasoning/alignment ลึก (p.16); ข้อมูลรั่ว/เทียบไม่ยุติธรรม (p.31); metric อย่าง BLEU/CIDEr ไม่จับความหมายเชิงภาพ-ข้อความ (p.31); black-box ตีความยาก (p.32).
- **ข้อควรระวังการอ้าง**: survey 25 ไม่ได้ให้อัตรา hallucination ของ VLM ใดเลย; เปเปอร์ที่ควรไปเปิดเอง ถ้าต้องการวัด hallucination คือ [316] "Evaluating object hallucination in large vision-language models" (ชื่อที่ระบุใน 25 p.41; เนื้อหาของมันไม่อยู่ในไฟล์).
- ข้อเสนอสำหรับ 3.5 ที่ **อิงสิ่งที่เปเปอร์ทำจริง**: (ก) ให้ผล VLM ผ่านการตรวจโดยตัวชี้วัดที่ตรวจได้ เช่น mask ที่ได้ต้องทับกับชิ้นส่วนที่ YOLO-seg หา (เชื่อมกับข้อ 3 ใน pipeline ของเรา) — แนวคิด guard 2 ชั้นของ 23 ใช้เป็นต้นแบบได้, (ข) วัดผลระดับ mAP/Recall และ confusion matrix ต่อคลาสเอง ไม่พึ่งเมตริกข้อความ (BERTScore/cosine) ตามข้อจำกัดที่ 23 p.17 และ 24 ยอมรับ.

### 5) งานที่ใช้ VLM กับ infrastructure/โยธา
- **ตรงสะพาน (อ่านครบเนื้อหา)**: 23 (สะพานญี่ปุ่น, LLaVA-1.5-7B QLoRA, ข้อความ + rule-based priority); 24 (สะพานคอนกรีตไต้หวัน, YOLO11-seg + Llama 3.2 Vision LoRA, พื้นที่/ต้นทุนซ่อม).
- **อ้างมือสองในเปเปอร์ (ต้องเปิดต้นฉบับก่อนอ้าง)**: Kunlamai et al. (VQA กับรายงานสะพาน) และ Chun et al. (captioning CNN+LSTM) (24 p.2-3); Chou et al. [16] ViT + YOLOv8 วัดพื้นที่ polygon + ต้นทุนซ่อม (24 p.3); Pu et al. MiniGPT4-7B (24 p.3) / Set-of-Mark MLLM ทำรายงานตรวจก่อสร้าง (23 p.4); Hsu et al. VL-Con (23 p.4); Mengiste et al. (23 p.4); Omar & Moselhi (LLM อ่านรายงานตรวจสะพาน, 23 p.4); Núñez Varillas et al. (ISARC 2024) UAV photogrammetry + CNN จำแนกความเสียหายคอนกรีตบนแบบจำลอง 3 มิติของสะพาน — **ใกล้ pipeline โดรน→3D ของเรามาก** (23 p.4); Zuo et al. (ISARC 2025) 3D reconstruction ตรวจจับความเสียหายด้วย transformer (23 p.4); Assad et al. (ISARC 2025) crack detection/segmentation YOLOv9/YOLO11/Mask R-CNN (23 p.4; ตัวเลข 87.8/87.1/75.5 คัดมาจาก 24 p.11).
- **ใน 25**: ไม่มีงานสะพาน; มี CityLLaVA (เมือง, p.18), GeoBench-VLM (ภาพดาวเทียม ภัยพิบัติ/โครงสร้างพื้นฐาน, p.24, p.30), RS5M (remote sensing, p.26). **ใน 37**: ไม่มี.
- **ช่องว่าง**: ไม่มีเปเปอร์ในกลุ่มนี้ที่ใช้ VLM หา box/mask ความเสียหายสะพาน หรือต่อ SAM; ไม่มีงานที่ใช้ภาพโดรนใต้สะพานกับ VLM โดยตรง.

### 6) Qwen มีพูดถึงในไฟล์ไหนบ้าง
- 23, 24, 37: **ไม่มี** (ค้นคำ "qwen" ทั้งไฟล์ = 0 ครั้ง ทั้ง 3 ไฟล์).
- **25 เท่านั้น** (11 ที่): หัวข้อ 4 บอกว่ากล่าวถึง Qwen-VL (p.18-19: ประโยคนำ "Gemini, XGen-7B, PaLI-Gemma2, Copilot, Qwen-VL, ChatGPT-4"); **หัวข้อ 4.4 Qwen-VL (p.19)** เขียนว่า "designed for high-precision multimodal reasoning, incorporating hybrid attention mechanisms and hierarchical encoders ... excellence in visual question answering, image captioning, and cross-modal retrieval ... effective for practical applications, such as document analysis and product description generation [225]. However, Qwen-VL faces challenges that include substantial fine-tuning requirements for specialized tasks ... computational inefficiencies during large-scale or complex operations ... dependence on high-quality multimodal data ... performance degradation [in data-scarce environments]"; **4.6 (p.20)** ระบุ "Qwen 2.5 VL [231]" ในรายการ VLM หลังปี 2023 และว่า Gemini/PaliGemma 2/Qwen 2.5 VL ฝึกด้วยข้อมูล "highly curated multilingual and synthetic datasets" (4.6.2); **Table 7 (p.21)**: Qwen 2.5 VL, ปี 2025, fine-tuning = "Instruction tuning", สถาปัตยกรรม "Transformer decoder with visual patch input", backbone "Qwen 2.5 + ViT", ขนาด 3B/7B/72B, ข้อมูล "Docs, images, audio", key innovation "OCR + document QA specialization"; **อ้างอิง [225] Qwen-VL (arXiv:2308.12966, ชื่อเรื่อง "A versatile vision-language model for understanding, localization, text reading, and beyond") และ [231] Qwen2.5-VL technical report (arXiv:2502.13923) อยู่ที่ p.39**.
- **ไม่มีหลักฐานเรื่อง Qwen 3.6 / 35B / ขนาด 35B ใดๆ** ในเอกสารทั้ง 4 ฉบับ → ห้ามอ้างสเปคหรือความสามารถของ "Qwen 3.6 35B" จากกลุ่มนี้.
- **ข้อควรระวัง**: คำบรรยาย Qwen ใน 25 เป็นภาพรวมกว้างๆ (เน้น VQA/captioning/OCR/เอกสาร ไม่พูดถึง grounding/box ทั้งที่ชื่ออ้างอิงต้นฉบับ [225] มีคำว่า localization) — **ยืนยันไม่ได้ว่าถูกต้องตามต้นฉบับ**; ถ้าจะใช้อธิบาย Qwen ให้เปิดรายงานเทคนิคต้นฉบับ [225]/[231] เอง.
- **เหตุผลที่เลือก Qwen**: ไม่มีเอกสารใดรองรับเฉพาะ Qwen. ที่ใกล้ที่สุดคือเหตุผลเชิงหลักการของ "โมเดลเปิด รันในเครื่อง fine-tune ได้": 24 p.3-4 (openness, fine-tuning flexibility, local deployment เพื่อความปลอดภัยข้อมูลโครงสร้างพื้นฐาน), 23 p.3 (ข้อจำกัดของ proprietary API: dependence, latency, privacy ใน regulated infrastructure), 23 p.6 (LLaVA-1.5-7B เลือกเพราะขนาดใช้ได้กับ consumer GPU) — ใช้อ้างหลักการได้ แต่ **ต้องเขียนว่าเป็นหลักการของงานอื่น ไม่ใช่การเทียบ Qwen กับตัวอื่น**.

### 7) เครื่องรันไหวไหม (สำหรับ 3.5)
- หลักฐานที่มี: 7B QLoRA ใน 16GB เทรน/อนุมานได้ (23 p.6-7; อนุมาน batch 8 ใช้ VRAM ≈78%, 10.06 s/ภาพ; 23 p.7); Llama 3.2 11B Vision 4-bit LoRA บน GPU เดียว (24 p.7), ระบบรวมใช้ 30–50 s/ภาพบน RTX A6000 (24 p.12); survey ชี้ว่า latency/พลังงาน/หน่วยความจำของ VLM ใหญ่เป็นอุปสรรคหลักของการ deploy และ quantization/pruning/distillation ช่วยแต่แลกกับความแม่นยำ (25 p.32).
- **ไม่มีหลักฐานสำหรับโมเดล 35B** (ขนาด/การ quantize/VRAM ที่ต้องใช้) — "ยืนยันไม่ได้จากกลุ่มนี้"; ตัวเลขที่ใกล้สุดคือ 7B/11B ที่ฝึกใน GPU 16GB ขึ้นไป ซึ่งเล็กกว่ามาก. สเปคเครื่องของนิสิตไม่ได้อยู่ในไฟล์ที่ฉันได้รับ จึงไม่ประเมิน.

---

## สรุปกลุ่ม G7 (5-10 บรรทัด)
- **ควรเข้า proposal**: **24 Chou et al. (2026)** — ใช้แน่ (peer-reviewed; บริบทสะพานคอนกรีต; YOLO11-seg + MLLM LoRA; วิธีแปลง mask→พื้นที่; 4 จาก 6 คลาสตรงกับเรา). **37 Zhang et al.** — ใช้เสริม 2.3 เฉพาะพื้นฐาน VLM/zero-shot/transfer/KD และข้อสังเกต dense prediction. **25 Danish et al.** — ใช้เสริม 2.3 (นิยาม, เส้นเวลา, LoRA/adapter/fine-tuning) และเป็นแหล่งเดียวที่มี Qwen แต่ **อย่าใช้บรรยายสถาปัตยกรรม Qwen** (ข้อมูลกว้าง/น่าสงสัย). **23 Yasuno (2026)** — ใช้เสริม (ตัวอย่าง QLoRA 7B ใน 16GB + เส้นโค้งข้อมูล 1k–4k + คำเตือน mode collapse) แต่เป็น preprint v1 และมีตัวเลข/เกณฑ์ที่ไม่สอดคล้องในตัวเอง.
- **ตัดได้/ไม่จำเป็น**: ไม่มีฉบับไหนต้องตัดทิ้งทั้งฉบับ; แต่ 37 ควรอ้างเฉพาะบทพื้นฐาน เพราะไม่ครอบคลุม MLLM.
- **ช่องว่าง (หัวข้อที่ยังไม่มีเปเปอร์รองรับในกลุ่มนี้)**:
  1. 2.3/3.5: **ความสามารถ grounding/ให้ box-จุด ของ MLLM (Qwen-VL/Qwen2.5-VL ขึ้นไป) พร้อมตัวเลข benchmark** — ไม่มี (ต้องใช้รายงานเทคนิค Qwen [225]/[231] ซึ่งเป็นแค่ชื่ออ้างอิงใน 25 + งาน referring/grounding benchmark อื่น).
  2. 3.5: **Qwen 3.6 35B** (สเปค, VRAM, quantization, ความสามารถ) — ไม่มีเลย.
  3. 3.5: **การส่งต่อกรอบ vs จุด ให้ SAM / VLM→SAM pipeline** — ไม่มี (ต้องดูเปเปอร์ SAM, YOLO+SAM ที่อยู่ในรหัส 28, 29 — กลุ่มอื่น).
  4. 2.3/3.5: **อัตรา hallucination เชิงตัวเลขของ VLM** — ไม่มี; มีแต่ mode collapse ของ 23 และข้ออ้างเชิงออกแบบ (RAG) ของ 24.
  5. **VLM + โดรน/ภาพใต้สะพาน หา bounding ของความเสียหาย** — ไม่มีในกลุ่ม (23 อ้างมือสองถึงงาน UAV + photogrammetry + CNN ของ Núñez Varillas et al. ซึ่งเป็น CNN ไม่ใช่ VLM).
  6. ขนาดข้อมูลสำหรับ fine-tune เพื่อ "ตอบพิกัด" — ไม่มี (มีเฉพาะสำหรับ "ตอบข้อความ").
