#用哪個模型訓練

import yaml
from pathlib import Path

runs = {
    "v2": "runs/detect/stage1-intact-v2",
    "v3": "runs/detect/stage1-intact-v3",   # 依你的實際資料夾名稱調整
}
keys = ["model", "data", "epochs", "imgsz", "batch", "patience",
        "optimizer", "lr0", "close_mosaic", "seed"]

args = {k: yaml.safe_load(Path(p, "args.yaml").read_text(encoding="utf-8"))
        for k, p in runs.items()}
for key in keys:
    a, b = args["v2"].get(key), args["v3"].get(key)
    mark = "" if a == b else "   <-- 不同"
    print(f"{key:13s} v2={a}   v3={b}{mark}")