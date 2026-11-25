# E1: จับคู่ทุกคู่ของ 34 ภาพ (สองรอบบิน) เก็บตัวเลขไว้วิเคราะห์ — ไม่แสดงภาพ
import glob, os, sys, time, json, itertools
import cv2, numpy as np
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
fs = sorted(glob.glob(src + '/*.JPG') + glob.glob(src + '/Not use/*.JPG'))
names = [os.path.relpath(f, src).replace(os.sep, '/') for f in fs]
def load(path, width):
    im = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
    s = width / im.shape[1]
    return cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
t0 = time.time()
ims = [load(f, 1600) for f in fs]
print('load+resize 34 imgs: %.1fs' % (time.time() - t0))
def feats(ims, nf, scale=1.0):
    sift = cv2.SIFT_create(nf); out = []
    for im in ims:
        g = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        if scale != 1.0: g = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        k, d = sift.detectAndCompute(g, None)
        out.append((np.float32([p.pt for p in k]) / scale, d))
    return out
t0 = time.time(); F = feats(ims, 4000); tF = time.time() - t0
t0 = time.time(); Fs = feats(ims, 1200, 0.5); tFs = time.time() - t0
print('SIFT full(4000@1600): %.1fs  cheap(1200@800): %.1fs' % (tF, tFs), 'avg kp', np.mean([len(p) for p, d in F]), np.mean([len(p) for p, d in Fs]))
bf = cv2.BFMatcher()
def match(Fa, Fb, ratio=0.75, thr=3.0):
    (pi, di), (pj, dj) = Fa, Fb
    good = [p[0] for p in bf.knnMatch(dj, di, k=2) if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    if len(good) < 8: return dict(good=len(good), inl=0)
    a = np.float32([pj[m.queryIdx] for m in good]); b = np.float32([pi[m.trainIdx] for m in good])
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=thr)
    if M is None: return dict(good=len(good), inl=0)
    inl = inl.ravel().astype(bool)
    H, inlH = cv2.findHomography(a, b, cv2.RANSAC, thr)
    return dict(good=len(good), inl=int(inl.sum()), M=M.tolist(), scale=float(np.hypot(M[0, 0], M[1, 0])), rot=float(np.degrees(np.arctan2(M[1, 0], M[0, 0]))),
                inlH=int(inlH.sum()) if inlH is not None else 0)
res = {}
for label, FF in (('full', F), ('cheap', Fs)):
    t0 = time.time(); out = []
    for i, j in itertools.combinations(range(len(fs)), 2):
        r = match(FF[i], FF[j]); r.update(i=i, j=j); out.append(r)
    res[label] = out
    print(label, 'all-pairs %d pairs: %.1fs (%.3fs/pair)' % (len(out), time.time() - t0, (time.time() - t0) / len(out)))
json.dump(dict(names=names, res=res, shapes=[im.shape[:2] for im in ims]), open('e1.json', 'w'))
np.savez('feats_full.npz', **{f'p{i}': F[i][0] for i in range(len(F))}, **{f'd{i}': F[i][1] for i in range(len(F))})
