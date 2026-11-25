# ต่อภาพแบบลูกโซ่: จับคู่ภาพที่อยู่ติดกัน (SIFT + RANSAC) แล้วสะสมการแปลงลงผืนเดียว
import cv2, glob, numpy as np, os, json
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
W, Hh = 1600, 1200
fs = sorted(glob.glob(os.path.join(src, '*.JPG')))
names = [os.path.basename(f)[4:8] for f in fs]
ims = [cv2.resize(cv2.imdecode(np.fromfile(f, np.uint8), 1), (W, Hh), interpolation=cv2.INTER_AREA) for f in fs]

sift = cv2.SIFT_create(4000)
feats = [sift.detectAndCompute(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), None) for im in ims]
bf = cv2.BFMatcher()

def match(i, j):
    """คืน (M 2x3 แบบ similarity ที่พาภาพ j ไปพิกัดภาพ i, จำนวน inlier, จำนวนคู่ที่ผ่าน ratio test, rmse px)"""
    (ki, di), (kj, dj) = feats[i], feats[j]
    good = [m for m, n in bf.knnMatch(dj, di, k=2) if m.distance < 0.75 * n.distance]
    if len(good) < 8: return None, 0, len(good), None
    pj = np.float32([kj[m.queryIdx].pt for m in good]); pi = np.float32([ki[m.trainIdx].pt for m in good])
    M, inl = cv2.estimateAffinePartial2D(pj, pi, method=cv2.RANSAC, ransacReprojThreshold=3)
    if M is None: return None, 0, len(good), None
    inl = inl.ravel().astype(bool)
    err = np.linalg.norm((pj[inl] @ M[:, :2].T + M[:, 2]) - pi[inl], axis=1)
    return M, int(inl.sum()), len(good), float(np.sqrt((err ** 2).mean()))

def overlap(M):
    """สัดส่วนพื้นที่ภาพ j ที่ตกในกรอบภาพ i"""
    m = cv2.warpAffine(np.ones((Hh, W), np.uint8), M, (W, Hh))
    return float(m.mean())

rows, T = [], [np.eye(3)]
print('\nคู่ติดกัน: inlier / คู่ที่ผ่าน, rmse(px ที่กว้าง 1600), ซ้อนทับ, เลื่อน dx, สเกล')
for i in range(len(ims) - 1):
    M, n, g, e = match(i, i + 1)
    ok = M is not None and n >= 30
    if ok:
        s = float(np.hypot(M[0, 0], M[1, 0])); ov = overlap(M)
        print(f'{names[i]}->{names[i+1]}  {n:4d}/{g:4d}  rmse {e:.2f}  overlap {ov*100:3.0f}%  dx {M[0,2]:+7.0f}  scale {s:.3f}')
        T.append(T[-1] @ np.vstack([M, [0, 0, 1]]))
    else:
        print(f'{names[i]}->{names[i+1]}  {n:4d}/{g:4d}  *** ต่อไม่ติด ***')
        T.append(None)
    rows.append(dict(a=names[i], b=names[i+1], inliers=n, good=g, rmse=e, ok=ok))
json.dump(rows, open('pairs.json', 'w'), ensure_ascii=False, indent=1)

# วาดผืนรวมของช่วงต่อเนื่องที่ยาวที่สุด (ภาพหลังทับภาพก่อน ไม่เบลนด์ เพื่อให้เห็นรอยต่อจริง)
segs, cur = [], [0]
for i in range(1, len(ims)):
    if T[i] is None: segs.append(cur); cur = [i]; T[i] = np.eye(3)
    else: cur.append(i)
segs.append(cur)
print('\nช่วงที่ต่อเนื่อง:', [[names[i] for i in s] for s in segs])
for k, seg in enumerate(segs):
    if len(seg) < 2: continue
    c = np.float32([[0, 0], [W, 0], [W, Hh], [0, Hh]]).reshape(-1, 1, 2)
    pts = np.vstack([cv2.perspectiveTransform(c, T[i]) for i in seg]).reshape(-1, 2)
    x0, y0 = np.floor(pts.min(0)); x1, y1 = np.ceil(pts.max(0))
    S = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1]])
    size = (int(x1 - x0), int(y1 - y0))
    canvas = np.zeros((size[1], size[0], 3), np.uint8); cover = np.zeros((size[1], size[0]), np.uint16)
    for i in seg:
        A = (S @ T[i])[:2]
        w = cv2.warpAffine(ims[i], A, size); m = cv2.warpAffine(np.ones((Hh, W), np.uint8), A, size)
        canvas[m > 0] = w[m > 0]; cover += m
    print(f'ผืน {k}: {len(seg)} ภาพ ขนาด {size}  พื้นที่ภาพรวมกัน/พื้นที่ผืน = {cover.sum()/ (cover>0).sum():.2f} เท่า (= นับซ้ำเฉลี่ยถ้าไม่รวมภาพ)')
    cv2.imwrite(f'mosaic_{k}.jpg', canvas, [cv2.IMWRITE_JPEG_QUALITY, 85])
    np.save(f'T_{k}.npy', np.array([S @ T[i] for i in seg]))
