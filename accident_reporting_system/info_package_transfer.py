
import base64
import json
import urllib.request
import urllib.error
from pathlib import Path


API_URL = "http://127.0.0.1:5000/api/accidents"


def convert_image_to_base64(image_path):
    """將圖片檔案轉換成 Base64 文字。"""

    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"找不到圖片：{path}")

    with open(path, "rb") as file:
        image_bytes = file.read()

    return base64.b64encode(image_bytes).decode("utf-8")


def send_information(information):
    """整理事故資訊並傳送給 Flask。"""

    image_path = information.get("image_path")

    if not image_path:
        raise ValueError("沒有提供圖片路徑。")

    # 圖片轉換成 Base64
    image_base64 = convert_image_to_base64(image_path)

    # 建立完整 JSON 封包
    package = {
        "event_id": information["event_id"],
        "timestamp": information["timestamp"],

        "description": information["description"],

        "location": {
            "latitude": information["latitude"],
            "longitude": information["longitude"]
        },

        "media": {
            "type": "image",
            "filename": Path(image_path).name,
            "encoding": "base64",
            "data": image_base64
        }
    }

    # JSON 轉成 UTF-8 位元組
    json_data = json.dumps(
        package,
        ensure_ascii=False
    ).encode("utf-8")

    # 傳送 HTTP POST
    request = urllib.request.Request(
        API_URL,
        data=json_data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    print("正在轉換並傳送事故資訊...")

    try:
        with urllib.request.urlopen(
            request,
            timeout=120
        ) as response:

            result = json.loads(
                response.read().decode("utf-8")
            )

            print("\n伺服器回應：")
            print(json.dumps(
                result,
                ensure_ascii=False,
                indent=4
            ))

            return result

    except urllib.error.HTTPError as error:
        print("傳送失敗：")
        print(error.code)
        print(error.read().decode("utf-8"))
        return None

    except urllib.error.URLError as error:
        print("無法連接 Flask：")
        print(error.reason)
        return None
