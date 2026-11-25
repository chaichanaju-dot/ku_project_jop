"""ต่อภาพแบบหาลำดับเอง — ใส่ภาพลำดับไหนก็ได้ ไม่พึ่งชื่อไฟล์

ขั้นตอน (แนวเดียวกับ Brown & Lowe 2007 และตัวต่อภาพโหมด SCANS ของ OpenCV — ดู วิธีหาลำดับภาพ_ค้นคว้า.md)
  1) หาจุดเด่น (SIFT) ของทุกภาพ
  2) ลองจับคู่ "ทุกคู่" แบบเร็ว ด้วยจุดเด่นที่แรงที่สุดชุดย่อย → ได้คู่ที่น่าจะซ้อนกัน
  3) ตรวจคู่เหล่านั้นแบบเต็ม: RANSAC หาการเลื่อน-หมุน-ย่อขยาย (similarity) ระหว่างสองภาพ
  4) ถ้าภาพมี GPS ฝังอยู่: ตัดคู่ที่ "ระยะบนภาพ" ขัดกับ "ระยะจาก GPS" (กันลายซ้ำบนคอนกรีตหลอก)
  5) มองภาพเป็นจุด คู่ที่ผ่านเป็นเส้นเชื่อม → กลุ่มที่เชื่อมถึงกัน = หนึ่งผืน
  6) วางภาพด้วยต้นไม้ที่เส้นเชื่อมแข็งแรงสุด แล้วปรับทุกภาพพร้อมกันให้ทุกคู่ลงรอย (least squares)
  7) ลำดับภาพ = ตำแหน่งที่ภาพไปอยู่บนผืน

ใช้ได้สองแบบ
  - สั่งรัน:  python ต่อภาพ_แกน.py [โฟลเดอร์ภาพ]      → ผลออกที่ ผลลัพธ์/
  - เป็นแกนของโปรแกรมหน้าเว็บ ต่อภาพ_แอป.py (เรียก stitch())

ต้องมี opencv-python และ numpy เท่านั้น

ponytail: ลองจับคู่ทุกคู่ = O(n²) วัดได้ ~2 ms/คู่ (34 ภาพ ~1 วินาที, 200 ภาพ ~40 วินาที)
          ถ้าภาพเกินหลายร้อย ให้คัดคู่ด้วย GPS/เวลาก่อน (แบบ OpenSfM matching_gps_neighbors)
ponytail: ใช้ similarity (เลื่อน หมุน ย่อขยาย) เพราะผิวที่ถ่ายเกือบเป็นระนาบและกล้องหันทิศเดิม
          ถ้าถ่ายคนละมุมมาก รอยต่อจะเหลื่อม ต้องเปลี่ยนเป็น homography + bundle adjustment
ponytail: อ่าน metadata เฉพาะ XMP ของ DJI (เวลา พิกัด ความสูง) กล้องอื่นจะไม่มี → ยังต่อได้จากภาพล้วน
"""
import glob
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
import os
import re
import sys
from datetime import datetime

import cv2
import numpy as np

WORK_WIDTH = 1600             # ความกว้างที่ย่อภาพก่อนคำนวณ
N_FEATURES = 4000             # จุดเด่นต่อภาพ
SUBSET = 1600                 # จุดเด่นที่แรงที่สุด ใช้ลองจับคู่ทุกคู่แบบเร็ว
DISCOVER_MIN = 8              # คู่ที่ได้จุดตรงกันเท่านี้จากชุดย่อย → ส่งไปตรวจเต็ม
SCALE_RANGE = (1 / 3, 3)      # ย่อขยายระหว่างสองภาพนอกช่วงนี้ถือว่าจับคู่ผิด
MAX_ROT_DEG = 30              # หมุนเกินนี้ถือว่าจับคู่ผิด
MIN_SPREAD = 0.05             # จุดที่ตรงกันต้องกระจายอย่างน้อย 5% ของความกว้างภาพ (กันจุดกระจุก)
CONFLICT = 0.15               # คู่ที่ขัดกับตำแหน่งรวมเกิน 15% ของความกว้างภาพ → ไม่ใช้
SESSION_GAP_S = 300           # ถ่ายห่างกันเกิน 5 นาที = คนละรอบบิน (GPS เทียบข้ามรอบไม่ได้)
MAX_CANVAS_PX = 120_000_000   # ผืนใหญ่กว่านี้แปลว่าการวางเพี้ยน ไม่วาด
HEAD_BYTES = 262144           # อ่านหัวไฟล์เท่านี้พอสำหรับ metadata

THREADS = min(8, os.cpu_count() or 2)


# ---------------------------------------------------------------- อ่านภาพและ metadata
def load(path, width=WORK_WIDTH):
    """อ่านภาพ (รองรับ path ไทย) แล้วย่อให้กว้างไม่เกิน width · คืน (ภาพ, ความกว้างเดิม)"""
    im = cv2.imdecode(np.fromfile(path, np.uint8), cv2.IMREAD_COLOR)
    w0 = im.shape[1]
    s = width / w0
    return (cv2.resize(im, None, fx=s, fy=s, interpolation=cv2.INTER_AREA) if s < 1 else im), w0


def read_meta(head):
    """อ่านเวลา/พิกัด/ความสูง/มุมกล้องจาก XMP ของ DJI ในหัวไฟล์ JPEG · ไม่มีก็คืน None"""
    a, b = head.find(b'<x:xmpmeta'), head.find(b'</x:xmpmeta>')
    if a < 0 or b < 0:
        return None
    x = head[a:b].decode('utf-8', 'replace')

    def get(*keys):
        for k in keys:
            m = re.search(r'%s\s*=\s*"([^"]*)"|<%s>([^<]*)<' % (re.escape(k), re.escape(k)), x)
            if m:
                return (m.group(1) or m.group(2) or '').strip()
        return None

    def num(*keys):
        try:
            return float(get(*keys))
        except (TypeError, ValueError):
            return None

    t = None
    try:
        t = datetime.fromisoformat((get('xmp:CreateDate') or '')[:19]).timestamp()
    except ValueError:
        pass
    m = dict(time=t,
             lat=num('drone-dji:GpsLatitude'), lon=num('drone-dji:GpsLongitude', 'drone-dji:GpsLongtitude'),
             alt=num('drone-dji:RelativeAltitude'),
             yaw=num('drone-dji:GimbalYawDegree'), pitch=num('drone-dji:GimbalPitchDegree'), roll=num('drone-dji:GimbalRollDegree'),
             gps_status=get('drone-dji:GpsStatus'), model=get('drone-dji:DroneModel', 'tiff:Model'))
    if m['lat'] is not None and m['lon'] is not None and abs(m['lat']) < 1e-9 and abs(m['lon']) < 1e-9:
        m['lat'] = m['lon'] = None          # 0,0 = ไม่มีพิกัดจริง
    return m if any(v is not None for v in m.values()) else None


def _enu(metas):
    """พิกัด lat/lon/alt → เมตร (ตะวันออก, เหนือ, สูง) เทียบกับภาพแรกที่มีพิกัด · ภาพที่ไม่มีพิกัดได้ None"""
    ref = next((m for m in metas if m and m.get('lat') is not None), None)
    out = []
    for m in metas:
        if not m or m.get('lat') is None:
            out.append(None)
            continue
        out.append(np.array([(m['lon'] - ref['lon']) * 111320.0 * np.cos(np.radians(ref['lat'])),
                             (m['lat'] - ref['lat']) * 111320.0, m.get('alt') or 0.0]))
    return out


def _sessions(metas):
    """แบ่งรอบบินจากเวลาถ่าย (ห่างกันเกิน SESSION_GAP_S = รอบใหม่) · ไม่มีเวลา = รอบ 0"""
    ses = [0] * len(metas)
    timed = sorted((m['time'], k) for k, m in enumerate(metas) if m and m.get('time') is not None)
    s = 0
    for n, (t, k) in enumerate(timed):
        if n and t - timed[n - 1][0] > SESSION_GAP_S:
            s += 1
        ses[k] = s
    return ses


# ---------------------------------------------------------------- จุดเด่นและการจับคู่
def _features(im):
    k, d = cv2.SIFT_create(N_FEATURES).detectAndCompute(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY), None)
    if d is None or not len(k):
        return np.zeros((0, 2), np.float32), np.zeros((0, 128), np.float32)
    order = np.argsort([-p.response for p in k])          # แรงสุดก่อน → ชุดย่อย = แถวบนสุด
    return np.float32([k[i].pt for i in order]), d[order]


def _match(fi, fj, top=None, ratio=0.75, thr=3.0):
    """หาการแปลง M (2x3) ที่พาภาพ j ไปพิกัดภาพ i · คืน (M, จุดใน j, จุดใน i, จำนวนคู่ที่ผ่าน ratio test) หรือ None"""
    (pi, di), (pj, dj) = fi, fj
    if top:
        pi, di, pj, dj = pi[:top], di[:top], pj[:top], dj[:top]
    if len(di) < 2 or len(dj) < 2:
        return None
    good = [p[0] for p in cv2.BFMatcher().knnMatch(dj, di, k=2) if len(p) == 2 and p[0].distance < ratio * p[1].distance]
    if len(good) < 8:
        return None
    a = np.float32([pj[m.queryIdx] for m in good])
    b = np.float32([pi[m.trainIdx] for m in good])
    cv2.setRNGSeed(0)                                    # ให้ RANSAC สุ่มแบบเดิมทุกครั้ง → ภาพชุดเดิมได้ผลเดิม
    M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=thr)
    if M is None:
        return None
    inl = inl.ravel().astype(bool)
    return M, a[inl], b[inl], len(good)


def _verify(fi, fj, width, min_inliers):
    """ตรวจคู่แบบเต็ม · คืน dict ของเส้นเชื่อม หรือ None ถ้าไม่ผ่าน"""
    r = _match(fi, fj)
    if r is None:
        return None
    M, a, b, good = r
    scale = float(np.hypot(M[0, 0], M[1, 0]))
    rot = float(np.degrees(np.arctan2(M[1, 0], M[0, 0])))
    if (len(a) < min_inliers or not SCALE_RANGE[0] <= scale <= SCALE_RANGE[1] or abs(rot) > MAX_ROT_DEG
            or np.ptp(a, axis=0).max() < MIN_SPREAD * width):
        return None
    err = np.linalg.norm(a @ M[:, :2].T + M[:, 2] - b, axis=1)
    return dict(M=np.vstack([M, [0, 0, 1]]), pj=a.astype(np.float64), pi=b.astype(np.float64), inl=len(a), good=good,
                conf=len(a) / (8 + 0.3 * good),          # เกณฑ์ของ Brown & Lowe (>1 = มั่นใจ)
                rmse=float(np.sqrt((err ** 2).mean())), scale=scale, rot=rot, status='ok', gps_diff=None)


# ---------------------------------------------------------------- ตรวจกับ GPS
def _gps_reject(E, metas, shapes):
    """ตัดเส้นเชื่อมที่ระยะบนภาพขัดกับระยะจาก GPS · เทียบเฉพาะคู่ในรอบบินเดียวกัน
    คืนคำอธิบายสั้นๆ ว่าใช้ GPS ตรวจได้หรือไม่"""
    pos, ses = _enu(metas), _sessions(metas)
    rows = []
    for (i, j), e in E.items():
        if pos[i] is None or pos[j] is None or ses[i] != ses[j]:
            continue
        ci = np.array([shapes[i][1] / 2, shapes[i][0] / 2])
        cj = (e['M'] @ np.array([shapes[j][1] / 2, shapes[j][0] / 2, 1.0]))[:2]
        rows.append(((i, j), float(np.linalg.norm(pos[i] - pos[j])), float(np.linalg.norm(cj - ci))))
    width = np.median([s[1] for s in shapes])
    ref = [(dg, dp) for k, dg, dp in rows if dp >= 0.2 * width]     # คู่ที่เลื่อนมากพอให้เทียบสเกลได้
    if len(ref) < 4:
        return 'no' if not rows else 'few'
    ratio = np.array([dg / dp for dg, dp in ref])        # เมตรต่อพิกเซลของแต่ละคู่
    gsd = float(np.median(ratio))
    if gsd <= 0 or 1.4826 * np.median(np.abs(ratio - gsd)) > 0.5 * gsd:
        return 'noisy'                                   # แต่ละคู่ให้สเกลไม่ไปทางเดียวกัน → พิกัดไม่น่าเชื่อ ไม่ใช้ตรวจ
    tol = 0.4 * gsd * width                              # คลาดได้ไม่เกิน 40% ของความกว้างที่ภาพหนึ่งใบเห็น
    for k, g, p in rows:
        pred = gsd * p
        E[k]['gps_diff'] = abs(g - pred)
        if abs(g - pred) > tol and not 0.4 <= g / max(pred, 1e-9) <= 2.5:
            E[k]['status'] = 'gps'
    return 'ok'


# ---------------------------------------------------------------- วางภาพ
def _find(parent, x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def _components(n, edges):
    parent = list(range(n))
    for i, j in edges:
        parent[_find(parent, i)] = _find(parent, j)
    groups = {}
    for k in range(n):
        groups.setdefault(_find(parent, k), []).append(k)
    return sorted(groups.values(), key=len, reverse=True)


def _tree(nodes, E, keys):
    """ต้นไม้ที่เส้นเชื่อมแข็งแรงสุด (maximum spanning tree ตามจำนวนจุดที่ตรงกัน) + รากที่อยู่กึ่งกลางต้นไม้"""
    parent = {k: k for k in nodes}
    adj = {k: [] for k in nodes}
    used = []
    for i, j in sorted(keys, key=lambda k: -E[k]['inl']):
        a, b = _find(parent, i), _find(parent, j)
        if a != b:
            parent[a] = b
            adj[i].append(j)
            adj[j].append(i)
            used.append((i, j))

    def far(s):                                          # จุดที่ไกลสุดจาก s และเส้นทางไปถึง
        prev, q = {s: None}, [s]
        for u in q:
            for v in adj[u]:
                if v not in prev:
                    prev[v] = u
                    q.append(v)
        path, u = [], q[-1]
        while u is not None:
            path.append(u)
            u = prev[u]
        return q[-1], path

    u, _ = far(nodes[0])
    _, path = far(u)
    return adj, path[len(path) // 2], used


def _A(p):
    """แถวของสมการเชิงเส้นสำหรับ T(a,b,tx,ty) · จุด p (m,2) → (2m,4)"""
    x, y = p[:, 0], p[:, 1]
    o, z = np.ones_like(x), np.zeros_like(x)
    return np.concatenate([np.stack([x, -y, o, z], 1), np.stack([y, x, z, o], 1)])


def _layout(nodes, E, keys, width):
    """คืน {ภาพ: T 3x3 (ภาพ → ผืน)} · เริ่มจากต้นไม้ แล้วปรับทุกภาพพร้อมกันแบบถ่วงน้ำหนัก (IRLS)
    เส้นเชื่อมที่ขัดกับตำแหน่งรวมจะถูกลดน้ำหนักเอง และถูกติดป้าย conflict"""
    if len(nodes) == 1:
        return {nodes[0]: np.eye(3)}
    adj, root, used = _tree(nodes, E, keys)
    for k in used:
        E[k]['tree'] = True
    T, q = {root: np.eye(3)}, [root]
    for u in q:                                          # ไล่จากรากออกไป ต่อการแปลงเป็นทอดๆ
        for v in adj[u]:
            if v not in T:
                M = E[(u, v)]['M'] if (u, v) in E else np.linalg.inv(E[(v, u)]['M'])
                T[v] = T[u] @ M
                q.append(v)
    # ปรับพร้อมกัน: หา (a,b,tx,ty) ของทุกภาพที่ทำให้จุดคู่กันของทุกเส้นเชื่อมไปตกที่เดียวกันบนผืน
    free = [k for k in nodes if k != root]
    pos = {k: 4 * n for n, k in enumerate(free)}
    B = {}
    for k in keys:
        J = np.hstack([_A(E[k]['pi']), -_A(E[k]['pj'])])
        B[k] = (J.T @ J) * (min(len(E[k]['pi']), 150) / len(E[k]['pi']))   # ไม่ให้คู่ที่จุดเยอะมากกลบคู่อื่น
    th = {k: np.array([T[k][0, 0], T[k][1, 0], T[k][0, 2], T[k][1, 2]]) for k in nodes}

    def resid(k):                                        # ความคลาดเฉลี่ยของเส้นเชื่อม k บนผืน (px)
        v = np.concatenate([th[k[0]], th[k[1]]])
        return float(np.sqrt(max(v @ B[k] @ v, 0) / min(len(E[k]['pi']), 150)))

    for _ in range(6):
        N, rhs = np.zeros((4 * len(free),) * 2), np.zeros(4 * len(free))
        for k in keys:
            w = 1.0 / (1.0 + (resid(k) / (0.03 * width)) ** 2)
            for s, u in enumerate(k):
                for t, v in enumerate(k):
                    blk = w * B[k][4 * s:4 * s + 4, 4 * t:4 * t + 4]
                    if u != root and v != root:
                        N[pos[u]:pos[u] + 4, pos[v]:pos[v] + 4] += blk
                    elif u != root:
                        rhs[pos[u]:pos[u] + 4] -= blk @ th[root]
        sol = np.linalg.solve(N + 1e-9 * np.eye(len(N)), rhs)
        for k in free:
            th[k] = sol[pos[k]:pos[k] + 4]
    for k in keys:
        E[k]['resid'] = resid(k)
        if E[k]['resid'] > CONFLICT * width:
            E[k]['status'] = 'conflict'
    T = {k: np.array([[v[0], -v[1], v[2]], [v[1], v[0], v[3]], [0, 0, 1]]) for k, v in th.items()}
    # ตั้งระดับและขนาด: ให้มุมและสเกลกึ่งกลางของทุกภาพเป็น 0° และ 1 (กล้องโดรนรักษาระดับอยู่แล้ว)
    rot = np.median([np.arctan2(t[1, 0], t[0, 0]) for t in T.values()])
    sc = np.median([np.hypot(t[0, 0], t[1, 0]) for t in T.values()])
    c, s = np.cos(-rot) / sc, np.sin(-rot) / sc
    G = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return {k: G @ t for k, t in T.items()}


# ---------------------------------------------------------------- วาดผืน
def _corners(shape):
    h, w = shape[:2]
    return np.float64([[0, 0], [w, 0], [w, h], [0, h]])


def _apply(T, pts):
    return pts @ T[:2, :2].T + T[:2, 2]


def _render(ims, order, T):
    """วาดผืน: แต่ละจุดเลือกพิกเซลจากภาพที่จุดนั้นอยู่ใกล้กลางภาพที่สุด (ไม่เบลนด์ เก็บพิกเซลจริง)"""
    pts = np.vstack([_apply(T[k], _corners(ims[k].shape)) for k in order])
    x0, y0 = np.floor(pts.min(0))
    x1, y1 = np.ceil(pts.max(0))
    W, H = int(x1 - x0), int(y1 - y0)
    if W * H > MAX_CANVAS_PX:
        raise ValueError(f'ผืนใหญ่ผิดปกติ ({W}×{H} px) การจับคู่น่าจะเพี้ยน')
    S = np.array([[1, 0, -x0], [0, 1, -y0], [0, 0, 1.0]])
    canvas = np.zeros((H, W, 3), np.uint8)
    best = np.zeros((H, W), np.float32)
    cover = np.zeros((H, W), np.uint8)
    polys, Ts = [], []
    for k in order:
        A = S @ T[k]
        h, w = ims[k].shape[:2]
        c = _apply(A, _corners(ims[k].shape))
        bx0, by0 = np.maximum(np.floor(c.min(0)).astype(int), 0)
        bx1, by1 = np.minimum(np.ceil(c.max(0)).astype(int), [W, H])
        size = (int(bx1 - bx0), int(by1 - by0))
        if size[0] <= 0 or size[1] <= 0:
            continue
        L = (np.array([[1, 0, -bx0], [0, 1, -by0], [0, 0, 1.0]]) @ A)[:2]      # วาดเฉพาะกรอบของภาพนี้ ไม่ใช่ทั้งผืน
        xx, yy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        wt = np.minimum(np.minimum(xx, w - 1 - xx), np.minimum(yy, h - 1 - yy)) + 1     # ระยะถึงขอบภาพ
        ww = cv2.warpAffine(wt, L, size)
        wi = cv2.warpAffine(ims[k], L, size)
        roi = (slice(by0, by1), slice(bx0, bx1))
        take = ww > best[roi]
        canvas[roi][take] = wi[take]
        best[roi][take] = ww[take]
        cover[roi] += (ww > 0).astype(np.uint8)
        polys.append(c.round(1).tolist())
        Ts.append(A)
    covered = int((cover > 0).sum())
    return dict(mosaic=canvas, cover=cover, polys=polys, T=np.array(Ts),
                dup=float(cover.sum(dtype=np.float64) / covered) if covered else 0.0)


def _gps_summary(order, centers, metas, orig_scale):
    """เทียบตำแหน่งภาพบนผืนกับ GPS/เวลาที่ฝังในภาพ (ใช้รายงาน ไม่ได้ใช้วางภาพ)"""
    pos, ses = _enu(metas), _sessions(metas)
    out = {}
    C = np.array([centers[k] for k in order])
    axis = np.linalg.svd(C - C.mean(0), full_matrices=False)[2][0] if len(order) > 1 else np.array([1.0, 0])
    m = {k: float((centers[k] - C.mean(0)) @ axis) for k in order}
    # ลำดับตามเวลาถ่าย ตรงกับลำดับบนผืนแค่ไหน (นับเป็นคู่ ภายในรอบบินเดียวกัน)
    timed = [k for k in order if metas[k] and metas[k].get('time') is not None]
    agree = total = 0
    for s in set(ses[k] for k in timed):
        g = [k for k in timed if ses[k] == s]
        c = sum((metas[a]['time'] - metas[b]['time']) * (m[a] - m[b]) > 0 for n, a in enumerate(g) for b in g[n + 1:])
        t = len(g) * (len(g) - 1) // 2
        agree += max(c, t - c)                           # ทิศบินกลับด้านได้
        total += t
    if total:
        out['time_agree'] = agree / total
        out['sessions'] = len(set(ses[k] for k in timed))
    g = [k for k in order if pos[k] is not None]
    if len(g) >= 4:
        P = np.array([pos[k][:2] for k in g])
        along = (P - P.mean(0)) @ np.linalg.svd(P - P.mean(0), full_matrices=False)[2][0]
        if np.ptp(along) >= 1.0:
            sid = sorted(set(ses[k] for k in g))
            D = np.array([[m[k]] + [float(ses[k] == s) for s in sid] for k in g])   # ความชันร่วม + ค่าเลื่อนต่อรอบบิน
            sol = np.linalg.lstsq(D, along, rcond=None)[0]
            r = along - D @ sol
            out.update(gps_n=len(g), gsd_mm=abs(float(sol[0])) * 1000, gps_rms_m=float(np.sqrt((r ** 2).mean())),
                       gps_span_m=float(np.ptp(along)), gsd_orig_mm=abs(float(sol[0])) * 1000 * orig_scale,
                       gps_status=sorted({str(metas[k].get('gps_status')) for k in g if metas[k].get('gps_status')}))
    return out


# ---------------------------------------------------------------- ทั้งกระบวนการ
def stitch(ims, names, metas=None, min_inliers=30, progress=None, orig_widths=None):
    """ต่อภาพโดยหาลำดับเอง · ims = ภาพ BGR ที่ย่อแล้ว, names = ชื่อ, metas = ผลจาก read_meta (หรือ None)

    คืน dict:
      segments — ผืนที่ต่อได้ (หนึ่งกลุ่มที่เชื่อมถึงกัน = หนึ่งผืน) เรียงจากผืนใหญ่สุด แต่ละผืนมี
                 names (เรียงตามตำแหน่งบนผืน = ลำดับที่โปรแกรมหาได้), mosaic, cover, polys, T, dup, check
      pairs    — เส้นเชื่อมทุกเส้นที่ตรวจผ่านขั้นจับคู่ พร้อมสถานะ (tree / extra / gps / conflict)
      stats    — จำนวนคู่ที่ลอง / คู่ที่ส่งตรวจ / คู่ที่ผ่าน และผลการใช้ GPS
    """
    n = len(ims)
    metas = metas or [None] * n
    say = progress or (lambda *a: None)
    width = float(np.median([im.shape[1] for im in ims]))

    def pmap(stage, fn, items):                          # ทำหลายเธรด + รายงานความคืบหน้า
        out = []
        with ThreadPoolExecutor(THREADS) as ex:
            for k, r in enumerate(ex.map(fn, items)):
                say(stage, k, len(items))
                out.append(r)
        return out

    F = pmap('หาจุดเด่นในภาพ', _features, ims)
    # จัดลำดับภายในตามเนื้อภาพ (ไม่ใช่ลำดับที่ใส่หรือชื่อไฟล์) → ภาพชุดเดิมได้ผลเดิมเสมอ ไม่ว่าจะใส่มาลำดับไหน
    perm = sorted(range(n), key=lambda k: (hashlib.md5(F[k][1].tobytes()).hexdigest(), names[k]))
    ims, names, metas, F = ([x[k] for k in perm] for x in (ims, names, metas, F))
    if orig_widths:
        orig_widths = [orig_widths[k] for k in perm]
    shapes = [im.shape[:2] for im in ims]

    # 2) ลองทุกคู่แบบเร็ว + คู่ที่ถ่ายติดกันตามเวลา (ถ้าภาพมีเวลา) ส่งตรวจเต็มเสมอ
    allp = [(i, j) for i in range(n) for j in range(i + 1, n)]
    total = len(allp)

    def quick(p):
        r = _match(F[p[0]], F[p[1]], top=SUBSET)
        return r is not None and len(r[1]) >= DISCOVER_MIN
    cand = {p for p, hit in zip(allp, pmap('ลองจับคู่ทุกคู่', quick, allp)) if hit}
    seq = sorted((k for k in range(n) if metas[k] and metas[k].get('time') is not None), key=lambda k: (metas[k]['time'], k))
    cand |= {(min(a, b), max(a, b)) for a, b in zip(seq, seq[1:])}

    # 3) ตรวจเต็ม
    cl = sorted(cand)
    E = {p: e for p, e in zip(cl, pmap('ตรวจคู่ที่น่าจะซ้อนกัน', lambda p: _verify(F[p[0]], F[p[1]], width, min_inliers), cl)) if e}

    # 4) ตรวจกับ GPS
    gps_use = _gps_reject(E, metas, shapes)

    # 5-6) แบ่งผืนแล้ววางภาพ (วางรอบแรก → ตัดคู่ที่ขัดกับภาพรวม → วางใหม่ถ้ามีการตัด)
    say('วางภาพลงผืน', 0, 1)
    T = {}
    for _ in range(2):
        keys = [k for k, e in E.items() if e['status'] == 'ok']
        for e in E.values():
            e.pop('tree', None)
        comps = _components(n, keys)
        T, before = {}, sum(e['status'] == 'conflict' for e in E.values())
        for comp in comps:
            T.update(_layout(comp, E, [k for k in keys if k[0] in comp], width))
        if sum(e['status'] == 'conflict' for e in E.values()) == before:
            break

    # รอยต่อเปราะ = คู่ที่มั่นใจต่ำและเป็นทางเชื่อมเดียว (ตัดแล้วผืนขาด) → ไม่มีคู่อื่นช่วยยืนยัน
    keys = [k for k, e in E.items() if e['status'] == 'ok']
    for k in keys:
        if E[k].get('tree') and E[k]['conf'] < 1:
            E[k]['bridge'] = len(_components(n, [x for x in keys if x != k])) > len(comps)

    # 7) เรียงลำดับตามตำแหน่งบนผืน แล้ววาด
    orig_scale = float(np.median([im.shape[1] / w0 for im, w0 in zip(ims, orig_widths)])) if orig_widths else 1.0
    segments = []
    for s, comp in enumerate(comps):
        say('วาดผืน', s, len(comps))
        cen = {k: _apply(T[k], np.array([[shapes[k][1] / 2, shapes[k][0] / 2]]))[0] for k in comp}
        C = np.array([cen[k] for k in comp])
        axis = 0 if np.ptp(C[:, 0]) >= np.ptp(C[:, 1]) else 1
        order = sorted(comp, key=lambda k: cen[k][axis])
        seg = _render(ims, order, T)
        seg.update(names=[names[k] for k in order], index=order, check=_gps_summary(order, cen, metas, orig_scale))
        segments.append(seg)

    # ถ้ามี GPS/เวลา: เรียงผืนที่แยกกันตามตำแหน่ง/เวลา ให้ผู้ใช้เห็นตามลำดับจริง
    pos = _enu(metas)

    def seg_key(seg):
        t = [metas[k]['time'] for k in seg['index'] if metas[k] and metas[k].get('time') is not None]
        return (-len(seg['index']), min(t) if t else 0)
    segments.sort(key=seg_key)

    # ตารางเส้นเชื่อม
    where = {k: s for s, seg in enumerate(segments) for k in seg['index']}
    pairs = []
    for (i, j), e in E.items():
        ov = None
        if e['status'] == 'ok' and where[i] == where[j]:
            pi_, pj_ = (_apply(T[k], _corners(shapes[k])).astype(np.float32) for k in (i, j))
            ov = float(cv2.intersectConvexConvex(pi_, pj_)[0] / min(cv2.contourArea(pi_), cv2.contourArea(pj_)))
        status = e['status'] if e['status'] != 'ok' else ('tree' if e.get('tree') else 'extra')
        pairs.append(dict(a=names[i], b=names[j], inliers=e['inl'], good=e['good'], conf=round(e['conf'], 2), rmse=e['rmse'],
                          resid=e.get('resid'), overlap=ov, scale=e['scale'], rot=e['rot'], status=status, gps_diff=e['gps_diff'],
                          ok=e['status'] == 'ok', weak=e['conf'] < 1, fragile=bool(e.get('bridge'))))
    rank = {nm: r for r, nm in enumerate(nm for seg in segments for nm in seg['names'])}
    pairs.sort(key=lambda p: (min(rank[p['a']], rank[p['b']]), max(rank[p['a']], rank[p['b']])))
    stats = dict(images=n, pairs_total=total, candidates=len(cand), verified=len(E),
                 used=sum(p['ok'] for p in pairs), gps_rejected=sum(p['status'] == 'gps' for p in pairs),
                 conflicts=sum(p['status'] == 'conflict' for p in pairs), gps_use=gps_use,
                 fragile=sum(p['ok'] and p['fragile'] for p in pairs),
                 has_time=sum(bool(m and m.get('time') is not None) for m in metas),
                 has_gps=sum(p is not None for p in pos))
    return dict(segments=segments, pairs=pairs, stats=stats)


if __name__ == '__main__':
    here = os.path.dirname(os.path.abspath(__file__))
    src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '..', '..', '04_ภาพและข้อมูลสนาม', 'ภาพโดรน_Agisoft')
    out_dir = os.path.join(here, 'ผลลัพธ์')
    os.makedirs(out_dir, exist_ok=True)
    fs = sorted({f for ext in ('jpg', 'jpeg', 'png') for f in glob.glob(os.path.join(src, '*.' + ext)) + glob.glob(os.path.join(src, '*.' + ext.upper()))})
    if len(fs) < 2:
        sys.exit(f'ต้องมีภาพอย่างน้อย 2 ภาพใน {src}')
    loaded = [load(f) for f in fs]
    metas = []
    for f in fs:
        with open(f, 'rb') as fh:
            metas.append(read_meta(fh.read(HEAD_BYTES)))
    res = stitch([im for im, _ in loaded], [os.path.basename(f) for f in fs], metas, orig_widths=[w for _, w in loaded],
                 progress=lambda stage, a, b: print(f'\r{stage} {a + 1}/{b}      ', end='', file=sys.stderr))
    print(file=sys.stderr)
    st = res['stats']
    print(f"ภาพ {st['images']} · ลองจับคู่ {st['pairs_total']} คู่ → ส่งตรวจ {st['candidates']} → ผ่าน {st['verified']} → ใช้ {st['used']}"
          f" (ตัดเพราะขัด GPS {st['gps_rejected']}, ขัดกับภาพรวม {st['conflicts']}) · GPS: {st['gps_use']}")
    for k, s in enumerate(res['segments']):
        h, w = s['mosaic'].shape[:2]
        print(f"ผืน {k}: {len(s['names'])} ภาพ ขนาด {w}×{h} ถ่ายซ้ำเฉลี่ย {s['dup']:.2f} เท่า")
        print('  ลำดับที่หาได้:', ' → '.join(os.path.splitext(x)[0] for x in s['names']))
        if s['check']:
            print('  เทียบกับข้อมูลในภาพ:', {a: (round(b, 3) if isinstance(b, float) else b) for a, b in s['check'].items()})
        cv2.imencode('.jpg', s['mosaic'], [cv2.IMWRITE_JPEG_QUALITY, 85])[1].tofile(os.path.join(out_dir, f'mosaic_{k}.jpg'))
        np.save(os.path.join(out_dir, f'T_{k}.npy'), s['T'])
    with open(os.path.join(out_dir, 'pairs.json'), 'w', encoding='utf-8') as fh:
        json.dump(res['pairs'], fh, ensure_ascii=False, indent=1)
    with open(os.path.join(out_dir, 'order.json'), 'w', encoding='utf-8') as fh:
        json.dump([dict(names=s['names'], check=s['check']) for s in res['segments']], fh, ensure_ascii=False, indent=1)
