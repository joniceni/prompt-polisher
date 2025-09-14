from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Load API Key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/polish', methods=['POST'])
def polish():
    try:
        data = request.get_json()
        user_prompt = data.get("prompt", "")

        if not user_prompt.strip():
            return jsonify({"error": "Prompt cannot be empty."}), 400

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites prompts to be clear, concise, and effective."},
                {"role": "user", "content": user_prompt}
            ]
        )

        polished = response["choices"][0]["message"]["content"].strip()
        return jsonify({"polished": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
