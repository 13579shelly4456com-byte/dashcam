from ultralytics import YOLO

def main():
    model = YOLO("yolo11n.pt")      # 從官方權重開始，不是 stage1 的 best.pt
    model.train(
        data="data.yaml",
        epochs=200,
        imgsz=640,
        batch=16,
        device=0,
        workers=2,
        patience=50,
        name="stage1-intact-v3",    # 新名稱，不覆蓋舊結果
    )

if __name__ == '__main__':
    main()