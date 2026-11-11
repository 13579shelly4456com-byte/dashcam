from pathlib import Path
from collections import Counter

names = ["intact-car", "intact-moto", "damaged-car", "damaged-moto", "accident"]
for split in ["train", "valid", "test"]:
    c = Counter()
    n_img = 0
    for f in Path(f"dataset_clean/{split}/labels").glob("*.txt"):
        n_img += 1
        c.update(int(l.split()[0]) for l in f.read_text().splitlines() if l.strip())
    print(split, n_img, "張", {names[k]: v for k, v in sorted(c.items())})