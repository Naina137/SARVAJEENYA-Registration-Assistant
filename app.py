from flask import Flask, render_template, request, jsonify
from chatbot import chat

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_api():

    data = request.get_json()

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "response": "Please enter a message."
        })

    response = chat(message)

    return jsonify({
        "response": response
    })


if __name__ == "__main__":
    app.run(debug=True)