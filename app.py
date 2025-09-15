import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Read env vars from Render Environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT", "").strip()

# Create OpenAI client (NO proxies, nothing extra)
# If OPENAI_PROJECT isn't set, OpenAI will still work with just the key.
client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT or None)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    data = request.get_json(silent=True) or {}
    user_prompt = (data.get("prompt") or "").strip()

    if not user_prompt:
        return jsonify({"error": "Prompt cannot be empty."}), 400

    try:
        # Use Chat Completions with a small, fast, inexpensive model
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You rewrite the user's text into a clear, specific, "
                        "actionable prompt for an AI assistant. Keep it concise, "
                        "preserve intent, add helpful structure, and output only "
                        "the rewritten prompt (no preamble)."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )
        polished = completion.choices[0].message.content.strip()
        return jsonify({"result": polished})

    except Exception as e:
        # Return the error so we can see it in the UI if something goes wrong
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 500


if __name__ == "__main__":
    # Local dev only; Render uses Gunicorn via Procfile
    app.run(host="0.0.0.0", port=8000, debug=False)
