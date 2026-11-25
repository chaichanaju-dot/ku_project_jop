# วิธีสร้างใหม่: python สร้างการ์ตูน.py  → ได้ cartoon.html แล้วพิมพ์เป็น PDF ด้วย Edge:
#   msedge --headless=new --no-pdf-header-footer --virtual-time-budget=8000 --print-to-pdf=สรุปการ์ตูน_ต่อภาพโดรน.pdf file:///<path>/cartoon.html
# ต้องมีโฟลเดอร์ fonts/ (Mali, OFL) และ _cartoon.css ของ repo (ดูตัวแปร BASE_CSS) · แก้ข้อความ/ภาพที่ฟังก์ชัน page1..page7 ด้านล่าง
# สร้างการ์ตูนสรุป "ต่อภาพโดรน" (A4 แนวตั้ง) — สไตล์เดียวกับ _cartoon.css ของการ์ตูนเตรียมประชุม
# ภาพทั้งหมดวาดเอง (SVG) ไม่มีภาพถ่ายจริง · ตัวเลขทั้งหมดมาจาก numbers.json / numbers2.json ของเอกสารสรุป
import json, os, sys, random

HERE = os.path.dirname(os.path.abspath(__file__))
J = json.load(open(os.path.join(HERE, 'numbers.json'), encoding='utf-8'))
K = json.load(open(os.path.join(HERE, 'numbers2.json'), encoding='utf-8'))
BASE_CSS = open(r'D:/00mk/เสาพัง/ku_project_jop/02_สรุปและบันทึกประกอบการเขียน/2_บันทึกการตัดสินใจและโน้ตเขียนเล่ม/การ์ตูน_เตรียมประชุม/_cartoon.css', encoding='utf-8').read()

INK = '#1f2430'
S21, C21, G21 = J['stats21'], J['check21'], J['gps21']
S34 = J['stats34']
T13N = J['t13nometa']

# ---------------------------------------------------------------- ตัวละคร (symbol)
SYMBOLS = f'''
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
<symbol id="drone" viewBox="0 0 140 104">
 <g stroke="{INK}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">
  <path d="M40 42 L18 28 M100 42 L122 28" fill="none" stroke-width="4"/>
  <path d="M18 28 L18 22 M122 28 L122 22" fill="none"/>
  <ellipse cx="18" cy="19" rx="17" ry="4.5" fill="#fff"/><ellipse cx="122" cy="19" rx="17" ry="4.5" fill="#fff"/>
  <path d="M47 80 L44 96 M93 80 L96 96" fill="none"/>
  <rect x="34" y="34" width="72" height="46" rx="21" fill="#ffd84d"/>
  <ellipse cx="55" cy="55" rx="5.6" ry="7.2" fill="{INK}" stroke="none"/><ellipse cx="85" cy="55" rx="5.6" ry="7.2" fill="{INK}" stroke="none"/>
  <circle cx="57" cy="52" r="2.1" fill="#fff" stroke="none"/><circle cx="87" cy="52" r="2.1" fill="#fff" stroke="none"/>
  <path d="M63 66 Q70 73 77 66" fill="none"/>
  <circle cx="45" cy="66" r="4.6" fill="#ff9d9d" stroke="none"/><circle cx="95" cy="66" r="4.6" fill="#ff9d9d" stroke="none"/>
  <circle cx="70" cy="88" r="11" fill="#2b2f3a"/><circle cx="70" cy="88" r="5.4" fill="#6ec1ff" stroke="none"/><circle cx="68" cy="86" r="1.7" fill="#fff" stroke="none"/>
 </g>
</symbol>
<symbol id="puzzle" viewBox="0 0 130 128">
 <g stroke="{INK}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">
  <path d="M33 104 V116 M83 104 V116" fill="none"/>
  <ellipse cx="31" cy="119" rx="10" ry="4.5" fill="{INK}" stroke="none"/><ellipse cx="85" cy="119" rx="10" ry="4.5" fill="{INK}" stroke="none"/>
  <g transform="translate(8 14)">
   <path d="M10 20 L40 20 C40 8 34 -2 50 -2 C66 -2 60 8 60 20 L90 20 L90 40 C102 40 112 34 112 50 C112 66 102 60 90 60 L90 90 L60 90 C60 78 66 68 50 68 C34 68 40 78 40 90 L10 90 L10 60 C22 60 32 66 32 50 C32 34 22 40 10 40 Z" fill="#8ec5ff"/>
   <ellipse cx="47" cy="44" rx="4.6" ry="6" fill="{INK}" stroke="none"/><ellipse cx="70" cy="44" rx="4.6" ry="6" fill="{INK}" stroke="none"/>
   <circle cx="48.6" cy="41.5" r="1.8" fill="#fff" stroke="none"/><circle cx="71.6" cy="41.5" r="1.8" fill="#fff" stroke="none"/>
   <path d="M51 56 Q58.5 63 66 56" fill="none"/>
   <circle cx="40" cy="55" r="4" fill="#ff9d9d" stroke="none"/><circle cx="77" cy="55" r="4" fill="#ff9d9d" stroke="none"/>
  </g>
 </g>
</symbol>
<symbol id="gps" viewBox="0 0 170 130">
 <g stroke="{INK}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">
  <rect x="4" y="52" width="46" height="30" rx="3" fill="#5aa9ff"/><path d="M19 52 V82 M35 52 V82 M4 67 H50" fill="none" stroke-width="2"/>
  <rect x="120" y="52" width="46" height="30" rx="3" fill="#5aa9ff"/><path d="M135 52 V82 M151 52 V82 M120 67 H166" fill="none" stroke-width="2"/>
  <path d="M50 67 H58 M112 67 H120" fill="none" stroke-width="4"/>
  <circle cx="85" cy="68" r="30" fill="#e9eef7"/>
  <path d="M57 56 Q85 14 113 56 Q85 47 57 56 Z" fill="#b07a4a"/>
  <path d="M63 55 L107 55 L101 63 L69 63 Z" fill="#8f5f36"/><circle cx="85" cy="31" r="4" fill="#8f5f36"/>
  <ellipse cx="75" cy="76" rx="3.4" ry="4.4" fill="{INK}" stroke="none"/><ellipse cx="96" cy="76" rx="3.4" ry="4.4" fill="{INK}" stroke="none"/>
  <path d="M77 88 Q85 92 94 86" fill="none"/>
  <rect x="66" y="99" width="38" height="17" rx="6" fill="#ffd84d"/>
  <text x="85" y="112" font-size="12" font-weight="700" text-anchor="middle" fill="{INK}" stroke="none" font-family="Mali, sans-serif">GPS</text>
 </g>
</symbol>
<symbol id="eng" viewBox="0 0 90 124">
 <g stroke="{INK}" stroke-width="3.2" stroke-linejoin="round" stroke-linecap="round">
  <path d="M35 104 V117 M55 104 V117" fill="none"/>
  <ellipse cx="33" cy="120" rx="8" ry="3.6" fill="{INK}" stroke="none"/><ellipse cx="57" cy="120" rx="8" ry="3.6" fill="{INK}" stroke="none"/>
  <rect x="20" y="64" width="50" height="42" rx="12" fill="#ff9f43"/>
  <path d="M33 66 V104 M57 66 V104" stroke="#fff" stroke-width="4" fill="none"/>
  <circle cx="45" cy="42" r="25" fill="#ffd9b3"/>
  <path d="M19 40 A26 26 0 0 1 71 40 Z" fill="#ffd84d"/><rect x="14" y="38" width="62" height="8" rx="4" fill="#ffc107"/><rect x="39" y="11" width="12" height="9" rx="3" fill="#ffc107"/>
  <circle cx="36" cy="54" r="3" fill="{INK}" stroke="none"/><circle cx="54" cy="54" r="3" fill="{INK}" stroke="none"/>
  <path d="M38 62 Q45 68 52 62" fill="none"/>
 </g>
</symbol>
</defs></svg>
'''


def use(sym, x, y, w, h=None, flip=False, extra=''):
    h = h if h is not None else w
    tf = f' transform="translate({x + w} {y}) scale(-1 1)"' if flip else ''
    xx = 0 if flip else x
    yy = 0 if flip else y
    return f'<use href="#{sym}" x="{xx}" y="{yy}" width="{w}" height="{h}"{tf}{extra}/>'


# ---------------------------------------------------------------- ภาพถ่ายการ์ตูน (วาดเอง)
def photo(x, y, w, h, rot=0, feats=(), label=None, shade='#dcd1bd', stripes=False, glow=None, dash=False, op=1):
    """กรอบภาพถ่ายที่วาดเอง · feats = [(ชนิด, rx, ry), ...] ตำแหน่งสัมพัทธ์ 0..1 ในภาพ"""
    ix, iy, iw, ih = 6, 6, w - 12, h - 12
    g = [f'<g transform="translate({x} {y}) rotate({rot} {w / 2} {h / 2})" opacity="{op}">']
    if not dash:
        g.append(f'<rect x="4" y="4" width="{w}" height="{h}" rx="5" fill="{INK}"/>')
    g.append(f'<rect x="0" y="0" width="{w}" height="{h}" rx="5" fill="#fff" stroke="{INK}" stroke-width="3"' + (' stroke-dasharray="9 6"' if dash else '') + '/>')
    g.append(f'<rect x="{ix}" y="{iy}" width="{iw}" height="{ih}" fill="{shade}" stroke="{INK}" stroke-width="1.5"/>')
    g.append(f'<clipPath id="c{abs(hash((x, y, w, rot, label))) % 10**8}"><rect x="{ix}" y="{iy}" width="{iw}" height="{ih}"/></clipPath>')
    cid = f'c{abs(hash((x, y, w, rot, label))) % 10**8}'
    g.append(f'<g clip-path="url(#{cid})">')
    if stripes:
        n = 9
        for i in range(n):
            xx = ix + iw * (i + 0.5) / n
            g.append(f'<path d="M{xx:.1f} {iy} V{iy + ih}" stroke="#9c8c72" stroke-width="3" opacity=".75"/>')
    else:
        for i, fx in enumerate((0.18, 0.46, 0.83)):
            xx = ix + iw * fx
            g.append(f'<path d="M{xx:.1f} {iy} q{4 if i % 2 else -4} {ih * 0.3:.1f} 0 {ih * 0.55:.1f} t{3 if i % 2 else -3} {ih * 0.45:.1f}" fill="none" stroke="#9c8c72" stroke-width="2.4" opacity=".55"/>')
    for k, rx, ry in feats:
        cx, cy = ix + iw * rx, iy + ih * ry
        if k == 'sticker':
            r = min(iw, ih) * 0.085
            g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="#ff7a2f" stroke="{INK}" stroke-width="2"/><circle cx="{cx - r * .3:.1f}" cy="{cy - r * .3:.1f}" r="{r * .22:.1f}" fill="#fff" stroke="none"/>')
        elif k == 'tape':
            g.append(f'<rect x="{cx - iw * .035:.1f}" y="{cy - ih * .1:.1f}" width="{iw * .07:.1f}" height="{ih * .2:.1f}" fill="#6ed98a" stroke="{INK}" stroke-width="2"/>')
        elif k == 'plate':
            g.append(f'<rect x="{cx - iw * .09:.1f}" y="{cy - ih * .05:.1f}" width="{iw * .18:.1f}" height="{ih * .1:.1f}" rx="2" fill="#b9bec7" stroke="{INK}" stroke-width="2"/><path d="M{cx - iw * .06:.1f} {cy:.1f} h{iw * .12:.1f}" stroke="{INK}" stroke-width="1.5"/>')
        elif k == 'crack':
            a = ih * 0.16
            g.append(f'<path d="M{cx - iw * .12:.1f} {cy - a:.1f} l{iw * .07:.1f} {a * .9:.1f} l-{iw * .03:.1f} {a * .5:.1f} l{iw * .08:.1f} {a * .8:.1f} l{iw * .06:.1f} {a * .5:.1f}" fill="none" stroke="{INK}" stroke-width="3.4" stroke-linejoin="round"/>')
        elif k == 'stain':
            g.append(f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{iw * .12:.1f}" ry="{ih * .16:.1f}" fill="#7a6a52" opacity=".55"/>')
        elif k == 'patch':
            g.append(f'<path d="M{cx - iw * .1:.1f} {cy + ih * .12:.1f} q{iw * .02:.1f} -{ih * .28:.1f} {iw * .12:.1f} -{ih * .2:.1f} q{iw * .1:.1f} {ih * .1:.1f} {iw * .02:.1f} {ih * .22:.1f} z" fill="#f2eee4" stroke="{INK}" stroke-width="1.8"/>')
    g.append('</g>')
    if glow:
        g.append(f'<rect x="-3" y="-3" width="{w + 6}" height="{h + 6}" rx="8" fill="none" stroke="{glow}" stroke-width="5"/>')
    if label:
        g.append(f'<text x="{w / 2}" y="{h + 17}" font-size="12.5" font-weight="600" text-anchor="middle" fill="{INK}" font-family="Mali, sans-serif">{label}</text>')
    g.append('</g>')
    return ''.join(g)


def beam(x, y, w, h=46, cracks=()):
    g = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#cfc6b4" stroke="{INK}" stroke-width="3.2"/>',
         f'<rect x="{x}" y="{y + h - 12}" width="{w}" height="12" rx="4" fill="#b9ae98" stroke="{INK}" stroke-width="3.2"/>']
    for cx in cracks:
        g.append(f'<path d="M{cx} {y + 4} l5 12 l-4 8 l6 12" fill="none" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
    return ''.join(g)


def pier(x, y, w, h):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#bfb6a3" stroke="{INK}" stroke-width="3.2"/>'


def water(x, y, w, h):
    waves = ''.join(f'<path d="M{x + i * 60} {y + 18} q15 -14 30 0 t30 0" fill="none" stroke="#6aa6d8" stroke-width="3"/>' for i in range(int(w / 60) + 1))
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#cfe7f7"/>' + waves


def arrow(x1, y1, x2, y2, col=INK, wd=5, head=14):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx1, hy1 = x2 - head * math.cos(a - 0.5), y2 - head * math.sin(a - 0.5)
    hx2, hy2 = x2 - head * math.cos(a + 0.5), y2 - head * math.sin(a + 0.5)
    return (f'<path d="M{x1} {y1} L{x2 - 3 * math.cos(a):.1f} {y2 - 3 * math.sin(a):.1f}" stroke="{col}" stroke-width="{wd}" stroke-linecap="round" fill="none"/>'
            f'<path d="M{x2} {y2} L{hx1:.1f} {hy1:.1f} L{hx2:.1f} {hy2:.1f} Z" fill="{col}" stroke="{col}" stroke-width="2" stroke-linejoin="round"/>')


def txt(x, y, s, size=16, col=INK, w=700, anchor='middle', rot=0):
    tr = f' transform="rotate({rot} {x} {y})"' if rot else ''
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{w}" fill="{col}" text-anchor="{anchor}" font-family="Mali, sans-serif"{tr}>{s}</text>'


def spark(x, y, r=10, col='#ffd84d'):
    return f'<path d="M{x} {y - r} L{x + r * .3} {y - r * .3} L{x + r} {y} L{x + r * .3} {y + r * .3} L{x} {y + r} L{x - r * .3} {y + r * .3} L{x - r} {y} L{x - r * .3} {y - r * .3} Z" fill="{col}" stroke="{INK}" stroke-width="2" stroke-linejoin="round"/>'


def icon_pin(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 28 C-14 10 -14 -4 0 -4 C14 -4 14 10 0 28 Z" fill="#ff6b6b" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="6" r="4.5" fill="#fff" stroke="{INK}" stroke-width="2"/></g>')


def icon_clock(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><circle cx="0" cy="0" r="15" fill="#fff" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M0 -9 V0 L7 5" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round"/></g>')


def icon_file(x, y, s=1.0, label='IMG'):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-12 -16 H4 L12 -8 V16 H-12 Z" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M4 -16 V-8 H12" fill="none" stroke="{INK}" stroke-width="2.5"/>'
            f'<text x="0" y="9" font-size="8" font-weight="700" text-anchor="middle" fill="{INK}" font-family="Mali, sans-serif">{label}</text></g>')


def icon_eye(x, y, s=1.0):
    return (f'<g transform="translate({x} {y}) scale({s})"><path d="M-17 0 Q0 -16 17 0 Q0 16 -17 0 Z" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="0" r="6.5" fill="{INK}"/><circle cx="2" cy="-2" r="2" fill="#fff"/></g>')


def magnifier(x, y, s=1.0, rot=0):
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})"><circle cx="0" cy="0" r="16" fill="#fff" fill-opacity=".55" stroke="{INK}" stroke-width="4"/>'
            f'<path d="M11 11 L28 28" stroke="{INK}" stroke-width="6" stroke-linecap="round"/></g>')


# ---------------------------------------------------------------- ตัวช่วย HTML
def bub(text, left, top, width, tail='down', tx=None, color='', cls=''):
    """ฟองคำพูดซ้อนบนกรอบภาพ · พิกัดเป็น % ของกรอบ"""
    style = f'left:{left}%;top:{top}%;width:{width}%;'
    if tx is not None:
        style += f'--tx:{tx}%;'
    return f'<div class="bub {tail} {color} {cls}" style="{style}">{text}</div>'


def panel(svg, bubbles='', vb=(700, 300), cls='', stickers=''):
    return f'<div class="panel {cls}"><svg viewBox="0 0 {vb[0]} {vb[1]}" xmlns="http://www.w3.org/2000/svg">{svg}</svg>{bubbles}{stickers}</div>'


def head(n, title, sub=''):
    return f'<div class="head"><div class="num">{n}</div><div class="title">{title}</div><div class="sub">{sub}</div></div>'


def foot(n):
    return f'<div class="foot"><span>ต่อภาพโดรน · ฉบับการ์ตูน · สรุปจาก PDF 2 ไฟล์</span><span>{n}</span></div>'


EXTRA_CSS = '''
@font-face { font-family: 'Mali'; font-weight: 400; src: url('fonts/Mali-Regular.ttf'); }
@font-face { font-family: 'Mali'; font-weight: 600; src: url('fonts/Mali-SemiBold.ttf'); }
@font-face { font-family: 'Mali'; font-weight: 700; src: url('fonts/Mali-Bold.ttf'); }
.panel { position: relative; border: 3px solid #1f2430; border-radius: 16px; background: #fff; box-shadow: 5px 5px 0 #1f2430; overflow: hidden; margin-bottom: 12px; }
.panel svg { display: block; width: 100%; height: auto; }
.panel.sky { background: #eaf4fb; } .panel.warm { background: #fff8e3; } .panel.mint { background: #eaf7ee; } .panel.rose { background: #fdeeee; }
.bub { position: absolute; background: #fff; border: 3px solid #1f2430; border-radius: 18px; padding: 5px 12px; font-size: 14.5px; line-height: 1.42; font-weight: 600; z-index: 3; }
.bub b { font-weight: 700; }
.bub::after { content: ''; position: absolute; width: 14px; height: 14px; background: inherit; border-right: 3px solid #1f2430; border-bottom: 3px solid #1f2430; }
.bub.down::after { left: var(--tx, 28%); bottom: -9px; transform: rotate(45deg); }
.bub.up::after { left: var(--tx, 28%); top: -9px; transform: rotate(225deg); }
.bub.left::after { left: -9px; top: var(--tx, 40%); transform: rotate(135deg); }
.bub.right::after { right: -9px; top: var(--tx, 40%); transform: rotate(-45deg); }
.bub.none::after { display: none; }
.bub.y { background: #fff3c4; } .bub.g { background: #e3f4ea; } .bub.p { background: #fde4e4; } .bub.b { background: #e8eef6; }
.bub.big { font-size: 17px; }
.sticker { position: absolute; z-index: 4; border: 3px solid #1f2430; background: #ffd84d; padding: 3px 12px; font-weight: 700; font-size: 14px; transform: rotate(-2deg); box-shadow: 3px 3px 0 #1f2430; line-height: 1.35; }
.sticker.g { background: #7fd3a0; } .sticker.r { background: #ff9d9d; } .sticker.w { background: #fff; }
.stats { display: flex; gap: 10px; margin: 0 0 12px; }
.stat { flex: 1; border: 3px solid #1f2430; border-radius: 14px; background: #fff; box-shadow: 4px 4px 0 #1f2430; text-align: center; padding: 5px 4px 6px; }
.stat .v { font-size: 27px; font-weight: 700; line-height: 1.15; }
.stat .k { font-size: 12.5px; font-weight: 600; color: #444; line-height: 1.3; }
.stat.g { background: #e3f4ea; } .stat.y { background: #fff3c4; } .stat.b { background: #e8eef6; }
.note2 { display: flex; gap: 10px; margin: 0 0 12px; }
.note2 > div { flex: 1; border: 3px solid #1f2430; border-radius: 4px; padding: 7px 11px; font-size: 14px; line-height: 1.45; font-weight: 600; background: #fff3c4; box-shadow: 4px 4px 0 #1f2430; transform: rotate(-.7deg); }
.note2 > div:nth-child(2) { background: #fde4e4; transform: rotate(.8deg); } .note2 > div:nth-child(3) { background: #e8eef6; transform: rotate(-.4deg); }
.note2 b { display: block; font-size: 15.5px; margin-bottom: 1px; }
.page { padding-bottom: 20mm; }
.cover-title { font-size: 62px; }
.cover-sub { font-size: 21px; }
.cover-tag { font-size: 14px; }
.chars { gap: 6px; margin-top: 4px; }
.chars > div { flex: 1; border: 3px solid #1f2430; border-radius: 14px; background: #fff; box-shadow: 4px 4px 0 #1f2430; padding: 6px 4px 7px; font-size: 13px; font-weight: 600; line-height: 1.3; }
.chars svg { width: 62px; height: 62px; margin-bottom: 3px; }
.chars b { display: block; font-size: 14.5px; }
.nextlist { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin: 0 0 12px; }
.nextlist > div { display: flex; gap: 9px; align-items: center; border: 3px solid #1f2430; border-radius: 14px; background: #fff; box-shadow: 4px 4px 0 #1f2430; padding: 8px 10px; font-size: 14.5px; font-weight: 600; line-height: 1.35; }
.nextlist .n { flex: none; width: 34px; height: 34px; border-radius: 50%; background: #1f2430; color: #fff; font-size: 17px; font-weight: 700; display: flex; align-items: center; justify-content: center; }
.nextlist > div:nth-child(1) { background: #e3f4ea; } .nextlist > div:nth-child(2) { background: #e8eef6; } .nextlist > div:nth-child(3) { background: #fff3c4; } .nextlist > div:nth-child(4) { background: #fde4e4; }
'''


def page(*parts, n):
    return f'<div class="page">{"".join(parts)}{foot(n)}</div>'


# @@PAGES_START@@
def long_strip(x, y, n, w=120, h=70, step=90, numbered=True, nums=None, label_y=None):
    """แถบภาพยาว = ภาพที่ต่อกันเป็นผืน (ซ้อนกัน) พร้อมเลขลำดับ"""
    g = []
    kinds = [[('sticker', .22, .5)], [('stain', .5, .5)], [('tape', .65, .5)], [('plate', .4, .6)], [('crack', .5, .5)], [('sticker', .72, .4)], [('stain', .3, .5)]]
    for i in range(n):
        g.append(photo(x + i * step, y, w, h, feats=kinds[i % len(kinds)]))
    if numbered:
        ly = label_y if label_y is not None else y + h + 22
        for i in range(n):
            lab = (nums[i] if nums else str(i + 1))
            g.append(f'<circle cx="{x + i * step + w / 2}" cy="{ly}" r="12.5" fill="{INK}"/>' + txt(x + i * step + w / 2, ly + 5.5, lab, 15, '#fff', 700))
    return ''.join(g)


def check(x, y, r=26, rot=-8):
    return (f'<g transform="translate({x} {y}) rotate({rot})"><circle r="{r}" fill="#2da562" stroke="{INK}" stroke-width="3"/>'
            f'<path d="M{-r * .46:.1f} {r * .04:.1f} l{r * .3:.1f} {r * .34:.1f} l{r * .62:.1f} {-r * .7:.1f}" fill="none" stroke="#fff" stroke-width="{r * .24:.1f}" stroke-linecap="round" stroke-linejoin="round"/></g>')


def inline_note(html_, cls='y'):
    return f'<div class="bub {cls} none" style="position:relative;display:block;margin:0 0 12px;border-radius:14px;width:auto;font-size:14.5px">{html_}</div>'


# ================================================================ หน้า 1 ปก
def cover():
    cloud = lambda x, y, s=1: (f'<g transform="translate({x} {y}) scale({s})"><path d="M0 40 q-6 -26 22 -26 q8 -26 40 -14 q30 -10 38 20 q22 2 18 20 z" fill="#fff" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/></g>')
    svg = [
        '<rect width="700" height="650" fill="#eaf4fb"/>',
        f'<circle cx="626" cy="76" r="38" fill="#ffe27a" stroke="{INK}" stroke-width="3"/>',
        cloud(430, 44, 1.1), cloud(40, 200, .9), cloud(560, 190, .8),
        water(0, 556, 700, 94), pier(150, 494, 48, 100), pier(500, 494, 48, 100),
        beam(16, 436, 668, 58, cracks=(120, 330, 580)),
        f'<path d="M300 130 C 380 80, 470 180, 570 148" fill="none" stroke="{INK}" stroke-width="3.5" stroke-dasharray="3 11" stroke-linecap="round"/>',
        arrow(552, 152, 624, 142),
    ]
    for i, (px_, col) in enumerate(((36, '#ffd84d'), (186, '#7fd3a0'), (336, '#8ec5ff'), (486, '#ffb4a2'))):
        svg.append(f'<rect x="{px_}" y="338" width="178" height="90" rx="7" fill="{col}" fill-opacity=".4" stroke="{INK}" stroke-width="2.8" stroke-dasharray="8 6"/>')
    svg += [use('drone', 64, 40, 220, 163), spark(296, 66, 12), spark(318, 106, 7), spark(272, 30, 7), txt(350, 312, 'ถ่ายหลายใบ ให้ซ้อนกัน', 19, INK, 700)]
    sc = panel(''.join(svg), vb=(700, 650), cls='sky')
    chars = """<div class="chars">
      <div><svg viewBox="0 0 140 104"><use href="#drone" width="140" height="104"/></svg><b>น้องโดรน</b>ถ่ายภาพคาน</div>
      <div><svg viewBox="0 0 130 128"><use href="#puzzle" width="130" height="128"/></svg><b>น้องจิ๊กซอว์</b>โปรแกรมต่อภาพ</div>
      <div><svg viewBox="0 0 170 130"><use href="#gps" width="170" height="130"/></svg><b>นักสืบ GPS</b>จับคู่หลอก</div>
      <div><svg viewBox="0 0 90 124"><use href="#eng" width="90" height="124"/></svg><b>วิศวกร</b>นับรอยร้าว</div>
    </div>"""
    return page('<div class="cover-tag">สรุปง่ายๆ จาก PDF 2 ไฟล์ · 23 พ.ย. 2569</div>', '<h1 class="cover-title">ต่อภาพโดรน</h1>',
                '<div class="cover-sub">ใส่ภาพมั่วๆ → ได้ภาพยาวผืนเดียว</div>', sc, chars, n=1)


# ================================================================ หน้า 2 ทำไมต้องต่อภาพ
def page2():
    s1 = [beam(-10, 150, 720, 56, cracks=(90, 260, 430, 600)), pier(120, 206, 46, 52), pier(520, 206, 46, 52),
          photo(30, 44, 170, 102, feats=[('crack', .5, .5)]), use('drone', 540, 16, 130, 97), spark(690, 20, 7),
          txt(420, 138, '… คานยาวมาก …', 17, '#7a6a52', 600)]
    p1 = panel(''.join(s1), vb=(700, 262), cls='warm', bubbles=bub('คานยาวจัง! ถ่ายใบเดียวเห็นแค่<b>นิดเดียว</b>', 31, 7, 47, 'right', 42, 'y'))
    s2 = [beam(-10, 176, 720, 56, cracks=(90, 260, 430, 600)), pier(120, 232, 46, 44), pier(520, 232, 46, 44)]
    xs = (30, 190, 350, 510)
    for i, px_ in enumerate(xs):
        s2.append(f'<rect x="{px_}" y="80" width="170" height="96" rx="6" fill="{["#ffd84d", "#7fd3a0", "#8ec5ff", "#ffb4a2"][i]}" fill-opacity=".42" stroke="{INK}" stroke-width="3" stroke-dasharray="8 6"/>')
    for px_ in (190, 350, 510):
        s2.append(f'<rect x="{px_}" y="80" width="10" height="96" fill="#ff6b6b" fill-opacity=".75"/>' + txt(px_ + 5, 73, 'ซ้อน', 14, '#c0392b', 700))
    s2.append(use('drone', 590, 2, 92, 68))
    p2 = panel(''.join(s2), vb=(700, 276), cls='sky', bubbles=bub('ถ่ายหลายใบ แต่ต้องให้<b>ซ้อนกัน</b>หน่อย ไม่งั้นมี<b>ช่องว่าง</b>', 3, 3, 74, 'none', None, 'y'))
    s3 = [photo(36, 44, 220, 132, feats=[('crack', .8, .5), ('sticker', .3, .35)]),
          photo(188, 72, 220, 132, feats=[('crack', .2, .5)]),
          '<rect x="194" y="78" width="64" height="120" fill="#ff6b6b" fill-opacity=".28" stroke="#c0392b" stroke-width="2.5" stroke-dasharray="5 4"/>',
          use('eng', 540, 76, 100, 138)]
    s3.append(f'<g transform="translate(450 92)"><rect x="0" y="0" width="68" height="50" rx="4" fill="#fff" stroke="{INK}" stroke-width="3"/><path d="M14 14 V36 M28 14 V36" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/><path d="M42 25 h16" stroke="#aaa" stroke-width="3"/></g>')
    p3 = panel(''.join(s3), vb=(700, 262), cls='rose',
               bubbles=bub('รอยร้าว <b>2 รอย</b>!', 66, 5, 28, 'down', 54, 'p') + bub('ไม่ใช่นะ! ใบ ก กับ ใบ ข ถ่าย<b>รอยเดียวกัน</b>', 4, 82, 58, 'up', 50, 'y'))
    stk = f"""<div class="stats">
      <div class="stat y"><div class="v">{J["dup21"]:.2f} เท่า</div><div class="k">ชุดทดสอบ: แต่ละจุดถูกถ่ายซ้ำเฉลี่ยขนาดนี้<br>ถ้านับทีละใบ = นับซ้ำ</div></div>
      <div class="stat g"><div class="v">ต่อก่อน นับทีหลัง</div><div class="k">ต่อภาพเป็นผืนเดียวก่อน<br>แล้วค่อยนับความเสียหาย</div></div></div>"""
    return page(head(1, 'ทำไมต้องต่อภาพ?', 'คานยาว ถ่ายใบเดียวไม่พอ'), p1, p2, p3, stk, n=2)


# ================================================================ หน้า 3 โจทย์ + คนอื่นทำยังไง
def flow_panel(n_strip, nums=None, ok=False, labels=True, bubbles='', cls='warm', vb_h=372):
    names = ('IMG_9863', 'IMG_0434', 'IMG_3257', 'IMG_8279')
    s = [photo(24, 78, 110, 72, rot=-7, feats=[('sticker', .6, .5)], label=names[0] if labels else None),
         photo(150, 60, 110, 72, rot=5, feats=[('stain', .5, .4)], label=names[2] if labels else None),
         photo(36, 172, 110, 72, rot=4, feats=[('tape', .5, .5)], label=names[1] if labels else None),
         photo(160, 156, 110, 72, rot=-5, feats=[('plate', .5, .5)], label=names[3] if labels else None),
         arrow(282, 150, 326, 150, INK, 6, 16), use('puzzle', 334, 70, 120, 117), spark(462, 78, 9), spark(338, 62, 6),
         arrow(394, 196, 394, 258, INK, 6, 16),
         long_strip(20, 268, 7, 120, 70, 90, True, nums, label_y=355)]
    if ok:
        s.append(check(600, 150, 30))
    return panel(''.join(s), vb=(700, vb_h), cls=cls, bubbles=bubbles)


def page3():
    top = flow_panel(7, bubbles=bub('โยนมาเลย! <b>ไม่ต้องเรียง</b><br>ชื่อไฟล์ก็มั่ว', 2, 2, 36, 'none', None, 'y')
                     + bub('ใบไหนอยู่ติดกันนะ…?', 40, 4, 30, 'down', 40, 'b')
                     + bub('ได้<b>ภาพยาวผืนเดียว</b>!', 61, 52, 36, 'none', None, 'g'))
    s2 = []
    for name, x in (('OpenCV', 20), ('OpenSfM', 186), ('COLMAP', 352), ('Metashape', 518)):
        s2.append(f'<rect x="{x}" y="20" width="162" height="100" rx="14" fill="#fff" stroke="{INK}" stroke-width="3"/>')
        s2.append(txt(x + 81, 52, name, 18, INK, 700)); s2.append(icon_eye(x + 81, 88, 1.7))
    s2.append(txt(350, 150, 'ตัดสินจาก “หน้าตาของภาพ” ทุกเจ้า', 18, '#c0392b', 700))
    s2.append('<path d="M20 172 H680" stroke="#bdb6a4" stroke-width="2.5" stroke-dasharray="6 6"/>')
    s2 += [icon_pin(60, 190, 1.4), icon_clock(190, 210, 1.4), icon_file(318, 210, 1.4, 'IMG')]
    s2 += [txt(430, 204, 'ส่วน GPS / เวลา / ชื่อไฟล์', 16, INK, 600, 'start'), txt(430, 228, '= ตัวช่วยเลือกคู่ให้ลองเร็วขึ้น', 16, INK, 700, 'start')]
    bot = panel(''.join(s2), vb=(700, 244), cls='sky')
    # ทดลองเอง: ปรับเกณฑ์ของ OpenCV (ผืนกว้างกี่ px)
    rows = (('1.0 (ค่าตั้งต้น)', 4128, '#ff9d9d', '4,128 px — ได้แค่บางส่วน'), ('0.7', 14607, '#7fd3a0', '14,607 px'), ('0.5', 14288, '#7fd3a0', '14,288 px'),
            ('0.3', 4099, '#ffe27a', '4,099 px — ผืนผิดปกติ'), ('0.1', 0, '#ff9d9d', 'ล้มเหลว (error)'))
    s3 = []
    for i, (lab, wpx, col, note_) in enumerate(rows):
        y = 52 + i * 34
        s3.append(txt(22, y + 18, f'เกณฑ์ {lab}', 14.5, INK, 600, 'start'))
        bw = max(wpx * 0.0222, 0)
        if bw:
            s3.append(f'<rect x="200" y="{y}" width="{bw:.0f}" height="24" rx="5" fill="{col}" stroke="{INK}" stroke-width="2.6"/>')
        else:
            s3.append(f'<path d="M204 {y + 4} l16 16 m0 -16 l-16 16" stroke="#e03131" stroke-width="4" stroke-linecap="round"/>')
        s3.append(txt(200 + bw + 10 if bw else 232, y + 18, note_, 14, INK, 700, 'start'))
    bar = panel(''.join(s3), vb=(700, 226), cls='warm', bubbles='<div class="sticker" style="left:2%;top:3%">ทดลองเอง: ปรับเกณฑ์ของ OpenCV (ชุด 21 ภาพ)</div>')
    return page(head(2, 'โจทย์ของเรา + คนอื่นเขาทำยังไง', 'ไปค้นเน็ตมาแล้ว'), top, '<div class="tag" style="margin:2px 0 6px">ไปแอบดูคนอื่นเขาทำ</div>', bot, bar, n=3)


# ================================================================ หน้า 4 วิธีของเรา
def page4():
    s1 = [photo(36, 40, 320, 180, feats=[('sticker', .72, .4), ('tape', .32, .6), ('plate', .55, .78), ('patch', .2, .32), ('stain', .85, .78)])]
    for cx, cy, r in ((264, 113, 24), (141, 147, 22), (211, 177, 24), (104, 100, 28)):
        s1.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e03131" stroke-width="4.5"/>')
    s1 += [use('puzzle', 462, 104, 120, 117), magnifier(606, 196, 1.3, 0), spark(620, 112, 9), txt(196, 246, 'วงแดง = “จุดสังเกต” ที่จำได้', 15.5, '#c0392b', 700)]
    p1 = panel(''.join(s1), vb=(700, 262), cls='warm',
               bubbles=bub('มีจุดสังเกตเยอะ = <b>จำง่าย</b>!<br>ผิวเรียบๆ ไม่มีอะไรเลย = ต่อยาก', 52, 4, 46, 'down', 36, 'y') + '<div class="sticker" style="left:2%;top:3%">① หา “จุดสังเกต”</div>')
    A = photo(24, 66, 210, 130, feats=[('sticker', .86, .3), ('stain', .8, .75), ('tape', .6, .5)])
    B = photo(300, 66, 210, 130, feats=[('sticker', .14, .3), ('stain', .06, .75), ('tape', -.2, .5)])

    def pt(px_, w, rx, ry, py_=66, h=130):
        return px_ + 6 + (w - 12) * rx, py_ + 6 + (h - 12) * ry
    s2 = [A, B]
    for (ra, rb) in ((('sticker', .86, .3), ('sticker', .14, .3)), (('stain', .8, .75), ('stain', .06, .75))):
        x1, y1 = pt(24, 210, ra[1], ra[2]); x2, y2 = pt(300, 210, rb[1], rb[2])
        s2.append(f'<path d="M{x1:.0f} {y1:.0f} L{x2:.0f} {y2:.0f}" stroke="#e03131" stroke-width="3.6" stroke-dasharray="7 5"/>')
    s2 += [use('puzzle', 556, 66, 110, 107), spark(668, 58, 8)]
    p2 = panel(''.join(s2), vb=(700, 250), cls='sky',
               bubbles=bub('จุดนี้<b>เหมือนกัน</b>เป๊ะ → สองใบนี้<b>ติดกัน</b>!', 50, 3, 47, 'none', None, 'g')
               + '<div class="sticker" style="left:2%;top:3%">② จับคู่ “ทุกใบกับทุกใบ”</div>'
               + f'<div class="sticker w" style="right:3%;bottom:4%;transform:rotate(1.5deg)">{S34["images"]} ใบ = {S34["pairs_total"]} คู่ · ใช้เวลา ~1 วินาที</div>')
    s3 = [long_strip(20, 92, 7, 120, 70, 90, True, label_y=190), use('puzzle', 578, 0, 92, 89)]
    p3 = panel(''.join(s3), vb=(700, 214), cls='mint',
               bubbles=bub('วางเรียงตามจุดที่ตรงกัน → <b>ตำแหน่งบนผืน = ลำดับของภาพ</b>', 2, 16, 66, 'none', None, 'y') + '<div class="sticker" style="left:2%;top:3%">③ วางเรียงเป็นผืน</div>')
    badge = """<div class="stats"><div class="stat b"><div class="v">ไม่ใช้ AI</div><div class="k">ใช้วิธีคำนวณ (SIFT + RANSAC)</div></div>
      <div class="stat b"><div class="v">ไม่ต่อเน็ต</div><div class="k">รันในเครื่อง ภาพไม่ออกไปไหน</div></div></div>"""
    return page(head(3, 'วิธีของเรา (3 ขั้น)', 'น้องจิ๊กซอว์ทำงาน'), p1, p2, p3, badge, n=4)


# ================================================================ หน้า 5 คู่หลอก
def page5():
    sa = [photo(40, 58, 240, 140, stripes=True), photo(420, 58, 240, 140, stripes=True),
          '<path d="M280 86 L420 86 M280 118 L420 118 M280 150 L420 150" stroke="#e03131" stroke-width="3.4" stroke-dasharray="7 5"/>', use('puzzle', 300, 0, 100, 98)]
    pa = panel(''.join(sa), vb=(700, 262), cls='rose',
               bubbles=bub('ลายเหมือนกันเลย! ต่อกันแน่ๆ ✓', 5, 80, 40, 'up', 78, 'p') + '<div class="sticker r" style="left:2%;top:3%">เจอ “คู่หลอก”</div>'
               + '<div class="sticker w" style="right:3%;bottom:7%;text-align:center">ต้นเหตุน่าจะเป็นลายซ้ำๆ บนผิว<br>(ยังไม่ยืนยัน)</div>')

    def ruler(x, y, w):
        n = int(w / 12)
        return (f'<rect x="{x}" y="{y}" width="{w}" height="22" rx="3" fill="#fff8e3" stroke="{INK}" stroke-width="3"/>'
                + ''.join(f'<path d="M{x + 12 + i * 12} {y} v{9 if i % 2 else 14}" stroke="{INK}" stroke-width="2"/>' for i in range(n - 1)))
    sb = [use('gps', 18, 40, 176, 134), magnifier(190, 160, 1.1, 0), use('puzzle', 556, 36, 110, 107),
          ruler(262, 58, 58), txt(291, 50, 'ภาพบอก 0.37 ม.', 15.5, '#2f6fd6', 700),
          ruler(262, 112, 262), txt(393, 156, 'GPS บอก 2.2 ม.', 15.5, '#c0392b', 700)]
    pb = panel(''.join(sb), vb=(700, 270), cls='sky',
               bubbles=bub('ภาพบอกว่าห่างกันแค่ 0.37 เมตร', 59, 3, 40, 'down', 62, 'b') + bub('แต่ฉันวัดได้ <b>2.2 เมตร</b> — โกหก!', 36, 69, 34, 'up', 10, 'p')
               + '<div class="sticker r" style="right:3%;bottom:5%">คู่หลอก ✗ ตัดทิ้ง</div>' + '<div class="sticker" style="left:2%;top:3%">นักสืบ GPS มาแล้ว</div>')
    real, fake, tol = K['real'], K['fake'], K['tol']
    xm = 2.5

    def ax(v):
        return 60 + 580 * v / xm
    dots, bins = [], {}
    for v in sorted(real):
        k = int(v / 0.05); bins[k] = bins.get(k, 0) + 1
        dots.append(f'<circle cx="{ax(v):.1f}" cy="{176 - 9.2 * (bins[k] - 1):.1f}" r="4.4" fill="#2da562" stroke="{INK}" stroke-width="1.5"/>')
    for v in fake:
        dots.append(f'<path d="M{ax(v):.1f} 166 l9 9 l-9 9 l-9 -9 z" fill="#e03131" stroke="{INK}" stroke-width="2"/>')
    sc = [f'<path d="M60 188 H640" stroke="{INK}" stroke-width="3"/>'] + [f'<path d="M{ax(t)} 188 v7" stroke="{INK}" stroke-width="2.5"/>' + txt(ax(t), 212, str(t), 13, '#555', 600) for t in (0, 0.5, 1.0, 1.5, 2.0, 2.5)]
    sc += dots + [f'<path d="M{ax(tol):.1f} 70 V188" stroke="#e03131" stroke-width="3" stroke-dasharray="7 6"/>', txt(ax(tol) + 8, 84, 'เส้นตัด', 14, '#e03131', 700, 'start'),
                  txt(350, 238, 'ระยะที่ภาพบอก ต่างจาก GPS กี่เมตร (เทียบได้เฉพาะรอบบินเดียวกัน)', 13.5, INK, 600),
                  f'<circle cx="400" cy="110" r="6" fill="#2da562" stroke="{INK}" stroke-width="1.6"/>', txt(414, 115, f'คู่จริง {len(real)} คู่ (ไม่เกิน {max(real):.2f} ม.)', 14.5, INK, 600, 'start'),
                  f'<path d="M400 134 l8 8 l-8 8 l-8 -8 z" fill="#e03131" stroke="{INK}" stroke-width="2"/>', txt(414, 147, f'คู่หลอก {len(fake)} คู่ ({fake[1]:.2f} และ {fake[0]:.2f} ม.)', 14.5, INK, 600, 'start')]
    pc = panel(''.join(sc), vb=(700, 252), cls='warm', bubbles='<div class="sticker g" style="left:2%;top:3%">ผลวัดจริง (ชุด 34 ภาพ)</div>')
    rule = inline_note('<b>นักสืบ GPS แค่ “ตรวจ” ไม่ได้ “วางภาพ”</b> — ภาพชุดนี้กล้องบันทึก GPS ว่า <b>Invalid</b> และงานจริงบินใต้สะพาน GPS อาจหาย จึงไม่ให้โปรแกรมพึ่ง GPS')
    return page(head(4, 'ระวัง! คู่หลอก', 'นักสืบ GPS ช่วยตรวจ'), pa, pb, pc, rule, n=5)


# ================================================================ หน้า 6 ผลลัพธ์
def page6():
    top = flow_panel(7, nums=['1', '2', '3', '4', '5', '…', '21'], ok=True, labels=False,
                     bubbles=bub('ใส่ <b>21 ใบ</b> สลับลำดับ ชื่อไฟล์มั่ว', 2, 2, 36, 'none', None, 'y') + bub('ต่อได้<b>ผืนเดียว</b> เรียงถูกหมด!', 60, 52, 37, 'none', None, 'g'), cls='mint')
    stats = f"""<div class="stats">
      <div class="stat g"><div class="v">{S21["images"]} / {S21["images"]}</div><div class="k">เรียงลำดับถูก<br>(ทิศซ้ายขวาอาจกลับด้าน)</div></div>
      <div class="stat y"><div class="v">{J["t21"]} วินาที</div><div class="k">เวลาคำนวณ<br>บน CPU ไม่ใช้การ์ดจอ</div></div>
      <div class="stat b"><div class="v">~{C21["gps_rms_m"] * 100:.0f} ซม.</div><div class="k">ตรงกับ GPS<br>ตลอดแนว {C21["gps_span_m"]:.0f} เมตร</div></div></div>"""
    s2 = [use('puzzle', 30, 56, 100, 98)]
    for i in range(11):
        c = '#8ec5ff' if i % 3 != 1 else '#ffd84d'
        s2.append(f'<rect x="{160 + i * 44}" y="84" width="58" height="48" rx="5" fill="{c}" stroke="{INK}" stroke-width="2.6"/>')
    s2.append(check(668, 108, 22))
    s2.append(txt(350, 168, f'{S34["images"]} ใบ จาก 2 รอบบิน (สลับสีกัน) → ได้ผืนเดียว', 15.5, INK, 700, 'start'))
    mid = panel(''.join(s2), vb=(700, 190), cls='sky',
                bubbles='<div class="sticker r" style="left:2%;top:3%">รวม 2 รอบบิน</div>' + f'<div class="sticker w" style="right:2%;top:5%">นักสืบ GPS จับคู่หลอกได้ {S34["gps_rejected"]} คู่</div>')
    cols = ('#7fd3a0', '#ffe27a', '#ffb347', '#ff8a8a')
    s3 = []
    for x, w, c in ((30, 120, 0), (150, 70, 1), (220, 130, 2), (350, 90, 1), (440, 80, 0), (520, 70, 1), (590, 36, 3), (626, 44, 2)):
        s3.append(f'<rect x="{x}" y="62" width="{w}" height="42" fill="{cols[c]}" stroke="{INK}" stroke-width="2.6"/>')
    s3.append(use('eng', 32, 118, 62, 85))
    for i, (t, c) in enumerate((('ถ่ายใบเดียว', 0), ('2 ใบ', 1), ('3 ใบ', 2), ('4 ใบขึ้นไป', 3))):
        s3.append(f'<rect x="{110 + i * 140}" y="218" width="18" height="18" rx="4" fill="{cols[c]}" stroke="{INK}" stroke-width="2.4"/>' + txt(134 + i * 140, 233, t, 14, INK, 600, 'start'))
    bot = panel(''.join(s3), vb=(700, 252), cls='warm',
                bubbles='<div class="sticker" style="left:2%;top:3%">แผนที่ “ถ่ายซ้ำกี่ใบ”</div>' + bub('รู้แล้วว่าตรงไหนถูกถ่ายซ้ำ → ขั้นต่อไปค่อยนับให้<b>ครั้งเดียว</b>', 17, 50, 62, 'left', 20, 'y'))
    return page(head(5, 'ลองกับภาพจริง', 'ผลทดลอง'), top, stats, mid, bot, n=6)


# ================================================================ หน้า 7 ข้อควรระวัง + ต่อไป
def page7():
    top = panel(use('puzzle', 36, 16, 100, 98) + f'<path d="M146 30 q-8 13 0 20 q8 -7 0 -20 z" fill="#bfe3ff" stroke="{INK}" stroke-width="2.4" stroke-linejoin="round"/>', vb=(700, 126), cls='rose',
                bubbles=bub('ยังไม่ใช่ของเสร็จสมบูรณ์นะ — พูดตรงๆ 3 ข้อ', 25, 22, 60, 'left', 38, 'p', 'big'))
    notes = f"""<div class="note2">
      <div><b>ไม่มี GPS ให้ตรวจ</b>คู่หลอกหลุดได้ — ชุดทดสอบ {T13N["stats"]["images"]} ภาพ ต่อผิด 3 ภาพ โปรแกรมทำได้แค่เตือน “รอยต่อเปราะ”</div>
      <div><b>ทดลองแค่ชุดเดียว</b>โดรนรุ่นเดียว ภาพชุดเดียว ยังไม่ลองใต้สะพานจริง</div>
      <div><b>ยังวัดขนาดจริงไม่ได้</b>สเกลจาก GPS เป็นแค่ค่าประมาณ ต้องใช้เลเซอร์ 4 จุด</div></div>"""
    s2 = ['<path d="M24 216 H690" stroke="#bdb6a4" stroke-width="3" stroke-dasharray="8 7"/>', use('drone', 8, 150, 100, 74)]
    for i, (x, col, t1, t2) in enumerate(((124, '#7fd3a0', 'ชุดเดิม', '+ ผิวเรียบ'), (264, '#8ec5ff', 'ใต้สะพาน', 'จริง'), (404, '#ffd84d', 'นับรอยเดียว', 'ครั้งเดียว'), (544, '#ff9d9d', 'วัดขนาด', 'จริง'))):
        s2.append(f'<rect x="{x + 44}" y="146" width="12" height="70" fill="#b07a4a" stroke="{INK}" stroke-width="3"/>')
        s2.append(f'<path d="M{x - 6} 78 H{x + 118} L{x + 138} 108 L{x + 118} 138 H{x - 6} Z" fill="{col}" stroke="{INK}" stroke-width="3" stroke-linejoin="round"/>')
        s2.append(f'<circle cx="{x + 12}" cy="108" r="11" fill="{INK}"/>' + txt(x + 12, 113.5, str(i + 1), 14, '#fff', 700))
        s2.append(txt(x + 78, 104, t1, 14, INK, 700) + txt(x + 78, 124, t2, 14, INK, 700))
    road = panel(''.join(s2), vb=(700, 236), cls='sky', bubbles='<div class="sticker" style="left:2%;top:3%">ขั้นต่อไป (เสนอ ยังไม่ได้ตัดสิน)</div>')
    nxt = """<div class="nextlist">
      <div><span class="n">1</span><span>ลองกับภาพชุดเดิมของโครงการ และผิวคอนกรีตเรียบ</span></div>
      <div><span class="n">2</span><span>ลองใต้สะพานจริงตอนบินนำร่อง (ธ.ค.) ว่า GPS ในภาพยังนิ่งไหม</span></div>
      <div><span class="n">3</span><span>ฉายมาสก์ (ต้องมี SAM ก่อน) ลงผืน → รอยเดียวนับ<b>ครั้งเดียว</b></span></div>
      <div><span class="n">4</span><span>ถ้าต้องวัดขนาดจริง ใช้สเกลเลเซอร์ต่อภาพ แล้วค่อยรวมผืน</span></div></div>"""
    end = panel(use('drone', 16, 34, 100, 74) + use('puzzle', 120, 16, 92, 90) + use('gps', 216, 18, 140, 107) + use('eng', 364, 10, 74, 102), vb=(700, 140), cls='warm',
                bubbles=bub('จบแล้ว! ตัวเลขและที่มาอยู่ใน<br>PDF ฉบับเต็ม 2 ไฟล์', 60, 26, 38, 'left', 40, 'g'))
    return page(head(6, 'ข้อควรระวัง + ต่อไป', 'พูดตรงๆ'), top, notes, road, nxt, end, n=7)


# @@PAGES_END@@
html = f'''<!doctype html><html lang="th"><head><meta charset="utf-8"><title>ต่อภาพโดรน ฉบับการ์ตูน</title>
<style>{BASE_CSS}
{EXTRA_CSS}</style></head><body>{SYMBOLS}{cover()}{page2()}{page3()}{page4()}{page5()}{page6()}{page7()}</body></html>'''
out = os.path.join(HERE, 'cartoon.html')
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html))
