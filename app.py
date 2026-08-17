import re
from flask import Flask, request, jsonify, render_template_string
from bs4 import BeautifulSoup

app = Flask(__name__)

# Giao diện HTML + CSS Đen Trắng nhúng trực tiếp
HTML_LAYOUT = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TÂM DZ TRA CỨU WEB</title>
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
            max-width: 480px;
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

        input[type="text"] {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #333;
            border-radius: 6px;
            color: #fff;
            font-size: 13px;
            margin-bottom: 20px;
            outline: none;
        }

        input[type="text"]:focus {
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

        .status {
            text-align: center;
            font-size: 12px;
            color: #aaa;
            margin: 20px 0 8px;
        }

        .progress-bar {
            width: 100%;
            height: 24px;
            background: #222;
            border: 1px solid #ffffff;
            border-radius: 4px;
            overflow: hidden;
            position: relative;
            margin-bottom: 20px;
        }

        .progress-fill {
            width: 0%;
            height: 100%;
            background: #ffffff;
            transition: width 0.3s;
        }

        .progress-text {
            position: absolute;
            width: 100%;
            text-align: center;
            line-height: 24px;
            font-size: 12px;
            font-weight: bold;
            color: #000;
            mix-blend-mode: difference;
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
        }

        th {
            background: #ffffff;
            color: #000000;
            font-weight: bold;
        }

        tr:nth-child(even) {
            background: #181818;
        }
    </style>
</head>
<body>

<div class="container">
    <h1>TÂM DZ TRA CỨU WEB</h1>

    <div class="section-label">1. Chọn File (.txt, .csv, .html):</div>
    <div class="file-upload-box">
        <label for="file-input" class="custom-file-btn">Chọn tệp</label>
        <input type="file" id="file-input" accept=".html,.txt,.csv" onchange="updateFileName()">
        <span class="file-name" id="file-name-display">Chưa chọn tệp...</span>
    </div>

    <div class="divider">--- HOẶC ---</div>

    <div class="section-label">2. Dán đường dẫn Web:</div>
    <input type="text" placeholder="https://example.com/dap-an">

    <button class="btn-submit" onclick="startSearch()">BẮT ĐẦU TRA CỨU</button>

    <div class="status" id="status-text">Sẵn sàng</div>
    <div class="progress-bar">
        <div class="progress-fill" id="progress-fill"></div>
        <div class="progress-text" id="progress-text">0%</div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Câu</th>
                <th>Đáp án</th>
            </tr>
        </thead>
        <tbody id="result-body">
            <tr>
                <td>Câu 00</td>
                <td>--</td>
            </tr>
        </tbody>
    </table>
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

    function startSearch() {
        const fileInput = document.getElementById('file-input');
        if (fileInput.files.length === 0) {
            alert("Vui lòng chọn file HTML để tra cứu!");
            return;
        }

        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        document.getElementById('status-text').innerText = "Đang xử lý...";
        document.getElementById('progress-fill').style.width = "50%";
        document.getElementById('progress-text').innerText = "50%";

        fetch('/parse', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('progress-fill').style.width = "100%";
            document.getElementById('progress-text').innerText = "100%";
            document.getElementById('status-text').innerText = "Hoàn tất!";

            const tbody = document.getElementById('result-body');
            tbody.innerHTML = '';

            if (data.data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="2">Không tìm thấy đáp án phù hợp</td></tr>';
                return;
            }

            data.data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${item.question}</td><td>${item.answer}</td>`;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            document.getElementById('status-text').innerText = "Lỗi xử lý file!";
            console.error(err);
        });
    }
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_LAYOUT)

@app.route('/parse', methods=['POST'])
def parse_file():
    results = []
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        content = file.read().decode('utf-8', errors='ignore')
        results = extract_answers(content)
    return jsonify({'data': results})

def extract_answers(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    answers = []
    
    questions = soup.find_all(['div', 'p', 'tr', 'li'], class_=re.compile(r'(question|item|cau|ques)', re.I))
    
    if not questions:
        questions = soup.find_all(text=re.compile(r'Câu\s*\d+', re.I))

    count = 1
    for q in questions:
        q_text = q.get_text() if hasattr(q, 'get_text') else str(q)
        match_q = re.search(r'Câu\s*(\d+)', q_text, re.I)
        q_num = match_q.group(1) if match_q else str(count)
        
        parent = q.parent if hasattr(q, 'parent') else q
        correct_ans = None
        
        ans_elem = parent.find(class_=re.compile(r'(correct|right|true|active|selected|checked)', re.I))
        if ans_elem:
            correct_ans = ans_elem.get_text().strip()
        else:
            match_ans = re.search(r'([A-D])[\.\:\s]+', parent.get_text())
            if match_ans:
                correct_ans = match_ans.group(1)
                
        if not correct_ans or len(correct_ans) > 20:
            correct_ans = "Đã chọn"

        answers.append({
            'question': f"Câu {q_num.zfill(2)}",
            'answer': correct_ans
        })
        count += 1
        
    seen = set()
    final_answers = []
    for item in answers:
        if item['question'] not in seen:
            seen.add(item['question'])
            final_answers.append(item)
            
    return final_answers

if __name__ == '__main__':
    app.run(debug=True)
        
