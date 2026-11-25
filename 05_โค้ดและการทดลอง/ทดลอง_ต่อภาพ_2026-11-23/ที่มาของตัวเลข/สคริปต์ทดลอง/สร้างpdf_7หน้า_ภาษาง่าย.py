# สร้าง HTML ของเอกสารสรุป (รุ่น 2) จากตัวเลขจริงใน numbers.json แล้วให้ Edge พิมพ์เป็น PDF
import json, os, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'numbers.json'), encoding='utf-8'))
for f in ('f1_keypoints.jpg', 'f3_matches_ransac.jpg'):
    if not os.path.exists(os.path.join(HERE, f)):
        shutil.copyfile(os.path.join(HERE, '..', 'doc', f), os.path.join(HERE, f))

s21, c21, g21 = J['stats21'], J['check21'], J['gps21']
s34, c34 = J['stats34'], J['check34']
t13, t13n = J['t13'], J['t13nometa']
n = len(J['nodes21'])

# ---------- รูป: แผนผังการเชื่อม ----------
W, X0, X1, Y = 680, 26, 654, 92
xs = [X0 + (X1 - X0) * k / (n - 1) for k in range(n)]
arcs = []
for e in J['edges21']:
    a, b = sorted((e['a'], e['b']))
    h = 16 + 20 * (b - a)
    if e['status'] == 'tree':
        arcs.append(f'<path d="M{xs[a]:.1f} {Y - 9} Q{(xs[a] + xs[b]) / 2:.1f} {Y - 9 - h} {xs[b]:.1f} {Y - 9}" fill="none" stroke="#1d5fd6" stroke-width="2"/>')
    else:
        arcs.append(f'<path d="M{xs[a]:.1f} {Y + 9} Q{(xs[a] + xs[b]) / 2:.1f} {Y + 9 + h} {xs[b]:.1f} {Y + 9}" fill="none" stroke="#8a92a0" stroke-width="1.6" stroke-dasharray="4 3"/>')
nodes = ''.join(f'<circle cx="{x:.1f}" cy="{Y}" r="9.5" fill="#fff" stroke="#16191e" stroke-width="1.4"/><text x="{x:.1f}" y="{Y + 3.6}" font-size="9.5" text-anchor="middle" font-weight="700">{k + 1}</text>'
                for k, x in enumerate(xs))
n_tree = sum(e['status'] == 'tree' for e in J['edges21'])
n_extra = sum(e['status'] == 'extra' for e in J['edges21'])
svg_graph = f'''<svg viewBox="0 0 {W} 176" xmlns="http://www.w3.org/2000/svg" font-family="Leelawadee UI, sans-serif">
{''.join(arcs)}{nodes}
<path d="M30 164 h26" stroke="#1d5fd6" stroke-width="2"/><text x="62" y="168" font-size="11" fill="#535b68">คู่ที่ใช้วางภาพ ({n_tree} คู่)</text>
<path d="M210 164 h26" stroke="#8a92a0" stroke-width="1.6" stroke-dasharray="4 3"/><text x="242" y="168" font-size="11" fill="#535b68">คู่ที่ยืนยันซ้ำ ({n_extra} คู่)</text>
</svg>'''

# ---------- รูป: ตำแหน่งบนผืน เทียบ GPS ----------
mx = max(max(d['pos'] for d in J['nodes21']), max(d['gps'] for d in J['nodes21'])) * 1.04
S, P0 = 250, 40


def px(v):
    return P0 + S * v / mx


def py(v):
    return 10 + S - S * v / mx


ticks = ''.join(f'<line x1="{px(t)}" y1="{py(0)}" x2="{px(t)}" y2="{py(0) + 4}" stroke="#868e9b"/><text x="{px(t)}" y="{py(0) + 16}" font-size="10" text-anchor="middle" fill="#535b68">{t}</text>'
                f'<line x1="{P0 - 4}" y1="{py(t)}" x2="{P0}" y2="{py(t)}" stroke="#868e9b"/><text x="{P0 - 7}" y="{py(t) + 3.5}" font-size="10" text-anchor="end" fill="#535b68">{t}</text>'
                for t in (0, 5, 10, 15, 20))
pts = ''.join(f'<circle cx="{px(d["pos"]):.1f}" cy="{py(d["gps"]):.1f}" r="3.4" fill="#1d5fd6" fill-opacity=".85"/>' for d in J['nodes21'])
svg_gps = f'''<svg viewBox="0 0 310 300" xmlns="http://www.w3.org/2000/svg" font-family="Leelawadee UI, sans-serif">
<rect x="{P0}" y="10" width="{S}" height="{S}" fill="#f4f6f9"/>
<line x1="{px(0)}" y1="{py(0)}" x2="{px(mx)}" y2="{py(mx)}" stroke="#c4321f" stroke-width="1.2" stroke-dasharray="5 4"/>
{ticks}{pts}
<text x="{P0 + S / 2}" y="294" font-size="11" text-anchor="middle" fill="#16191e">ตำแหน่งบนผืน (ม.)</text>
<text x="11" y="{10 + S / 2}" font-size="11" text-anchor="middle" fill="#16191e" transform="rotate(-90 11 {10 + S / 2})">ตำแหน่งจาก GPS (ม.)</text>
<text x="{P0 + 10}" y="28" font-size="10.5" fill="#c4321f">เส้นประ = ตรงกันพอดี</text>
</svg>'''

# ---------- รูป: แนวตั้งบนผืน เทียบความสูงในภาพ ----------
A = J['alt21']
posn = [d['pos'] for d in J['nodes21']]
vmax = max(max(abs(d['y']) for d in A), max(abs(d['alt']) for d in A)) * 1.15
AW, AH, AX, AY = 300, 200, 44, 14


def ax(v):
    return AX + AW * v / max(posn)


def ay(v):
    return AY + AH / 2 - (AH / 2) * v / vmax


line_m = ' '.join(f'{ax(p):.1f},{ay(d["y"]):.1f}' for p, d in zip(posn, A))
line_a = ' '.join(f'{ax(p):.1f},{ay(d["alt"]):.1f}' for p, d in zip(posn, A))
yt = ''.join(f'<line x1="{AX}" y1="{ay(t)}" x2="{AX + AW}" y2="{ay(t)}" stroke="#e2e5ea"/><text x="{AX - 6}" y="{ay(t) + 3.5}" font-size="10" text-anchor="end" fill="#535b68">{t:+.1f}</text>' for t in (-0.5, 0, 0.5))
xt = ''.join(f'<text x="{ax(t)}" y="{AY + AH + 14}" font-size="10" text-anchor="middle" fill="#535b68">{t}</text>' for t in (0, 5, 10, 15, 20))
svg_alt = f'''<svg viewBox="0 0 360 262" xmlns="http://www.w3.org/2000/svg" font-family="Leelawadee UI, sans-serif">
<rect x="{AX}" y="{AY}" width="{AW}" height="{AH}" fill="#f4f6f9"/>{yt}{xt}
<polyline points="{line_m}" fill="none" stroke="#1d5fd6" stroke-width="2.2"/>
<polyline points="{line_a}" fill="none" stroke="#1f8a3e" stroke-width="2.2" stroke-dasharray="6 3"/>
<path d="M{AX + 8} {AY + 14} h22" stroke="#1d5fd6" stroke-width="2.2"/><text x="{AX + 36}" y="{AY + 18}" font-size="10.5" fill="#16191e">แนวตั้งของภาพบนผืน</text>
<path d="M{AX + 8} {AY + 30} h22" stroke="#1f8a3e" stroke-width="2.2" stroke-dasharray="6 3"/><text x="{AX + 36}" y="{AY + 34}" font-size="10.5" fill="#16191e">ความสูงโดรนที่ฝังในภาพ</text>
<text x="{AX + AW / 2}" y="256" font-size="11" text-anchor="middle" fill="#16191e">ตำแหน่งตามแนวคาน (ม.)</text>
<text x="11" y="{AY + AH / 2}" font-size="11" text-anchor="middle" fill="#16191e" transform="rotate(-90 11 {AY + AH / 2})">สูง/ต่ำกว่าค่าเฉลี่ย (ม.)</text>
</svg>'''

cut = J['cut34']
cut_txt = ' และ '.join(f'{c["inl"]} จุด' for c in sorted(cut, key=lambda c: -c['inl']))
cut_diff = ' และ '.join(f'{c["diff"]:.2f}' for c in sorted(cut, key=lambda c: -c['inl']))
cov = J['cover21']
seg13 = ', '.join(str(len(x)) for x in t13['segs'] if len(x) > 1)
lone13 = sum(len(x) == 1 for x in t13['segs'])
seg13n = ', '.join(str(len(x)) for x in t13n['segs'] if len(x) > 1)

html = f'''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>โปรแกรมต่อภาพโดรนทำงานอย่างไร</title>
<style>
  @page {{ size: A4; margin: 16mm 16mm 18mm; }}
  :root {{ --ink:#16191e; --ink2:#535b68; --ink3:#868e9b; --line:#e2e5ea; --soft:#f4f6f9; --blue:#1d5fd6; --blue-soft:#e8effc;
          --green:#1f8a3e; --green-soft:#e5f4ea; --red:#c4321f; --red-soft:#fcebe8; --amber:#8a5a00; --amber-soft:#fff5d8; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: "Leelawadee UI", "Sarabun", sans-serif; color: var(--ink); font-size: 11.2pt; line-height: 1.62; margin: 0;
         -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
  h1 {{ font-size: 24pt; line-height: 1.25; margin: 0 0 4px; letter-spacing: -.01em; }}
  h2 {{ font-size: 15pt; margin: 22px 0 8px; display: flex; align-items: center; gap: 10px; break-after: avoid; }}
  h2 .n {{ width: 26px; height: 26px; border-radius: 50%; background: var(--blue); color: #fff; font-size: 11pt; display: inline-grid; place-items: center; flex: none; }}
  h3 {{ font-size: 12pt; margin: 14px 0 4px; break-after: avoid; }}
  p {{ margin: 5px 0 8px; }}
  .lead {{ color: var(--ink2); font-size: 12pt; margin-bottom: 14px; }}
  .meta {{ color: var(--ink3); font-size: 9.5pt; border-bottom: 1px solid var(--line); padding-bottom: 10px; margin-bottom: 16px; }}
  .box {{ border-radius: 10px; padding: 10px 14px; margin: 10px 0; break-inside: avoid; }}
  .box.blue {{ background: var(--blue-soft); }} .box.green {{ background: var(--green-soft); }}
  .box.amber {{ background: var(--amber-soft); }} .box.gray {{ background: var(--soft); }} .box.red {{ background: var(--red-soft); }}
  .box b.t {{ display: block; margin-bottom: 2px; }}
  figure {{ margin: 10px 0 14px; break-inside: avoid; }}
  figure img, figure svg {{ width: 100%; display: block; border-radius: 8px; }}
  figcaption {{ font-size: 9.5pt; color: var(--ink2); margin-top: 5px; }}
  .flow {{ display: grid; grid-template-columns: repeat(6, 1fr); gap: 7px; margin: 12px 0 6px; }}
  .flow div {{ background: var(--soft); border-radius: 10px; padding: 8px 6px; text-align: center; font-size: 9.3pt; line-height: 1.4; position: relative; }}
  .flow div b {{ display: block; font-size: 10pt; color: var(--blue); margin-bottom: 2px; }}
  .flow div:not(:last-child)::after {{ content: "→"; position: absolute; right: -8px; top: 50%; transform: translateY(-50%); color: var(--ink3); font-weight: 700; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 10pt; margin: 8px 0; break-inside: avoid; }}
  th, td {{ border-bottom: 1px solid var(--line); padding: 5px 8px; text-align: left; vertical-align: top; }}
  th {{ color: var(--ink2); font-weight: 600; background: var(--soft); }}
  td.num {{ text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }}
  .sw {{ display: inline-block; width: 11px; height: 11px; border-radius: 3px; vertical-align: -1px; margin-right: 5px; }}
  ul {{ margin: 4px 0 8px; padding-left: 20px; }} li {{ margin: 2px 0; }}
  .two {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: start; }}
  .pb {{ break-before: page; }}
  figure.narrow img {{ width: 46%; margin: 0 auto; }}
  .keep {{ break-inside: avoid; }}
  figure.narrow figcaption {{ text-align: center; }}
  .small {{ font-size: 9.5pt; color: var(--ink2); }}
  .bars {{ display: grid; grid-template-columns: 150px 1fr 60px; gap: 5px 10px; align-items: center; font-size: 10pt; margin: 8px 0 4px; }}
  .bars i {{ display: block; height: 14px; border-radius: 4px; }}
  .yes {{ color: var(--green); font-weight: 600; }} .no {{ color: var(--red); font-weight: 600; }} .part {{ color: var(--amber); font-weight: 600; }}
  code {{ font-size: 9.6pt; }}
  .src {{ font-size: 9pt; color: var(--ink2); }} .src li {{ margin: 3px 0; word-break: break-all; }}
</style>
</head>
<body>

<h1>โปรแกรมต่อภาพโดรน ทำงานอย่างไร</h1>
<p class="lead">สรุปแบบภาษาง่าย สำหรับทีม T-BHI — รุ่นที่ <b>ใส่ภาพลำดับไหนก็ได้ แล้วได้ผืนภาพออกมาเลย</b> โปรแกรมหาเองว่าภาพไหนต่อกับภาพไหน</p>
<div class="meta">เขียนโดย Claude กับมะขาม · 23 พ.ย. 2569 (รุ่น 2 แทนฉบับบ่ายวันเดียวกัน) · ตัวเลขทุกตัวผู้จัดทำคำนวณเองจากภาพในโฟลเดอร์ <code>04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft</code> ·
รายละเอียดการค้นคว้าและที่มาอยู่ในไฟล์ <code>วิธีหาลำดับภาพ_ค้นคว้า.md</code> ข้างไฟล์นี้</div>

<h2><span class="n">1</span>โปรแกรมนี้ทำอะไร</h2>
<p>บินโดรนไล่ถ่ายคานยาวๆ ต้องถ่ายหลายใบให้ <b>ซ้อนกัน</b> ไม่งั้นมีช่องว่างที่ไม่มีใครเห็น แต่พอซ้อนกัน รอยเสียหายเดียวกันจะโผล่ในหลายภาพ ถ้านับทีละภาพแล้วเอามารวมจะนับซ้ำ</p>
<div class="box blue"><b class="t">โปรแกรมเอาภาพมาต่อเป็นผืนเดียว และรู้ว่าทุกจุดบนผืนมาจากภาพไหนบ้าง</b>
ของใหม่ในรุ่นนี้: <b>ไม่ต้องเรียงภาพ ไม่ต้องตั้งชื่อไฟล์ให้เรียง</b> ลากภาพทั้งกองมาวาง โปรแกรมเริ่มต่อเอง และบอกลำดับที่หาได้กลับมาให้ดู</div>

<h2><span class="n">2</span>ภาพรวม 6 ขั้น</h2>
<div class="flow">
  <div><b>หาจุดเด่น</b>มุม คราบ รอย ที่จำได้ ในทุกภาพ</div>
  <div><b>ลองทุกคู่</b>จับคู่ภาพทุกใบกับทุกใบ แบบเร็ว</div>
  <div><b>ตรวจละเอียด</b>เฉพาะคู่ที่น่าจะซ้อนกัน</div>
  <div><b>ตรวจกับ GPS</b>ตัดคู่ที่ระยะขัดกัน</div>
  <div><b>วางภาพ</b>ปรับทุกใบพร้อมกันให้ลงรอย</div>
  <div><b>ได้ผืน + ลำดับ</b>ลำดับ = ตำแหน่งบนผืน</div>
</div>
<p class="small">ทั้งหมดรันในเครื่องตัวเอง ไม่ใช้ AI ไม่ต่ออินเทอร์เน็ต ใช้ไลบรารี OpenCV ที่อยู่ในตาราง 3.1 ของเล่มอยู่แล้ว · แนวคิดหลักมาจากงานของ Brown &amp; Lowe (2007) ซึ่งตัวต่อภาพของ OpenCV ก็ทำตาม</p>

<h2><span class="n">3</span>ทีละขั้น</h2>

<h3>ขั้นที่ 1 — หาจุดเด่นในแต่ละภาพ</h3>
<div class="two keep">
  <p>เหมือนเวลาหาทางในเมือง เราจำ "จุดสังเกต" เช่น ป้ายร้าน ต้นไม้ใหญ่ โปรแกรมหาจุดที่หน้าตาไม่ซ้ำใครในภาพ เช่น มุมคราบ ขอบรอยซ่อม สติกเกอร์ แล้วจด "ลายนิ้วมือ" ของจุดนั้นไว้ (วิธีชื่อ SIFT) ลายนิ้วมือนี้ยังเหมือนเดิมแม้ภาพถูกย่อ ขยาย หรือหมุนนิดหน่อย<br><br>ภาพหนึ่งใบมีจุดเด่นราว 3,500 จุด ส่วนผิวคอนกรีตเรียบๆ แทบไม่มีจุดเลย — นี่คือเหตุผลที่ภาพต้องซ้อนกันบนบริเวณที่มีลวดลาย</p>
  <figure style="margin-top:0"><img src="f1_keypoints.jpg"><figcaption>รูป 1 จุดเด่นที่โปรแกรมหาเจอในภาพหนึ่งใบ (วงเหลือง แสดงครึ่งเดียวให้ไม่รก)</figcaption></figure>
</div>

<h3>ขั้นที่ 2 — ลองจับคู่ "ทุกคู่"</h3>
<p>โปรแกรมไม่รู้ว่าภาพไหนอยู่ติดกัน จึง <b>ลองภาพทุกใบกับทุกใบ</b> ({s21["images"]} ภาพ = {s21["pairs_total"]} คู่) ฟังดูเยอะ แต่ขั้นนี้ใช้เฉพาะจุดเด่นที่ชัดที่สุด 1,600 จุดต่อภาพ จึงเร็วมาก (ราว 2 มิลลิวินาทีต่อคู่) คู่ไหนมีจุดตรงกันพอสมควรก็ส่งต่อไปตรวจละเอียด ที่เหลือทิ้ง</p>
<div class="box gray"><b class="t">ทำไมไม่เรียงตามชื่อไฟล์ หรือเวลา ไปเลย</b>
ชื่อไฟล์ใช้ได้ถ้าไม่มีใครเปลี่ยนชื่อและภาพมาจากการบินรอบเดียว เวลาถ่ายก็เช่นกัน — ทั้งสองอย่างบอกไม่ได้ว่าภาพจาก <b>คนละรอบบิน</b> ซ้อนกันไหม ส่วนเนื้อภาพบอกได้เสมอ (ดูตารางในหัวข้อ 4)</div>

<h3>ขั้นที่ 3 — ตรวจละเอียด และคัดคู่จุดที่จับผิด</h3>
<p>คู่ที่ผ่านขั้น 2 ถูกจับคู่ใหม่ด้วยจุดเด่นทั้งหมด แล้วคัดคู่จุดที่ผิดด้วยวิธีคล้าย <b>โหวต</b> (RANSAC): สุ่มหยิบคู่จุดมาสองคู่ ถามว่า "ถ้าสองภาพต่อกันแบบนี้ คู่อื่นเห็นด้วยกี่คู่" ทำซ้ำหลายรอบ เลือกแบบที่มีคนเห็นด้วยมากที่สุด ผลคือ "สูตรวางภาพ" ของคู่นั้น 4 ค่า: เลื่อนซ้ายขวา เลื่อนขึ้นลง หมุน ย่อขยาย</p>
<figure><img src="f3_matches_ransac.jpg"><figcaption>รูป 2 สองภาพที่ซ้อนกัน: <span style="color:var(--green)"><b>เขียว</b></span> = คู่จุดที่เห็นด้วยกัน (เก็บ) · <span style="color:var(--red)"><b>แดง</b></span> = คู่ที่จับผิด (ทิ้ง)</figcaption></figure>
<p class="small">สองภาพนับว่า "ต่อกันได้" เมื่อมีคู่จุดเห็นด้วยกันอย่างน้อย 30 คู่ ย่อขยายกันไม่เกิน 3 เท่า หมุนไม่เกิน 30° และจุดไม่กระจุกอยู่ที่เดียว (ค่าเหล่านี้ผู้จัดทำตั้งเอง)</p>

<h3>ขั้นที่ 4 — ตรวจกับ GPS ที่ฝังในภาพ (กันคู่หลอก)</h3>
<p>พอลองทุกคู่ ก็เจอปัญหาใหม่: <b>ลายบนผิวคอนกรีตที่ซ้ำเป็นช่วงๆ ทำให้ภาพที่ไม่ได้ซ้อนกันจริง ดูเหมือนต่อกันได้</b> ในภาพชุดทดสอบมีแบบนี้ 2 คู่ ({cut_txt} ที่ตรงกัน ซึ่งผ่านเกณฑ์ 30) แยกด้วยเนื้อภาพอย่างเดียวไม่ออก</p>
<p>ภาพจากโดรนมีพิกัดฝังอยู่ โปรแกรมจึงเทียบว่า <b>ระยะที่ภาพบอก</b> กับ <b>ระยะที่ GPS บอก</b> ไปด้วยกันไหม:</p>
<div class="bars">
  <span>คู่จริง (ตัวอย่าง)</span><i style="background:var(--green);width:55%"></i><span>1.2 ม.</span>
  <span class="small">GPS ของคู่เดียวกัน</span><i style="background:#9fd3ae;width:57%"></i><span>1.3 ม.</span>
  <span>คู่หลอก — ภาพบอกว่า</span><i style="background:var(--red);width:16%"></i><span>0.37 ม.</span>
  <span class="small">GPS ของคู่เดียวกัน</span><i style="background:#f0a79c;width:96%"></i><span>2.2 ม.</span>
</div>
<p>คู่จริงในชุดนี้ ระยะสองแบบต่างกันไม่เกิน {J["gpsdiff34max"]:.2f} ม. ส่วนคู่หลอกต่างกัน {cut_diff} ม. โปรแกรมจึงตัดคู่หลอกทิ้งได้</p>
<div class="box amber"><b class="t">GPS ใช้ตรวจ ไม่ได้ใช้วางภาพ</b>
ภาพชุดนี้กล้องบันทึกสถานะ GPS ว่า "Invalid" ทุกภาพ และงานจริงของเราบินใต้สะพาน จึงไม่ให้โปรแกรมพึ่ง GPS ถ้าไม่มี GPS หรือ GPS ไม่นิ่ง โปรแกรมยังต่อได้จากเนื้อภาพ เพียงแต่ไม่มีตัวกันคู่หลอก และจะเตือนตรงรอยต่อที่เสี่ยง
· เทียบเฉพาะภาพในรอบบินเดียวกัน (ถ่ายห่างกันไม่เกิน 5 นาที) เพราะข้ามรอบบิน GPS เลื่อนไป 1.29 ม.</div>

<h3>ขั้นที่ 5 — วางภาพลงผืน</h3>
<p>มองภาพเป็นจุด คู่ที่ผ่านการตรวจเป็นเส้นเชื่อม กลุ่มที่เชื่อมถึงกันหมด = หนึ่งผืน (ถ้ามีภาพที่ไม่เชื่อมกับใคร ก็แยกออกมาเอง) โปรแกรมเริ่มวางจากภาพกึ่งกลาง ไล่ออกไปตามเส้นเชื่อมที่แข็งแรงที่สุด แล้ว <b>ปรับทุกภาพพร้อมกัน</b> ให้ทุกคู่ลงรอยมากที่สุด ไม่ใช่ต่อทีละใบเป็นลูกโซ่แบบรุ่นก่อน ความคลาดจึงไม่สะสมไปทางเดียว</p>
<figure>{svg_graph}<figcaption>รูป 3 แผนผังการเชื่อมของภาพชุดหลัก {n} ภาพ (วงกลม = ภาพ เรียงตามลำดับที่หาได้) เส้นทึบ = คู่ที่ใช้วางภาพ เส้นประ = คู่ที่ข้ามไปอีกใบ ช่วยยืนยันและดึงผืนไม่ให้เพี้ยน</figcaption></figure>

<h3>ขั้นที่ 6 — ได้ผืน และลำดับภาพ</h3>
<p>เมื่อทุกภาพมีตำแหน่งบนผืน <b>ลำดับภาพก็คือตำแหน่งนั้นเอง</b> (ซ้ายไปขวา) ตอนวาด แต่ละจุดบนผืนเลือกพิกเซลจากภาพที่จุดนั้นอยู่ใกล้กลางภาพที่สุด ไม่มีการเกลี่ยสีผสมกัน ทุกพิกเซลยังเป็นของจริงจากภาพใดภาพหนึ่ง · ใส่ภาพชุดเดิมกี่ครั้ง ลำดับไหน ก็ได้ผลเดิม</p>

<div class="keep"><h2><span class="n">4</span>ข้อมูลที่ฝังในภาพ มีอะไร ใช้ทำอะไร</h2>
<p>อ่านจากไฟล์ทั้ง 34 ภาพ (กล้อง DJI Mini 3 Pro ถ่าย 23 มี.ค. 2023 สองรอบบิน)</p>
<table>
  <tr><th style="width:17%">ข้อมูล</th><th style="width:30%">ในภาพชุดนี้</th><th style="width:21%">ใช้เรียงภาพได้ไหม</th><th>โปรแกรมใช้ทำอะไร</th></tr>
  <tr><td><b>เนื้อภาพ</b></td><td>จุดเด่นราว 3,500 จุดต่อภาพ</td><td class="yes">ได้ และแม่นที่สุด</td><td>ตัวหลักในการหาคู่และวางภาพ</td></tr>
  <tr><td><b>เวลาถ่าย</b></td><td>มีทุกภาพ ละเอียดระดับวินาที</td><td class="part">ได้เฉพาะในรอบบินเดียว</td><td>แบ่งรอบบิน · คู่ที่ถ่ายติดกันถูกส่งตรวจเสมอ · รายงานว่าลำดับตรงกับเวลาไหม</td></tr>
  <tr><td><b>พิกัด GPS</b></td><td>มีทุกภาพ แต่กล้องบันทึกสถานะ "Invalid" · ในรอบบินเดียวคลาดจากผืนเฉลี่ย {c21["gps_rms_m"]:.2f} ม.</td><td class="part">พอได้ แต่ไม่ละเอียดพอจะวาง</td><td>ตัดคู่หลอก · รายงานว่าผืนตรงกับ GPS แค่ไหน · ประมาณสเกล</td></tr>
  <tr><td><b>ความสูง</b></td><td>6.0–7.1 ม. ละเอียด 0.1 ม.</td><td class="no">ไม่ได้</td><td>ใช้ร่วมกับ GPS ตอนเทียบระยะ</td></tr>
  <tr><td><b>มุมกล้อง</b></td><td>ก้มเงย 0° เอียงข้าง 0° ทุกภาพ</td><td class="no">ไม่ได้</td><td>ยังไม่ใช้ (ลองแล้วช่วยได้นิดเดียว)</td></tr>
  <tr><td><b>ชื่อไฟล์</b></td><td>เรียงตามลำดับถ่าย</td><td class="part">ได้ ถ้าไม่มีใครเปลี่ยนชื่อ</td><td>ไม่ใช้เลย (รุ่นก่อนใช้)</td></tr>
</table></div>
<p class="small">โปรแกรมทำแผนที่จากภาพโดรนที่มีชื่อเสียง (OpenSfM, OpenDroneMap, COLMAP, Metashape) ก็ใช้ GPS และเวลาในบทบาทเดียวกัน คือช่วยคัดว่าควรลองคู่ไหน ตัวตัดสินยังเป็นการจับคู่จุดบนภาพ · COLMAP แนะนำว่าถ้าภาพไม่เกินหลายร้อยให้ลองทุกคู่ได้เลย</p>

<h2><span class="n">5</span>ผลกับภาพจริง</h2>
<p>ทดสอบโดย <b>สลับลำดับภาพและตั้งชื่อไฟล์มั่ว</b> ก่อนใส่ทุกครั้ง</p>
<figure><img src="f_mosaic.jpg"><figcaption>รูป 4 ผืนจากชุดหลัก {n} ภาพ ตัวเลข = ลำดับที่โปรแกรมหาได้ ขนาด {J["size21"][0]:,} × {J["size21"][1]:,} px</figcaption></figure>
<table>
  <tr><th style="width:36%">ชุดที่ใส่</th><th>ผล</th></tr>
  <tr><td><b>ชุดหลัก {s21["images"]} ภาพ</b> (รอบบินเดียว ซ้อนกันดี)</td><td>ได้ผืนเดียว <b>ลำดับถูกทั้ง {s21["images"]} ภาพ</b> (ทิศซ้าย→ขวาอาจกลับด้านจากลำดับถ่าย เพราะโปรแกรมไม่รู้ว่าต้นทางคือปลายไหน) · ลอง {s21["pairs_total"]} คู่ → ตรวจละเอียด {s21["candidates"]} → ใช้ {s21["used"]} คู่ · คำนวณ {J["t21"]} วินาที</td></tr>
  <tr><td><b>สองรอบบินรวมกัน {s34["images"]} ภาพ</b></td><td>ได้ผืนเดียวทั้ง {s34["images"]} ภาพ ภาพสองรอบแทรกกันตามตำแหน่งจริง · <b>ตัดคู่หลอก {s34["gps_rejected"]} คู่ด้วย GPS</b> · คำนวณ {J["t34"]} วินาที</td></tr>
  <tr><td><b>รอบบินที่ซ้อนกันน้อย {t13["stats"]["images"]} ภาพ</b> (โฟลเดอร์ Not use)</td><td>ต่อได้เป็นผืนย่อย {seg13} ภาพ และมี {lone13} ภาพที่ต่อกับใครไม่ได้ · ตัดคู่หลอก {t13["stats"]["gps_rejected"]} คู่ — โปรแกรมบอกตรงๆ ว่าต่อไม่ครบ ไม่ฝืนต่อ</td></tr>
  <tr><td>ชุดเดียวกัน แต่ <b>ลบข้อมูล GPS ออก</b></td><td>ได้ผืนย่อย {seg13n} ภาพ โดย <b>ผืน 3 ภาพต่อผิด</b> เพราะคู่หลอก · โปรแกรมเตือน "รอยต่อเปราะ" {t13n["stats"]["fragile"]} จุด (รวมจุดที่ผิด) แต่บอกเองไม่ได้ว่าจุดไหนผิด</td></tr>
</table>

<div class="keep"><h3>ผืนที่ได้ ตรงกับการเคลื่อนที่จริงของโดรนไหม</h3>
<div class="two">
  <figure>{svg_gps}<figcaption>รูป 5 แนวนอน: ตำแหน่งของแต่ละภาพบนผืน เทียบกับ GPS — เกาะเส้นตลอด คลาดเฉลี่ย {c21["gps_rms_m"]:.2f} ม. ตลอดแนว {c21["gps_span_m"]:.1f} ม.</figcaption></figure>
  <figure>{svg_alt}<figcaption>รูป 6 แนวตั้ง: ผืนบอกว่าภาพค่อยๆ สูงขึ้น ซึ่งตรงกับความสูงโดรนที่ฝังในภาพ (ผืน {g21["ymos"]:.2f} ม. · ความสูงในภาพ {g21["yalt"]:.2f} ม.)</figcaption></figure>
</div></div>
<table>
  <tr><th>สิ่งที่วัด (ชุดหลัก {s21["images"]} ภาพ)</th><th class="num">ผล</th><th>อ่านว่า</th></tr>
  <tr><td>ลำดับบนผืน เทียบลำดับเวลาที่ถ่าย</td><td class="num">{c21["time_agree"] * 100:.0f}%</td><td>ตรงกันทุกคู่</td></tr>
  <tr><td>รอยต่อคลาดหลังวางทุกภาพ</td><td class="num">{g21["resid"][0]:.1f} px (สูงสุด {g21["resid"][1]:.1f})</td><td>ที่ความกว้างภาพ 1600 px</td></tr>
  <tr><td>ตำแหน่งบนผืน เทียบ GPS</td><td class="num">คลาด {c21["gps_rms_m"]:.2f} ม.</td><td>ตลอดแนว {c21["gps_span_m"]:.1f} ม.</td></tr>
  <tr><td>สเกลโดยประมาณจาก GPS</td><td class="num">{c21["gsd_orig_mm"]:.2f} มม./พิกเซล</td><td>ของภาพต้นฉบับ — ค่าประมาณ ใช้แทนเลเซอร์ไม่ได้</td></tr>
  <tr><td>ถ่ายซ้ำเฉลี่ย</td><td class="num">{J["dup21"]:.2f} เท่า</td><td>ถ้าไม่รวมภาพ รอยเสียหายถูกนับเกือบสองครั้ง</td></tr>
</table>
<figure><img src="f_heat.jpg"><figcaption>รูป 7 จุดไหนถูกถ่ายกี่ภาพ
  <span class="sw" style="background:#22c55e"></span>1 ภาพ ({cov[0]}%)
  <span class="sw" style="background:#facc08"></span>2 ภาพ ({cov[1]}%)
  <span class="sw" style="background:#f9730c"></span>3 ภาพ ({cov[2]}%)
  <span class="sw" style="background:#dc263c"></span>4 ภาพขึ้นไป ({cov[3]}%) — นับทั้งภาพ รวมพื้นหลังที่ไม่ใช่คาน</figcaption></figure>

<h2><span class="n">6</span>หน้าจอโปรแกรม</h2>
<div class="two">
  <figure><img src="ui_input.png"><figcaption>รูป 8 ลากภาพทั้งกองมาวาง (ชื่อไฟล์ในรูปตั้งมั่วไว้ทดสอบ) โปรแกรมเตรียมภาพแล้วเริ่มต่อเอง</figcaption></figure>
  <figure><img src="ui_result.png"><figcaption>รูป 9 ผลลัพธ์: ผืนภาพ ปุ่มดาวน์โหลด แถบ "ลำดับที่โปรแกรมหาได้" และผลเทียบกับเวลา/GPS</figcaption></figure>
</div>
<table>
  <tr><th style="width:32%">ส่วนบนหน้าจอ</th><th>ใช้ทำอะไร</th></tr>
  <tr><td>ช่องวางภาพ</td><td>ลากภาพมาวางหรือคลิกเลือก ไม่ต้องเรียง ใส่เพิ่มทีหลังได้ โปรแกรมต่อใหม่ให้เอง</td></tr>
  <tr><td>ดาวน์โหลดภาพ (.jpg)</td><td>เอาผืนที่ต่อแล้วไปใช้</td></tr>
  <tr><td>ลำดับที่โปรแกรมหาได้</td><td>ภาพเล็กเรียงตามตำแหน่งบนผืน คลิกแล้วโปรแกรมชี้ภาพนั้นบนผืน</td></tr>
  <tr><td>เทียบกับข้อมูลที่ฝังในภาพ</td><td>ลำดับตรงกับเวลาถ่ายไหม ตำแหน่งตรงกับ GPS แค่ไหน สเกลประมาณเท่าไร</td></tr>
  <tr><td>แผนที่ภาพที่ทับกัน</td><td>สีแบบรูป 7</td></tr>
  <tr><td>โปรแกรมหาลำดับได้อย่างไร</td><td>กดเปิดดูตารางทุกคู่: ใช้วางภาพ / ยืนยันซ้ำ / ตัดเพราะขัดกับ GPS / รอยต่อเปราะ</td></tr>
  <tr><td>ตั้งค่า (ปกติไม่ต้องแตะ)</td><td>ปิดการต่ออัตโนมัติ หรือปรับเกณฑ์จุดที่ตรงกันขั้นต่ำ</td></tr>
</table>
<p><b>วิธีเปิด:</b> ดับเบิลคลิก <code>เปิดโปรแกรมต่อภาพ.bat</code> ในโฟลเดอร์ <code>05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23/</code> · เครื่องต้องมี Python กับ <code>opencv-python</code> และ <code>numpy</code> · ปิดหน้าต่างดำเมื่อเลิกใช้</p>
<div class="box green"><b class="t">ภาพไม่ออกนอกเครื่อง</b>หน้าเว็บกับตัวคำนวณรันในเครื่องตัวเอง (ที่อยู่ 127.0.0.1) ตรงตามกฎของโครงงานที่ห้ามส่งภาพไปบริการภายนอก</div>

<h2><span class="n">7</span>ยังทำอะไรไม่ได้ (บอกอาจารย์ตรงๆ)</h2>
<table>
  <tr><th style="width:34%">ข้อจำกัด</th><th>รายละเอียด</th></tr>
  <tr><td>ไม่มี GPS = ไม่มีตัวกันคู่หลอก</td><td>ถ้าลายบนผิวซ้ำและภาพซ้อนกันน้อย โปรแกรมต่อผิดได้ ทำได้แค่เตือนรอยต่อที่เสี่ยง</td></tr>
  <tr><td>ตัวตรวจ GPS ทดสอบกับภาพชุดเดียว</td><td>โดรน Mini 3 Pro บินข้างคานในที่โล่ง ยังไม่รู้ว่าใต้สะพานจริง หรือกับ Matrice 4E พิกัดจะนิ่งแบบนี้ไหม</td></tr>
  <tr><td>ไม่รู้ว่าภาพเป็นชิ้นส่วนไหน</td><td>ภาพที่ต่อกันได้ถูกรวมเป็นผืนเดียว ผู้ใช้ยังต้องแยกภาพตามชิ้นส่วนก่อนใส่ (ตามบันทึกการบินใน 3.3.4)</td></tr>
  <tr><td>ถ่ายคนละมุม รอยต่อเหลื่อม</td><td>โปรแกรมถือว่าผิวเป็นระนาบและกล้องหันทิศเดิม ตอนรวมสองรอบบินที่มุมต่างกัน ~10° รอยต่อคลาดสูงสุด {J["resid34"][1]:.0f} px</td></tr>
  <tr><td>ยังวัดขนาดจริงไม่ได้</td><td>สเกลจาก GPS เป็นค่าประมาณ ต้องใช้เลเซอร์ 4 จุดตามหัวข้อ 3.6</td></tr>
  <tr><td>ยังไม่ได้ลอง</td><td>ผิวคอนกรีตเรียบสะอาด · ภาพชุดเดิมของโครงการ (rawdata) · ภาพมากกว่า 34 ใบ</td></tr>
</table>
<div class="box red"><b class="t">แก้ข้อความในฉบับก่อน</b>
ฉบับบ่ายเขียนว่าผืนเอียง "ทั้งที่คานจริงตรง" — <b>ข้อนี้ไม่ได้ตรวจและผิดเป็นส่วนใหญ่</b> ความสูงที่ฝังในภาพบอกว่าโดรนไต่ขึ้นจริง {g21["yalt"]:.2f} ม. ตลอดแนว (รูป 6) ผืนจึงเอียงตามจริงเป็นหลัก รุ่นก่อน (ต่อเป็นลูกโซ่) ให้ผืนสูงต่างกัน 1.55 ม. คือเกินจริงราว 0.5 ม. รุ่นนี้ได้ {g21["ymos"]:.2f} ม. · ยังบอกไม่ได้ว่าโดรนไต่ขึ้นเพราะคานลาดจริงหรือเพราะนักบิน</div>

<h3>คำที่ใช้</h3>
<table>
  <tr><td style="width:24%"><b>จุดเด่น / SIFT</b></td><td>ตำแหน่งในภาพที่หน้าตาไม่ซ้ำ จำได้ และวิธีมาตรฐานที่ใช้หา</td></tr>
  <tr><td><b>RANSAC</b></td><td>วิธีสุ่มแล้วโหวต เพื่อทิ้งคู่จุดที่จับผิด</td></tr>
  <tr><td><b>คู่หลอก</b></td><td>สองภาพที่จุดตรงกันมากพอจะผ่านเกณฑ์ ทั้งที่ไม่ได้ถ่ายบริเวณเดียวกัน</td></tr>
  <tr><td><b>รอบบิน</b></td><td>ภาพที่ถ่ายต่อเนื่องกัน ห่างกันไม่เกิน 5 นาที</td></tr>
  <tr><td><b>รอยต่อเปราะ</b></td><td>จุดที่ผืนต่อกันด้วยคู่ภาพคู่เดียว และคู่นั้นมั่นใจต่ำ ไม่มีคู่อื่นช่วยยืนยัน</td></tr>
</table>

<h3>แหล่งอ้างอิง (เปิดอ่านต้นฉบับแล้วทุกรายการ)</h3>
<ul class="src">
  <li>Brown, M. and Lowe, D. (2007). Automatic Panoramic Image Stitching using Invariant Features. IJCV. https://www.cs.ubc.ca/~lowe/papers/07brown.pdf</li>
  <li>OpenCV stitching module (ซอร์สสาขา 4.x). https://github.com/opencv/opencv/tree/4.x/modules/stitching/src</li>
  <li>OpenSfM. https://opensfm.readthedocs.io/en/latest/using.html · OpenDroneMap. https://docs.opendronemap.org/arguments/matcher-neighbors/</li>
  <li>COLMAP Tutorial. https://colmap.github.io/tutorial.html · Agisoft Metashape Pro 2.1 User Manual หน้า 39. https://www.agisoft.com/pdf/metashape-pro_2_1_en.pdf</li>
  <li>ExifTool GPS Tags. https://exiftool.org/TagNames/GPS.html</li>
</ul>

</body>
</html>
'''
mask = '--mask' in sys.argv
if mask:
    html = html.replace('</style>', '  img { filter: brightness(0) !important; }\n</style>')
out = os.path.join(HERE, 'สรุป_mask.html' if mask else 'สรุป.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html))
