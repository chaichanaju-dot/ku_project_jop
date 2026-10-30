# วิเคราะห์ผลเทรนอัตโนมัติ — รันหลังเทรนเสร็จทุกครั้ง
# ทำ 3 อย่างที่ตกลงกันไว้ให้ครบในคำสั่งเดียว:
#   1. วัดผลรายคลาสบน test (และ test_core ถ้ามี) → รู้ว่าคลาสไหนแม่น คลาสไหนไม่แม่น
#   2. นับจำนวนตัวอย่างแต่ละคลาสในทุก split → รู้ว่าคลาสไหนบางเกินไปจนวัดผลไม่น่าเชื่อถือ
#   3. เตือนเองว่าคลาสไหนควร "เติม train" (แม่นน้อย) และคลาสไหนควร "ย้ายเข้า test" (บางเกินไป)
#
# วิธีรัน:  python analyze_results.py                     (ใช้ผลเทรนรอบล่าสุดอัตโนมัติ)
#          python analyze_results.py runs/rtdetr_damage/train-4   (ระบุรอบเองก็ได้)
import sys                              # อ่าน argument ที่ผู้ใช้พิมพ์ต่อท้ายคำสั่ง
import collections                      # ใช้ Counter นับจำนวนตัวอย่างต่อคลาส
from pathlib import Path
from ultralytics import RTDETR

PROJECT_ROOT = Path(__file__).resolve().parent.parent  # ถอยขึ้นมา 2 ชั้น (สคริปต์นี้อยู่ใน bridge_damage_yolo_rtdetr/) ให้ตรงกับ D:\Project AI
DATA_DIR = PROJECT_ROOT / "dataset" / "damage_rtdetr"
RUNS_DIR = PROJECT_ROOT / "runs" / "rtdetr_damage"
CLASSES = ["Crack", "Efflorescence", "Rust_Stain", "Spalling", "Exposed_Rebar", "Honeycomb"]

MIN_TEST_PER_CLASS = 10                 # ต่ำกว่านี้ถือว่า test บางเกินไป ตัวเลขแกว่งจนเชื่อไม่ได้ (ถูก/ผิดภาพเดียวคะแนนกระโดด 20-30%)
WEAK_MAP_THRESHOLD = 0.30               # mAP ต่ำกว่านี้ถือว่าคลาสนี้ยังอ่อน ควรหาภาพเพิ่มลง train


def find_latest_run():
    # หาโฟลเดอร์ผลเทรนที่ใหม่ที่สุด (ดูจากเวลาที่ไฟล์ best.pt ถูกสร้าง) เพื่อไม่ต้องพิมพ์ชื่อรอบเอง
    runs = [d for d in RUNS_DIR.iterdir() if (d / "weights" / "best.pt").exists()]
    if not runs:
        raise FileNotFoundError(f"ไม่เจอผลเทรนที่มี best.pt ใน {RUNS_DIR} — ต้องเทรนให้เสร็จก่อน")
    return max(runs, key=lambda d: (d / "weights" / "best.pt").stat().st_mtime)


def count_instances(split):
    # นับว่าแต่ละคลาสมีกี่ "ตัวอย่าง" (annotation) ใน split นั้น — ไม่ใช่นับจำนวนภาพ เพราะ 1 ภาพมีได้หลายตัวอย่าง
    counter = collections.Counter()
    label_dir = DATA_DIR / split / "labels"
    if not label_dir.exists():
        return counter
    for txt in label_dir.glob("*.txt"):
        for line in txt.read_text(encoding="utf-8").splitlines():
            if line.strip():                                     # ข้ามบรรทัดว่าง (ภาพที่ไม่มี label)
                counter[CLASSES[int(line.split()[0])]] += 1      # ตัวเลขตัวแรกของบรรทัดคือหมายเลขคลาส
    return counter


def per_class_map(run_dir, data_yaml):
    # โหลดโมเดลที่เทรนเสร็จแล้วมาวัดผลใหม่บนชุดที่ระบุ แล้วดึง mAP รายคลาสออกมา
    model = RTDETR(str(run_dir / "weights" / "best.pt"))
    # workers=0 = ไม่แตก process ย่อยมาช่วยโหลดภาพ — ภาพ test มีไม่กี่สิบภาพ ไม่ต้องใช้ และกันปัญหา multiprocessing บน Windows
    metrics = model.val(data=str(data_yaml), split="test", workers=0, verbose=False)
    result = {}
    for i, name in enumerate(CLASSES):
        # ใช้ ap50 (ความแม่นที่เกณฑ์ทับซ้อน 0.5) ให้เป็นมาตรฐานเดียวกับ mAP@0.5 รวมด้านล่าง จะได้อ่านเทียบกันได้
        # (ถ้าใช้ metrics.box.maps จะได้ mAP50-95 ซึ่งเข้มกว่า ตัวเลขจะต่ำกว่าและเทียบกับ training_log เดิมไม่ได้)
        result[name] = float(metrics.box.ap50[i])
    result["_overall"] = float(metrics.box.map50)                # mAP@0.5 รวมทุกคลาส
    return result


def main():
    # ต้องครอบด้วย if __name__ == "__main__" เพราะ Windows ใช้ multiprocessing แบบ spawn
    # ถ้าโค้ดอยู่ระดับบนสุด มันจะถูกรันซ้ำในทุก worker จนพัง (เจอมาแล้วจริงตอนทดสอบสคริปต์นี้)
    run_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else find_latest_run()
    print(f"วิเคราะห์ผลจาก: {run_dir.name}\n")

    train_counts = count_instances("train")
    valid_counts = count_instances("valid")
    test_counts = count_instances("test")
    scores = per_class_map(run_dir, DATA_DIR / "data.yaml")

    print(f"\nmAP@0.5 รวมทุกคลาส = {scores['_overall']:.3f}\n")
    print(f"{'Class':<16}{'train':>8}{'valid':>8}{'test':>8}{'mAP':>10}   สถานะ")
    print("-" * 70)

    need_more_train, need_more_test = [], []
    for name in CLASSES:
        flags = []
        if test_counts[name] < MIN_TEST_PER_CLASS:
            flags.append("test บาง")                              # วัดผลไม่น่าเชื่อถือ ต้องย้ายภาพเข้า test
            need_more_test.append(name)
        if scores[name] < WEAK_MAP_THRESHOLD:
            flags.append("ยังอ่อน")                               # โมเดลยังทำได้ไม่ดี ต้องเติมภาพลง train
            need_more_train.append(name)
        print(f"{name:<16}{train_counts[name]:>8}{valid_counts[name]:>8}{test_counts[name]:>8}"
              f"{scores[name]:>10.3f}   {', '.join(flags) if flags else 'ok'}")

    print("\n" + "=" * 70)
    if need_more_train:
        print(f"ควรหาภาพเพิ่มลง TRAIN (โมเดลยังทำได้ไม่ดี): {', '.join(need_more_train)}")
    if need_more_test:
        print(f"ควรย้ายภาพจาก train เข้า TEST (ตัวอย่างน้อยเกินไปจนวัดผลไม่น่าเชื่อถือ): {', '.join(need_more_test)}")
    if not need_more_train and not need_more_test:
        print("ทุกคลาสผ่านเกณฑ์ทั้งจำนวนตัวอย่างและความแม่นยำ")
    print("=" * 70)
    print("\nอย่าลืมอัปเดต สรุป/training_log.md ด้วยผลรอบนี้")


if __name__ == "__main__":
    main()
