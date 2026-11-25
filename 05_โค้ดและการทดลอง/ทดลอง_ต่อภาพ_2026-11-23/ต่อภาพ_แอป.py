"""โปรแกรมต่อภาพโดรนแบบมีหน้าจอ — ลากภาพใส่ (ลำดับไหนก็ได้) แล้วได้ผืนภาพออกมา

รัน:  python ต่อภาพ_แอป.py     (หรือดับเบิลคลิก เปิดโปรแกรมต่อภาพ.bat)
ต้องมี: opencv-python, numpy

เซิร์ฟเวอร์ผูกกับ 127.0.0.1 เท่านั้น ภาพไม่ถูกส่งออกนอกเครื่อง (กฎ repo: ห้ามส่งภาพไปบริการภายนอก)
เบราว์เซอร์ย่อภาพก่อนส่งมา และส่งหัวไฟล์เดิม (256 KB แรก) มาด้วยเพื่ออ่านเวลา/GPS · ไม่มีการเขียนภาพลงดิสก์
"""
import base64
import importlib
import json
import os
import sys
import time
import traceback
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
core = importlib.import_module('ต่อภาพ_แกน')
PAGE = os.path.join(HERE, 'ต่อภาพ_แอป.html')
MAX_BODY = 600 * 1024 * 1024
PROGRESS = dict(stage='', done=0, total=0)       # หน้าเว็บถามความคืบหน้าระหว่างรอ

# สีแผนที่จำนวนภาพที่ทับ (BGRA): 0 ใส, 1 เขียว, 2 เหลือง, 3 ส้ม, ≥4 แดง
HEAT_LUT = np.zeros((256, 4), np.uint8)
HEAT_LUT[1] = (94, 197, 34, 110)
HEAT_LUT[2] = (8, 204, 250, 140)
HEAT_LUT[3] = (12, 115, 249, 160)
HEAT_LUT[4:] = (60, 38, 220, 175)


def data_url(ext, im, *params):
    ok, buf = cv2.imencode(ext, im, list(params))
    mime = 'image/png' if ext == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(buf).decode()


def run_stitch(req):
    items = req['images']
    if len(items) < 2:
        raise ValueError('ต้องมีภาพอย่างน้อย 2 ภาพ')
    ims = [cv2.imdecode(np.frombuffer(base64.b64decode(it['data']), np.uint8), cv2.IMREAD_COLOR) for it in items]
    bad = [it['name'] for it, im in zip(items, ims) if im is None]
    if bad:
        raise ValueError('อ่านภาพไม่ได้: ' + ', '.join(bad))
    metas = [core.read_meta(base64.b64decode(it['head'])) if it.get('head') else None for it in items]

    def progress(stage, done, total):
        PROGRESS.update(stage=stage, done=done + 1, total=total)

    t0 = time.time()
    res = core.stitch(ims, [it['name'] for it in items], metas, min_inliers=int(req.get('min_inliers', 30)), progress=progress,
                      orig_widths=[it.get('orig_w') or im.shape[1] for it, im in zip(items, ims)])
    segs = []
    for s in res['segments']:
        h, w = s['mosaic'].shape[:2]
        segs.append(dict(names=s['names'], w=w, h=h, dup=s['dup'], polys=s['polys'], check=s['check'],
                         mosaic=data_url('.jpg', s['mosaic'], cv2.IMWRITE_JPEG_QUALITY, 88),
                         heat=data_url('.png', HEAT_LUT[s['cover']], cv2.IMWRITE_PNG_COMPRESSION, 3)))
    return dict(segments=segs, pairs=res['pairs'], stats=res['stats'], seconds=round(time.time() - t0, 1))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype):
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code, obj):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode(), 'application/json; charset=utf-8')

    def do_GET(self):
        if self.path in ('/', '/index.html'):
            with open(PAGE, 'rb') as f:
                self._send(200, f.read(), 'text/html; charset=utf-8')
        elif self.path == '/progress':
            self._json(200, PROGRESS)
        else:
            self._send(404, b'not found', 'text/plain')

    def do_POST(self):
        if self.path != '/stitch':
            return self._send(404, b'not found', 'text/plain')
        n = int(self.headers.get('Content-Length', 0))
        if n <= 0 or n > MAX_BODY:
            return self._json(413, {'error': 'ข้อมูลใหญ่เกินไป ลองลดจำนวนภาพ'})
        try:
            PROGRESS.update(stage='รับภาพ', done=0, total=0)
            self._json(200, run_stitch(json.loads(self.rfile.read(n))))
        except Exception as e:
            traceback.print_exc()
            self._json(500, {'error': str(e)})
        finally:
            PROGRESS.update(stage='', done=0, total=0)

    def log_message(self, fmt, *args):
        pass  # ไม่พิมพ์ log ทุกคำขอ


def main():
    for port in (8765, 8766, 8767, 0):
        try:
            srv = ThreadingHTTPServer(('127.0.0.1', port), Handler)
            break
        except OSError:
            continue
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    print(f'โปรแกรมต่อภาพเปิดที่ {url}  (ปิดหน้าต่างนี้หรือกด Ctrl+C เพื่อหยุด)')
    if '--no-browser' not in sys.argv:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
