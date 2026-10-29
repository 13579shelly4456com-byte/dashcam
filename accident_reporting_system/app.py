import sqlite3
import uuid
from pathlib import Path

from flask import (
    Flask,
    render_template,
    request,
    send_from_directory,
)
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 固定使用專案資料夾內的資料庫
BASE_DIR = Path(app.root_path)
DATABASE = BASE_DIR / "accident.db"
UPLOAD_FOLDER = BASE_DIR / "uploads"

# 單次上傳大小限制：10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def get_db_connection():
    """建立資料庫連線。"""
    conn = sqlite3.connect(str(DATABASE))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """建立資料表，並補上舊資料庫缺少的欄位。"""
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            description TEXT NOT NULL,
            image_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = {
        row["name"]
        for row in conn.execute(
            "PRAGMA table_info(reports)"
        ).fetchall()
    }

    # 舊資料庫沒有這些欄位時才新增，不會刪除原有通報
    if "image_filename" not in columns:
        conn.execute(
            "ALTER TABLE reports ADD COLUMN image_filename TEXT"
        )

    if "latitude" not in columns:
        conn.execute(
            "ALTER TABLE reports ADD COLUMN latitude REAL"
        )

    if "longitude" not in columns:
        conn.execute(
            "ALTER TABLE reports ADD COLUMN longitude REAL"
        )

    conn.commit()
    conn.close()


def allowed_file(filename):
    """檢查圖片副檔名是否允許。"""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


@app.route("/")
def home():
    """首頁：事故通報表單。"""
    return render_template("index.html")


@app.route("/report", methods=["POST"])
def report():
    """接收事故通報並寫入資料庫。"""
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()

    latitude_text = request.form.get("latitude", "").strip()
    longitude_text = request.form.get("longitude", "").strip()

    # 檢查必填欄位
    if not location or not description:
        return render_template(
            "index.html",
            error="請填寫事故地點與事故描述。"
        ), 400

    # GPS 座標必須同時提供，或同時留空
    if bool(latitude_text) != bool(longitude_text):
        return render_template(
            "index.html",
            error="緯度與經度必須同時填寫。"
        ), 400

    latitude = None
    longitude = None

    if latitude_text and longitude_text:
        try:
            latitude = float(latitude_text)
            longitude = float(longitude_text)
        except ValueError:
            return render_template(
                "index.html",
                error="GPS 座標必須是有效的數字。"
            ), 400

        if not -90 <= latitude <= 90:
            return render_template(
                "index.html",
                error="緯度必須介於 -90 到 90 之間。"
            ), 400

        if not -180 <= longitude <= 180:
            return render_template(
                "index.html",
                error="經度必須介於 -180 到 180 之間。"
            ), 400

    # 圖片為選填
    image = request.files.get("image")
    image_filename = None

    if image and image.filename:
        original_filename = secure_filename(image.filename)

        if not original_filename or not allowed_file(original_filename):
            return render_template(
                "index.html",
                error="圖片格式只接受 JPG、JPEG、PNG 或 WEBP。"
            ), 400

        extension = original_filename.rsplit(".", 1)[1].lower()
        image_filename = f"{uuid.uuid4().hex}.{extension}"

        image.save(UPLOAD_FOLDER / image_filename)

    # 寫入資料庫
    conn = get_db_connection()

    try:
        cursor = conn.execute("""
            INSERT INTO reports (
                location,
                description,
                image_filename,
                latitude,
                longitude
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            location,
            description,
            image_filename,
            latitude,
            longitude,
        ))

        report_id = cursor.lastrowid
        conn.commit()

    except sqlite3.Error:
        conn.rollback()

        # 若資料庫寫入失敗，避免留下沒有對應通報的照片
        if image_filename:
            image_path = UPLOAD_FOLDER / image_filename
            if image_path.exists():
                image_path.unlink()

        return render_template(
            "index.html",
            error="通報資料儲存失敗，請稍後再試。"
        ), 500

    finally:
        conn.close()

    # 只有資料庫寫入成功後，才顯示通報確認頁面
    return render_template(
        "result.html",
        location=location,
        description=description,
        report_id=report_id,
        image_filename=image_filename,
        latitude=latitude,
        longitude=longitude,
    )


# 暫時停用事故列表頁面，保留程式碼供未來恢復。
# 若要重新啟用，取消以下區塊的註解即可。
#
# @app.route("/reports")
# def reports():
#     """顯示全部事故事件。"""
#     conn = get_db_connection()
#
#     rows = conn.execute("""
#         SELECT
#             id,
#             location,
#             description,
#             image_filename,
#             created_at,
#             latitude,
#             longitude
#         FROM reports
#         ORDER BY id DESC
#     """).fetchall()
#
#     conn.close()
#
#     return render_template("reports.html", reports=rows)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    """提供已上傳的事故照片。"""
    return send_from_directory(
        str(UPLOAD_FOLDER),
        filename
    )


@app.errorhandler(413)
def file_too_large(error):
    """處理超過 10 MB 的上傳檔案。"""
    return render_template(
        "index.html",
        error="上傳檔案太大，請選擇小於 10 MB 的圖片。"
    ), 413


# 啟動網站前先確認資料表存在
init_db()

if __name__ == "__main__":
    app.run(debug=True)
