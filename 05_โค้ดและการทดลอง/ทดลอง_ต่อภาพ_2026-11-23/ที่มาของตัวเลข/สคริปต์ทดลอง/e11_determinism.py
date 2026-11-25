import sys, glob, os, importlib, random, json, hashlib, numpy as np, cv2
sys.path.insert(0, 'D:/00mk/เสาพัง/ku_project_jop/05_โค้ดและการทดลอง/ทดลอง_ต่อภาพ_2026-11-23')
core = importlib.import_module('ต่อภาพ_แกน')
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
def short(f): return ('N:' if 'Not use' in f else '') + os.path.basename(f)[4:8]
files = sorted(glob.glob(src + '/*.JPG')) + sorted(glob.glob(src + '/Not use/*.JPG'))
ims = [cv2.imread('small/' + short(f).replace(':', '_') + '.jpg') for f in files]; metas = [core.read_meta(open(f, 'rb').read(core.HEAD_BYTES)) for f in files]
names = [short(f) for f in files]
sig = []
for seed in (0, 1, 2):
    idx = list(range(len(files))); random.Random(seed).shuffle(idx)
    res = core.stitch([ims[k] for k in idx], [names[k] for k in idx], [metas[k] for k in idx])
    pairs = sorted((min(p['a'], p['b']), max(p['a'], p['b']), p['inliers'], p['status'] in ('tree', 'extra')) for p in res['pairs'])
    segs = [s['names'] for s in res['segments']]
    sig.append((hashlib.md5(json.dumps(pairs).encode()).hexdigest()[:8], len(pairs), [len(s) for s in segs], res['segments'][0]['mosaic'].shape[:2], res['stats']['candidates'], res['stats']['gps_rejected']))
    print('shuffle seed', seed, sig[-1])
print('ชุดคู่ภาพ+จำนวนจุดเหมือนกันทุกรอบ:', len({s[0] for s in sig}) == 1)
