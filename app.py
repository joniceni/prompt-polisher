import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI, APIConnectionError, RateLimitError, OpenAIError

# Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Read secrets from environment (Render → Settings → Environment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_PROJECT = os.getenv("OPENAI_PROJECT")

# Create OpenAI client (new SDK)
# Both api_key AND project must be set when you’re using a Project Key.
client = OpenAI(api_key=OPENAI_API_KEY, project=OPENAI_PROJECT)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    return "ok", 200

@app.route("/polish", methods=["POST"])
def polish():
    try:
        data = request.get_json(silent=True) or {}
        user_prompt = (data.get("prompt") or "").strip()
        if not user_prompt:
            return jsonify({"error": "Please enter some text to polish."}), 400

        # System prompt that shapes the tone/content of the rewrite
        system_msg = (
            "You are a precise prompt-polishing assistant. "
            "Rewrite the user's rough idea into a single clear, actionable prompt "
            "that works well in ChatGPT (or similar). Avoid preamble. Output only the final prompt."
        )

        # OpenAI Chat Completions (new client, project-scoped)
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )

        polished = completion.choices[0].message.content.strip()
        return jsonify({"text": polished})
    except APIConnectionError:
        return jsonify({"error": "APIConnectionError: Connection error."}), 502
    except RateLimitError:
        return jsonify({"error": "Rate limited. Please try again in a moment."}), 429
    except OpenAIError as e:
        return jsonify({"error": f"OpenAI error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    # Local dev convenience
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
