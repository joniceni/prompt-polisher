import os, requests
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set on this service")

client = OpenAI(api_key=API_KEY)
PRIMARY_MODEL = "gpt-4o-mini"
FALLBACK_MODEL = "gpt-4o-mini-translate"  # permissive fallback

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.get("/diag")
def diag():
    try:
        _ = client.models.list()
        return {"ok": True, "msg": "OpenAI reachable and key accepted"}, 200
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}, 500

@app.get("/curl")
def curl():
    # raw HTTPS probe (bypasses the SDK)
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {API_KEY}"},
            timeout=15,
        )
        return {"status": r.status_code, "ok": r.ok, "text": r.text[:4000]}, 200
    except Exception as e:
        return {"status": 0, "ok": False, "error": f"{type(e).__name__}: {e}"}, 500

@app.post("/api/polish")
def api_polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400

    sysmsg = (
        "You polish prompts. Keep intent, remove fluff, tighten wording, "
        "and make the result direct and ready to paste into an AI model. "
        "Use British English."
    )

    def call(model_name):
        return client.chat.completions.create(
            model=model_name,
            messages=[{"role": "system", "content": sysmsg},
                      {"role": "user", "content": text}],
            temperature=0.5,
            max_tokens=220,
        )

    try:
        try:
            resp = call(PRIMARY_MODEL)
        except Exception as first:
            # Try a permissive fallback model if the first fails due to access
            resp = call(FALLBACK_MODEL)
        out = resp.choices[0].message.content.strip()
        return jsonify({"ok": True, "response": out}), 200

    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
