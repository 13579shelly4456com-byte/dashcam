#測量短邊像素
from pathlib import Path
from PIL import Image
from collections import defaultdict

IMGSZ = 640
THRESHOLDS = [20, 16, 12]
names = {0: "intact-car", 1: "intact-moto", 2: "damaged-car",
         3: "damaged-moto", 4: "accident"}

for split in ["train", "valid", "test"]:
    img_dir = Path(f"dataset/{split}/images")
    lbl_dir = Path(f"dataset/{split}/labels")
    if not lbl_dir.exists():
        continue
    total = defaultdict(int)
    below = {t: defaultdict(int) for t in THRESHOLDS}
    for lbl in lbl_dir.glob("*.txt"):
        img = next(img_dir.glob(lbl.stem + ".*"), None)
        if img is None:
            continue
        w, h = Image.open(img).size
        scale = IMGSZ / max(w, h)
        for line in lbl.read_text().splitlines():
            p = line.split()
            if len(p) < 5:
                continue
            c = int(p[0])
            short = min(float(p[3]) * w, float(p[4]) * h) * scale
            total[c] += 1
            for t in THRESHOLDS:
                if short < t:
                    below[t][c] += 1
    print(f"\n== {split} ==")
    for c in sorted(total):
        row = f"{names.get(c, c):14s} 總數 {total[c]:5d}"
        for t in THRESHOLDS:
            n = below[t][c]
            row += f" | <{t}px: {n:4d} ({100*n/total[c]:.0f}%)"
        print(row)