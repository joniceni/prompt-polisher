import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set.")

client = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/polish")
def polish():
    try:
        data = request.get_json(force=True) or {}
        raw = (data.get("text") or "").strip()
        if not raw:
            return jsonify({"error": "Empty input."}), 400

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content":
                 "You turn rough ideas into clear, structured, high-impact prompts. "
                 "Keep it concise, actionable, and free of meta-chatter."},
                {"role": "user", "content": raw}
            ],
            temperature=0.2,
            max_tokens=600,
        )
        out = resp.choices[0].message.content.strip()
        return jsonify({"polished": out}), 200
    except Exception as e:
        app.logger.exception("Polish failed: %s", e)
        return jsonify({"error": "Server error contacting AI. Try again."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
