# ตัวเลขสำหรับกราฟ "ต่างจาก GPS" ของทุกคู่ในชุด 34 ภาพ (พิมพ์เฉพาะตัวเลข ไม่แสดงภาพ)
import sys, glob, os, importlib, json, numpy as np, cv2
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
def short(f): return ('N' if 'Not use' in f else '') + os.path.basename(f)[4:8]
files = sorted(glob.glob(src + '/*.JPG')) + sorted(glob.glob(src + '/Not use/*.JPG'))
loaded = [core.load(f) for f in files]
ims = [im for im, _ in loaded]
metas = [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
res = core.stitch(ims, [short(f) for f in files], metas, orig_widths=[w for _, w in loaded])
used = [p for p in res['pairs'] if p['ok'] and p['gps_diff'] is not None]
cut = [p for p in res['pairs'] if p['status'] == 'gps']
out = dict(real=[round(p['gps_diff'], 3) for p in used], fake=[round(p['gps_diff'], 3) for p in cut],
           real_n=len(used), used_total=sum(p['ok'] for p in res['pairs']), cross=sum(p['ok'] and p['gps_diff'] is None for p in res['pairs']),
           gsd_mm=res['segments'][0]['check']['gsd_mm'], width=float(np.median([im.shape[1] for im in ims])))
out['tol'] = 0.4 * out['gsd_mm'] / 1000 * out['width']
out['lowconf'] = sorted([(p['conf'], p['a'], p['b'], p['inliers'], p['gps_diff']) for p in res['pairs'] if p['ok']])[:6]
out['fakeconf'] = [(p['conf'], p['a'], p['b'], p['inliers']) for p in cut]
out['weak_used'] = sum(p['ok'] and p['conf'] < 1 for p in res['pairs'])
print('lowconf used', out['lowconf']); print('fake', out['fakeconf'], '| weak used', out['weak_used'])
print({k: (v if not isinstance(v, list) else (len(v), min(v), max(v))) for k, v in out.items()})
print('fake', out['fake'], '| real sorted top5', sorted(out['real'])[-5:])
json.dump(out, open('../doc2/numbers2.json', 'w'))
