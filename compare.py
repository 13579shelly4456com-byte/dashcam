from ultralytics import YOLO

names = ["intact-car", "intact-moto", "damaged-car", "damaged-moto", "accident"]
models = [
    ("stage1 v3", "runs/detect/stage1-intact-v3/weights/best.pt"),
    ("stage2", "runs/detect/stage2/weights/best.pt"),   # 依你的資料夾名稱調整
]

def main():
    for tag, path in models:
        r = YOLO(path).val(data="data.yaml", split="val", device=0, workers=0,
                           plots=False, verbose=False)
        print(f"\n{tag}  mAP50 {r.box.map50:.3f}  mAP50-95 {r.box.map:.3f}")
        for i, c in enumerate(r.box.ap_class_index):
            print(f"   {names[c]:12s} P {r.box.p[i]:.3f}  R {r.box.r[i]:.3f}  "
                  f"mAP50 {r.box.ap50[i]:.3f}  mAP50-95 {r.box.ap[i]:.3f}")

if __name__ == '__main__':
    main()
#比較mAP50和mAP50-95的差異，並輸出結果