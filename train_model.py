from ultralytics import YOLO

model = YOLO("yolov8n.pt")

model.train(
    data='data/datasets/defence_surveillance/data.yaml',
    epochs=50,
    imgsz=640
)