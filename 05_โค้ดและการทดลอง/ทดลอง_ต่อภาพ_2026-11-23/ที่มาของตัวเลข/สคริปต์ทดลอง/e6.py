# E6: ตัวเลขสำหรับออกแบบ — (ก) คัดคู่แบบเร็วด้วยจุดเด่นชุดย่อย (ข) ตรวจคู่หลอกด้วยการเทียบเนื้อภาพ (NCC) (ค) ตรวจด้วย GPS ในรอบบินเดียวกัน
import glob, os, json, time, itertools, datetime
import cv2, numpy as np
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
fs = sorted(glob.glob(src + '/*.JPG') + glob.glob(src + '/Not use/*.JPG'))
names = [os.path.relpath(f, src).replace(os.sep, '/') for f in fs]; n = len(fs)
short = [x.replace('Not use/', 'N:').replace('DJI_', '').replace('.JPG', '') for x in names]
os.makedirs('small', exist_ok=True)
ims = []
for f, nm in zip(fs, short):
    p = 'small/' + nm.replace(':', '_') + '.jpg'
    if not os.path.exists(p):
        im = cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_COLOR); s = 1600 / im.shape[1]
        cv2.imwrite(p, cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 92])
    ims.append(cv2.imread(p))
e1 = json.load(open('e1.json')); full = {(r['i'], r['j']): r for r in e1['res']['full']}
e2 = json.load(open('e2.json')); ov = {tuple(map(int, k.split(','))): v for k, v in e2['ov'].items()}; edges = {tuple(e) for e in e2['edges']}
FALSE = {(short.index('N:0311'), short.index('N:0312')), (short.index('N:0312'), short.index('N:0313'))}
sift = cv2.SIFT_create(4000); F = []
for im in ims:
    k, d = sift.detectAndCompute(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), None)
    F.append((np.float32([p.pt for p in k]), d, np.float32([p.response for p in k])))
bf = cv2.BFMatcher()
def match(pi, di, pj, dj, ratio=0.75):
    good = [p[0] for p in bf.knnMatch(dj, di, k=2) if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    if len(good) < 8: return 0, len(good)
    a = np.float32([pj[m.queryIdx] for m in good]); b = np.float32([pi[m.trainIdx] for m in good])
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=3)
    if M is None: return 0, len(good)
    s = np.hypot(M[0, 0], M[1, 0])
    return (int(inl.sum()) if 1/3 <= s <= 3 else 0), len(good)
# (ก) คัดคู่ด้วยชุดย่อย top-K ตาม response
real = edges - FALSE
for K in (800, 1200, 1600):
    sub = []
    for p, d, r in F:
        idx = np.argsort(-r)[:K]; sub.append((p[idx], d[idx]))
    t0 = time.time(); res = {}
    for i, j in itertools.combinations(range(n), 2): res[(i, j)] = match(sub[i][0], sub[i][1], sub[j][0], sub[j][1])[0]
    dt = time.time() - t0
    for thr in (6, 8, 10):
        cand = {p for p, v in res.items() if v >= thr}
        print(f'top-{K}: {dt:.1f}s ({dt/len(res)*1000:.1f} ms/pair) | inl>={thr}: candidates {len(cand)} recall(real edges) {len(cand & real)/len(real):.3f} missed {sorted((short[i], short[j], full[(i,j)]["inl"]) for i, j in real - cand)[:6]} | false kept {len(cand & FALSE)} | non-edges {len(cand - edges)}')
# (ข) NCC ของเนื้อภาพในบริเวณที่อ้างว่าซ้อน
def hp(im):
    g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).astype(np.float32)
    g = cv2.resize(g, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
    return g - cv2.GaussianBlur(g, (0, 0), 6)
H = [hp(im) for im in ims]
def ncc(i, j, M):
    S = np.diag([0.25, 0.25, 1.0]); A = (S @ np.vstack([M, [0, 0, 1]]) @ np.linalg.inv(S))[:2]
    h, w = H[i].shape
    wj = cv2.warpAffine(H[j], A, (w, h)); m = cv2.warpAffine(np.ones_like(H[j]), A, (w, h)) > 0.99
    if m.sum() < 0.03 * h * w: return None, m.mean()
    a = H[i][m]; b = wj[m]; a = a - a.mean(); b = b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9)), float(m.mean())
rows = []
for (i, j) in sorted(edges):
    c, area = ncc(i, j, np.array(full[(i, j)]['M'])); rows.append((c, area, full[(i, j)]['inl'], short[i], short[j], (i, j) in FALSE))
print('NCC (เนื้อภาพในส่วนซ้อน) ของขอบทั้ง 89:')
tr = np.array([r[0] for r in rows if not r[5] and r[0] is not None]); 
print('  real edges: n %d  min %.2f  p5 %.2f  p25 %.2f  median %.2f' % (len(tr), tr.min(), np.percentile(tr, 5), np.percentile(tr, 25), np.median(tr)))
print('  lowest real:', [(round(r[0], 2), round(r[1], 2), r[2], r[3], r[4]) for r in sorted([r for r in rows if not r[5] and r[0] is not None])[:8]])
print('  FALSE edges:', [(None if r[0] is None else round(r[0], 2), round(r[1], 2), r[2], r[3], r[4]) for r in rows if r[5]])
print('  edges with too-small overlap for NCC:', [(r[2], r[3], r[4], round(r[1], 3)) for r in rows if r[0] is None])
# คู่ที่ไม่ซ้อนจริงแต่ inlier 15-29 (ถ้าลดเกณฑ์)
low = [(p, r) for p, r in full.items() if 15 <= r['inl'] < 30 and 1/3 <= r.get('scale', 0) <= 3]
lr = [(round(ncc(i, j, np.array(r['M']))[0] or -9, 2), r['inl'], short[i], short[j], round(ov[(i, j)], 2)) for (i, j), r in low]
print('  pairs with inl 15-29: (ncc, inl, a, b, true overlap):', sorted(lr, reverse=True))
json.dump([[r[0], r[1], r[2], r[3], r[4], r[5]] for r in rows], open('e6_ncc.json', 'w'))
