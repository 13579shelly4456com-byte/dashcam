from pathlib import Path
from PIL import Image, ImageDraw
from ultralytics import YOLO

model = YOLO("runs/detect/stage2/weights/best.pt")
names = ["intact-car", "intact-moto", "damaged-car", "damaged-moto", "accident"]
img_dir = Path("dataset/valid/images")
lbl_dir = Path("dataset/valid/labels")
out = Path("misses")
out.mkdir(exist_ok=True)

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
    im = Image.open(img).convert("RGB")
    w, h = im.size
    r = model.predict(im, conf=0.25, device=0, verbose=False)[0]
    preds = [(b.xyxy[0].tolist(), int(b.cls[0]), float(b.conf[0])) for b in r.boxes]
    gts = []
    for line in lbl.read_text().splitlines():
        p = line.split()
        if len(p) < 5 or int(p[0]) < 2:
            continue
        cx, cy, bw, bh = map(float, p[1:5])
        gts.append((int(p[0]), [(cx-bw/2)*w, (cy-bh/2)*h, (cx+bw/2)*w, (cy+bh/2)*h]))
    if all(any(pc == c and iou(g, pb) >= 0.3 for pb, pc, _ in preds) for c, g in gts):
        continue
    d = ImageDraw.Draw(im)
    for pb, pc, cf in preds:
        color = (0, 120, 255) if pc < 2 else (255, 0, 0)
        d.rectangle(pb, outline=color, width=1 if pc < 2 else 3)
        d.text((pb[0] + 3, pb[3] - 12), f"{names[pc]} {cf:.2f}", fill=color)
    for c, g in gts:
        d.rectangle(g, outline=(0, 255, 0), width=3)
        d.text((g[0] + 3, g[1] + 3), "GT " + names[c], fill=(0, 255, 0))
    im.save(out / (img.stem[:40] + ".jpg"))

    #綠框是你的標註，紅框是模型預測的 damaged 與 accident，藍色細框是 intact 預測