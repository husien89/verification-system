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
    
from flask import Flask, send_file
import qrcode
import io
from reportlab.pdfgen import canvas

app = Flask(__name__)

@app.route("/")
def home():
    return "Verification System is running!"

@app.route("/qr")
def generate_qr():
    data = "Verification Successful - Husien"
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route("/pdf")
def generate_pdf():
    # إنشاء ملف PDF في الذاكرة
    buf = io.BytesIO()
    c = canvas.Canvas(buf)
    
    # كتابة نص رسمي
    c.drawString(100, 750, "Verification Document")
    c.drawString(100, 730, "Owner: Husien")
    c.drawString(100, 710, "Status: Verified")
    
    # إنشاء QR وإضافته داخل PDF
    qr_data = "Verification Successful - Husien"
    qr_img = qrcode.make(qr_data)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    
    # إدراج QR في PDF
    from reportlab.lib.utils import ImageReader
    qr_reader = ImageReader(qr_buf)
    c.drawImage(qr_reader, 100, 600, width=100, height=100)
    
    c.showPage()
    c.save()
    
    buf.seek(0)
    return send_file(buf, mimetype="application/pdf", as_attachment=True, download_name="verification.pdf")
