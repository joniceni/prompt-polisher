import os
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

# ---------- CRITICAL ----------
# Do NOT pass 'proxies' or custom http_client here.
# Just rely on environment (HTTP_PROXY/HTTPS_PROXY) if you actually need a proxy.
# --------------------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

app = Flask(__name__)

@app.get("/health")
def health():
    # quick probe endpoint for Render
    return {"status": "ok"}, 200

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        prompt = request.form.get("prompt", "").strip()
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a concise, helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=250,
            )
            answer = resp.choices[0].message.content.strip()
            return jsonify({"response": answer})
        except Exception as e:
            # Surface exact error in logs and as JSON
            app.logger.exception("OpenAI error")
            return jsonify({"error": str(e)}), 500

    return render_template("index.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
