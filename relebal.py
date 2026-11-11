import os

# 宣告妳的資料集根資料夾路徑（對應妳的 dataset 路徑）
dataset_root = r"C:/Users/user/Desktop/專題/dashcam/dataset"

# 需要處理的子資料夾中的 labels 目錄
label_subdirs = [
    "train/labels",
    "valid/labels",
    "test/labels"  # 如果有 test 的話就保留，沒有可以註解掉
]

# 定義舊編號到新編號的對應字典 (範例：把原本是 0 的改成 4，原本是 4 的改成 0)
mapping = {
    0: 4,
    1: 2,
    2: 3,
    3: 0,
    4: 1
}

for subdir in label_subdirs:
    label_dir = os.path.join(dataset_root, subdir)
    
    if not os.path.exists(label_dir):
        print(f"⚠️ 找不到路徑，跳過: {label_dir}")
        continue
        
    print(f"正在處理資料夾: {label_dir}")
    count = 0
    
    for filename in os.listdir(label_dir):
        if filename.endswith(".txt"):
            file_path = os.path.join(label_dir, filename)
            
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            new_lines = []
            modified = False
            
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                
                # 取得原本的類別編號 (通常在第一個欄位)
                old_class_id = int(parts[0])
                
                # 如果在對應字典裡，就進行替換
                if old_class_id in mapping:
                    parts[0] = str(mapping[old_class_id])
                    modified = True
                    
                new_lines.append(" ".join(parts) + "\n")
                
            # 寫回原本的 .txt 檔案
            if modified:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                count += 1

    print(f"-> 成功修正 {count} 個標籤檔案！\n")

print("🎉 所有資料夾的標籤編號批次轉換完成！")