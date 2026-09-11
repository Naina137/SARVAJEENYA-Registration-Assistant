from flask import Flask, render_template, request, jsonify

from chatbot import chat, reset_chat


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


@app.route("/reset", methods=["POST"])
def reset():

    reset_chat()

    return jsonify({
        "success": True
    })


if __name__ == "__main__":

    app.run(debug=True)