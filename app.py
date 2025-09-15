from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Load API Key and Project ID from environment
api_key = os.getenv("OPENAI_API_KEY")
project_id = os.getenv("OPENAI_PROJECT")

client = OpenAI(api_key=api_key, project=project_id)

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

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an assistant that rewrites prompts to be clear, concise, and effective."},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=200
        )

        polished_prompt = response.choices[0].message.content.strip()
        return jsonify({"polished_prompt": polished_prompt})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
