from flask import Flask, render_template_string, request, make_response
import uuid
from datetime import datetime
import qrcode
from io import BytesIO
import base64
from PIL import Image

app = Flask(__name__)
certificates = {}

INDEX_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام التحقق من الشهادات</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', Tahoma, sans-serif; }
        body { background: linear-gradient(135deg, #1e3a8a, #3b82f6); min-height: 100vh; padding: 20px; }
        .container { max-width: 800px; margin: 0 auto; background: white; border-radius: 16px; padding: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        h1 { text-align: center; color: #1e3a8a; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; font-weight: bold; color: #374151; margin-bottom: 8px; }
        input, select { width: 100%; padding: 12px; border: 2px solid #e5e7eb; border-radius: 8px; font-size: 16px; }
        input:focus, select:focus { outline: none; border-color: #3b82f6; }
        button { width: 100%; padding: 15px; background: linear-gradient(135deg, #16a34a, #22c55e); color: white; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; margin-top: 10px; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(22, 163, 74, 0.3); }
        .links { margin-top: 25px; text-align: center; }
        .links a { color: #3b82f6; text-decoration: none; margin: 0 10px; }
        .template-preview { width: 100%; height: 150px; background: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 12px; margin-top: 10px; display: flex; align-items: center; justify-content: center; color: #6b7280; font-size: 14px; overflow: hidden; }
        .template-preview img { max-width: 100%; max-height: 100%; object-fit: contain; }
        .file-hint { font-size: 12px; color: #6b7280; margin-top: 5px; }
        .en { direction: ltr; text-align: left; margin-top: 5px; color: #6b7280; font-size: 13px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏛️ نظام إصدار الشهادات والتحقق منها</h1>
        
        <form method="POST" action="/generate" enctype="multipart/form-data">
            
            <div class="form-group">
                <label>🎨 اختر قالب الشهادة</label>
                <select name="template_choice" id="templateSelect" required>
                    <option value="">-- اختر القالب --</option>
                    <option value="default">قالب رسمي أزرق</option>
                    <option value="gold">قالب ذهبي فاخر</option>
                    <option value="minimal">قالب بسيط</option>
                    <option value="upload">📁 رفع قالب خاص بي من الجوال</option>
                </select>
                <div class="template-preview" id="templatePreview">معاينة القالب هنا</div>
            </div>

            <div class="form-group" id="uploadTemplateGroup" style="display:none;">
                <label>رفع صورة القالب</label>
                <input type="file" name="custom_template" accept="image/*">
                <div class="file-hint">يفضل PNG شفاف أو JPG بجودة عالية</div>
            </div>

            <div class="form-group">
                <label>🔴 اختر الختم</label>
                <select name="seal_choice" id="sealSelect" required>
                    <option value="">-- اختر الختم --</option>
                    <option value="none">بدون ختم</option>
                    <option value="official">ختم رسمي دائري</option>
                    <option value="gold">ختم ذهبي</option>
                    <option value="red">ختم أحمر</option>
                    <option value="upload">📁 رفع ختم خاص بي</option>
                </select>
            </div>

            <div class="form-group" id="uploadSealGroup" style="display:none;">
                <label>رفع صورة الختم</label>
                <input type="file" name="custom_seal" accept="image/*">
                <div class="file-hint">يفضل PNG شفاف</div>
            </div>

            <div class="form-group">
                <label>🏷️ اختر اللوغو</label>
                <select name="logo_choice" id="logoSelect" required>
                    <option value="">-- اختر اللوغو --</option>
                    <option value="none">بدون لوغو</option>
                    <option value="shield">درع أمني</option>
                    <option value="star">نجمة</option>
                    <option value="upload">📁 رفع لوغو خاص بي</option>
                </select>
            </div>

            <div class="form-group" id="uploadLogoGroup" style="display:none;">
                <label>رفع صورة اللوغو</label>
                <input type="file" name="custom_logo" accept="image/*">
                <div class="file-hint">يفضل PNG شفاف</div>
            </div>

            <div class="form-group">
                <label>الاسم الكامل</label>
                <input type="text" name="full_name" required placeholder="مثال: الحسين أحمد محمد">
            </div>
            
            <div class="form-group">
                <label>الكنية / اللقب</label>
                <input type="text" name="surname" required placeholder="مثال: الحسيني">
            </div>
            
            <div class="form-group">
                <label>نوع الشهادة</label>
                <select name="cert_type" required>
                    <option value="">-- اختر النوع --</option>
                    <option>بكالوريوس</option>
                    <option>دبلوم</option>
                    <option>ماجستير</option>
                    <option>دكتوراه</option>
                    <option>شهادة خبرة</option>
                    <option>إفادة</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>التخصص</label>
                <input type="text" name="major" placeholder="مثال: التجارة الدولية">
            </div>
            
            <div class="form-group">
                <label>اسم الجامعة / الجهة</label>
                <input type="text" name="institution" required placeholder="مثال: جامعة برلين">
            </div>
            
            <div class="form-group">
                <label>تاريخ الإصدار</label>
                <input type="date" name="issue_date" required>
            </div>

            <button type="submit">📄 إنشاء الشهادة بدقة عالية</button>
        </form>

        <div class="links">
            <p><a href="/qr">📱 رمز QR عام للنظام</a> | <a href="/verify">✅ صفحة التحقق</a></p>
        </div>
    </div>

    <script>
        const templateSelect = document.getElementById('templateSelect');
        const uploadTemplateGroup = document.getElementById('uploadTemplateGroup');
        const sealSelect = document.getElementById('sealSelect');
        const uploadSealGroup = document.getElementById('uploadSealGroup');
        const logoSelect = document.getElementById('logoSelect');
        const uploadLogoGroup = document.getElementById('uploadLogoGroup');
        const preview = document.getElementById('templatePreview');

        const previews = {
            default: '<img src="https://cdn-icons-png.flaticon.com/512/2991/2991106.png" style="max-width:100%;">',
            gold: '<img src="https://cdn-icons-png.flaticon.com/512/3072/3072766.png" style="max-width:100%;">',
            minimal: '<img src="https://cdn-icons-png.flaticon.com/512/2659/2659960.png" style="max-width:100%;">'
        };

        templateSelect.addEventListener('change', () => {
            uploadTemplateGroup.style.display = templateSelect.value === 'upload' ? 'block' : 'none';
            preview.innerHTML = previews[templateSelect.value] || 'اختر قالباً لمعاينته';
        });
        sealSelect.addEventListener('change', () => {
            uploadSealGroup.style.display = sealSelect.value === 'upload' ? 'block' : 'none';
        });
        logoSelect.addEventListener('change', () => {
            uploadLogoGroup.style.display = logoSelect.value === 'upload' ? 'block' : 'none';
        });
    </script>
</body>
</html>
'''

CERT_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>شهادة - {{data.full_name}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Times New Roman', serif; background: #f8fafc; padding: 20px; }
        .certificate { width: 100%; max-width: 800px; margin: 0 auto; background: white; border: 15px solid #1e3a8a; padding: 40px; position: relative; box-shadow: 0 0 30px rgba(0,0,0,0.15); min-height: 1100px; }
        .header { text-align: center; margin-bottom: 30px; position: relative; z-index: 2; }
        .logo-area { position: absolute; top: 10px; left: 10px; z-index: 3; }
        .logo-area img { width: 80px; height: 80px; object-fit: contain; }
        .title { font-size: 36px; font-weight: bold; color: #1e3a8a; margin: 20px 0; border-bottom: 3px solid #eab308; padding-bottom: 15px; }
        .content { margin: 50px 0; line-height: 2.5; font-size: 20px; position: relative; z-index: 2; }
        .row { margin: 15px 0; padding-bottom: 10px; border-bottom: 1px dashed #ccc; }
        .label { font-weight: bold; color: #374151; display: inline-block; width: 180px; }
        .value { color: #111827; font-size: 20px; }
        .qr-section { margin-top: 40px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; position: relative; z-index: 2; }
        .qr-box { text-align: center; }
        .qr-img { width: 160px; height: 160px; border: 2px solid #1e3a8a; padding: 5px; background: white; }
        .verify-text { font-size: 13px; color: #6b7280; margin-top: 8px; }
        .code { font-family: monospace; background: #f3f4f6; padding: 8px 12px; border-radius: 4px; font-size: 14px; margin-top: 5px; word-break: break-all; }
        .footer { margin-top: 80px; display: flex; justify-content: space-between; align-items: flex-end; position: relative; z-index: 2; }
        .signature { text-align: center; border-top: 1px solid #333; padding-top: 15px; width: 200px; }
        .signature img { width: 100px; height: 100px; object-fit: contain; margin-bottom: 5px; }
        .actions { margin-top: 40px; text-align: center; position: relative; z-index: 10; }
        .btn { display: inline-block; padding: 12px 25px; margin: 8px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 16px; border: none; cursor: pointer; }
        .btn-whatsapp { background: #25d366; color: white; }
        .btn-print { background: #f59e0b; color: white; }
        .btn-pdf { background: #3b82f6; color: white; }
        @media print { body { background: white; } .actions { display: none; } }
    </style>
</head>
<body>
    <div class="certificate">
        {% if custom_template_b64 %}
        <img src="data:image/png;base64,{{custom_template_b64}}" style="position:absolute; top:0; left:0; width:100%; height:100%; z-index:1; object-fit:contain;">
        {% endif %}

        <div class="logo-area">
            {% if custom_logo_b64 %}
            <img src="data:image/png;base64,{{custom_logo_b64}}" alt="Logo">
            {% endif %}
        </div>

        <div class="header">
            <div class="title">{% if data.cert_type == 'بكالوريوس' %}شهادة بكالوريوس{% elif data.cert_type == 'ماجستير' %}شهادة ماجستير{% elif data.cert_type == 'دكتوراه' %}شهادة دكتوراه{% elif data.cert_type == 'دبلوم' %}دبلوم{% elif data.cert_type == 'شهادة خبرة' %}شهادة خبرة{% elif data.cert_type == 'إفادة' %}إفادة رسمية{% else %}شهادة تصديق{% endif %}
</div>
        </div>

        <div class="content">
            <div class="row"><span class="label">الاسم الكامل:</span><span class="value">{{data.full_name}}</span></div>
            <div class="row"><span class="label">الكنية / اللقب:</span><span class="value">{{data.surname}}</span></div>
            <div class="row"><span class="label">نوع الشهادة:</span><span class="value">{{data.cert_type}}</span></div>
            <div class="row"><span class="label">التخصص:</span><span class="value">{{data.major}}</span></div>
            <div class="row"><span class="label">الجامعة / الجهة:</span><span class="value">{{data.institution}}</span></div>
            <div class="row"><span class="label">تاريخ الإصدار:</span><span class="value">{{data.issue_date}}</span></div>
            <div class="row"><span class="label">رقم التحقق:</span><span class="value code">{{data.verify_code}}</span></div>
        </div>

        <div class="qr-section">
            <div class="qr-box">
                <img src="data:image/png;base64,{{qr_b64}}" class="qr-img" alt="QR Code">
                <div class="verify-text">امسح الرمز للتحقق من صحة الشهادة</div>
            </div>
            <div class="qr-box" style="text-align:right; max-width:50%;">
                <p><strong>رابط التحقق:</strong></p>
                <div class="code">{{verify_url}}</div>
            </div>
        </div>

        <div class="footer">
            <div class="signature">
                {% if custom_seal_b64 %}
                <img src="data:image/png;base64,{{custom_seal_b64}}" alt="Seal">
                {% endif %}
                <div>الختم والتوقيع</div>
            </div>
            <div style="text-align:right;">
                <p>تاريخ الطباعة: {{current_date}}</p>
            </div>
        </div>
    </div>

    <div class="actions">
        <button onclick="window.print()" class="btn btn-print">🖨️ طباعة بدقة عالية</button>
        <a href="https://wa.me/?text=شهادة%%20تحقق%%20-%%20{{data.full_name}}%%0Aرقم%%20التحقق:%%20{{data.verify_code}}%%0Aالرابط:%%20{{verify_url}}" target="_blank" class="btn btn-whatsapp">📱 إرسال عبر واتساب</a>
        <button onclick="window.print()" class="btn btn-pdf">📄 حفظ كـ PDF</button>
    </div>
</body>
</html>
'''

VERIFY_HTML = '''
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نتيجة التحقق - {{data.verify_code}}</title>
    <style>
        * { box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body { background: linear-gradient(135deg, #f0fdf4, #dcfce7); min-height: 100vh; padding: 20px; }
        .container { max-width: 500px; margin: 0 auto; background: white; border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }
        .check-icon { width: 100px; height: 100px; background: #22c55e; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px; font-size: 60px; color: white; }
        h1 { color: #16a34a; margin-bottom: 5px; }
        .status { font-size: 20px; color: #15803d; margin-bottom: 30px; }
        .data { text-align: right; background: #f8fafc; padding: 20px; border-radius: 10px; border: 1px solid #e5e7eb; }
        .data-row { padding: 10px 0; border-bottom: 1px solid #eee; }
        .data-row:last-child { border-bottom: none; }
        .label { font-weight: bold; color: #374151; display: inline-block; width: 140px; }
        .value { color: #111827; }
        .code { font-family: monospace; background: #e5e7eb; padding: 5px 10px; border-radius: 4px; font-size: 13px; }
        .valid-badge { display: inline-block; background: #22c55e; color: white; padding: 8px 20px; border-radius: 30px; font-weight: bold; margin-top: 25px; font-size: 18px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="check-icon">✓</div>
        <h1>تم التحقق بنجاح!</h1>
        <p class="status">وثيقة أصلية وموثقة ✅</p>
        
        <div class="data">
            <div class="data-row"><span class="label">الاسم الكامل:</span><span class="value">{{data.full_name}}</span></div>
            <div class="data-row"><span class="label">الكنية:</span><span class="value">{{data.surname}}</span></div>
            <div class="data-row"><span class="label">نوع الشهادة:</span><span class="value">{{data.cert_type}}</span></div>
            <div class="data-row"><span class="label">الجامعة:</span><span class="value">{{data.institution}}</span></div>
            <div class="data-row"><span class="label">التاريخ:</span><span class="value">{{data.issue_date}}</span></div>
            <div class="data-row"><span class="label">رقم التحقق:</span><span class="value code">{{data.verify_code}}</span></div>
        </div>

        <div class="valid-badge">✅ صالح وموثق</div>
    </div>
</body>
</html>
'''

def generate_qr_base64(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def get_image_base64(file_storage):
    if not file_storage or file_storage.filename == '':
        return None
    try:
        img = Image.open(file_storage)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()
    except:
        return None

@app.route('/')
def index():
    return render_template_string(INDEX_HTML)

@app.route('/generate', methods=['POST'])
def generate():
    full_name = request.form.get('full_name')
    surname = request.form.get('surname')
    cert_type = request.form.get('cert_type')
    major = request.form.get('major', '')
    institution = request.form.get('institution')
    issue_date = request.form.get('issue_date')
    
    template_choice = request.form.get('template_choice')
    seal_choice = request.form.get('seal_choice')
    logo_choice = request.form.get('logo_choice')
    
    custom_template_b64 = get_image_base64(request.files.get('custom_template'))
    custom_seal_b64 = get_image_base64(request.files.get('custom_seal'))
    custom_logo_b64 = get_image_base64(request.files.get('custom_logo'))
    
    verify_code = str(uuid.uuid4())
    certificates[verify_code] = {
        'full_name': full_name,
        'surname': surname,
        'cert_type': cert_type,
        'major': major,
        'institution': institution,
        'issue_date': issue_date,
        'verify_code': verify_code,
        'template_choice': template_choice,
        'seal_choice': seal_choice,
        'logo_choice': logo_choice,
        'created_at': datetime.now().isoformat()
    }
    
    verify_url = request.host_url + f"verify?code={verify_code}"
    qr_b64 = generate_qr_base64(verify_url)
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    return render_template_string(CERT_HTML, 
                                  data=certificates[verify_code],
                                  verify_url=verify_url,
                                  qr_b64=qr_b64,
                                  current_date=current_date,
                                  custom_template_b64=custom_template_b64,
                                  custom_seal_b64=custom_seal_b64,
                                  custom_logo_b64=custom_logo_b64)

@app.route('/verify')
def verify():
    code = request.args.get('code', '')
    if code in certificates:
        return render_template_string(VERIFY_HTML, data=certificates[code])
    return '<div style="text-align:center; padding:50px; font-family:Arial;"><h1 style="color:red;">❌ غير موجود</h1><p>رمز التحقق غير صالح.</p></div>'

@app.route('/qr')
def qr_page():
    return f'<html><body style="text-align:center; padding:50px;"><h1>📱 رمز QR عام</h1><img src="data:image/png;base64,{generate_qr_base64(request.host_url)}"/></body></html>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
