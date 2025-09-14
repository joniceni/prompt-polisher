from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI

# Tell Flask where to find static and template files
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load OpenAI client with API key from environment
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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

        # Use GPT to polish the text
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites messy draft prompts into sharp, clear, and effective prompts for ChatGPT or other AI tools."},
                {"role": "user", "content": user_text}
            ],
            temperature=0.7,
            max_tokens=200
        )

        polished = response.choices[0].message.content.strip()
        return jsonify({"polished": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run on the port Render expects
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
