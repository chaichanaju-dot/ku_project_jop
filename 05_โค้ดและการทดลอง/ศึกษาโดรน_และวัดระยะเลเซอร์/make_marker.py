"""สร้างไฟล์ SVG ของ ArUco marker ขนาดจริงเป็นมิลลิเมตร -> สั่งพิมพ์ได้ตรงขนาด
    python make_marker.py 0 200 marker0.svg
"""
import sys, cv2

mid = int(sys.argv[1]) if len(sys.argv) > 1 else 0
mm = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
out = sys.argv[3] if len(sys.argv) > 3 else f"aruco_{mid}_{int(mm)}mm.svg"

N = 6                                   # 4x4 + ขอบดำ 1 ช่อง
bits = cv2.aruco.generateImageMarker(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50), mid, N)
cell = mm / N
quiet = cell                            # quiet zone ขาว 1 ช่อง — ห้ามตัดทิ้ง
total = mm + 2 * quiet

rects = "".join(
    f'<rect x="{quiet + c*cell:.4f}" y="{quiet + r*cell:.4f}" width="{cell:.4f}" height="{cell:.4f}" fill="#000"/>'
    for r in range(N) for c in range(N) if bits[r, c] == 0
)

open(out, "w", encoding="utf-8").write(
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{total}mm" height="{total + 8}mm" '
    f'viewBox="0 0 {total} {total + 8}">'
    f'<rect width="{total}" height="{total + 8}" fill="#fff"/>{rects}'
    f'<text x="{total/2}" y="{total + 5.5}" font-family="Arial" font-size="4" text-anchor="middle">'
    f'ArUco DICT_4X4_50  id={mid}  |  ด้านดำ = {mm:.1f} mm  |  วัดจริงก่อนใช้</text></svg>'
)
print(f"{out}  ด้านดำ {mm} mm, quiet zone {quiet:.1f} mm, กระดาษรวม {total:.1f} mm")
