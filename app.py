import os, json, requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

API_KEY  = os.environ.get("OPENAI_API_KEY")
API_BASE = os.environ.get("OPENAI_API_BASE", "https://api.openai.com/v1")
PROJECT  = os.environ.get("OPENAI_PROJECT")  # optional

if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set on this service")

PRIMARY_MODEL  = "gpt-4o-mini"
FALLBACK_MODEL = "gpt-4o-mini-translate"  # permissive fallback

def _headers():
    h = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    if PROJECT:
        h["OpenAI-Project"] = PROJECT
    return h

def _no_proxy():
    # Force NO proxy even if HTTP(S)_PROXY exists in a linked env group
    return {}

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.get("/diag")
def diag():
    try:
        r = requests.get(f"{API_BASE}/models", headers=_headers(), timeout=20, proxies=_no_proxy())
        return {"ok": r.ok, "status": r.status_code, "text": r.text[:2000]}, (200 if r.ok else 500)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}, 500

def chat_complete(model: str, user_text: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system",
             "content": "You polish prompts. Keep intent, remove fluff, tighten wording. British English. Output only the improved prompt."},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.5,
        "max_tokens": 220,
    }
    r = requests.post(
        f"{API_BASE}/chat/completions",
        headers=_headers(),
        json=payload,
        timeout=60,
        proxies=_no_proxy(),
    )
    r.raise_for_status()
    data = r.json()
    return (data["choices"][0]["message"]["content"] or "").strip()

@app.post("/api/polish")
def api_polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400
    try:
        try:
            out = chat_complete(PRIMARY_MODEL, text)
        except Exception:
            out = chat_complete(FALLBACK_MODEL, text)
        return jsonify({"ok": True, "response": out}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
