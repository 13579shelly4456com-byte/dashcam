#刪除短邊<12像素的框
from pathlib import Path
import shutil
from PIL import Image

SRC, DST = Path("dataset"), Path("dataset_clean")
IMGSZ = 640        # 你打算訓練用的 imgsz
MIN_SIDE = 12     # 依上面選的方案調整

removed = 0
for split in ["train", "valid", "test"]:
    img_dir, lbl_dir = SRC / split / "images", SRC / split / "labels"
    if not img_dir.exists():
        continue
    (DST / split / "images").mkdir(parents=True, exist_ok=True)
    (DST / split / "labels").mkdir(parents=True, exist_ok=True)
    for img in img_dir.iterdir():
        shutil.copy(img, DST / split / "images" / img.name)
        lbl = lbl_dir / (img.stem + ".txt")
        if not lbl.exists():
            continue
        w, h = Image.open(img).size
        scale = IMGSZ / max(w, h)
        keep = []
        for line in lbl.read_text().splitlines():
            p = line.split()
            if len(p) < 5:
                continue
            short = min(float(p[3]) * w, float(p[4]) * h) * scale
            if short >= MIN_SIDE:
                keep.append(line)
            else:
                removed += 1
        (DST / split / "labels" / lbl.name).write_text(
            "\n".join(keep) + ("\n" if keep else ""))
print("刪除框數:", removed)