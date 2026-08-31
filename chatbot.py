import json
import random

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from nlp import preprocess
from data import (
    extract_name,
    extract_email,
    validate_name,
    validate_email,
    save_registration
)


# Load intents
with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# Prepare training data
sentences = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(preprocess(pattern))
        labels.append(intent["tag"])


# TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sentences)


# Train classifier
model = LogisticRegression()
model.fit(X, labels)


def predict_intent(message):

    processed = preprocess(message)
    vector = vectorizer.transform([processed])

    return model.predict(vector)[0]


def get_response(intent):

    for item in data["intents"]:

        if item["tag"] == intent:
            return random.choice(item["responses"])

    return "Sorry, I didn't understand that."


# --------------------------------
# REGISTRATION CHAT
# --------------------------------

user_data = {}
state = "start"


def chat(message):

    global state
    global user_data

    # START
    if state == "start":

        intent = predict_intent(message)

        if intent == "greeting":
            state = "name"
            return "Hello! 👋 Welcome! What is your name?"

        if intent == "registration":
            state = "name"
            return "Sure! Let's start your registration. What is your name?"

        return get_response(intent)


    # NAME
    elif state == "name":

        name = extract_name(message)

        # If user simply enters a name
        if not name:
            possible_name = message.strip()

            if validate_name(possible_name):
                name = possible_name.title()

        if name and validate_name(name):

            user_data["name"] = name

            state = "email"

            return (
                f"Nice to meet you, {name}! 😊\n"
                "Please enter your email address."
            )

        return (
            "Please enter a valid name.\n"
            "Example: My name is Naina"
        )


    # EMAIL
    elif state == "email":

        email = extract_email(message)

        if email and validate_email(email):

            user_data["email"] = email

            state = "program"

            return (
                "Great! ✅ Email verified.\n"
                "Which internship/program would you like to register for?"
            )

        return "Please enter a valid email address."


    # PROGRAM
    elif state == "program":

        program = message.strip()

        if len(program) < 2:

            return "Please enter a valid program name."

        user_data["program"] = program

        state = "confirm"

        return (
            "\nPlease confirm your registration details:\n\n"
            f"👤 Name: {user_data['name']}\n"
            f"📧 Email: {user_data['email']}\n"
            f"🎓 Program: {user_data['program']}\n\n"
            "Type YES to confirm."
        )


    # CONFIRMATION
    elif state == "confirm":

        if message.strip().lower() in ["yes", "y", "confirm"]:

            registration_id = save_registration(user_data)

            state = "completed"

            return (
                "\n🎉 REGISTRATION SUCCESSFUL!\n\n"
                f"Registration ID: {registration_id}\n"
                f"Name: {user_data['name']}\n"
                f"Email: {user_data['email']}\n"
                f"Program: {user_data['program']}\n"
            )

        elif message.strip().lower() in ["no", "n", "cancel"]:

            user_data.clear()
            state = "start"

            return (
                "Registration cancelled.\n"
                "You can start again anytime."
            )

        else:

            return "Please type YES to confirm or NO to cancel."


    # COMPLETED
    elif state == "completed":

        return (
            "Your registration has already been completed. ✅\n"
            "Thank you!"
        )


# --------------------------------
# TERMINAL TEST
# --------------------------------

if __name__ == "__main__":

    print("\n🤖 AI Registration Assistant")
    print("Type 'exit' to stop.\n")

    while True:

        user_message = input("You: ")

        if user_message.lower() == "exit":

            print("Bot: Goodbye! 👋")
            break

        response = chat(user_message)

        print("Bot:", response)