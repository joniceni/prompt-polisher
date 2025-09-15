import os
import requests
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Create OpenAI client (no proxies!)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.json
        prompt = data.get("prompt", "")

        if not prompt.strip():
            return jsonify({"error": "No prompt provided"}), 400

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Polish the user’s text into a clear, concise, British English prompt. Do not use Oxford commas."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )

        polished = response.choices[0].message.content.strip()
        return jsonify({"polished": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/diag")
def diag():
    """Simple health check for debugging API connectivity"""
    try:
        models = client.models.list()
        model_ids = [m.id for m in models.data]
        return jsonify({"ok": True, "models": model_ids})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
