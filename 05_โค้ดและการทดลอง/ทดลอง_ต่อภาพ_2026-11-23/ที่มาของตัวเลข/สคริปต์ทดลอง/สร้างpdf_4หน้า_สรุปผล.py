# สร้างเอกสารสรุปผล (รุ่นสั้น ไม่มีภาพถ่าย เฉพาะตารางและกราฟ) จาก numbers.json + numbers2.json
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'numbers.json'), encoding='utf-8'))
K = json.load(open(os.path.join(HERE, 'numbers2.json'), encoding='utf-8'))
s21, c21, g21 = J['stats21'], J['check21'], J['gps21']
s34, c34 = J['stats34'], J['check34']
t13, t13n = J['t13'], J['t13nometa']

CSS = '''
  @page { size: A4; margin: 15mm 15mm 16mm; }
  :root { --ink:#16191e; --ink2:#535b68; --ink3:#868e9b; --line:#e2e5ea; --soft:#f4f6f9; --blue:#1d5fd6; --blue-soft:#e8effc;
          --green:#1f8a3e; --green-soft:#e5f4ea; --red:#c4321f; --red-soft:#fcebe8; --amber:#8a5a00; --amber-soft:#fff5d8; }
  * { box-sizing: border-box; }
  body { font-family: "Leelawadee UI", "Sarabun", sans-serif; color: var(--ink); font-size: 10.6pt; line-height: 1.58; margin: 0;
         -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  h1 { font-size: 22pt; line-height: 1.25; margin: 0 0 3px; letter-spacing: -.01em; }
  h2 { font-size: 13.5pt; margin: 18px 0 7px; display: flex; align-items: center; gap: 9px; break-after: avoid; }
  h2 .n { width: 24px; height: 24px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 10.5pt; display: inline-grid; place-items: center; flex: none; }
  h3 { font-size: 11.4pt; margin: 12px 0 4px; break-after: avoid; }
  p { margin: 4px 0 7px; }
  .lead { color: var(--ink2); font-size: 11.4pt; margin-bottom: 10px; }
  .meta { color: var(--ink3); font-size: 9pt; border-bottom: 1px solid var(--line); padding-bottom: 8px; margin-bottom: 12px; }
  .box { border-radius: 10px; padding: 9px 13px; margin: 9px 0; break-inside: avoid; }
  .box.blue { background: var(--blue-soft); } .box.green { background: var(--green-soft); }
  .box.amber { background: var(--amber-soft); } .box.gray { background: var(--soft); } .box.red { background: var(--red-soft); }
  .box b.t { display: block; margin-bottom: 2px; }
  .box ul { margin: 3px 0 2px; padding-left: 18px; } .box li { margin: 2px 0; }
  figure { margin: 8px 0 10px; break-inside: avoid; }
  figure svg { width: 100%; display: block; border-radius: 8px; }
  figcaption { font-size: 9pt; color: var(--ink2); margin-top: 4px; }
  table { width: 100%; border-collapse: collapse; font-size: 9.4pt; margin: 7px 0; }
  tr { break-inside: avoid; }
  table.k { break-inside: avoid; }
  th, td { border-bottom: 1px solid var(--line); padding: 4px 7px; text-align: left; vertical-align: top; }
  th { color: var(--ink2); font-weight: 600; background: var(--soft); }
  td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
  ul { margin: 3px 0 7px; padding-left: 19px; } li { margin: 2px 0; }
  .two { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; align-items: start; }
  .pb { break-before: page; }
  .small { font-size: 9pt; color: var(--ink2); }
  .yes { color: var(--green); font-weight: 600; } .no { color: var(--red); font-weight: 600; } .part { color: var(--amber); font-weight: 600; }
  code { font-size: 9pt; }
  .q { color: var(--ink2); font-style: italic; }
  .src { font-size: 8.6pt; color: var(--ink2); } .src li { margin: 2px 0; word-break: break-all; }
  .keep { break-inside: avoid; }
'''

# ---------- กราฟ A: ต่างจาก GPS ของคู่จริง เทียบคู่หลอก ----------
real, fake, tol = K['real'], K['fake'], K['tol']
AX0, AW, AY = 24, 300, 120
xmax = 2.5


def ax(v):
    return AX0 + AW * v / xmax


bins = {}
dots = []
for v in sorted(real):
    k = int(v / 0.045)
    bins[k] = bins.get(k, 0) + 1
    dots.append(f'<circle cx="{ax(v):.1f}" cy="{AY - 7 - 7.2 * (bins[k] - 1):.1f}" r="3.2" fill="#1f8a3e" fill-opacity=".85"/>')
for v in fake:
    dots.append(f'<path d="M{ax(v):.1f} {AY - 15} l6 6 l-6 6 l-6 -6 z" fill="#c4321f"/><text x="{ax(v):.1f}" y="{AY - 24}" font-size="10" text-anchor="middle" fill="#c4321f" font-weight="700">{v:.2f}</text>')
ticks = ''.join(f'<line x1="{ax(t)}" y1="{AY}" x2="{ax(t)}" y2="{AY + 4}" stroke="#868e9b"/><text x="{ax(t)}" y="{AY + 16}" font-size="10" text-anchor="middle" fill="#535b68">{t}</text>' for t in (0, 0.5, 1.0, 1.5, 2.0, 2.5))
svg_a = f'''<svg viewBox="0 0 350 205" xmlns="http://www.w3.org/2000/svg" font-family="Leelawadee UI, sans-serif">
<rect x="{AX0}" y="8" width="{AW}" height="{AY - 8}" fill="#f4f6f9"/>
<line x1="{AX0}" y1="{AY}" x2="{AX0 + AW}" y2="{AY}" stroke="#868e9b"/>
<line x1="{ax(tol):.1f}" y1="8" x2="{ax(tol):.1f}" y2="{AY}" stroke="#c4321f" stroke-dasharray="5 4" stroke-width="1.3"/>
<text x="{ax(tol) + 5:.1f}" y="22" font-size="10" fill="#c4321f">เกณฑ์ตัด ≈ {tol:.1f} ม.</text>
{''.join(dots)}{ticks}
<text x="{AX0 + AW / 2}" y="152" font-size="11" text-anchor="middle" fill="#16191e">ระยะที่ภาพบอก ต่างจากระยะที่ GPS บอก (ม.)</text>
<circle cx="40" cy="176" r="3.6" fill="#1f8a3e"/><text x="49" y="180" font-size="10.5" fill="#16191e">คู่จริง {len(real)} คู่ (สูงสุด {max(real):.2f} ม.)</text>
<path d="M205 170 l6 6 l-6 6 l-6 -6 z" fill="#c4321f"/><text x="216" y="180" font-size="10.5" fill="#16191e">คู่หลอก {len(fake)} คู่</text>
<text x="40" y="198" font-size="9.5" fill="#535b68">เทียบได้เฉพาะคู่ในรอบบินเดียวกัน (38 จาก 87 คู่ที่ใช้)</text>
</svg>'''

# ---------- กราฟ B: ตำแหน่งบนผืน เทียบ GPS ----------
nodes = J['nodes21']
mx = max(max(d['pos'] for d in nodes), max(d['gps'] for d in nodes)) * 1.04
S, P0 = 236, 38


def px(v):
    return P0 + S * v / mx


def py(v):
    return 10 + S - S * v / mx


tk = ''.join(f'<line x1="{px(t)}" y1="{py(0)}" x2="{px(t)}" y2="{py(0) + 4}" stroke="#868e9b"/><text x="{px(t)}" y="{py(0) + 16}" font-size="10" text-anchor="middle" fill="#535b68">{t}</text>'
             f'<line x1="{P0 - 4}" y1="{py(t)}" x2="{P0}" y2="{py(t)}" stroke="#868e9b"/><text x="{P0 - 7}" y="{py(t) + 3.5}" font-size="10" text-anchor="end" fill="#535b68">{t}</text>'
             for t in (0, 5, 10, 15, 20))
pts = ''.join(f'<circle cx="{px(d["pos"]):.1f}" cy="{py(d["gps"]):.1f}" r="3.3" fill="#1d5fd6" fill-opacity=".85"/>' for d in nodes)
svg_b = f'''<svg viewBox="0 0 300 290" xmlns="http://www.w3.org/2000/svg" font-family="Leelawadee UI, sans-serif">
<rect x="{P0}" y="10" width="{S}" height="{S}" fill="#f4f6f9"/>
<line x1="{px(0)}" y1="{py(0)}" x2="{px(mx)}" y2="{py(mx)}" stroke="#c4321f" stroke-width="1.2" stroke-dasharray="5 4"/>
{tk}{pts}
<text x="{P0 + S / 2}" y="284" font-size="11" text-anchor="middle" fill="#16191e">ตำแหน่งบนผืน (ม.)</text>
<text x="11" y="{10 + S / 2}" font-size="11" text-anchor="middle" fill="#16191e" transform="rotate(-90 11 {10 + S / 2})">ตำแหน่งจาก GPS (ม.)</text>
<text x="{P0 + 9}" y="27" font-size="10" fill="#c4321f">เส้นประ = ตรงกันพอดี</text>
</svg>'''

seg13 = ', '.join(str(len(x)) for x in t13['segs'] if len(x) > 1)
lone13 = sum(len(x) == 1 for x in t13['segs'])
seg13n = ', '.join(str(len(x)) for x in t13n['segs'] if len(x) > 1)

BODY = f'''
<h1>สรุปผล: ให้โปรแกรมหาลำดับภาพเอง</h1>
<p class="lead">ค้นคว้าวิธีที่คนอื่นใช้ · ตรวจข้อมูลที่ฝังในภาพ · เลือกวิธี · ทดลองกับภาพจริง</p>
<div class="meta">โครงงาน T-BHI · เขียนโดย Claude กับมะขาม · 23 พ.ย. 2569 · ตัวเลขทุกตัวผู้จัดทำคำนวณเอง จากภาพ 34 ใบในโฟลเดอร์ <code>04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft</code> (อ่านอย่างเดียว) ·
เอกสารนี้ไม่มีภาพถ่าย มีเฉพาะตารางและกราฟ · รายละเอียดเต็มอยู่ใน <code>วิธีหาลำดับภาพ_ค้นคว้า.md</code></div>

<div class="box blue"><b class="t">สรุปสั้นที่สุด</b>
<ul>
  <li><b>โจทย์:</b> ให้คนเอาภาพไปใส่แล้วได้ผืนภาพเลย โดยไม่ต้องเรียงภาพ — ลองใช้ GPS หรือข้อมูลในภาพ และดูวิธีที่คนอื่นทำ</li>
  <li><b>ที่ค้นเจอ:</b> ทุกเจ้าหาคู่ภาพที่ซ้อนกัน <b>จากเนื้อภาพ</b> ส่วน GPS / เวลา / ชื่อไฟล์ ใช้เป็นตัวช่วยคัดว่าจะลองคู่ไหนเท่านั้น</li>
  <li><b>ที่เลือก:</b> ลองจับคู่ภาพ <b>ทุกคู่</b> จากเนื้อภาพ แล้วใช้ GPS <b>ตรวจ</b> ผลอีกที ไม่ได้ใช้วางภาพ — เพราะภาพชุดนี้กล้องบันทึก GPS ว่า Invalid ทุกใบ และงานจริงบินใต้สะพาน</li>
  <li><b>ผล:</b> ใส่ {s21["images"]} ภาพแบบสลับลำดับและตั้งชื่อมั่ว → ผืนเดียว <b>ลำดับถูกทั้ง {s21["images"]} ภาพ</b> ตรงกับ GPS เฉลี่ย {c21["gps_rms_m"]:.2f} ม. ใช้เวลา {J["t21"]} วินาที</li>
  <li><b>ข้อควรระวัง:</b> ถ้าไม่มี GPS ให้ตรวจ คู่ภาพหลอกหลุดได้ (ชุดทดสอบ: ต่อผิด 3 ภาพ) · GPS ตรวจได้เฉพาะภาพในรอบบินเดียวกัน</li>
</ul></div>

<h2><span class="n">1</span>คนอื่นทำอย่างไร</h2>
<table>
  <tr><th style="width:17%">เครื่องมือ</th><th style="width:47%">เอกสารเขียนว่า</th><th>ความหมายกับงานเรา</th></tr>
  <tr><td><b>Brown &amp; Lowe (2007)</b> งานต้นแบบ [1]</td>
      <td><span class="q">"insensitive to the ordering ... of the input images"</span> · จับคู่จุดเด่น k = 4 · เลือก m = 6 ภาพที่จุดตรงกันมากสุดเป็นคู่ที่น่าจะซ้อน · รับคู่เมื่อ ni &gt; 8.0 + 0.3·nf (ni = จุดที่ลงรอย)</td>
      <td>ไม่ต้องเรียงภาพ · สูตรนี้เป็นที่มาของ "ความมั่นใจ" ที่โปรแกรมคำนวณ</td></tr>
  <tr><td><b>OpenCV Stitcher</b> [2]</td>
      <td>ความมั่นใจ = inliers / (8 + 0.3 × matches) ตามเปเปอร์ข้างบน · ภาพนอกกลุ่มใหญ่สุดถูกทิ้ง (เกณฑ์ตั้งต้น 1) · โหมด SCANS ใช้แบบจำลองเลื่อน-หมุน-ย่อขยาย</td>
      <td><b>ทดลองเอง</b> (21 ภาพ): เกณฑ์ตั้งต้นได้ผืนกว้าง 4,128 px · ลดเหลือ 0.7 → 14,607 px · 0.3 → ขนาดผิดปกติ (4,099×3,633) · 0.1 → ล้มเหลว</td></tr>
  <tr><td><b>OpenSfM / OpenDroneMap</b> [3][4]</td>
      <td><span class="q">"pairs can be restricted by GPS distance, capture time or file name order"</span> · ODM <code>--matcher-neighbors</code>: <span class="q">"nearest images based on GPS exif data"</span></td>
      <td>GPS และเวลาใช้ลดจำนวนคู่ที่ต้องลอง</td></tr>
  <tr><td><b>COLMAP</b> [5]</td>
      <td>Exhaustive: <span class="q">"every image is matched against every other image"</span> ใช้ได้ถ้า <span class="q">"up to several hundreds"</span> · Sequential ต้องให้ชื่อไฟล์เรียง · Spatial ใช้ GPS · Vocabulary tree สำหรับหลายพันภาพ</td>
      <td>งานเรา 20–40 ภาพต่อชิ้นส่วน ลองทุกคู่ได้</td></tr>
  <tr><td><b>Metashape</b> [6]</td>
      <td>Generic: <span class="q">"matching photos using lower accuracy setting first"</span> · Reference: <span class="q">"based on the measured camera locations (if present)"</span> · Sequential: ตามลำดับภาพ</td>
      <td>เหมือนที่เราทำ: ลองแบบเร็วก่อน แล้วตรวจละเอียดเฉพาะคู่ที่น่าจะซ้อน</td></tr>
</table>
<p class="small">ที่ค้นเจอแต่ยังไม่ได้เปิดอ่านต้นฉบับ จึงไม่อ้างในเอกสารนี้: งานตรวจสะพานด้วยโดรนในที่ไม่มีสัญญาณ GNSS (เช่น ใต้พื้นสะพาน) เก็บลิงก์ไว้ในไฟล์ค้นคว้า · ยังหาเอกสารของ DJI ที่อธิบายค่า GpsStatus = Invalid ไม่เจอ (ExifTool ไม่มีฟิลด์นี้ในรายการ XMP ของ DJI [7])</p>

<h2><span class="n">2</span>ในภาพมีข้อมูลอะไร ใช้เรียงภาพได้แค่ไหน</h2>
<table class="k">
  <tr><th style="width:15%">ข้อมูลในภาพ</th><th style="width:30%">ในภาพชุดนี้ (34 ใบ)</th><th>ผลวัด และใช้ได้แค่ไหน</th></tr>
  <tr><td><b>เวลาถ่าย</b></td><td>มีทุกใบ ละเอียดระดับวินาที · สองรอบบิน (11:34–11:43 และ 12:00–12:08)</td>
      <td>เรียงภายในรอบเดียวได้ถูก (ตรงกับผืน 100% ในชุดหลัก) แต่ <b>บอกไม่ได้ว่าคนละรอบบินซ้อนกันไหม</b></td></tr>
  <tr><td><b>พิกัด GPS</b></td><td>มีทุกใบ แต่กล้องบันทึกสถานะ "Invalid" (EXIF: <code>V</code> = Measurement Void [7])</td>
      <td>ในรอบเดียว ขยับตามภาพสม่ำเสมอ คลาดจากผืนเฉลี่ย {c21["gps_rms_m"]:.2f} ม. ตลอด {c21["gps_span_m"]:.1f} ม. · ข้ามรอบบิน พิกัดเลื่อน 1.29 ม.</td></tr>
  <tr><td><b>ความสูง</b></td><td>6.0–7.1 ม.</td><td>ขึ้นลงตามแนวตั้งบนผืน (สหสัมพันธ์ 0.98)</td></tr>
  <tr><td><b>มุมกล้อง</b></td><td>ก้มเงย 0° เอียงข้าง 0° ทุกใบ</td><td>ไม่ได้ใช้ (ลองล็อกไม่ให้ภาพหมุน ช่วยได้นิดเดียว)</td></tr>
  <tr><td><b>ชื่อไฟล์</b></td><td>เรียงตามลำดับถ่าย</td><td>ใช้ได้ถ้าไม่มีใครเปลี่ยนชื่อและมาจากรอบบินเดียว — โปรแกรมไม่ใช้</td></tr>
</table>
<div class="box amber"><b class="t">ข้อควรรู้เรื่องข้อมูลในภาพชุดนี้</b>
กล้อง DJI Mini 3 Pro เวลาในไฟล์ระบุ 23 มี.ค. 2023 พิกัดราว 15.69N 100.12E (ไม่ใช่สะพานกรณีศึกษา) แต่เพราะกล้องบันทึก GPS ว่า Invalid
<b>จึงยังไม่ควรถือว่าเวลาและพิกัดนี้ตรงกับความจริง</b> · สิ่งที่ยืนยันได้จากการวัดคือพิกัดที่ฝังอยู่ขยับสอดคล้องกับภาพ ซึ่งพอสำหรับใช้ตรวจ</div>

<h2><span class="n">3</span>ที่เลือก และเหตุผล (วัดจากภาพจริง)</h2>
<p><b>ขั้นตอน:</b> หาจุดเด่น (SIFT) → ลองจับคู่ทุกคู่แบบเร็ว → ตรวจละเอียดคู่ที่น่าจะซ้อน (RANSAC) → ตัดคู่ที่ขัดกับ GPS → วางทุกภาพพร้อมกัน → ลำดับ = ตำแหน่งบนผืน · ภาพชุดเดิมได้ผลเดิมเสมอ ไม่ว่าใส่ลำดับไหน</p>

<div class="keep"><h3>เหตุผลที่ 1 — ลองทุกคู่ไหว และแม่นกว่าการคัดด้วยเวลา/GPS</h3>
<p>34 ภาพ = 561 คู่ ใช้จุดเด่นที่แรงสุด 1,600 จุดต่อภาพ คู่ละราว 2 มิลลิวินาที รวม 1.2 วินาที (ใช้จุดเต็มคู่ละ 51 มิลลิวินาที รวม 29 วินาที)</p>
<table class="k">
  <tr><th>วิธีเลือกคู่ที่จะลอง</th><th class="num">ต้องลอง (จาก 561 คู่)</th><th class="num">เจอคู่ที่ต่อกันได้จริง*</th></tr>
  <tr><td>เวลาถ่าย: ±3 ใบที่ติดกัน</td><td class="num">96 (17%)</td><td class="num no">45%</td></tr>
  <tr><td>GPS: 8 ใบที่ใกล้ที่สุด</td><td class="num">148 (26%)</td><td class="num part">99%</td></tr>
  <tr><td>GPS: อยู่ภายใน 3 ม.</td><td class="num">111 (20%)</td><td class="num part">92%</td></tr>
  <tr><td><b>เนื้อภาพ: ลองทุกคู่ด้วยจุดเด่นชุดย่อย (วิธีที่ใช้)</b></td><td class="num">561 (100%) ใช้ 1.2 วินาที</td><td class="num yes">100%</td></tr>
</table>
<p class="small">* คู่ที่จุดลงรอย ≥ 30 จากการลองทุกคู่แบบเต็ม (89 คู่ รวมคู่หลอก 2 คู่) · ตัวเลือกเวลา/GPS ต้องรู้พารามิเตอร์ (±3, 8 ใบ, 3 ม.) ล่วงหน้า ส่วนวิธีที่ใช้ไม่ต้องตั้งอะไร</p></div>

<h3>เหตุผลที่ 2 — ลองทุกคู่แล้วเจอ "คู่หลอก" จึงต้องมีตัวตรวจ</h3>
<p>ภาพ 2 คู่ในโฟลเดอร์ Not use (N0311–N0312 และ N0312–N0313) จับคู่ได้ 58 และ 32 จุดด้วยการเลื่อนที่ดูสมเหตุสมผล จึงผ่านเกณฑ์ 30 จุด — แต่ภาพบอกว่าเลื่อนเพียง 0.37 ม. ขณะที่ GPS บอก 2.2–2.5 ม. และเมื่อลองวางรวมกับภาพอื่น (การทดลองแรก ก่อนมีตัวตรวจ) คู่ทั้งสองขัดกับตำแหน่งที่ภาพอื่นกำหนดถึง 1,170 และ 1,298 px (ที่ภาพกว้าง 1600 px) จึงสรุปว่าเป็นคู่หลอก · ลายบนผิวที่ซ้ำน่าจะเป็นต้นเหตุ ยังไม่ได้ยืนยัน</p>
<ul>
  <li><b>แยกด้วยเนื้อภาพไม่ได้:</b> ความมั่นใจแบบ Brown–Lowe ของคู่หลอก = 0.71 และ 0.77 แต่คู่จริงที่ใช้วางภาพ {K["weak_used"]} จาก 87 คู่มีความมั่นใจต่ำกว่า 1 และต่ำสุด 0.57 · ความคล้ายของเนื้อภาพในส่วนซ้อน (NCC) ของคู่หลอก 0.25 ขณะที่คู่จริงมีตั้งแต่ −0.04 (มัธยฐาน 0.36)</li>
  <li><b>แยกด้วย GPS ได้:</b> คู่จริงต่างจาก GPS ไม่เกิน {max(K["real"]):.2f} ม. คู่หลอก {fake[1]:.2f} และ {fake[0]:.2f} ม. (กราฟ 1)</li>
</ul>

<div class="keep"><h2><span class="n">4</span>ผลกับภาพจริง</h2>
<p>ทดสอบโดย <b>สลับลำดับภาพและตั้งชื่อไฟล์มั่ว</b> ก่อนใส่ทุกครั้ง</p>
<div class="two">
  <figure>{svg_a}<figcaption>กราฟ 1 ระยะต่างจาก GPS ของแต่ละคู่ภาพในชุด 34 ภาพ — คู่จริงอยู่ใต้เกณฑ์ทั้งหมด คู่หลอกอยู่เหนือเกณฑ์ทั้งสอง</figcaption></figure>
  <figure>{svg_b}<figcaption>กราฟ 2 ชุดหลัก {s21["images"]} ภาพ: ตำแหน่งแต่ละภาพบนผืน เทียบกับ GPS — เกาะเส้นตลอด คลาดเฉลี่ย {c21["gps_rms_m"]:.2f} ม. ตลอดแนว {c21["gps_span_m"]:.1f} ม.</figcaption></figure>
</div></div>
<table>
  <tr><th style="width:33%">ชุดที่ใส่</th><th>ผล</th></tr>
  <tr><td><b>ชุดหลัก {s21["images"]} ภาพ</b> (รอบบินเดียว ซ้อนกันดี)</td>
      <td>ผืนเดียว {J["size21"][0]:,}×{J["size21"][1]:,} px · <b>ลำดับถูกทั้ง {s21["images"]} ภาพ</b> (ทิศซ้าย→ขวาอาจกลับด้านจากลำดับถ่าย เพราะโปรแกรมไม่รู้ว่าต้นทางคือปลายไหน) · ลอง {s21["pairs_total"]} คู่ → ตรวจละเอียด {s21["candidates"]} → ใช้ {s21["used"]} คู่ · รอยต่อคลาดมัธยฐาน {g21["resid"][0]:.1f} px สูงสุด {g21["resid"][1]:.1f} px (ที่ภาพกว้าง 1600 px) · ตรงกับเวลาถ่าย 100% · {J["t21"]} วินาที</td></tr>
  <tr><td><b>สองรอบบินรวม {s34["images"]} ภาพ</b></td>
      <td>ผืนเดียวทั้ง {s34["images"]} ภาพ ภาพสองรอบเรียงแทรกกันตามตำแหน่งบนผืน · ใช้ {s34["used"]} คู่ ตัดคู่หลอก {s34["gps_rejected"]} คู่ด้วย GPS · รอยต่อคลาดสูงสุด {J["resid34"][1]:.0f} px · {J["t34"]} วินาที</td></tr>
  <tr><td><b>รอบบินซ้อนน้อย {t13["stats"]["images"]} ภาพ</b> (Not use) มี GPS</td>
      <td>ผืนย่อย {seg13} ภาพ และมี {lone13} ภาพที่ต่อกับใครไม่ได้ · ตัดคู่หลอก {t13["stats"]["gps_rejected"]} คู่ — โปรแกรมบอกตรงๆ ว่าต่อไม่ครบ ไม่ฝืนต่อ</td></tr>
  <tr><td>ชุดเดียวกัน <b>ลบ GPS ออก</b></td>
      <td>ผืนย่อย {seg13n} ภาพ โดย <b>ผืน 3 ภาพต่อผิด</b> เพราะคู่หลอก · โปรแกรมเตือน "รอยต่อเปราะ" {t13n["stats"]["fragile"]} จุด รวมจุดที่ผิด แต่บอกเองไม่ได้ว่าจุดไหนผิด</td></tr>
</table>
<p>เทียบวิธีรุ่นก่อน (ต่อเป็นลูกโซ่ตามชื่อไฟล์) บนชุดหลัก: แนวนอนคลาดจาก GPS พอกัน (0.09 / {g21["rms"]:.2f} ม.) แต่แนวตั้ง รุ่นก่อนให้ผืนสูงต่างกัน 1.55 ม. รุ่นนี้ {g21["ymos"]:.2f} ม. ความสูงโดรนที่ฝังในภาพ {g21["yalt"]:.2f} ม.</p>

<h2><span class="n">5</span>ที่ต้องรู้ (ข้อจำกัด)</h2>
<ul>
  <li><b>GPS ตรวจได้เฉพาะคู่ในรอบบินเดียวกัน:</b> ในชุด 34 ภาพ เทียบได้ 38 จาก 87 คู่ที่ใช้ อีก 49 คู่ข้ามรอบบิน ไม่มี GPS ให้เทียบ</li>
  <li><b>ไม่มี GPS = ไม่มีตัวกันคู่หลอก:</b> ทำได้แค่เตือน "รอยต่อเปราะ" (คู่ที่ผืนพึ่งอยู่คู่เดียว และความมั่นใจต่ำ)</li>
  <li><b>ตัวตรวจ GPS ทดสอบกับภาพชุดเดียว</b> โดรนรุ่นเดียว บินข้างคานในที่โล่ง — ยังไม่รู้ว่าใต้สะพานจริง หรือกับ Matrice 4E พิกัดที่ฝังจะนิ่งแบบนี้ไหม</li>
  <li><b>เกณฑ์ตัวเลขผู้จัดทำตั้งเอง</b> (8 / 30 จุด, ย่อขยาย 3 เท่า, หมุน 30°, GPS 40%, รอบบิน 5 นาที) จากภาพชุดนี้ชุดเดียว · พิกเซลที่ต่างเล็กน้อย (เช่น ภาพบีบอัดซ้ำ) ทำให้คู่ที่จุดลงรอยใกล้ 30 ผ่าน/ไม่ผ่านได้ — เจอจริง: ชุด 34 ภาพได้ 84–87 คู่ ตัดคู่หลอก 1–2 คู่ ขึ้นกับว่าอ่านไฟล์ต้นฉบับหรือสำเนาที่บีบอัดซ้ำ</li>
  <li><b>แบบจำลองเลื่อน-หมุน-ย่อขยาย:</b> รวมสองรอบบินที่หันกล้องต่างกันราว 10° รอยต่อคลาดสูงสุด {J["resid34"][1]:.0f} px (ชุดหลักอย่างเดียว {g21["resid"][1]:.1f} px) — มุมที่ต่างอาจเป็นเหตุ ยังไม่ได้แยกทดสอบ</li>
  <li><b>สเกลจาก GPS เป็นค่าประมาณ</b> ({c21["gsd_orig_mm"]:.2f} มม. ต่อพิกเซลของภาพต้นฉบับ) ใช้แทนเลเซอร์ 4 จุดตามหัวข้อ 3.6 ไม่ได้</li>
  <li><b>ยังไม่ได้ลอง:</b> ผิวคอนกรีตเรียบสะอาด · ภาพชุดเดิมของโครงการ (rawdata) · ภาพมากกว่า 34 ใบ</li>
</ul>
<div class="box red"><b class="t">แก้ข้อความที่เคยบอกผิด</b>
ตอนบ่ายวันเดียวกัน Claude บอกว่าผืนเอียง "เพราะความคลาดสะสม ไม่ใช่คานเอียงจริง" โดยไม่ได้ตรวจ — <b>ผิดเป็นส่วนใหญ่</b> ความสูงที่ฝังในภาพบอกว่าโดรนไต่ขึ้นจริง {g21["yalt"]:.2f} ม.
(สหสัมพันธ์กับแนวตั้งบนผืน 0.98) ส่วนที่เป็นความคลาดของวิธีเก่ามีราว 0.5 ม. · ยังบอกไม่ได้ว่าโดรนไต่ขึ้นเพราะคานลาดจริงหรือเพราะนักบิน</div>

<h2><span class="n">6</span>ขั้นต่อไป <span class="small" style="font-weight:400">(เสนอ ยังไม่ได้ตัดสิน)</span></h2>
<ol>
  <li>ลองกับภาพชุดเดิมของโครงการ (บินสูง 20–40 ม. ซ้อน 70–80%) และผิวคอนกรีตเรียบ</li>
  <li>ทดสอบตัวตรวจ GPS ใต้สะพานจริงตอนบินนำร่อง (ธ.ค.) ด้วย Matrice 4E — ดูว่าพิกัดที่ฝังยังนิ่งไหม และถ้าไม่นิ่ง โปรแกรมต่อได้แค่ไหนเมื่อไม่มี GPS</li>
  <li>ฉายมาสก์ความเสียหายของแต่ละภาพลงผืน (ต้องมีมาสก์จาก SAM ก่อน) ให้ความเสียหายในส่วนซ้อนนับครั้งเดียว — ตรงกับ "ทางที่ 1" ที่อาจารย์เสนอวันที่ 10 พ.ย.</li>
  <li>ถ้าต้องวัดขนาดจริงบนผืน ใช้สเกลเลเซอร์ต่อภาพ แล้วค่อยรวมผืน</li>
</ol>

<h3>ไฟล์</h3>
<ul class="src">
  <li>โปรแกรม (ดับเบิลคลิก <code>เปิดโปรแกรมต่อภาพ.bat</code>): <code>D:\\00mk\\เสาพัง\\ku_project_jop\\05_โค้ดและการทดลอง\\ทดลอง_ต่อภาพ_2026-11-23\\</code></li>
  <li>ค้นคว้าละเอียด (คำอ้างอิงตามต้นฉบับ ผลทดลอง): <code>…\\วิธีหาลำดับภาพ_ค้นคว้า.md</code> · อธิบายโปรแกรมแบบภาษาง่าย: <code>…\\สรุป_โปรแกรมต่อภาพ_ภาษาง่าย.pdf</code></li>
</ul>
<h3>แหล่งอ้างอิง (เปิดอ่านต้นฉบับแล้วทุกรายการ)</h3>
<ul class="src">
  <li>[1] Brown, M. and Lowe, D. (2007). Automatic Panoramic Image Stitching using Invariant Features. IJCV — https://www.cs.ubc.ca/~lowe/papers/07brown.pdf</li>
  <li>[2] OpenCV stitching module, ซอร์สสาขา 4.x — https://github.com/opencv/opencv/tree/4.x/modules/stitching/src</li>
  <li>[3] OpenSfM — https://opensfm.readthedocs.io/en/latest/using.html · [4] OpenDroneMap — https://docs.opendronemap.org/arguments/matcher-neighbors/</li>
  <li>[5] COLMAP Tutorial — https://colmap.github.io/tutorial.html</li>
  <li>[6] Agisoft Metashape Pro 2.1 User Manual หน้า 39 — https://www.agisoft.com/pdf/metashape-pro_2_1_en.pdf</li>
  <li>[7] ExifTool GPS Tags https://exiftool.org/TagNames/GPS.html · DJI Tags https://exiftool.org/TagNames/DJI.html</li>
</ul>
'''

html = f'<!doctype html><html lang="th"><head><meta charset="utf-8"><title>สรุปผล: ให้โปรแกรมหาลำดับภาพเอง</title><style>{CSS}</style></head><body>{BODY}</body></html>'
out = os.path.join(HERE, 'สรุปผล.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html))
