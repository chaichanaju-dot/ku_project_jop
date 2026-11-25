import cv2, glob, numpy as np, os, time
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
fs = sorted(glob.glob(os.path.join(src, '*.JPG')))
ims = [cv2.resize(cv2.imdecode(np.fromfile(f, np.uint8), 1), (1600, 1200), interpolation=cv2.INTER_AREA) for f in fs]
for name, mode in [('scans', cv2.Stitcher_SCANS), ('pano', cv2.Stitcher_PANORAMA)]:
    t = time.time()
    st = cv2.Stitcher_create(mode)
    code, out = st.stitch(ims)
    print(name, 'status', code, 'sec %.0f' % (time.time() - t), None if out is None else out.shape)
    if code == 0: cv2.imwrite(f'stitcher_{name}.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 85])
