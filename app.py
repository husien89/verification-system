from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Verification System is running!"from flask import Flask, send_file
import qrcode
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "Verification System is running!"

@app.route("/qr")
def generate_qr():
    # النص اللي تريد تحويله إلى QR
    data = "Verification Successful - Husien"
    
    # إنشاء QR
    img = qrcode.make(data)
    
    # حفظ الصورة في الذاكرة
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    # إرسال الصورة كملف
    return send_file(buf, mimetype="image/png")
