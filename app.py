import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

app = Flask(__name__)  # serves /static automatically

# OpenAI client (no proxies arg)
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.get("/health")
def health():
    return {"status": "ok"}, 200

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
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
