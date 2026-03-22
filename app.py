from flask import Flask, render_template_string, request
from logic import translator

app = Flask(__name__)

UI = """
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <title>Slovian NSS | Model 2.0</title>
    <style>
        body { background: #010409; color: #e6edf3; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; padding: 50px; }
        .wrapper { max-width: 900px; margin: 0 auto; }
        .editor { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 20px; }
        textarea { width: 100%; height: 150px; background: #010409; color: #79c0ff; border: 1px solid #30363d; border-radius: 6px; padding: 15px; font-size: 18px; resize: vertical; }
        .btn { background: #238636; color: #ffffff; border: 1px solid rgba(240, 246, 252, 0.1); border-radius: 6px; padding: 10px 20px; font-weight: 600; cursor: pointer; margin-top: 15px; width: 100%; }
        .btn:hover { background: #2ea043; }
        .output { margin-top: 30px; background: #161b22; border-left: 4px solid #f0883e; padding: 20px; border-radius: 0 6px 6px 0; }
        .output h3 { color: #8b949e; margin-top: 0; font-size: 12px; text-transform: uppercase; }
        .result-text { font-size: 24px; color: #ffa657; font-family: "Courier New", monospace; }
    </style>
</head>
<body>
    <div class="wrapper">
        <div class="editor">
            <h2 style="color: #58a6ff;">Slovian Language Engine</h2>
            <form method="POST">
                <textarea name="content" placeholder="Wpisz polski tekst...">{{ original }}</textarea>
                <button type="submit" class="btn">REKONSTRUUJ FORMĘ</button>
            </form>
        </div>
        {% if result %}
        <div class="output">
            <h3>Wynik rekonstrukcji prasłowiańskiej (NSS):</h3>
            <div class="result-text">{{ result }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    original = ""
    if request.method == 'POST':
        original = request.form.get('content', '')
        result = translator.process_text(original)
    return render_template_string(UI, result=result, original=original)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
