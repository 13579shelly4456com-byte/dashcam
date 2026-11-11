from pathlib import Path
from PIL import Image
from collections import Counter

sizes = Counter()
for img in Path("dataset/train/images").iterdir():
    sizes[Image.open(img).size] += 1
for s, n in sizes.most_common():
    print(s, n)