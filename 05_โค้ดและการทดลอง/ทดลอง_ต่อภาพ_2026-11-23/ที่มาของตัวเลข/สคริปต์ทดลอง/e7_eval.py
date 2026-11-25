# E7: ทดสอบแกนใหม่กับภาพจริง — สลับลำดับ + ตั้งชื่อมั่ว แล้วเทียบกับ GPS/เวลา (พิมพ์เฉพาะตัวเลข)
import sys, glob, os, time, json, random, importlib
import cv2, numpy as np
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
P2 = sorted(glob.glob(src + '/*.JPG')); P1 = sorted(glob.glob(src + '/Not use/*.JPG'))
def short(f): return ('N:' if 'Not use' in f else '') + os.path.basename(f)[4:8]
cache = {}
def get(f):
    if f not in cache:
        small = 'small/' + short(f).replace(':', '_') + '.jpg'
        im = cv2.imread(small); meta = core.read_meta(open(f, 'rb').read(core.HEAD_BYTES))
        cache[f] = (im, meta)
    return cache[f]
def run(label, files, seed=1, use_meta=True, min_inliers=30):
    files = list(files); random.Random(seed).shuffle(files)
    ims = [get(f)[0] for f in files]; metas = [get(f)[1] if use_meta else None for f in files]
    names = ['img_%03d.jpg' % random.Random(seed * 7 + k).randrange(1000) + str(k) for k in range(len(files))]   # ชื่อมั่ว ไม่เรียง
    true = {nm: short(f) for nm, f in zip(names, files)}
    t0 = time.time(); res = core.stitch(ims, names, metas, min_inliers=min_inliers, orig_widths=[8064] * len(ims)); dt = time.time() - t0
    st = res['stats']
    print(f'\n=== {label}: {len(files)} ภาพ (สลับลำดับ seed {seed}, metadata {"ใช้" if use_meta else "ไม่ใช้"}) — {dt:.1f} วินาที')
    print(f"  คู่: ลอง {st['pairs_total']} → ส่งตรวจ {st['candidates']} → ผ่าน {st['verified']} → ใช้ {st['used']} | ตัดเพราะ GPS {st['gps_rejected']} | ขัดภาพรวม {st['conflicts']} | gps_use {st['gps_use']}")
    for p in res['pairs']:
        if not p['ok']: print('   ตัด:', true[p['a']], true[p['b']], 'inl', p['inliers'], 'conf', p['conf'], p['status'], 'gps_diff', None if p['gps_diff'] is None else round(p['gps_diff'], 2), 'resid', None if p['resid'] is None else round(p['resid']))
    for k, s in enumerate(res['segments']):
        h, w = s['mosaic'].shape[:2]
        ck = {a: (round(b, 3) if isinstance(b, float) else b) for a, b in s['check'].items()}
        print(f"  ผืน {k}: {len(s['names'])} ภาพ {w}×{h} dup {s['dup']:.2f} | {' '.join(true[x] for x in s['names'])}")
        if ck: print('     check:', ck)
    rs = np.array([p['resid'] for p in res['pairs'] if p['ok'] and p['resid'] is not None])
    if len(rs): print('  ความคลาดของคู่บนผืน (px): median %.1f  p90 %.1f  max %.1f | weak edges (conf<1) ที่ใช้: %d' % (np.median(rs), np.percentile(rs, 90), rs.max(), sum(p['ok'] and p['weak'] for p in res['pairs'])))
    return res, true
r2, t2 = run('รอบบิน 2 (ชุดหลัก)', P2, seed=1)
run('รอบบิน 2 (ชุดหลัก) สลับอีกแบบ', P2, seed=5)
run('รอบบิน 2 ไม่ใช้ metadata', P2, seed=1, use_meta=False)
r34, t34 = run('สองรอบบินรวมกัน', P2 + P1, seed=2)
run('รอบบิน 1 (Not use: ภาพซ้อนน้อย)', P1, seed=3)
run('รอบบิน 1 ไม่ใช้ metadata', P1, seed=3, use_meta=False)
json.dump({'order2': [t2[x] for x in r2['segments'][0]['names']]}, open('e7.json', 'w'))
