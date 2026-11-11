from ultralytics import YOLO

for name, path in [
    ("train-3", "runs/detect/train-3/weights/best.pt"),
    ("train-4", "runs/detect/train-4/weights/best.pt"),
]:
    m = YOLO(path)
    r = m.val(data="data.yaml")
    print(name, "mAP50:", round(r.box.map50, 4), "mAP50-95:", round(r.box.map, 4))

    #比較mAP50和mAP50-95的差異，並輸出結果