# เทรน RT-DETR ใหม่จากศูนย์ (ไม่ต่อยอดจาก best.pt รอบ 1/2 อีกต่อไป)
# เหตุผล: dataset เดิมผ่านการรวม/แก้ label หลายรอบจนสะเปะสะปะ ผู้ใช้จะจัดระเบียบ dataset ใหม่ทั้งก้อน
# เทรนต่อจากน้ำหนักเก่าที่เคยเห็น label ที่ยังไม่เรียบร้อยมาก่อน เสี่ยงพาความสับสนเดิมติดไปด้วย
# เลยเริ่มจาก rtdetr-l.pt (pretrained เปล่า) ใหม่ทั้งหมด — ผลเทรนรอบ 1/2 เดิม (runs/train, train-2, train-3)
# ยังเก็บไว้เทียบเฉยๆ ไม่ได้ลบทิ้ง แค่สคริปต์นี้ไม่ไปยุ่งกับมันแล้ว
import subprocess                    # เรียก robocopy sync ข้อมูล (ก๊อปแบบ retry ได้ เสถียรกว่า shutil บน network path ที่หลุดได้)
from pathlib import Path
from ultralytics import RTDETR      # RT-DETR ของ ultralytics ใช้ data.yaml/label format เดียวกับ YOLO detect (กล่อง ไม่ใช่ mask)

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # โฟลเดอร์โปรเจกต์ (สคริปต์นี้อยู่ใน train/ เลยต้องถอยขึ้นมา 1 ชั้น) — อาจเป็น D:\ หรือ \\tsclient\D\ ถ้าต่อผ่าน RDP
NETWORK_DATA_DIR = PROJECT_ROOT / "dataset" / "damage_rtdetr"        # dataset ที่จัดระเบียบใหม่ (ต้องรันสคริปต์เตรียม dataset ให้เสร็จก่อน แล้วผลลัพธ์ต้องอยู่ path นี้เสมอ)
NETWORK_RUNS_DIR = PROJECT_ROOT / "runs" / "rtdetr_damage"           # ผลเทรนสุดท้ายจะถูกก๊อปกลับมาเก็บถาวรที่นี่ (รวมกับผลรอบเก่าในโฟลเดอร์เดียวกัน เทียบกันง่าย)

# เทรนจาก local disk เท่านั้น ห้ามชี้ไป network drive ตรงๆ — เจอมาแล้วจริงว่า RDP หลุดกลางทาง (แม้แค่ 1-2 วิ)
# ทำให้ python อ่าน dataset ไม่ได้ เทรนพังทิ้งทั้งรอบ (เทรนเป็นชั่วโมง หลุดทีเดียวเสียของหมด)
LOCAL_CACHE = Path(r"C:\tbhi_local")
LOCAL_DATA_DIR = LOCAL_CACHE / "dataset" / "damage_rtdetr"
LOCAL_RUNS_DIR = LOCAL_CACHE / "runs" / "rtdetr_damage"
DATA_YAML = LOCAL_DATA_DIR / "data.yaml"

# 6 คลาสความเสียหายที่ตกลงกันไว้ — แค่จดไว้อ้างอิง ลำดับจริงต้องตรงกับที่ตั้งไว้ตอน label ใน Roboflow (ดูใน data.yaml)
CLASSES = ["Crack", "Efflorescence", "Rust_Stain", "Spalling", "Exposed_Rebar", "Honeycomb"]

PRETRAINED = "rtdetr-l.pt"          # เริ่มจากโมเดลสำเร็จรูปเปล่าๆ (ไม่ใช่ best.pt เก่า) — ตัดปัญหาน้ำหนักเก่าที่เห็น label สะเปะสะปะมาก่อน
EPOCHS = 300                        # ตั้งไว้สูง เพราะมี early stopping (patience) มาหยุดเองถ้าไม่ดีขึ้นแล้ว
PATIENCE = 50                       # ไม่ดีขึ้นติดกัน 50 epoch ก็หยุดเทรน กันจำข้อมูล train จนเกินไป (overfit)
IMGSZ = 960                         # ภาพหลายใบใน dataset มีความละเอียดต้นฉบับสูงกว่า 640px จริง (ไม่ได้ถูกบีบตั้งแต่ export แล้ว) ใช้ 960 ให้เห็นรอยร้าวเล็กๆ ชัดขึ้น
BATCH = 8                           # ปรับตาม VRAM จริง (เช็คจาก nvidia-smi ตอนเทรนถ้า error out of memory ให้ลดลง)
DEVICE = 0                          # ใช้ GPU ตัวแรก (RTX 5070 Ti)


def main():
    # ต้องครอบส่วนที่รันจริงด้วย if __name__ == "__main__" เพราะ Windows ใช้ multiprocessing แบบ spawn
    # (ultralytics เปิด dataloader worker หลาย process ตอนเทรน) ถ้าไม่ครอบ โค้ดระดับบนสุดจะถูกรันซ้ำในทุก worker จนวนลูปไม่จบ
    if not NETWORK_DATA_DIR.exists():
        raise FileNotFoundError(
            f"ไม่เจอ dataset ที่ {NETWORK_DATA_DIR} — ต้องจัดระเบียบ/export dataset ใหม่ให้เสร็จก่อน "
            "แล้วผลลัพธ์ต้องอยู่ path นี้เสมอ (train/valid/test + data.yaml)"
        )

    # sync dataset จาก network มา local ก่อนเทรนทุกครั้ง (robocopy ก๊อปแค่ไฟล์ที่เปลี่ยน/ใหม่ ถ้ารันซ้ำจะเร็วขึ้นมาก)
    # robocopy คืน exit code 0-7 = สำเร็จ (แค่ต่างเฉดสำเร็จ), >=8 ถึงจะถือว่า error จริง เลยไม่เช็ค returncode แบบโปรแกรมทั่วไป
    subprocess.run(["robocopy", str(NETWORK_DATA_DIR), str(LOCAL_DATA_DIR), "/E", "/NFL", "/NDL", "/NJH", "/NJS"])

    # split_labels.py/reexport_lock_split.py เขียน path เต็มของ network ไว้ใน data.yaml (บรรทัด "path: ...") ต้องแก้ให้ชี้ local แทนก่อนเทรน
    yaml_text = DATA_YAML.read_text(encoding="utf-8")
    yaml_text = yaml_text.replace(str(NETWORK_DATA_DIR), str(LOCAL_DATA_DIR))
    DATA_YAML.write_text(yaml_text, encoding="utf-8")

    model = RTDETR(PRETRAINED)  # โหลดโมเดลสำเร็จรูปเปล่าๆ มาต่อยอด (transfer learning จากศูนย์ ไม่ใช่จาก best.pt เก่า)

    model.train(
        data=str(DATA_YAML),        # path data.yaml ของ dataset ความเสียหาย (local แล้ว)
        epochs=EPOCHS,               # จำนวนรอบเทรนสูงสุด (early stopping จะตัดก่อนถ้าไม่ดีขึ้น)
        patience=PATIENCE,           # early stopping — กันเทรนนานเกินจนจำข้อมูล train เป๊ะ
        imgsz=IMGSZ,                  # ขนาดภาพที่ใช้เทรน
        batch=BATCH,                  # จำนวนภาพต่อรอบอัปเดต (ปรับตาม VRAM)
        device=DEVICE,                # เทรนบน GPU
        project=str(LOCAL_RUNS_DIR),  # เซฟผลลง local ระหว่างเทรน (กัน checkpoint เสียหายถ้า network หลุดกลางทาง)
        name="train",                 # ปล่อยให้ ultralytics เติมเลขต่อท้ายเอง (train-4) ต่อจาก train-3 เดิม
        plots=True,                   # เซฟกราฟ PR/F1/confusion matrix ไว้ดูตอนวิเคราะห์ผล (ต้องดูทุกครั้งตาม memory rule)
    )

    # เทรนเสร็จแล้วค่อย sync ผลกลับไปเก็บถาวรที่ project จริง (network drive) — ทำทีเดียวหลังเทรนจบ ไม่เสี่ยงระหว่างเทรน
    subprocess.run(["robocopy", str(LOCAL_RUNS_DIR), str(NETWORK_RUNS_DIR), "/E", "/NFL", "/NDL", "/NJH", "/NJS"])

    print("เทรนใหม่เสร็จแล้ว — เช็คผลที่", NETWORK_RUNS_DIR,
          "(โฟลเดอร์ train-4 หรือเลขล่าสุด) เทียบกับ train-3 (รอบเก่า) แล้วอัปเดต training_log.md กับ work_diary.md ตามที่ตกลงกันไว้")


if __name__ == "__main__":
    main()
