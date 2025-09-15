from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__, static_folder="static", template_folder="templates")

# Build OpenAI client (no 'proxies' kwarg)
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT"),
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(silent=True) or {}
        user_prompt = (data.get("prompt") or "").strip()
        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Ask the model to rewrite the user's rough idea into a sharp, clear prompt
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that rewrites prompts to be clear, concise, and effective. "
                        "Keep the user's intent but sharpen objectives, add key details, and specify format/constraints when useful. "
                        "Return only the improved prompt—no extra commentary."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
        )

        polished = completion.choices[0].message.content.strip()
        return jsonify({"polished": polished})

    except Exception as e:
        # Don’t leak internals in production; this is handy while we finish setup.
        return jsonify({"error": f"Server error: {str(e)}"}), 500


if __name__ == "__main__":
    # Local debug: on Render this block isn’t used (gunicorn runs the app)
    app.run(host="0.0.0.0", port=5000, debug=True)
