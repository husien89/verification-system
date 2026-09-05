from flask import Flask, send_file
import io
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
import uuid

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>✅ نظام التحقق يعمل بنجاح! — Verification System is Running!</h1>
    <p>📱 اذهب إلى الرابط /qr لإنشاء رمز QR — Go to /qr for QR Code</p>
    <p>📄 اذهب إلى الرابط /pdf لإنشاء الشهادة — Go to /pdf for Certificate PDF</p>
    """

@app.route('/qr')
def generate_qr():
    data = "تم التحقق بنجاح — Verification Successful"
    img = qrcode.make(data)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return send_file(buf, mimetype="image/png")

@app.route('/pdf')
def create_pdf():
    student_name = "حسين — Husien"
    verification_code = str(uuid.uuid4())
    qr_data = f"رمز التحقق — Verification Code: {verification_code}"
    
    qr_img = qrcode.make(qr_data)
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format='PNG')
    qr_buf.seek(0)
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica-Bold", 22)
    c.drawCentredString(width/2, height-150, "شهادة التحقق — Verification Certificate")
    
    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height-250, "الاسم — Name: " + student_name)
    c.drawCentredString(width/2, height-290, "رمز التحقق — Verification Code: " + verification_code)
    c.drawCentredString(width/2, height-330, "تاريخ الإصدار — Issue Date: 2026-09-05")
    
    qr_reader = ImageReader(qr_buf)
    c.drawImage(qr_reader, width/2 - 75, height-450, width=150, height=150)
    
    c.save()
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"certificate_{verification_code}.pdf",
        mimetype="application/pdf"
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
