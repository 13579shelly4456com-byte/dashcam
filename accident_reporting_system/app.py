
import base64
import binascii
import uuid

from flask import Flask, jsonify, render_template, request


app = Flask(__name__)

# 限制接收資料大小
app.config["MAX_CONTENT_LENGTH"] = 70 * 1024 * 1024

# 暫存最新收到的事故資訊
# 不使用資料庫，也不儲存圖片檔案
LATEST_INFORMATION = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/accidents", methods=["POST"])
def receive_accident():
    global LATEST_INFORMATION

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "沒有收到有效的 JSON 資料"
        }), 400

    try:
        # 取得事故基本資訊
        event_id = data["event_id"]
        timestamp = data["timestamp"]
        description = data["description"]

        # 取得 GPS
        location = data["location"]
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])

        if not (-90 <= latitude <= 90):
            raise ValueError("緯度超出有效範圍")

        if not (-180 <= longitude <= 180):
            raise ValueError("經度超出有效範圍")

        # 取得圖片 Base64
        media = data["media"]

        if media["type"] != "image":
            raise ValueError("目前只接受圖片資料")

        filename = media["filename"]
        extension = filename.rsplit(".", 1)[-1].lower()

        if extension not in ["jpg", "jpeg", "png", "webp"]:
            raise ValueError("不支援的圖片格式")

        image_base64 = media["data"]

        # 解碼 Base64，確認資料有效
        image_bytes = base64.b64decode(
            image_base64,
            validate=True
        )

        # 限制解碼後圖片大小為 50 MB
        if len(image_bytes) > 50 * 1024 * 1024:
            raise ValueError("圖片大小超過限制")

        # 轉成網頁可以直接顯示的 Base64 格式
        mime_type = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp"
        }[extension]

        image_data_url = (
            f"data:{mime_type};base64,{image_base64}"
        )

        # 將最新事故資訊暫存在記憶體
        LATEST_INFORMATION = {
            "success": True,
            "event_id": event_id,
            "timestamp": timestamp,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "image_data": image_data_url
        }

        return jsonify({
            "success": True,
            "message": "事故資訊接收成功",
            "event_id": event_id
        }), 200

    except (KeyError, TypeError, ValueError, binascii.Error) as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400


@app.route("/api/latest", methods=["GET"])
def get_latest_information():

    if LATEST_INFORMATION is None:
        return jsonify({
            "received": False
        })

    return jsonify({
        "received": True,
        "information": LATEST_INFORMATION
    })


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "success": False,
        "message": "傳送資料超過大小限制"
    }), 413


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )
