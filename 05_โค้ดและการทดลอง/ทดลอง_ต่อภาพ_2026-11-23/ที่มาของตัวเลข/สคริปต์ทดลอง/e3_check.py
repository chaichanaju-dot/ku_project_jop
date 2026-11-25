import json, itertools, numpy as np, networkx as nx
d = json.load(open('e1.json')); names = d['names']; n = len(names); shapes = d['shapes']
short = [x.replace('Not use/', 'N:').replace('DJI_', '').replace('.JPG', '') for x in names]
full = {(r['i'], r['j']): r for r in d['res']['full']}
e2 = json.load(open('e2.json')); ov = {tuple(map(int, k.split(','))): v for k, v in e2['ov'].items()}
T = {int(k): np.array(v) for k, v in e2['T'].items()}
z = [(full[p]['inl'], full[p]['good'], short[p[0]], short[p[1]]) for p, v in ov.items() if v == 0]
z.sort(reverse=True)
print('pairs with ZERO geometric overlap:', len(z), '| top inliers:', z[:12])
zc = sorted([(round(full[p]['inl'] / (8 + 0.3 * full[p]['good']), 2), full[p]['inl'], short[p[0]], short[p[1]]) for p, v in ov.items() if v == 0], reverse=True)[:8]
print('  top conf among zero-overlap:', zc)
# ขอบของ N:0312
k = short.index('N:0312')
print('edges of N:0312 (other, inl, good, scale, rot, dx, dy  | tree-predicted dx,dy):')
for (i, j), r in full.items():
    if k in (i, j) and r['inl'] >= 15:
        M = np.vstack([np.array(r['M']), [0, 0, 1]])           # j -> i
        Mk = M if j == k else np.linalg.inv(M)                 # k -> other
        o = i if j == k else j
        P = np.linalg.inv(T[o]) @ T[k]                         # tree-predicted k -> other
        print('  ', short[o], r['inl'], r['good'], round(float(np.hypot(Mk[0, 0], Mk[1, 0])), 3), round(float(np.degrees(np.arctan2(Mk[1, 0], Mk[0, 0]))), 2),
              round(Mk[0, 2]), round(Mk[1, 2]), '|', round(P[0, 2]), round(P[1, 2]), 'scale', round(float(np.hypot(P[0, 0], P[1, 0])), 3))
# ตำแหน่งกลางภาพบนผืน (ตามต้นไม้) เรียงตาม x
c = {i: (T[i] @ np.array([shapes[i][1] / 2, shapes[i][0] / 2, 1]))[:2] for i in range(n)}
order = sorted(range(n), key=lambda i: c[i][0])
print('order along mosaic x:', [short[i] for i in order])
print('scale per image (tree):', {short[i]: round(float(np.hypot(T[i][0, 0], T[i][1, 0])), 2) for i in order})
print('rotation per image (deg, tree):', {short[i]: round(float(np.degrees(np.arctan2(T[i][1, 0], T[i][0, 0]))), 1) for i in order})
