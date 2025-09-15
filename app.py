import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__, static_folder="static", template_folder="templates")

# Read secrets from Render’s Environment (Dashboard → Environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")  # optional but recommended

# Create the OpenAI client (new SDK)
client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(force=True) or {}
        user_prompt = (data.get("prompt") or "").strip()

        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Keep it tight so it’s snappy (you can adjust later)
        system = (
            "You are a prompt-polishing assistant. Rewrite the user's draft "
            "into a sharp, specific, unambiguous prompt that can be dropped "
            "straight into ChatGPT (or any LLM). Keep the user's intent. "
            "Use plain language, include useful constraints (tone, format, audience), "
            "and remove fluff."
        )

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.4,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
        )

        text = resp.choices[0].message.content.strip()
        return jsonify({"result": text})

    except Exception as e:
        # Don’t leak internals to users; return a short message
        return jsonify({"error": f"APIConnectionError: {str(e)}"}), 500


# Gunicorn looks for "app"
if __name__ == "__main__":
    # Handy for local runs; Render will use gunicorn (see Procfile)
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
