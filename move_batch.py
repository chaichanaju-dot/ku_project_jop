# ย้ายภาพชุดหนึ่งจากโฟลเดอร์ต้นทาง ไปโฟลเดอร์ปลายทาง แบบ move จริง (ต้นทางหายไปแน่นอน)
# รันซ้ำได้เรื่อยๆ — ทุกครั้งจะหยิบเฉพาะภาพที่ "ยังไม่เคยถูกย้าย" เพราะภาพที่ย้ายไปแล้วจะหายจากต้นทางเอง
import shutil
from pathlib import Path

SOURCE_DIR = r"D:\Project AI\ใส่โฟลเดอร์ต้นทาง"     # โฟลเดอร์ที่ดาวน์โหลดภาพมากองไว้
DEST_DIR = r"D:\Project AI\ใส่โฟลเดอร์ปลายทาง"       # โฟลเดอร์ที่จะเอาไปอัปโหลด Roboflow
BATCH_SIZE = 50                                        # จำนวนภาพที่จะย้ายต่อรอบ (ปรับได้ตามต้องการ)

Path(DEST_DIR).mkdir(parents=True, exist_ok=True)      # สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี

# หาไฟล์ภาพทั้งหมดในต้นทาง (นับเฉพาะนามสกุลรูปภาพทั่วไป)
images = [p for p in Path(SOURCE_DIR).iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")]

batch = images[:BATCH_SIZE]                            # หยิบมาแค่ BATCH_SIZE แรก
for img in batch:
    shutil.move(str(img), str(Path(DEST_DIR) / img.name))  # move จริง (ไม่ใช่ copy) ต้นทางหายไปแน่นอน

print(f"ย้ายไปแล้ว {len(batch)} ภาพ | เหลือในต้นทาง {len(images) - len(batch)} ภาพ")
