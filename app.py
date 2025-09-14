from flask import Flask, render_template, request
from openai import OpenAI
import os

app = Flask(__name__, template_folder="templates")

# OpenAI client (reads your key from Secrets)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


@app.route("/", methods=["GET", "POST"])
def home():
    response_text = None
    if request.method == "POST":
        user_input = request.form.get("text_input", "").strip()
        if user_input:
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{
                        "role":
                        "system",
                        "content":
                        "You are Charles. Rewrite the user's text into a single, clear AI prompt. Be concise. Output only the improved prompt."
                    }, {
                        "role": "user",
                        "content": user_input
                    }],
                    max_tokens=200,
                    temperature=0.3)
                response_text = resp.choices[0].message.content
            except Exception as e:
                response_text = f"Error: {e}"

    return render_template("index.html", response_text=response_text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
