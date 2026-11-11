from ultralytics import YOLO

def main():
    model = YOLO("yolo11n.pt")  
    model.train(
        data="data.yaml",
        epochs=300,
        imgsz=640,
        batch=16,
        device=0,
        workers=2,
        patience=50,
        optimizer="AdamW",   # 明確指定，lr0 才會生效
        lr0=0.0005,
        cos_lr=True,
        warmup_epochs=1,
        close_mosaic=20,
        name="stage2-B",
    )

if __name__ == '__main__':
    main()