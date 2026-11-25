# E2: สร้างกราฟจากผลจับคู่ทุกคู่ ดูการกระจายของ inlier หา component วางภาพ แล้วเช็กคู่หลอก
import json, itertools, numpy as np, networkx as nx
d = json.load(open('e1.json')); names = d['names']; n = len(names); shapes = d['shapes']
short = [x.replace('Not use/', 'N:').replace('DJI_', '').replace('.JPG', '') for x in names]
full = {(r['i'], r['j']): r for r in d['res']['full']}; cheap = {(r['i'], r['j']): r for r in d['res']['cheap']}
inl = np.array([r['inl'] for r in d['res']['full']])
print('full: pairs', len(inl), '| inl>=30:', (inl >= 30).sum(), '| 15-29:', ((inl >= 15) & (inl < 30)).sum(), '| 8-14:', ((inl >= 8) & (inl < 15)).sum(), '| <8:', (inl < 8).sum())
print('histogram of inliers (all pairs):', np.histogram(inl, bins=[0, 4, 8, 12, 16, 20, 30, 50, 100, 200, 500, 2000])[0].tolist())
def ok(r, mi=30): return r['inl'] >= mi and 1/3 <= r.get('scale', 0) <= 3
G = nx.Graph(); G.add_nodes_from(range(n))
for (i, j), r in full.items():
    if ok(r): G.add_edge(i, j, w=r['inl'], M=np.vstack([np.array(r['M']), [0, 0, 1]]))  # M: j -> i
comps = sorted(nx.connected_components(G), key=len, reverse=True)
print('components:', [len(c) for c in comps], '| edges', G.number_of_edges())
# วางภาพ: maximum spanning tree จากราก = จุดกึ่งกลางของต้นไม้
T_all = {}
for c in comps:
    sub = G.subgraph(c); mst = nx.maximum_spanning_tree(sub, weight='w')
    root = nx.center(mst)[0] if len(c) > 1 else next(iter(c))
    T = {root: np.eye(3)}
    for a, b in nx.bfs_edges(mst, root):
        i, j = min(a, b), max(a, b); M = G[i][j]['M']        # พา j -> i
        T[b] = T[a] @ (M if b == j else np.linalg.inv(M))
    T_all.update(T)
    print(' comp size', len(c), 'root', short[root], 'tree depth', max(nx.shortest_path_length(mst, root).values()), 'mst edges', mst.number_of_edges(), 'extra edges', sub.number_of_edges() - mst.number_of_edges())
# ตรวจขอบที่ไม่อยู่ในต้นไม้: การแปลงของมันเข้ากับตำแหน่งที่ต้นไม้ให้ไหม (คลาดที่มุมภาพ)
def corner_err(i, j, M):
    h, w = shapes[j]; c = np.float32([[0, 0, 1], [w, 0, 1], [w, h, 1], [0, h, 1]]).T
    a = (T_all[i] @ M @ c)[:2]; b = (T_all[j] @ c)[:2]
    return float(np.sqrt(((a - b) ** 2).sum(0)).max())
errs = [(corner_err(i, j, G[i][j]['M']), i, j, G[i][j]['w']) for i, j in G.edges()]
e = np.array([x[0] for x in errs])
print('edge consistency vs tree layout (max corner error px): median %.1f  p90 %.1f  max %.1f' % (np.median(e), np.percentile(e, 90), e.max()))
print('edges with corner error > 60px:', [(short[i], short[j], w, round(x)) for x, i, j, w in sorted(errs, reverse=True) if x > 60][:20])
# ความจริงเชิงเรขาคณิต: คู่ที่กรอบภาพซ้อนกันบนผืน (จากตำแหน่งต้นไม้)
import cv2
def poly(i):
    h, w = shapes[i]; c = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    return cv2.perspectiveTransform(c, T_all[i]).reshape(-1, 2)
P = [poly(i) for i in range(n)]
def iou_small(i, j):
    ret, inter = cv2.intersectConvexConvex(P[i].astype(np.float32), P[j].astype(np.float32))
    return ret / min(cv2.contourArea(P[i].astype(np.float32)), cv2.contourArea(P[j].astype(np.float32)))
ov = {(i, j): iou_small(i, j) for i, j in itertools.combinations(range(n), 2)}
true = {p for p, v in ov.items() if v > 0.10}
edges = {(min(i, j), max(i, j)) for i, j in G.edges()}
print('geometric overlap>10%% pairs: %d | verified edges: %d | edges that are NOT overlapping (false): %d | overlapping but no edge: %d' % (len(true), len(edges), len(edges - true), len(true - edges)))
print(' false edges:', [(short[i], short[j], full[(i, j)]['inl'], round(ov[(i, j)], 2)) for i, j in sorted(edges - true)])
miss = sorted(true - edges, key=lambda p: -ov[p])
print(' overlapping pairs without edge (ov, inl, good):', [(short[i], short[j], round(ov[(i, j)], 2), full[(i, j)]['inl'], full[(i, j)]['good']) for i, j in miss][:30])
# inlier ของคู่จริง vs คู่ไม่ซ้อน
ti = np.array([full[p]['inl'] for p in true]); fi = np.array([full[p]['inl'] for p in ov if p not in true])
print('inliers of truly-overlapping pairs: min %d  p10 %d  median %d' % (ti.min(), np.percentile(ti, 10), np.median(ti)), '| non-overlapping pairs: max %d  p99 %d  median %d' % (fi.max(), np.percentile(fi, 99), np.median(fi)))
# Brown-Lowe / OpenCV confidence = inl / (8 + 0.3*good)
conf = lambda r: r['inl'] / (8 + 0.3 * r['good'])
tc = np.array([conf(full[p]) for p in true]); fc = np.array([conf(full[p]) for p in ov if p not in true])
print('conf of overlapping pairs: min %.2f p10 %.2f median %.2f | non-overlapping: max %.2f p99 %.2f' % (tc.min(), np.percentile(tc, 10), np.median(tc), fc.max(), np.percentile(fc, 99)))
print('overlapping pairs with conf<1.0 (OpenCV default จะตัดทิ้ง):', sum(tc < 1.0), 'of', len(tc))
# cheap pass: เก็บคู่จริงได้แค่ไหน
for thr in (8, 10, 12, 15, 20):
    cand = {p for p, r in cheap.items() if r['inl'] >= thr}
    print('cheap inl>=%d: candidates %d | recall of verified edges %.3f | recall of overlap>10%% %.3f | precision(overlap) %.2f' % (thr, len(cand), len(cand & edges) / len(edges), len(cand & true) / len(true), len(cand & true) / max(1, len(cand))))
json.dump(dict(T={str(k): v.tolist() for k, v in T_all.items()}, ov={f'{i},{j}': v for (i, j), v in ov.items()}, edges=sorted(edges), true=sorted(true)), open('e2.json', 'w'))
# rotation ของคู่ติดกันในรอบบิน 2
print('rot(deg) & scale of consecutive pairs in pass 2:', [(short[j], round(full[(i, j)]['rot'], 2), round(full[(i, j)]['scale'], 3)) for i, j in [(k, k + 1) for k in range(0, 20)]])
