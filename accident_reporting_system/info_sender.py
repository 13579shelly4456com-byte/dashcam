
from datetime import datetime, timezone
from pathlib import Path
import uuid

from info_package_transfer import send_information


# 模擬已經取得的事故資訊
BASE_DIR = Path(__file__).resolve().parent

information = {
    "event_id": f"ACC-{uuid.uuid4().hex[:10]}",

    "timestamp": datetime.now(
        timezone.utc
    ).astimezone().isoformat(),

    "description": "系統偵測到疑似交通事故，車輛發生碰撞。",

    # 模擬手機或 GPS 模組取得的座標
    "latitude": 24.1477,
    "longitude": 120.6736,

    # 模擬攝影機取得的事故圖片
    "image_path": str(BASE_DIR / "test.jpg")
}


if __name__ == "__main__":

    print("已取得事故資訊：")
    print("事故編號：", information["event_id"])
    print("事故描述：", information["description"])
    print("GPS：", information["latitude"], information["longitude"])

    # 將資料交給轉換及傳送程式
    result = send_information(information)

    if result and result.get("success"):
        print("\n事故資訊已成功送達 Flask。")
    else:
        print("\n事故資訊傳送失敗。")
