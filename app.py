import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Tell Flask where things live
app = Flask(__name__, static_folder="static", template_folder="templates")

# --- OpenAI client configured for PROJECT KEYS ---
# Set both env vars on Render:
#   OPENAI_API_KEY = sk-proj-... (your project key)
#   OPENAI_PROJECT = proj_...    (your project ID)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT", "")

client = OpenAI(
    api_key=OPENAI_API_KEY,
    project=OPENAI_PROJECT or None  # None if not set
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return "ok", 200

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(force=True) or {}
        rough = (data.get("prompt") or "").strip()
        if not rough:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        system = (
            "You rewrite messy or vague draft prompts into one clear, specific, "
            "actionable prompt ready to paste into ChatGPT. Preserve intent. "
            "No preamble—return only the polished prompt."
        )

        # New SDK (v1.x) call; works with project keys when 'project' is set on client
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": rough}
            ],
            temperature=0.3,
            max_tokens=300
        )

        polished = resp.choices[0].message.content.strip()
        return jsonify({"prompt": polished})

    except Exception as e:
        # Bubble the message so you can see what’s wrong from the UI
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500

if __name__ == "__main__":
    # Local run (Render uses Procfile/gunicorn)
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
