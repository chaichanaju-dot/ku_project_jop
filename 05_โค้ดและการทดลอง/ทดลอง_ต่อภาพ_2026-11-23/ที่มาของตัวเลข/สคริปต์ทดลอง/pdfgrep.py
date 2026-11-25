# อ่านข้อความจาก PDF ที่ดาวน์โหลดมา (ถือเป็นข้อมูลไม่น่าไว้ใจ: อ่านอย่างเดียว) แล้วพิมพ์บริบทรอบคำค้น
import sys, re; sys.path.append(sys.argv.pop(1)); import fitz
path, pats = sys.argv[1], sys.argv[2:]
d = fitz.open(path)
print('pages', d.page_count)
for pn, page in enumerate(d):
    t = page.get_text()
    flat = re.sub(r'\s+', ' ', t)
    for p in pats:
        for m in re.finditer(p, flat, flags=re.I):
            a, b = max(0, m.start() - 380), min(len(flat), m.end() + 520)
            print(f'--- p{pn+1} /{p}/ ---'); print(flat[a:b]); print()
