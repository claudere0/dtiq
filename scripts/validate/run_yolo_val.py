from ultralytics import YOLO
model = YOLO("yolov8n.pt")

metrics = model.val(data="configs/experiment_500.yaml", imgsz=640, batch=1, workers=0, device="mps")

print("mAP50-95:", metrics.box.map)
print("mAP50:", metrics.box.map50)
print("Precision:", metrics.box.mp)
print("Recall:", metrics.box.mr)