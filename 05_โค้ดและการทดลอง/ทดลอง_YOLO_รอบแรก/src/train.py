import sys
from pathlib import Path

import torch
import yaml
from ultralytics import YOLO

DATA = "data.yaml"
WEIGHTS = "yolo26n-obb.pt"
EPOCHS = 150
IMGSZ = 640
BATCH = 4

cfg = yaml.safe_load(Path(DATA).read_text(encoding="utf-8"))

for split in ("train", "val"):
    images_dir = Path(cfg[split])
    labels_dir = images_dir.parent / "labels" if images_dir.name == "images" else images_dir / "labels"
    for f in list(labels_dir.glob("*.txt"))[:20]:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.strip() and len(line.split()) != 9:
                sys.exit(f"[error] {f} isn't OBB format (expected 9 values/line: class + 8 coords) "
                         f"- re-export the dataset from Roboflow as 'YOLO OBB'")

model = YOLO(WEIGHTS)
if model.task != "obb":
    sys.exit(f"[error] {WEIGHTS} loaded as task='{model.task}', need an *-obb.pt weight")

device = "0" if torch.cuda.is_available() else "cpu"
batch = BATCH
while True:
    try:
        model.train(data=DATA, epochs=EPOCHS, imgsz=IMGSZ, batch=batch, device=device, workers=0)
        break
    except torch.cuda.OutOfMemoryError:
        torch.cuda.empty_cache()
        if batch <= 1:
            sys.exit("[error] CUDA out of memory even at batch=1 - try a smaller IMGSZ")
        batch //= 2
        print(f"[warn] CUDA out of memory - retrying with batch={batch}")

metrics = model.val()
print(f"best weights: {model.trainer.best}")
print(f"mAP50={metrics.box.map50:.4f}  mAP50-95={metrics.box.map:.4f}")
