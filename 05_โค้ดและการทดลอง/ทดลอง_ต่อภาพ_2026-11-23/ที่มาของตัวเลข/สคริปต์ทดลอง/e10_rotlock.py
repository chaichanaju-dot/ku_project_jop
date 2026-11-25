# E10: ถ้าล็อกไม่ให้ภาพหมุน (กล้องโดรนได้ระดับ: roll=0, pitch=0 ทุกภาพ) ผืนตรงกับความสูงจริงขึ้นไหม
import sys, glob, os, importlib, random, numpy as np, cv2
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
def short(f): return ('N:' if 'Not use' in f else '') + os.path.basename(f)[4:8]
P2 = sorted(glob.glob(src + '/*.JPG')); P1 = sorted(glob.glob(src + '/Not use/*.JPG'))
orig_layout = core._layout
def make_layout(lock):
    def _layout(nodes, E, keys, width):
        if len(nodes) == 1: return {nodes[0]: np.eye(3)}
        adj, root, used = core._tree(nodes, E, keys)
        for k in used: E[k]['tree'] = True
        T, q = {root: np.eye(3)}, [root]
        for u in q:
            for v in adj[u]:
                if v not in T:
                    M = E[(u, v)]['M'] if (u, v) in E else np.linalg.inv(E[(v, u)]['M'])
                    T[v] = T[u] @ M; q.append(v)
        free = [k for k in nodes if k != root]; pos = {k: 4 * n for n, k in enumerate(free)}
        B = {}
        for k in keys:
            J = np.hstack([core._A(E[k]['pi']), -core._A(E[k]['pj'])])
            B[k] = (J.T @ J) * (min(len(E[k]['pi']), 150) / len(E[k]['pi']))
        th = {k: np.array([T[k][0, 0], T[k][1, 0], T[k][0, 2], T[k][1, 2]]) for k in nodes}
        def resid(k):
            v = np.concatenate([th[k[0]], th[k[1]]]); return float(np.sqrt(max(v @ B[k] @ v, 0) / min(len(E[k]['pi']), 150)))
        for _ in range(6):
            N, rhs = np.zeros((4 * len(free),) * 2), np.zeros(4 * len(free))
            for k in keys:
                w = 1.0 / (1.0 + (resid(k) / (0.03 * width)) ** 2)
                for s, u in enumerate(k):
                    for t, v in enumerate(k):
                        blk = w * B[k][4 * s:4 * s + 4, 4 * t:4 * t + 4]
                        if u != root and v != root: N[pos[u]:pos[u] + 4, pos[v]:pos[v] + 4] += blk
                        elif u != root: rhs[pos[u]:pos[u] + 4] -= blk @ th[root]
            if lock:
                for k in free: N[pos[k] + 1, pos[k] + 1] += lock
            sol = np.linalg.solve(N + 1e-9 * np.eye(len(N)), rhs)
            for k in free: th[k] = sol[pos[k]:pos[k] + 4]
        for k in keys: E[k]['resid'] = resid(k)
        T = {k: np.array([[v[0], -v[1], v[2]], [v[1], v[0], v[3]], [0, 0, 1]]) for k, v in th.items()}
        rot = np.median([np.arctan2(t[1, 0], t[0, 0]) for t in T.values()]); sc = np.median([np.hypot(t[0, 0], t[1, 0]) for t in T.values()])
        c, s = np.cos(-rot) / sc, np.sin(-rot) / sc
        G = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        return {k: G @ t for k, t in T.items()}
    return _layout
def run(files, lock, label):
    ims = [cv2.imread('small/' + short(f).replace(':', '_') + '.jpg') for f in files]; metas = [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
    names = [short(f) for f in files]
    core._layout = make_layout(lock)
    res = core.stitch(ims, names, metas); seg = res['segments'][0]
    cen = {nm: (seg['T'][n] @ np.array([800, 600, 1]))[:2] for n, nm in enumerate(seg['names'])}
    pos = core._enu(metas); ses = core._sessions(metas)
    g = [k for k, nm in enumerate(names) if nm in cen]
    P = np.array([pos[k][:2] for k in g]); alt = np.array([pos[k][2] for k in g]); along = (P - P.mean(0)) @ np.linalg.svd(P - P.mean(0), full_matrices=False)[2][0]
    C = np.array([cen[names[k]] for k in g]); S = np.array([[float(ses[k] == s) for s in sorted(set(ses))] for k in g])
    sol = np.linalg.lstsq(np.c_[C[:, 0], S], along, rcond=None)[0]; r = along - np.c_[C[:, 0], S] @ sol; gsd = abs(sol[0])
    sol2 = np.linalg.lstsq(np.c_[C[:, 1], S], alt, rcond=None)[0]; r2 = alt - np.c_[C[:, 1], S] @ sol2
    rs = np.array([p['resid'] for p in res['pairs'] if p['ok']]); rot = [np.degrees(np.arctan2(t[1, 0], t[0, 0])) for t in seg['T']]
    h, w = seg['mosaic'].shape[:2]
    print(f'{label:34s} ผืน {w}×{h} | คู่คลาด median {np.median(rs):.1f} p90 {np.percentile(rs,90):.1f} max {rs.max():.1f} px | GPS แนวนอน rms {np.sqrt((r**2).mean()):.3f} ม. | แนวตั้ง: ความชัน {abs(sol2[0])*1000:.2f} vs แนวนอน {gsd*1000:.2f} มม./px (อัตราส่วน {abs(sol2[0])/gsd:.2f}), คลาดจากความสูง rms {np.sqrt((r2**2).mean()):.3f} ม. | มุมหมุน {min(rot):.2f}..{max(rot):.2f}°')
for lock in (0, 1e12):
    run(P2, lock, f'รอบบิน 2 lock={lock:g}')
for lock in (0, 1e12):
    run(P2 + P1, lock, f'สองรอบบิน lock={lock:g}')
