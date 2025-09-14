from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

# Load API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json()
        user_text = data.get("text", "")

        if not user_text.strip():
            return jsonify({"error": "No text provided"}), 400

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are Charles, an AI assistant that rewrites messy prompts into clear, sharp ones."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=200,
            temperature=0.7
        )

        polished = response["choices"][0]["message"]["content"].strip()
        return jsonify({"polished": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
