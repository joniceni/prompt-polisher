import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__, template_folder="templates", static_folder="static")

# Get API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in the environment")

client = OpenAI(api_key=OPENAI_API_KEY)

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
                        "Polish prompts. Make them sharper, clearer, and shorter. "
                        "Never use Oxford commas."
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
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
