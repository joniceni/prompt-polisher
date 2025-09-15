import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI

# Create the OpenAI client.
# IMPORTANT: We pass ONLY api_key and (optionally) project.
# No proxies, no http_client — keeps us compatible with the pinned SDK.
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT") or None
)

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route("/")
def index():
    return render_template("index.html")

# Simple health check that doesn't touch OpenAI (helps isolate issues)
@app.route("/health")
def health():
    return jsonify({"ok": True}), 200

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(force=True)
        user_prompt = (data or {}).get("prompt", "").strip()
        if not user_prompt:
            return jsonify({"error": "Prompt cannot be empty."}), 400

        # Use the Chat Completions API with the current SDK
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You rewrite prompts so they’re clear, specific, and actionable. "
                        "Be concise but thorough. Keep the user's intent and context."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        polished = resp.choices[0].message.content.strip()
        return jsonify({"polished": polished})

    except Exception as e:
        # Return the message so we can see issues without digging into logs
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Local run
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
