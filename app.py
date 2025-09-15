import os
import traceback
from flask import Flask, request, jsonify, render_template, send_from_directory
from openai import OpenAI

# Be explicit about folders (prevents "blank page" if Flask can't auto-find them)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)

# Quick health + sanity endpoints
@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.get("/whoami")
def whoami():
    return "Flask is running and routing correctly.", 200

# Serve static explicitly if needed
@app.get("/static/<path:filename>")
def custom_static(filename):
    return send_from_directory(STATIC_DIR, filename)

# --- OpenAI client (no proxies) ---
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.post("/api/polish")
def api_polish():
    prompt = (request.form.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"ok": False, "error": "No prompt provided"}), 400
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise, helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=250,
        )
        answer = resp.choices[0].message.content.strip()
        return jsonify({"ok": True, "response": answer}), 200
    except Exception as e:
        app.logger.exception("OpenAI call failed")
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/")
def index():
    # Never return blank: if template fails, show a simple HTML fallback
    try:
        return render_template("index.html")
    except Exception:
        app.logger.exception("Template render failed")
        return (
            "<h1>Template error</h1>"
            "<p>Flask couldn't render <code>templates/index.html</code>.</p>"
            "<p>Traceback:</p>"
            f"<pre>{traceback.format_exc()}</pre>",
            500,
        )

# Catch-all error page so you never see a white screen
@app.errorhandler(Exception)
def handle_any_error(e):
    app.logger.exception("Unhandled error")
    return (
        "<h1>Application error</h1>"
        f"<p>{str(e)}</p>"
        f"<pre>{traceback.
