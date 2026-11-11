from pathlib import Path
from PIL import Image
from ultralytics import YOLO

model = YOLO("runs/detect/stage1-intact-v2/weights/best.pt")
names = {0: "car", 1: "moto"}
img_dir = Path("dataset_clean/valid/images")
lbl_dir = Path("dataset_clean/valid/labels")

def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    ua = (a[2]-a[0])*(a[3]-a[1]) + (b[2]-b[0])*(b[3]-b[1]) - inter
    return inter / ua if ua else 0

rows = []
for img in sorted(img_dir.iterdir()):
    w, h = Image.open(img).size
    scale = 640 / max(w, h)
    gts = []
    lbl = lbl_dir / (img.stem + ".txt")
    if lbl.exists():
        for line in lbl.read_text().splitlines():
            p = line.split()
            if len(p) < 5:
                continue
            cx, cy, bw, bh = map(float, p[1:5])
            gts.append([(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h])
    r = model.predict(img, conf=0.5, device=0, verbose=False)[0]
    extra = []
    for b in r.boxes:
        x1, y1, x2, y2 = b.xyxy[0].tolist()
        if not any(iou([x1, y1, x2, y2], g) >= 0.3 for g in gts):
            short = min(x2 - x1, y2 - y1) * scale
            extra.append(f"{names[int(b.cls[0])]} {float(b.conf[0]):.2f} 短邊{short:.0f}px")
    if extra:
        rows.append((len(extra), img.name[:45], extra))

for n, name, extra in sorted(rows, reverse=True):
    print(n, name, extra)