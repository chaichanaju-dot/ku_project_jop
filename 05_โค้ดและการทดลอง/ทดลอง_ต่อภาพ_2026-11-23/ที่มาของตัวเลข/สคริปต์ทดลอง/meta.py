# อ่าน metadata จากภาพ (EXIF ผ่าน Pillow + XMP ของ DJI ด้วย regex) — พิมพ์เฉพาะตัวเลข ไม่เปิดภาพ
import glob, os, re, sys, json
from PIL import Image, ExifTags
src = "D:/00mk/เสาพัง/ku_project_jop/04_ภาพและข้อมูลสนาม/ภาพโดรน_Agisoft"
fs = sorted(glob.glob(src + '/*.JPG') + glob.glob(src + '/Not use/*.JPG'))
def xmp(path):
    b = open(path, 'rb').read(400000)
    i = b.find(b'<x:xmpmeta'); j = b.find(b'</x:xmpmeta>')
    return b[i:j + 12].decode('utf-8', 'replace') if i >= 0 else ''
rows = []
for k, f in enumerate(fs):
    im = Image.open(f); ex = im.getexif()
    d = {ExifTags.TAGS.get(t, t): v for t, v in ex.items()}
    sub = {ExifTags.TAGS.get(t, t): v for t, v in ex.get_ifd(0x8769).items()}
    gps = {ExifTags.GPSTAGS.get(t, t): v for t, v in ex.get_ifd(0x8825).items()}
    x = xmp(f)
    xa = dict(re.findall(r'([A-Za-z\-]+:[A-Za-z0-9]+)="([^"]*)"', x))
    if k == 0:
        print('== EXIF IFD0:', {k2: (str(v)[:60]) for k2, v in d.items() if k2 not in ('XPComment', 'XPKeywords')})
        print('== EXIF sub:', {k2: (str(v)[:50]) for k2, v in sub.items() if k2 not in ('MakerNote', 'UserComment')})
        print('== GPS:', {k2: str(v)[:60] for k2, v in gps.items()})
        print('== XMP attrs:'); [print('   ', a, '=', v[:70]) for a, v in xa.items()]
        print('== XMP length', len(x))
    rows.append(dict(name=os.path.relpath(f, src).replace(os.sep, '/'), exif=d.get('DateTime'), dto=sub.get('DateTimeOriginal'), subsec=sub.get('SubsecTimeOriginal'),
                     model=d.get('Model'), fl=float(sub.get('FocalLength', 0) or 0), fl35=sub.get('FocalLengthIn35mmFilm'), dz=str(sub.get('DigitalZoomRatio')),
                     gps={k2: str(v) for k2, v in gps.items()}, xmp=xa))
json.dump(rows, open('meta_raw.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('n', len(rows))
