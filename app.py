import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set on this service")

client = OpenAI(api_key=API_KEY)
MODEL = "gpt-4o-mini"   # change here if your project doesn’t have this model

@app.get("/health")
def health():
    return {"status": "ok"}, 200

# Quick connectivity + permissions check
@app.get("/diag")
def diag():
    try:
        # light call that also surfaces auth/permission issues
        _ = client.models.list()
        return {"ok": True, "msg": "OpenAI reachable and key accepted"}, 200
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}"}, 500

@app.post("/api/polish")
def api_polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400

    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You polish prompts. Keep intent, remove fluff, tighten wording, "
                        "and make it direct and ready to paste into an AI model. "
                        "Use British English."
                    ),
                },
                {"role": "user", "content": text},
            ],
            temperature=0.5,
            max_tokens=220,
        )
        out = resp.choices[0].message.content.strip()
        return jsonify({"ok": True, "response": out}), 200

    except Exception as e:
        # Bubble the real cause to the UI (auth/quota/model access/network)
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
