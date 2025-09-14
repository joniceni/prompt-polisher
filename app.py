from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)

# Create OpenAI client with API key from environment variable
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.json
        user_text = data.get("text", "")

        if not user_text.strip():
            return jsonify({"error": "No text provided"}), 400

        # Call OpenAI to polish the text
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Charles, a witty but professional AI that rewrites prompts to be sharper, clearer, and more effective."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7
        )

        polished = response.choices[0].message.content.strip()
        return jsonify({"polished": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="
