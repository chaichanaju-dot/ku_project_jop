# E9: (ก) ชุดภาพซ้อนน้อยหลังแก้ตัวตรวจ GPS (ข) วิธีเดิม (ลูกโซ่ตามชื่อ) เทียบวิธีใหม่ ด้วย GPS และความสูง
import sys, glob, os, importlib, random, numpy as np, cv2
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน'); old = importlib.import_module('ต่อภาพ_ลูกโซ่')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
def short(f): return ('N:' if 'Not use' in f else '') + os.path.basename(f)[4:8]
P2 = sorted(glob.glob(src + '/*.JPG')); P1 = sorted(glob.glob(src + '/Not use/*.JPG'))
def data(files):
    return [cv2.imread('small/' + short(f).replace(':', '_') + '.jpg') for f in files], [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
# (ก)
ims, metas = data(P1); idx = list(range(len(P1))); random.Random(3).shuffle(idx)
res = core.stitch([ims[k] for k in idx], [f'x{k}' for k in range(len(idx))], [metas[k] for k in idx])
nm = {f'x{k}': short(P1[i]) for k, i in enumerate(idx)}
print('รอบบิน 1 (ภาพซ้อนน้อย): gps_use', res['stats']['gps_use'], '| ตัดเพราะ GPS', [(nm[p['a']], nm[p['b']], p['inliers'], round(p['gps_diff'], 2)) for p in res['pairs'] if p['status'] == 'gps'])
print('  ผืน:', [[nm[x] for x in s['names']] for s in res['segments']])
# (ข)
ims, metas = data(P2); names = [short(f) for f in P2]
pos = core._enu(metas); P = np.array([p[:2] for p in pos]); alt = np.array([p[2] for p in pos])
along = (P - P.mean(0)) @ np.linalg.svd(P - P.mean(0), full_matrices=False)[2][0]
def report(label, centers):
    C = np.array(centers); x, y = C[:, 0], C[:, 1]
    A = np.c_[x, np.ones(len(x))]; k, b = np.linalg.lstsq(A, along, rcond=None)[0]; r = along - A @ [k, b]
    gsd = abs(k)
    A2 = np.c_[y, np.ones(len(y))]; k2, b2 = np.linalg.lstsq(A2, alt, rcond=None)[0]; r2 = alt - A2 @ [k2, b2]
    print(f'{label:26s} แนวนอน: {gsd*1000:.3f} มม./px, คลาดจาก GPS rms {np.sqrt((r**2).mean()):.3f} ม. (max {np.abs(r).max():.2f}) | แนวตั้ง: ช่วง y {np.ptp(y):.0f} px = {np.ptp(y)*gsd:.2f} ม. เทียบช่วงความสูง {np.ptp(alt):.2f} ม., สหสัมพันธ์ {abs(np.corrcoef(y, alt)[0,1]):.3f}, ความชัน {abs(k2)*1000:.2f} มม./px')
pairs, segs = old.stitch(ims, names)
T = segs[0]['T']; report('วิธีเดิม (ลูกโซ่ตามชื่อ)', [(T[k] @ np.array([800, 600, 1]))[:2] for k in range(len(ims))])
idx = list(range(len(ims))); random.Random(1).shuffle(idx)
res = core.stitch([ims[k] for k in idx], [names[k] for k in idx], [metas[k] for k in idx])
seg = res['segments'][0]; cen = {nmn: (seg['T'][n] @ np.array([800, 600, 1]))[:2] for n, nmn in enumerate(seg['names'])}
report('วิธีใหม่ (หาลำดับเอง)', [cen[x] for x in names])
rot = [np.degrees(np.arctan2(t[1, 0], t[0, 0])) for t in seg['T']]; sc = [np.hypot(t[0, 0], t[1, 0]) for t in seg['T']]
print('วิธีใหม่: มุมหมุนของแต่ละภาพบนผืน (องศา) min %.2f max %.2f | สเกล min %.2f max %.2f' % (min(rot), max(rot), min(sc), max(sc)))
rot0 = [np.degrees(np.arctan2(t[1, 0], t[0, 0])) for t in T]
print('วิธีเดิม: มุมหมุนสะสม (องศา) min %.2f max %.2f' % (min(rot0), max(rot0)))
