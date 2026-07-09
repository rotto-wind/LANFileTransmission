from flask import Flask, render_template, request, jsonify
from pathlib import Path
from werkzeug.utils import secure_filename
import socket

def port_available(port):
    s = socket.socket()
    try:
        # 0.0.0.0 让这个 Socket 绑定到本机的所有 IPv4 网络接口的这个端口
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()

def get_unique_filename(filename):
    """
    test.txt
    test(1).txt
    test(2).txt
    """

    path = app.config["UPLOAD_FOLDER"] / filename

    if not path.exists():
        return path

    stem = path.stem # 文件名，如 photo
    suffix = path.suffix # 文件扩展名，如 .jpg

    i = 1
    while True:
        new_path = app.config["UPLOAD_FOLDER"] / f"{stem}({i}){suffix}"

        if not new_path.exists():
            return new_path
        i += 1

app = Flask(__name__)
app.json.ensure_ascii = False # 不让json把非ASCII字符编码成\uXXXX格式

UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 3600 * 24

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():

    # "file"与表单中input的name对应
    if "file" not in request.files:
        # 把python字典转换成json，400（Bad Request）
        return jsonify({
            "success": False,
            "message": "没有收到文件(no file received)"
        }), 400
    
    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "success": False,
            "message": "未选择文件(no file selected)"
        }), 400
    
    filename = secure_filename(file.filename)

    save_path = get_unique_filename(filename)
    file.save(save_path) # 把上传的文件保存到服务器磁盘

    return jsonify({
        "success": True,
        "message": "上传成功(upload successfully)",
        "filename": save_path.name
    })


if __name__ == "__main__":
    ports = [5000, 5001, 8000, 8001, 8080]
    for port in ports:
        if port_available(port):
            try:
                app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
            except KeyboardInterrupt:
                print("Server stopped by user.")
            break