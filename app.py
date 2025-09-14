from flask import Flask, render_template, request, jsonify
import os, openai

app = Flask(__name__, static_folder="static", template_folder="templates")

# OpenAI key from Render env var
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(force=True)
        user_prompt = (data.get("prompt") or "").strip()
        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # --- Simple rewriter system prompt ---
        system_prompt = (
            "You rewrite prompts so they’re clear, specific, and actionable. "
            "Keep the user’s intent. If the input is vague, infer sensible specifics."
        )

        # --- Choose a model you have access to ---
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
        )

        polished = completion.choices[0].message.content.strip()
        return jsonify({"prompt": polished})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # For local; Render runs via Procfile
    app.run(host="0.0.0.0", port=8000, debug=False)
