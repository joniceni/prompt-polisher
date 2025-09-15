import os, requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

# Read and gently normalise the key (never crash on whitespace)
API_KEY  = (os.environ.get("OPENAI_API_KEY") or "").strip()
API_BASE = "https://api.openai.com/v1"
PROJECT  = (os.environ.get("OPENAI_PROJECT") or "").strip() or None

PRIMARY_MODEL  = "gpt-4o-mini"
FALLBACK_MODEL = "gpt-4o"

def _headers():
    if not API_KEY:
        # We still allow the app to boot so the page loads, but API calls will show a clear message.
        return {}
    h = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    if PROJECT:
        h["OpenAI-Project"] = PROJECT
    return h

def _no_proxy():
    # Force no proxy so nothing interferes with requests
    return {}

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/polish")
def polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400
    if not API_KEY:
        return jsonify({"ok": False, "error": "OPENAI_API_KEY is not set on this service."}), 500

    try:
        payload = {
            "model": PRIMARY_MODEL,
            "messages": [
                {"role": "system",
                 "content": "Polish the user’s text into a sharp, concise British English prompt. No Oxford commas."},
                {"role": "user", "content": text},
            ],
            "max_tokens": 200,
            "temperature": 0.5,
        }

        r = requests.post(f"{API_BASE}/chat/completions",
                          headers=_headers(), json=payload,
                          timeout=60, proxies=_no_proxy())
        if not r.ok:
            # Retry once with a more permissive model (helps when a model isn’t enabled)
            payload["model"] = FALLBACK_MODEL
            r = requests.post(f"{API_BASE}/chat/completions",
                              headers=_headers(), json=payload,
                              timeout=60, proxies=_no_proxy())

        r.raise_for_status()
        data = r.json()
        out = (data["choices"][0]["message"]["content"] or "").strip()
        return jsonify({"ok": True, "response": out})

    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.get("/diag")
def diag():
    if not API_KEY:
        return {"ok": False, "error": "OPENAI_API_KEY is not set"}, 200
    try:
        r = requests.get(f"{API_BASE}/models", headers=_headers(),
                         timeout=20, proxies=_no_proxy())
        return {"ok": r.ok, "status": r.status_code, "text": r.text[:1000]}, (200 if r.ok else 500)
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}, 500

if __name__ == "__main__":
    # local dev
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
