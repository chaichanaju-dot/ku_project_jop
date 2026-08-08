from ultralytics import YOLO

# Load a pretrained YOLO26n-seg model (segmentation task, not detection)
model = YOLO("yolo26n-seg.pt")  # Load a pretrained YOLO model

# Train the model on the COCO8 dataset for 100 epochs
train_results = model.train(
    data="data.yaml",  # Path to dataset configuration file
    epochs=20,  # Number of training epochs
    imgsz=640,  # Image size for training
    device="0",
    workers=0,  # Device to run on (e.g., 'cpu', 0, [0,1,2,3])
    batch=2,  # fixed small batch: batch=4 OOM'd on this 4GB GPU during backward
)
metrics = model.val()  # Evaluate the model on the validation set