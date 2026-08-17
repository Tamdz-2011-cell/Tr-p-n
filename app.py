import os
import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string, request, jsonify

# Tự động khởi tạo file requirements.txt nếu chưa tồn tại trên server
if not os.path.exists("requirements.txt"):
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write("flask\nrequests\nbeautifulsoup4\ngunicorn\n")

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tâm DZ - Tra Cứu Đáp Án Web</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #0d0d0d;
            color: #ffffff;
            font-family: 'Courier New', Courier, monospace;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 15px;
        }
        .container {
            border: 2px solid #ff3333;
            padding: 20px;
            width: 100%;
            max-width: 600px;
            border-radius: 8px;
            background-color: #1a1a1a;
            box-shadow: 0 0 15px rgba(255, 51, 51, 0.3);
            text-align: center;
        }
        h1 {
            color: #ff3333;
            text-transform: uppercase;
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        .input-group { margin-bottom: 15px; text-align: left; }
        label { display: block; margin-bottom: 5px; color: #ff6666; font-size: 0.85em; }
        input[type="file"], input[type="text"] {
            background-color: #262626;
            color: #ffffff;
            border: 1px solid #ff3333;
            padding: 10px;
            width: 100%;
            border-radius: 4px;
            font-family: inherit;
        }
        input[type="file"]::file-selector-button {
            background-color: #ff3333;
            color: #0d0d0d;
            border: none;
            padding: 6px 10px;
            border-radius: 3px;
            cursor: pointer;
            font-weight: bold;
            margin-right: 8px;
        }
        .divider {
            margin: 10px 0;
            color: #888;
            font-size: 0.8em;
            position: relative;
        }
        .divider::before, .divider::after {
            content: ""; position: absolute; top: 50%;
            width: 40%; height: 1px; background-color: #444;
        }
        .divider::before { left: 0; } .divider::after { right: 0; }
        button {
            background-color: #ff3333;
            color: #0d0d0d;
            border: none;
            padding: 12px;
            cursor: pointer;
            font-weight: bold;
            text-transform: uppercase;
            margin-top: 10px;
            border-radius: 4px;
            font-size: 0.95em;
            width: 100%;
        }
        button:hover { background-color: #ff6666; }
        #progress-container { display: none; margin-top: 20px; }
        #status-text { margin-bottom: 8px; font-size: 0.85em; color: #cccccc; }
        #progress-bar {
            width: 100%; background-color: #262626;
            border-radius: 5px; overflow: hidden; border: 1px solid #444;
        }
        #progress-fill {
            height: 20px; width: 0%; background-color: #ff3333;
            text-align: center; line-height: 20px; font-weight: bold;
            color: #0d0d0d; transition: width 0.3s ease; font-size: 0.8em;
        }
        #error-box {
            color: #ff4d4d; margin-top: 15px; font-weight: bold; display: none;
            padding: 10px; background-color: rgba(255, 77, 77, 0.1);
            border: 1px solid #ff4d4d; border-radius: 4px; font-size: 0.85em;
        }
        #result-container {
            display: none; margin-top: 20px; max-height: 300px;
            overflow-y: auto; border: 1px solid #ff3333; border-radius: 4px;
        }
        #result-table { width: 100%; border-collapse: collapse; color: #ffffff; text-align: left; }
        #result-table th, #result-table td { padding: 8px 12px; border-bottom: 1px solid #333; font-size: 0.85em; }
        #result-table th { background-color: #ff3333; color: #0d0d0d; position: sticky; top: 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Tâm DZ Tra Cứu Web</h1>
        <form id="upload-form">
            <div class="input-group">
                <label for="file">1. Chọn File (.txt, .csv, .html):</label>
                <input type="file" id="file" name="file" accept=".txt,.csv,.log,.html,.htm">
            </div>
            
            <div class="divider">HOẶC</div>

            <div class="input-group">
                <label for="link">2. Dán đường dẫn Web:</label>
                <input type="text" id="link" name="link" placeholder="https://example.com/dap-an">
            </div>

            <button type="button" onclick="startProcess()">Bắt đầu Tra cứu</button>
        </form>
        
        <div id="progress-container">
            <p id="status-text">Đang khởi tạo...</p>
            <div id="progress-bar">
                <div id="progress-fill">0%</div>
            </div>
        </div>

        <div id="error-box"></div>

        <div id="result-container">
            <table id="result-table">
                <thead>
                    <tr>
                        <th style="width: 30%;">Câu</th>
                        <th style="width: 70%;">Đáp án</th>
                    </tr>
                </thead>
                <tbody id="result-body">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        async function startProcess() {
            let fileInput = document.getElementById('file');
            let linkInput = document.getElementById('link');
            let errorBox = document.getElementById('error-box');
            let progressContainer = document.getElementById('progress-container');
            let resultContainer = document.getElementById('result-container');
            let fill = document.getElementById('progress-fill');
            let statusText = document.getElementById('status-text');
            
            errorBox.style.display = 'none';
            errorBox.innerText = "";
            
            if (!fileInput.files[0] && !linkInput.value.trim()) {
                errorBox.innerText = "Vui lòng chọn File hoặc nhập Link!";
                errorBox.style.display = 'block';
                return;
            }

            progressContainer.style.display = 'block';
            resultContainer.style.display = 'none';
            
            fill.style.width = '30%';
            fill.innerHTML = '30%';
            statusText.innerText = "Đang gửi yêu cầu...";

            let formData = new FormData(document.getElementById('upload-form'));

            try {
                fill.style.width = '70%';
                fill.innerHTML = '70%';
                statusText.innerText = "Đang bóc tách dữ liệu...";

                let response = await fetch('/api/lookup', {
                    method: 'POST',
                    body: formData
                });

                let result = await response.json();

                if (result.success) {
                    fill.style.width = '100%';
                    fill.innerHTML = '100%';
                    statusText.innerText = "Hoàn tất!";
                    setTimeout(() => { showResults(result.data); }, 300);
                } else {
                    progressContainer.style.display = 'none';
                    errorBox.innerText = result.error || "Có lỗi xảy ra.";
                    errorBox.style.display = 'block';
                }
            } catch (error) {
                progressContainer.style.display = 'none';
                errorBox.innerText = "Lỗi kết nối máy chủ!";
                errorBox.style.display = 'block';
            }
        }

        function showResults(data) {
            let tbody = document.getElementById('result-body');
            tbody.innerHTML = "";

            if (!data || data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="2" style="text-align:center; color:#aaa;">Không tìm thấy đáp án hợp lệ!</td></tr>`;
            } else {
                data.forEach(item => {
                    let row = `<tr><td style="font-weight:bold; color:#ff6666;">${item.q}</td><td>${item.a}</td></tr>`;
                    tbody.innerHTML += row;
                });
            }
            
            document.getElementById('result-container').style.display = 'block';
        }
    </script>
</body>
</html>
"""

def parse_text_to_answers(content):
    results = []
    lines = content.splitlines()
    pattern = re.compile(r'^(?:Câu\s*)?(\d+)[\.\s:\-\)]+(.+)$', re.IGNORECASE)

    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if match:
            q_num = f"Câu {match.group(1)}"
            answer = match.group(2).strip()
            results.append({"q": q_num, "a": answer})
    return results

@app.route("/", methods=["GET"])
def index():
    return render_template_string(TEMPLATE)

@app.route("/api/lookup", methods=["POST"])
def lookup():
    text_content = ""
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename.lower()
        try:
            raw_data = file.read()
            try:
                content = raw_data.decode('utf-8')
            except UnicodeDecodeError:
                content = raw_data.decode('latin-1')
            
            if filename.endswith(('.html', '.htm')):
                soup = BeautifulSoup(content, 'html.parser')
                for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                    element.decompose()
                text_content = soup.get_text(separator="\n")
            else:
                text_content = content
        except Exception as e:
            return jsonify({"success": False, "error": f"Lỗi đọc file: {str(e)}"})
            
    elif 'link' in request.form and request.form['link'].strip() != '':
        url = request.form['link'].strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.get(url, headers=headers, timeout=10)
            res.encoding = res.apparent_encoding or 'utf-8'
            
            soup = BeautifulSoup(res.text, 'html.parser')
            for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
                element.decompose()
                
            text_content = soup.get_text(separator="\n")
        except Exception as e:
            return jsonify({"success": False, "error": f"Lỗi tải link: {str(e)}"})
    else:
        return jsonify({"success": False, "error": "Vui lòng nhập File hoặc Link!"})

    parsed_results = parse_text_to_answers(text_content)
    return jsonify({"success": True, "data": parsed_results})

if __name__ == "__main__":
    app.run(debug=True)
