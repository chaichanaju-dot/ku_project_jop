# ตัวเลขและรูปสุดท้ายสำหรับเอกสาร (ใช้แกนตัวจริง) — พิมพ์เฉพาะตัวเลข ไม่แสดงภาพ
import sys, glob, os, importlib, json, time
import numpy as np, cv2

sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
OUT = '../doc2'
os.makedirs(OUT, exist_ok=True)


def short(f):
    return ('N' if 'Not use' in f else '') + os.path.basename(f)[4:8]


def data(files):
    loaded = [core.load(f) for f in files]
    metas = [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
    return [im for im, _ in loaded], metas, [w for _, w in loaded]


def save(name, im):
    cv2.imencode('.jpg', im, [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tofile(os.path.join(OUT, name))


P2 = sorted(glob.glob(src + '/*.JPG'))
P1 = sorted(glob.glob(src + '/Not use/*.JPG'))
J = {}

# ---------- ชุดหลัก 21 ภาพ ----------
ims, metas, ow = data(P2)
names = [short(f) for f in P2]
t0 = time.time()
res = core.stitch(ims, names, metas, orig_widths=ow)
J['t21'] = round(time.time() - t0, 1)
seg = res['segments'][0]
st = res['stats']
print('21 ภาพ:', st, '| เวลา', J['t21'], 'วิ | ผืน', seg['mosaic'].shape[1], 'x', seg['mosaic'].shape[0], '| dup %.2f' % seg['dup'])
print('  check', seg['check'])
rank = {nm: k for k, nm in enumerate(seg['names'])}
cen = {nm: (seg['T'][k] @ np.array([ims[0].shape[1] / 2, ims[0].shape[0] / 2, 1]))[:2] for k, nm in enumerate(seg['names'])}
pos = core._enu(metas)
P = np.array([p[:2] for p in pos])
alt = np.array([p[2] for p in pos])
along = (P - P.mean(0)) @ np.linalg.svd(P - P.mean(0), full_matrices=False)[2][0]
x = np.array([cen[n][0] for n in names])
y = np.array([cen[n][1] for n in names])
k, b = np.linalg.lstsq(np.c_[x, np.ones(len(x))], along, rcond=None)[0]
r = along - (k * x + b)
k2, b2 = np.linalg.lstsq(np.c_[y, np.ones(len(y))], alt, rcond=None)[0]
gsd = abs(k)
print('  แนวนอน: %.3f มม./px rms %.3f ม. max %.2f | แนวตั้ง: ช่วง y %.0f px = %.2f ม. เทียบความสูง %.2f ม. สหสัมพันธ์ %.3f' % (
    gsd * 1000, np.sqrt((r ** 2).mean()), np.abs(r).max(), np.ptp(y), np.ptp(y) * gsd, np.ptp(alt), abs(np.corrcoef(y, alt)[0, 1])))
rot = [float(np.degrees(np.arctan2(t[1, 0], t[0, 0]))) for t in seg['T']]
sc = [float(np.hypot(t[0, 0], t[1, 0])) for t in seg['T']]
print('  มุมหมุนต่อภาพ %.2f..%.2f° | สเกลต่อภาพ %.2f..%.2f' % (min(rot), max(rot), min(sc), max(sc)))
rs = [p['resid'] for p in res['pairs'] if p['ok']]
gd = [p['gps_diff'] for p in res['pairs'] if p['ok'] and p['gps_diff'] is not None]
ov = [p['overlap'] for p in res['pairs'] if p['status'] == 'tree']
print('  คลาดบนผืน px median %.1f max %.1f | ต่างจาก GPS ของคู่ที่ใช้: median %.2f max %.2f ม. | ซ้อนทับของคู่ที่ใช้วาง: %.0f–%.0f%%' % (
    np.median(rs), max(rs), np.median(gd), max(gd), min(ov) * 100, max(ov) * 100))
cover = seg['cover']
m = cover > 0
J['cover21'] = [round(100 * float(((cover == c) if c < 4 else (cover >= 4)).sum()) / m.sum(), 1) for c in (1, 2, 3, 4)]
print('  สัดส่วนผืนที่ถ่าย 1/2/3/≥4 ภาพ:', J['cover21'])
J['stats21'] = st
J['check21'] = seg['check']
J['size21'] = [int(seg['mosaic'].shape[1]), int(seg['mosaic'].shape[0])]
J['dup21'] = seg['dup']
J['nodes21'] = [dict(n=nm, pos=float((cen[nm][0] - x.min()) * gsd), gps=float(along[names.index(nm)] * (-1 if k < 0 else 1))) for nm in seg['names']]
g0 = min(d['gps'] for d in J['nodes21'])
for d in J['nodes21']:
    d['gps'] -= g0
J['edges21'] = [dict(a=rank[p['a']], b=rank[p['b']], status=p['status'], inl=p['inliers']) for p in res['pairs']]
J['alt21'] = [dict(n=nm, y=float(-(cen[nm][1] - y.mean()) * gsd), alt=float(alt[names.index(nm)] - alt.mean())) for nm in seg['names']]
J['gps21'] = dict(gsd_mm=gsd * 1000, rms=float(np.sqrt((r ** 2).mean())), ymos=float(np.ptp(y) * gsd), yalt=float(np.ptp(alt)), corr=float(abs(np.corrcoef(y, alt)[0, 1])),
                  rot=[min(rot), max(rot)], resid=[float(np.median(rs)), float(max(rs))], gpsdiff=[float(np.median(gd)), float(max(gd))])

# รูป: ผืนพร้อมลำดับ + แผนที่ภาพทับ
mo = seg['mosaic'].copy()
for kk, pts in enumerate(seg['polys']):
    cv2.polylines(mo, [np.int32(pts)], True, (255, 255, 255), 3, cv2.LINE_AA)
    cx = int(np.mean([p_[0] for p_ in pts]))
    cy = int(min(p_[1] for p_ in pts)) + 90
    for col, th in (((0, 0, 0), 14), ((255, 255, 255), 5)):
        cv2.putText(mo, str(kk + 1), (cx - 30, cy), cv2.FONT_HERSHEY_SIMPLEX, 2.6, col, th, cv2.LINE_AA)
s_ = 2400 / mo.shape[1]
save('f_mosaic.jpg', cv2.resize(mo, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA))
lut = np.array([[0, 0, 0], [94, 197, 34], [8, 204, 250], [12, 115, 249], [60, 38, 220]], np.uint8)
mix = seg['mosaic'].copy()
mix[m] = (0.45 * seg['mosaic'][m] + 0.55 * lut[np.minimum(cover, 4)][m]).astype(np.uint8)
save('f_heat.jpg', cv2.resize(mix, None, fx=s_, fy=s_, interpolation=cv2.INTER_AREA))

# ---------- สองรอบบิน 34 ภาพ ----------
ims, metas, ow = data(P2 + P1)
names = [short(f) for f in P2 + P1]
t0 = time.time()
res = core.stitch(ims, names, metas, orig_widths=ow)
J['t34'] = round(time.time() - t0, 1)
print('34 ภาพ:', res['stats'], '| เวลา', J['t34'], '| ผืน', [len(s['names']) for s in res['segments']], res['segments'][0]['mosaic'].shape[:2][::-1], 'dup %.2f' % res['segments'][0]['dup'])
print('  check', res['segments'][0]['check'])
print('  ตัด:', [(p['a'], p['b'], p['inliers'], p['conf'], p['status'], None if p['gps_diff'] is None else round(p['gps_diff'], 2)) for p in res['pairs'] if not p['ok']])
gd = [p['gps_diff'] for p in res['pairs'] if p['ok'] and p['gps_diff'] is not None]
rs = [p['resid'] for p in res['pairs'] if p['ok']]
print('  ต่างจาก GPS ของคู่ที่ใช้ (รอบบินเดียวกัน): max %.2f ม. | คลาดบนผืน median %.1f max %.1f px' % (max(gd), np.median(rs), max(rs)))
J['stats34'] = res['stats']
J['check34'] = res['segments'][0]['check']
J['order34'] = res['segments'][0]['names']
J['size34'] = list(res['segments'][0]['mosaic'].shape[:2][::-1])
J['cut34'] = [dict(a=p['a'], b=p['b'], inl=p['inliers'], diff=p['gps_diff']) for p in res['pairs'] if p['status'] == 'gps']
J['gpsdiff34max'] = float(max(gd))
J['resid34'] = [float(np.median(rs)), float(max(rs))]

# ---------- รอบบินที่ภาพซ้อนน้อย 13 ภาพ ----------
ims, metas, ow = data(P1)
names = [short(f) for f in P1]
for use in (True, False):
    res = core.stitch(ims, names, metas if use else None, orig_widths=ow)
    key = 't13' if use else 't13nometa'
    J[key] = dict(stats=res['stats'], segs=[s['names'] for s in res['segments']],
                  cut=[dict(a=p['a'], b=p['b'], inl=p['inliers'], diff=p['gps_diff']) for p in res['pairs'] if p['status'] == 'gps'],
                  fragile=[[p['a'], p['b'], p['inliers'], p['conf']] for p in res['pairs'] if p['ok'] and p['fragile']])
    print('13 ภาพ', 'ใช้ metadata' if use else 'ไม่ใช้ metadata', ':', res['stats'], '| ผืน', J[key]['segs'], '| ตัด', J[key]['cut'], '| เปราะ', J[key]['fragile'])
json.dump(J, open(os.path.join(OUT, 'numbers.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
