import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")

api_key = os.environ.get("OPENAI_API_KEY")
project_id = os.environ.get("OPENAI_PROJECT")  # optional, but helpful for sk-proj keys

if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment")

# If OPENAI_PROJECT is present we pass it; otherwise we rely on the project encoded in the key.
client = OpenAI(api_key=api_key, project=project_id) if project_id else OpenAI(api_key=api_key)

@app.get("/health")
def health():
    return {"status": "ok"}, 200

@app.post("/api/polish")
def api_polish():
    text = (request.form.get("prompt") or "").strip()
    if not text:
        return jsonify({"ok": False, "error": "Please enter a prompt."}), 400

    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You polish prompts. Keep intent, remove fluff, tighten wording, "
                        "and make the result direct and ready to paste into an AI model. "
                        "Use British English."
                    )
                },
                {"role": "user", "content": text}
            ],
            temperature=0.5,
            max_tokens=220,
        )
        answer = resp.choices[0].message.content.strip()
        return jsonify({"ok": True, "response": answer}), 200

    except Exception as e:
        # Return the exact message so the UI shows what’s wrong (auth, quota, etc.)
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
