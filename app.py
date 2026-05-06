import requests
from flask import Flask, render_template_string, request
app = Flask(__name__)
COHERE_API_KEY = "cohere_GiGUqfSiGFYegGEkhuI67g13bgr2qUN0j0hO4CW40Gpvcx"
COHERE_URL = "https://api.cohere.ai/v2/chat"
PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Text Summarizer Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header h1 { color: white; font-size: 32px; letter-spacing: 2px; }
        .header p { color: rgba(255,255,255,0.6); font-size: 14px; margin-top: 8px; }
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 24px;
            padding: 40px;
            width: 90%;
            max-width: 650px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        }
        .options { display: flex; gap: 10px; margin-bottom: 15px; }
        .option-btn {
            flex: 1;
            padding: 10px;
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 10px;
            background: rgba(255,255,255,0.05);
            color: white;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
            text-align: center;
        }
        .option-btn.active { background: linear-gradient(135deg, #667eea, #764ba2); border-color: transparent; }
        textarea {
            width: 100%;
            height: 200px;
            padding: 15px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.15);
            border-radius: 14px;
            font-size: 14px;
            resize: none;
            outline: none;
            color: white;
            line-height: 1.6;
        }
        textarea::placeholder { color: rgba(255,255,255,0.3); }
        textarea:focus { border-color: #667eea; }
        .counter { color: rgba(255,255,255,0.4); font-size: 12px; text-align: right; margin: 8px 0 15px; }
        .counter span { color: #667eea; font-weight: bold; }
        button {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 16px;
            border-radius: 14px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            font-weight: bold;
            letter-spacing: 1px;
            transition: opacity 0.3s;
        }
        button:hover { opacity: 0.85; }
        .loading { display: none; text-align: center; color: rgba(255,255,255,0.6); margin-top: 20px; font-size: 14px; }
        .loading span { display: inline-block; animation: pulse 1.5s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }
        .result {
            margin-top: 25px;
            background: rgba(102,126,234,0.15);
            border: 1px solid rgba(102,126,234,0.3);
            border-radius: 14px;
            padding: 20px;
            font-size: 15px;
            color: rgba(255,255,255,0.9);
            line-height: 1.8;
        }
        .result-header { color: #667eea; font-size: 12px; font-weight: bold; letter-spacing: 2px; margin-bottom: 10px; }
        .result-footer { color: rgba(255,255,255,0.3); font-size: 11px; text-align: right; margin-top: 10px; }
        .error { margin-top: 15px; color: #ff6b6b; text-align: center; font-size: 14px; }
        .footer { color: rgba(255,255,255,0.3); font-size: 12px; text-align: center; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>📝 Text Summarizer Pro</h1>
        <p>Summarize any text in any language instantly using AI</p>
    </div>
    <div class="card">
        <div class="options">
            <div class="option-btn active" onclick="setLength('short', this)">Short</div>
            <div class="option-btn" onclick="setLength('medium', this)">Medium</div>
            <div class="option-btn" onclick="setLength('long', this)">Long</div>
        </div>
        <textarea id="inputText" placeholder="Paste your text here... (max 2000 words)" oninput="updateCounter()">{{ input_text }}</textarea>
        <div class="counter"><span id="wordCount">0</span> / 2000 words</div>
        <input type="hidden" id="summaryLength" value="short">
        <button onclick="summarize()">⚡ Summarize Now</button>
        <div class="loading" id="loading"><span>⏳ Summarizing your text, please wait...</span></div>
        {% if summary %}
        <div class="result">
            <div class="result-header">SUMMARY</div>
            {{ summary }}
            <div class="result-footer">{{ summary | length }} characters</div>
        </div>
        {% endif %}
        {% if error %}<p class="error">{{ error }}</p>{% endif %}
    </div>
    <div class="footer">Powered by Cohere AI</div>
    <script>
        function setLength(val, el) {
            document.getElementById("summaryLength").value = val;
            document.querySelectorAll(".option-btn").forEach(b => b.classList.remove("active"));
            el.classList.add("active");
        }
        function updateCounter() {
            let text = document.getElementById("inputText").value;
            let words = text.trim() === "" ? 0 : text.trim().split(" ").filter(w => w).length;
            document.getElementById("wordCount").innerText = words;
        }
        function summarize() {
            let text = document.getElementById("inputText").value;
            let words = text.trim().split(" ").filter(w => w).length;
            if (words > 2000) { alert("Text exceeds 2000 words limit!"); return; }
            document.getElementById("loading").style.display = "block";
            let length = document.getElementById("summaryLength").value;
            let form = document.createElement("form");
            form.method = "POST";
            let input1 = document.createElement("input");
            input1.type = "hidden"; input1.name = "text"; input1.value = text;
            let input2 = document.createElement("input");
            input2.type = "hidden"; input2.name = "length"; input2.value = length;
            form.appendChild(input1); form.appendChild(input2);
            document.body.appendChild(form);
            form.submit();
        }
        updateCounter();
    </script>
</body>
</html>
"""
@app.route("/", methods=["GET", "POST"])
def home():
    summary = ""
    error = ""
    input_text = ""
    if request.method == "POST":
        input_text = request.form.get("text", "")
        length = request.form.get("length", "medium")
        words = input_text.strip().split()
        if len(words) > 2000:
            error = "Text exceeds 2000 words limit!"
        elif len(words) < 10:
            error = "Text is too short to summarize!"
        else:
            length_instruction = {"short": "in 2-3 sentences", "medium": "in one paragraph", "long": "in multiple paragraphs"}
            headers = {"Authorization": f"Bearer {COHERE_API_KEY}", "Content-Type": "application/json"}
            data = {
                "model": "command-a-03-2025",
                "messages": [{"role": "user", "content": f"Summarize the following text {length_instruction[length]}:\n\n{input_text}"}]
            }
            response = requests.post(COHERE_URL, json=data, headers=headers)
            if response.status_code == 200:
                summary = response.json()["message"]["content"][0]["text"]
            else:
                error = "Something went wrong, please try again!"
    return render_template_string(PAGE, summary=summary, error=error, input_text=input_text)
if __name__ == "__main__":
    app.run(debug=True)
