from pathlib import Path
from PIL import Image
from ultralytics import YOLO

model = YOLO("runs/detect/stage2/weights/best.pt")
names = ["intact-car", "intact-moto", "damaged-car", "damaged-moto", "accident"]
img_dir = Path("dataset/valid/images")    # 依 data.yaml 的 valid 路徑調整
lbl_dir = Path("dataset/valid/labels")

def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    ua = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - inter
    return inter / ua if ua else 0

for img in sorted(img_dir.iterdir()):
    lbl = lbl_dir / (img.stem + ".txt")
    if not lbl.exists():
        continue
    w, h = Image.open(img).size
    r = model.predict(img, conf=0.25, device=0, verbose=False)[0]
    preds = [(b.xyxy[0].tolist(), int(b.cls[0])) for b in r.boxes]
    for line in lbl.read_text().splitlines():
        p = line.split()
        if len(p) < 5 or int(p[0]) < 2:
            continue
        c = int(p[0])
        cx, cy, bw, bh = map(float, p[1:5])
        gt = [(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h]
        same = any(pc == c and iou(gt, pb) >= 0.3 for pb, pc in preds)
        if not same:
            seen = sorted({names[pc] for pb, pc in preds if iou(gt, pb) >= 0.3})
            print(f"{img.name[:45]}  漏掉 {names[c]}  重疊的預測: {seen or '無（判成背景）'}")