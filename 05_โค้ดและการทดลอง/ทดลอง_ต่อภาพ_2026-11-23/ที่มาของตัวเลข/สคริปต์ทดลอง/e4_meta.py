# E4/E5: เทียบ metadata (เวลา, GPS, ความสูง) กับตำแหน่งบนผืนที่ได้จากภาพ
import json, itertools, numpy as np
d = json.load(open('e1.json')); names = d['names']; n = len(names); shapes = d['shapes']
short = [x.replace('Not use/', 'N:').replace('DJI_', '').replace('.JPG', '') for x in names]
full = {(r['i'], r['j']): r for r in d['res']['full']}
e2 = json.load(open('e2.json')); ov = {tuple(map(int, k.split(','))): v for k, v in e2['ov'].items()}
T = {int(k): np.array(v) for k, v in e2['T'].items()}
meta = {m['name']: m for m in json.load(open('meta.json', encoding='utf-8'))}
E = np.array([meta[x]['E'] for x in names]); N = np.array([meta[x]['N'] for x in names])
alt = np.array([float(meta[x]['xmp']['drone-dji:RelativeAltitude']) for x in names])
import datetime
t = np.array([datetime.datetime.strptime(meta[x]['dto'], '%Y:%m:%d %H:%M:%S').timestamp() for x in names]); t -= t.min()
c = np.array([(T[i] @ np.array([shapes[i][1] / 2, shapes[i][0] / 2, 1]))[:2] for i in range(n)])
p1 = np.arange(n) < 13; p2 = ~p1
# แกนตามแนวบิน = ทิศหลักของ GPS
P = np.c_[E, N]; Pc = P - P.mean(0); u = np.linalg.svd(Pc, full_matrices=False)[2][0]
along = Pc @ u; across = Pc @ np.array([-u[1], u[0]])
print('along-track direction (E,N):', u.round(3), '| along range %.1f m | across-track std %.2f m (pass1 %.2f, pass2 %.2f)' % (np.ptp(along), across.std(), across[p1].std(), across[p2].std()))
# 1) mosaic x กับ along-track: fit เส้นตรงต่อรอบบิน
for lab, m in (('pass1', p1), ('pass2', p2), ('both', np.ones(n, bool))):
    A = np.c_[c[m, 0], np.ones(m.sum())]; k, b = np.linalg.lstsq(A, along[m], rcond=None)[0]; r = along[m] - A @ [k, b]
    print(f'{lab}: along = {k*1000:.3f} mm/px * x + b | residual rms {r.std():.2f} m  max {np.abs(r).max():.2f} m | corr {np.corrcoef(c[m,0], along[m])[0,1]:.4f}')
A = np.c_[c[:, 0], p1, p2]; sol = np.linalg.lstsq(A, along, rcond=None)[0]; r = along - A @ sol
print('both passes, separate offsets: %.3f mm/px, offset diff between passes %.2f m, residual rms %.2f m max %.2f m' % (sol[0] * 1000, sol[1] - sol[2], r.std(), np.abs(r).max()))
gsd = abs(sol[0])
# 2) mosaic y กับความสูง
A = np.c_[c[:, 1], p1, p2]; s2 = np.linalg.lstsq(A, alt, rcond=None)[0]; r2 = alt - A @ s2
print('alt = %.3f mm/px * y + offset(pass) | residual rms %.2f m | corr pass2 %.3f pass1 %.3f' % (s2[0] * 1000, r2.std(), np.corrcoef(c[p2, 1], alt[p2])[0, 1], np.corrcoef(c[p1, 1], alt[p1])[0, 1]))
print('pass2: mosaic y range %.0f px = %.2f m (ด้วยสเกลแนวนอน) | relAlt range %.2f m | along range %.2f m' % (np.ptp(c[p2, 1]), np.ptp(c[p2, 1]) * gsd, np.ptp(alt[p2]), np.ptp(along[p2])))
print('pass2 centers (name, x px, y px, along m, alt m):'); [print('   ', short[i], round(c[i, 0]), round(c[i, 1]), round(along[i], 2), alt[i]) for i in sorted(np.where(p2)[0], key=lambda i: c[i, 0])]
# 3) ลำดับ: เวลา / GPS / ภาพ
from scipy.stats import kendalltau
def swaps(a, b): return kendalltau(a, b)[0]
print('order agreement (Kendall tau) mosaic-x vs time: pass1 %.3f pass2 %.3f | mosaic-x vs GPS along: pass1 %.3f pass2 %.3f both %.3f' % (
    abs(swaps(c[p1, 0], t[p1])), abs(swaps(c[p2, 0], t[p2])), abs(swaps(c[p1, 0], along[p1])), abs(swaps(c[p2, 0], along[p2])), abs(swaps(c[:, 0], along))))
# 4) การคัดคู่ด้วย metadata: recall ของคู่ที่ซ้อนกันจริง
edges = {tuple(e) for e in e2['edges']}; true = {tuple(e) for e in e2['true']}
ot = np.argsort(t); rank_t = np.empty(n, int); rank_t[ot] = np.arange(n)
D = np.sqrt((E[:, None] - E[None]) ** 2 + (N[:, None] - N[None]) ** 2 + (alt[:, None] - alt[None]) ** 2)
def cand_time(k): return {(min(i, j), max(i, j)) for i in range(n) for j in range(n) if i != j and abs(rank_t[i] - rank_t[j]) <= k}
def cand_gps(k): return {(min(i, j), max(i, j)) for i in range(n) for j in np.argsort(D[i])[1:k + 1]}
def cand_gps_r(rad): return {(i, j) for i, j in itertools.combinations(range(n), 2) if D[i, j] <= rad}
def rep(lab, cset): print(f'  {lab:28s} pairs {len(cset):4d}/{n*(n-1)//2} | recall edges(inl>=30) {len(cset & edges)/len(edges):.3f} | recall overlap>10% {len(cset & true)/len(true):.3f}')
for k in (1, 2, 3): rep(f'time ±{k}', cand_time(k))
for k in (3, 4, 6, 8): rep(f'GPS nearest {k}', cand_gps(k))
for rad in (2.0, 2.5, 3.0, 4.0): rep(f'GPS radius {rad} m', cand_gps_r(rad))
rep('time ±2 ∪ GPS nearest 6', cand_time(2) | cand_gps(6))
rep('time ±2 ∪ GPS radius 3 m', cand_time(2) | cand_gps_r(3.0))
# 5) ความสอดคล้องของขอบกับ GPS: ระยะ GPS เทียบกับระยะบนภาพ × gsd (ใช้การแปลงของขอบเอง ไม่ใช่ต้นไม้)
print('edge check: |GPS along diff| vs |image shift|*gsd (m)')
rows = []
for (i, j), r in full.items():
    if r['inl'] >= 30 and 1/3 <= r.get('scale', 0) <= 3:
        M = np.array(r['M']); ci = np.array([shapes[i][1] / 2, shapes[i][0] / 2]); cj = M @ np.array([shapes[j][1] / 2, shapes[j][0] / 2, 1])
        si = np.hypot(T[i][0, 0], T[i][1, 0])   # สเกลของภาพ i บนผืน (เพื่อแปลง px ของภาพ i เป็น px ผืน)
        dpx = np.linalg.norm(cj - ci) * si; dg = np.hypot(along[i] - along[j], alt[i] - alt[j])
        rows.append((abs(dg - dpx * gsd), dg, dpx * gsd, r['inl'], round(r['inl'] / (8 + 0.3 * r['good']), 2), short[i], short[j], round(ov[(i, j)], 2)))
rows.sort(reverse=True)
for x in rows[:10]: print('   diff %.2f m | gps %.2f m | img %.2f m | inl %d conf %.2f | %s-%s ov %.2f' % x)
dd = np.array([x[0] for x in rows]); print('   all edges diff: median %.2f  p90 %.2f  p95 %.2f m' % (np.median(dd), np.percentile(dd, 90), np.percentile(dd, 95)))
