from ultralytics import YOLO

def main():
    # 載入你上次訓練好的 best.pt 當作起手式，讓模型「溫故知新」
    model = YOLO("runs/detect/train-4/weights/best.pt")

    # 開始新一輪訓練
    results = model.train(
       data="data.yaml",
        epochs=2,
        imgsz=640,
        batch=16,
        device=0,
        workers=2,
        name="gpu-test",
    )
    

if __name__ == '__main__':
    main()