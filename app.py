import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.post("/api/polish")
def api_polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt to polish."}), 400
    if client is None:
        return jsonify({"ok": False, "error": "Missing OPENAI_API_KEY on the server."}), 503

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Polish and tighten prompts. Keep meaning, increase clarity, reduce fluff."},
                {"role": "user", "content": text}
            ],
            temperature=0.5,
            max_tokens=220,
        )
        out = resp.choices[0].message.content.strip()
        return jsonify({"ok": True, "response": out}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
