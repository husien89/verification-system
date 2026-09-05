# verification-system
# Verification System — نظام التحقق والتصديق > **منصة مفتوحة المصدر للتحقق من صحة المستندات، البيانات، والمعلومات — بلا قيود، شفافة، وموثوقة**
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Verification System is running!"
    Flask
gunicorn
reportlab
qrcode
web: gunicorn app🍎
python-3.10.12
