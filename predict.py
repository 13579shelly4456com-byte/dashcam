from ultralytics import YOLO

def main():
    
    model = YOLO("runs/detect/stage2/weights/best.pt")

    # 2. 對 test 資料夾裡面的圖片進行預測
    # save=True 會把框好物件的照片自動存到 runs/detect/predict 資料夾中
    results = model(source="dataset/test/images", save=True) 

    print("測試完成！結果已經儲存至 runs/detect/predict 底下！")

if __name__ == '__main__':
    main()