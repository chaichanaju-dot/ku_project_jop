# ตรวจข้อสันนิษฐาน: ตัวต่อภาพสำเร็จรูปของ OpenCV ทิ้งภาพเพราะเกณฑ์ความมั่นใจ (pano_confidence_thresh = 1) จริงไหม
import cv2 as _c; _c.ocl.setUseOpenCL(False)
# รันบนสำเนาย่อ 1600 px ที่แคชไว้ — พิมพ์เฉพาะตัวเลข ไม่แสดงภาพ
import glob, os, time, cv2, numpy as np
ims = [cv2.imread(f) for f in sorted(glob.glob('small/*.jpg')) if not os.path.basename(f).startswith('N_')]
print('images', len(ims), ims[0].shape)
for mode_name, mode in (('SCANS', cv2.Stitcher_SCANS), ('PANORAMA', cv2.Stitcher_PANORAMA)):
    for thr in (1.0, 0.7, 0.5, 0.3, 0.1):
        st = cv2.Stitcher_create(mode)
        st.setPanoConfidenceThresh(thr)
        t = time.time(); status, out = st.stitch(ims); dt = time.time() - t
        print(f'{mode_name:8s} thresh {thr:3.1f}: status {status} ' + ('' if out is None else f'ผืน {out.shape[1]}x{out.shape[0]}') + f'  {dt:.1f}s')
