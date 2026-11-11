from pathlib import Path
from collections import Counter

for split in ["train", "valid", "test"]:
    c = Counter()
    empty = 0
    for f in Path(f"dataset_clean/{split}/labels").glob("*.txt"):
        lines = [l for l in f.read_text().splitlines() if l.strip()]
        if not lines:
            empty += 1
        c.update(int(l.split()[0]) for l in lines)
    print(split, dict(sorted(c.items())), "空標註檔:", empty)