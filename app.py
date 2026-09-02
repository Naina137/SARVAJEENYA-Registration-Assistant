from flask import Flask, render_template, request, jsonify
from chatbot import chat

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_api():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a message."
        })

    try:
        response = chat(message)

        return jsonify({
            "response": response
        })

    except Exception as e:
        print("Chat error:", e)
        return jsonify({
            "response": "Sorry, something went wrong. Please try again."
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)