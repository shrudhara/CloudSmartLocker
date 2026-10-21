
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "cloud_files")
DATA_FILE = os.path.join(BASE_DIR, "notes.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Cloud Smart Locker</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #eef3f9;
            margin: 0;
            color: #243047;
        }
        header {
            background: #183b70;
            color: white;
            padding: 24px;
            text-align: center;
        }
        main { max-width: 850px; margin: 25px auto; padding: 15px; }
        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 3px 12px #00000010;
        }
        input, textarea, button {
            box-sizing: border-box;
            width: 100%;
            padding: 11px;
            margin: 7px 0;
        }
        button {
            background: #2463a6;
            color: white;
            border: 0;
            border-radius: 6px;
            cursor: pointer;
        }
        a { color: #2463a6; }
        .item {
            background: #f4f7fb;
            padding: 12px;
            margin: 8px 0;
            border-radius: 7px;
            overflow-wrap: anywhere;
        }
        small { color: #63718a; }
    </style>
</head>
<body>
<header>
    <h1>☁ Cloud Smart Locker</h1>
    <p>Your simple digital notes and file locker</p>
</header>
<main>
    <div class="card">
        <h2>📝 Create a Note</h2>
        <form method="POST" action="/add_note">
            <input name="title" placeholder="Enter note title" required>
            <textarea name="content" placeholder="Write your note here..."
                      rows="4" required></textarea>
            <button type="submit">Save Note</button>
        </form>
    </div>

    <div class="card">
        <h2>📤 Upload a File</h2>
        <form method="POST" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <small>Maximum file size: 5 MB</small>
            <button type="submit">Upload File</button>
        </form>
    </div>

    <div class="card">
        <h2>📚 Saved Notes ({{ notes|length }})</h2>
        {% for note in notes %}
        <div class="item">
            <strong>{{ note.title }}</strong><br>
            {{ note.content }}<br>
            <small>{{ note.time }}</small>
        </div>
        {% else %}
        <p>No notes yet. Create your first note!</p>
        {% endfor %}
    </div>

    <div class="card">
        <h2>📁 My Files ({{ files|length }})</h2>
        {% for file in files %}
        <div class="item">
            📄 {{ file }}
            <a href="{{ url_for('download_file', filename=file) }}">
                — Download
            </a>
        </div>
        {% else %}
        <p>No files uploaded yet.</p>
        {% endfor %}
    </div>

    <p style="text-align:center">
        Cloud Computing Mini Project | Python and Flask
    </p>
</main>
</body>
</html>
"""


def read_notes():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_notes(notes):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=4, ensure_ascii=False)


@app.route("/")
def home():
    notes = read_notes()
    files = sorted(os.listdir(UPLOAD_FOLDER))
    return render_template_string(HTML, notes=notes, files=files)


@app.route("/add_note", methods=["POST"])
def add_note():
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if title and content:
        notes = read_notes()
        notes.insert(0, {
            "title": title,
            "content": content,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M")
        })
        save_notes(notes)

    return redirect(url_for("home"))


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if file and file.filename:
        filename = secure_filename(file.filename)

        if filename:
            file.save(os.path.join(UPLOAD_FOLDER, filename))

    return redirect(url_for("home"))


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(
        UPLOAD_FOLDER, filename, as_attachment=True
    )


@app.errorhandler(413)
def file_too_large(error):
    return "File is too large. Please upload a file under 5 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)
