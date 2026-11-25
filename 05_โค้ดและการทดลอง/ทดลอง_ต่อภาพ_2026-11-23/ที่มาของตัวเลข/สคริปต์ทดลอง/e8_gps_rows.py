import sys, glob, os, importlib, numpy as np, cv2
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
def short(f): return ('N:' if 'Not use' in f else '') + os.path.basename(f)[4:8]
def rows_for(files, label):
    ims = [cv2.imread('small/' + short(f).replace(':', '_') + '.jpg') for f in files]
    metas = [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
    F = [core._features(im) for im in ims]; n = len(ims); shapes = [im.shape[:2] for im in ims]
    E = {}
    for i in range(n):
        for j in range(i + 1, n):
            e = core._verify(F[i], F[j], 1600.0, 30)
            if e: E[(i, j)] = e
    pos, ses = core._enu(metas), core._sessions(metas)
    print(f'--- {label}: edges {len(E)}')
    out = []
    for (i, j), e in sorted(E.items()):
        if ses[i] != ses[j]: continue
        ci = np.array([shapes[i][1] / 2, shapes[i][0] / 2]); cj = (e['M'] @ np.array([shapes[j][1] / 2, shapes[j][0] / 2, 1.0]))[:2]
        dg = float(np.linalg.norm(pos[i] - pos[j])); dh = float(np.linalg.norm(pos[i][:2] - pos[j][:2])); dp = float(np.linalg.norm(cj - ci))
        out.append((short(files[i]), short(files[j]), e['inl'], round(e['conf'], 2), round(dg, 2), round(dh, 2), round(dp), round(dg / dp * 1000, 2) if dp > 1 else None, round(e['scale'], 2)))
    for r in out: print('  ', r)
    return out
P2 = sorted(glob.glob(src + '/*.JPG')); P1 = sorted(glob.glob(src + '/Not use/*.JPG'))
print('(a, b, inl, conf, d_gps3d m, d_gps_horiz m, d_img px, mm/px, scale)')
r1 = rows_for(P1, 'pass 1')
r2 = rows_for(P2, 'pass 2')
