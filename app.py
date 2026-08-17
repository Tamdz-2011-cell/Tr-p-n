import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TamdzXWifi WEB</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
        }

        body {
            background-color: #0d0d0d;
            color: #ffffff;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 520px;
            background: #141414;
            border: 2px solid #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 0 20px rgba(255, 255, 255, 0.15);
        }

        h1 {
            text-align: center;
            font-size: 22px;
            letter-spacing: 2px;
            margin-bottom: 24px;
            color: #ffffff;
            text-transform: uppercase;
            border-bottom: 1px solid #333;
            padding-bottom: 12px;
        }

        .section-label {
            font-size: 13px;
            color: #aaa;
            margin-bottom: 8px;
        }

        .file-upload-box {
            border: 1px dashed #ffffff;
            border-radius: 6px;
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 10px;
            background: #1a1a1a;
            margin-bottom: 16px;
        }

        input[type="file"] {
            display: none;
        }

        .custom-file-btn {
            background: #ffffff;
            color: #000000;
            padding: 8px 14px;
            font-weight: bold;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            transition: 0.2s;
        }

        .custom-file-btn:hover {
            background: #ccc;
        }

        .file-name {
            font-size: 12px;
            color: #888;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .divider {
            text-align: center;
            color: #555;
            font-size: 12px;
            margin: 12px 0;
        }

        textarea {
            width: 100%;
            height: 100px;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 6px;
            color: #fff;
            font-size: 13px;
            margin-bottom: 20px;
            outline: none;
            resize: vertical;
        }

        textarea:focus {
            border-color: #fff;
        }

        .btn-submit {
            width: 100%;
            padding: 14px;
            background: #ffffff;
            color: #000000;
            border: none;
            font-weight: bold;
            font-size: 15px;
            border-radius: 6px;
            cursor: pointer;
            letter-spacing: 1px;
            transition: 0.2s;
        }

        .btn-submit:hover {
            background: #dddddd;
        }

        /* Màn hình chờ Fullscreen Overlay */
        #loading-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: #0d0d0d;
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            padding: 20px;
        }

        .loading-title {
            font-size: 18px;
            letter-spacing: 2px;
            margin-bottom: 20px;
            text-transform: uppercase;
        }

        .progress-bar-container {
            width: 80%;
            max-width: 400px;
            height: 28px;
            background: #1a1a1a;
            border: 2px solid #ffffff;
            border-radius: 6px;
            position: relative;
            overflow: hidden;
        }

        .progress-fill {
            width: 0%;
            height: 100%;
            background: #ffffff;
            transition: width 0.2s linear;
        }

        .progress-text {
            position: absolute;
            width: 100%;
            text-align: center;
            line-height: 28px;
            font-size: 13px;
            font-weight: bold;
            color: #000;
            mix-blend-mode: difference;
        }

        /* Khung hiển thị bảng kết quả */
        #result-screen {
            display: none;
            margin-top: 20px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }

        th, td {
            border: 1px solid #333;
            padding: 10px;
            text-align: left;
            font-size: 13px;
            word-break: break-word;
        }

        th {
            background: #ffffff;
            color: #000000;
            font-weight: bold;
        }

        tr:nth-child(even) {
            background: #181818;
        }

        .btn-back {
            margin-top: 15px;
            width: 100%;
            padding: 10px;
            background: transparent;
            color: #fff;
            border: 1px solid #fff;
            border-radius: 6px;
            cursor: pointer;
            font-weight: bold;
        }

        .btn-back:hover {
            background: #222;
        }
    </style>
</head>
<body>

<!-- Màn hình chính nhập liệu -->
<div class="container" id="main-container">
    <h1>TamdzXWifi WEB</h1>

    <div class="section-label">1. Tải file văn bản (.txt):</div>
    <div class="file-upload-box">
        <label for="file-input" class="custom-file-btn">Chọn file TXT</label>
        <input type="file" id="file-input" accept=".txt" onchange="updateFileName()">
        <span class="file-name" id="file-name-display">Chưa chọn tệp...</span>
    </div>

    <div class="divider">--- HOẶC ---</div>

    <div class="section-label">2. Dán đoạn văn bản/câu hỏi:</div>
    <textarea id="text-input" placeholder="Dán nội dung bài tập hoặc văn bản câu hỏi vào đây..."></textarea>

    <button class="btn-submit" onclick="startSearch()">BẮT ĐẦU TRA CỨU</button>

    <!-- Khung bảng kết quả -->
    <div id="result-screen">
        <div class="section-label" style="color: #fff; font-weight: bold;">KẾT QUẢ TRA CỨU:</div>
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">Câu</th>
                    <th style="width: 25%;">Loại</th>
                    <th style="width: 50%;">Đáp án / Nội dung</th>
                </tr>
            </thead>
            <tbody id="result-body">
            </tbody>
        </table>
        <button class="btn-back" onclick="resetForm()">LÀM MỚI</button>
    </div>
</div>

<!-- Màn hình chờ Tiến Trình Fullscreen -->
<div id="loading-screen">
    <div class="loading-title" id="loading-status">ĐANG TRA CỨU DỮ LIỆU...</div>
    <div class="progress-bar-container">
        <div class="progress-fill" id="progress-fill"></div>
        <div class="progress-text" id="progress-text">0%</div>
    </div>
</div>

<script>
    function updateFileName() {
        const input = document.getElementById('file-input');
        const display = document.getElementById('file-name-display');
        if (input.files.length > 0) {
            display.innerText = input.files[0].name;
            display.style.color = "#ffffff";
        }
    }

    function setProgress(percent, text) {
        document.getElementById('progress-fill').style.width = percent + '%';
        document.getElementById('progress-text').innerText = percent + '%';
        if (text) {
            document.getElementById('loading-status').innerText = text;
        }
    }

    function startSearch() {
        const fileInput = document.getElementById('file-input');
        const textInput = document.getElementById('text-input').value;

        const formData = new FormData();

        if (fileInput.files.length > 0) {
            formData.append('file', fileInput.files[0]);
        } else if (textInput.trim() !== "") {
            formData.append('text', textInput);
        } else {
            alert("Vui lòng chọn file .txt hoặc dán nội dung câu hỏi!");
            return;
        }

        // Hiện màn hình tiến trình full màn hình
        document.getElementById('loading-screen').style.display = 'flex';
        setProgress(10, "ĐANG ĐỌC DỮ LIỆU...");

        let progress = 10;
        const interval = setInterval(() => {
            if (progress < 85) {
                progress += Math.floor(Math.random() * 15) + 5;
                if (progress > 85) progress = 85;
                setProgress(progress, "ĐANG PHÂN TÍCH CÂU HỎI...");
            }
        }, 150);

        fetch('/parse', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(interval);
            setProgress(100, "HOÀN TẤT!");

            setTimeout(() => {
                // Ẩn màn hình tiến trình
                document.getElementById('loading-screen').style.display = 'none';

                // Hiển thị bảng kết quả
                const resultScreen = document.getElementById('result-screen');
                const tbody = document.getElementById('result-body');
                tbody.innerHTML = '';

                if (!data.data || data.data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3">Không tìm thấy câu hỏi hoặc đáp án.</td></tr>';
                } else {
                    data.data.forEach(item => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `<td>${item.question}</td><td>${item.type}</td><td>${item.answer}</td>`;
                        tbody.appendChild(tr);
                    });
                }
                resultScreen.style.display = 'block';
            }, 500);
        })
        .catch(err => {
            clearInterval(interval);
            document.getElementById('loading-screen').style.display = 'none';
            alert("Lỗi xử lý dữ liệu!");
            console.error(err);
        });
    }

    function resetForm() {
        document.getElementById('file-input').value = '';
        document.getElementById('file-name-display').innerText = 'Chưa chọn tệp...';
        document.getElementById('text-input').value = '';
        document.getElementById('result-screen').style.display = 'none';
        setProgress(0, "ĐANG TRA CỨU DỮ LIỆU...");
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/parse', methods=['POST'])
def parse():
    content = ""
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        content = file.read().decode('utf-8', errors='ignore')
    elif 'text' in request.form:
        content = request.form['text']

    results = process_text(content)
    return jsonify({'data': results})

def process_text(text):
    results = []
    lines = text.split('\n')
    
    current_q = None
    q_count = 1

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        q_match = re.search(r'^(Câu|Câu hỏi)\s*(\d+)', line_str, re.IGNORECASE)
        if q_match:
            current_q = f"Câu {q_match.group(2).zfill(2)}"
        elif current_q is None:
            current_q = f"Câu {str(q_count).zfill(2)}"

        mc_match = re.search(r'\b([A-D])[\.\:\)]\s*(.*)', line_str)
        if mc_match:
            results.append({
                'question': current_q,
                'type': 'Trắc nghiệm',
                'answer': f"Đáp án {mc_match.group(1)}"
            })
            current_q = None
            q_count += 1
            continue

        if len(line_str) > 5 and not q_match:
            results.append({
                'question': current_q,
                'type': 'Tự luận / Khác',
                'answer': line_str[:100] + ('...' if len(line_str) > 100 else '')
            })
            current_q = None
            q_count += 1

    return results

if __name__ == '__main__':
    app.run(debug=True)
                           
