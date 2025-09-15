from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import os

app = Flask(__name__)

# Initialise OpenAI client using API key from environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt", "")

        if not prompt.strip():
            return jsonify({"error": "No prompt provided"}), 400

        try:
            # Call GPT model
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.7
            )

            reply = response.choices[0].message.content.strip()
            return jsonify({"response": reply})

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # GET request – show form
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
