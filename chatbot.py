import json
import random
import re

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


# =========================================================
# LOAD INTENTS
# =========================================================

with open("intents.json", "r", encoding="utf-8") as file:
    data = json.load(file)


# =========================================================
# PREPARE TRAINING DATA
# =========================================================

sentences = []
labels = []

for intent in data["intents"]:
    for pattern in intent["patterns"]:
        sentences.append(preprocess(pattern))
        labels.append(intent["tag"])


# =========================================================
# TF-IDF + LOGISTIC REGRESSION
# =========================================================

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(sentences)

model = LogisticRegression()
model.fit(X, labels)


# =========================================================
# INTENT PREDICTION
# =========================================================

def predict_intent(message):
    processed = preprocess(message)
    vector = vectorizer.transform([processed])

    return model.predict(vector)[0]


def get_response(intent):

    for item in data["intents"]:

        if item["tag"] == intent:
            return random.choice(item["responses"])

    return "I could not understand your request. Please try again."


# =========================================================
# REGISTRATION STATE
# =========================================================

user_data = {}
state = "start"


# =========================================================
# GREETING DETECTION
# =========================================================

def is_greeting(message):

    text = message.strip().lower()

    greetings = {
        "hello",
        "hi",
        "hey",
        "hii",
        "hiii",
        "helo",
        "hola",
        "namaste",
        "namaskar",
        "नमस्ते",
        "नमस्कार"
    }

    if text in greetings:
        return True

    # Handles phrases like:
    # "hello assistant"
    # "hi there"
    # "namaste sir"

    for greeting in greetings:

        if text.startswith(greeting + " "):
            return True

    return False


# =========================================================
# CHAT FUNCTION
# =========================================================

def chat(message):

    global state
    global user_data

    message = message.strip()

    if not message:
        return "Please enter a message to continue."


    # =====================================================
    # START
    # =====================================================

    if state == "start":

        # Direct greeting support
        if is_greeting(message):

            state = "name"

            return (
                "Welcome to the AI Registration Assistant.\n\n"
                "Let's begin your registration.\n"
                "What is your name?"
            )

        # Registration intent
        intent = predict_intent(message)

        if intent == "greeting":

            state = "name"

            return (
                "Welcome to the AI Registration Assistant.\n\n"
                "Let's begin your registration.\n"
                "What is your name?"
            )

        if intent == "registration":

            state = "name"

            return (
                "Sure. Let's start your registration.\n\n"
                "What is your name?"
            )

        return get_response(intent)


    # =====================================================
    # NAME
    # =====================================================

    elif state == "name":

        name = extract_name(message)

        # If extractor does not detect the name,
        # check whether the complete message itself is a name.

        if not name:

            possible_name = message.strip()

            if validate_name(possible_name):
                name = possible_name.title()

        if name and validate_name(name):

            user_data["name"] = name

            state = "email"

            return (
                f"Nice to meet you, {name}.\n\n"
                "Please enter your email address."
            )

        return (
            "Please enter a valid name.\n\n"
            "Example: Naina Kumari"
        )


    # =====================================================
    # EMAIL
    # =====================================================

    elif state == "email":

        email = extract_email(message)

        if email and validate_email(email):

            user_data["email"] = email

            state = "program"

            return (
                "Email verified successfully.\n\n"
                "Which internship or program "
                "would you like to register for?"
            )

        return (
            "Please enter a valid email address.\n\n"
            "Example: name@example.com"
        )


    # =====================================================
    # PROGRAM
    # =====================================================

    elif state == "program":

        program = message.strip()

        if len(program) < 2:

            return (
                "Please enter a valid internship or "
                "program name."
            )

        user_data["program"] = program

        state = "confirm"

        return (
            "Please review your registration details.\n\n"
            f"Name: {user_data['name']}\n"
            f"Email: {user_data['email']}\n"
            f"Program: {user_data['program']}\n\n"
            "Type YES to confirm or NO to cancel."
        )


    # =====================================================
    # CONFIRMATION
    # =====================================================

    elif state == "confirm":

        answer = message.lower()

        if answer in ["yes", "y", "confirm", "confirmed"]:

            registration_id = save_registration(user_data)

            state = "completed"

            return (
                "REGISTRATION SUCCESSFUL\n\n"
                f"Registration ID: {registration_id}\n"
                f"Name: {user_data['name']}\n"
                f"Email: {user_data['email']}\n"
                f"Program: {user_data['program']}\n\n"
                "Your registration has been completed successfully."
            )

        elif answer in ["no", "n", "cancel", "cancelled"]:

            user_data.clear()
            state = "start"

            return (
                "Registration cancelled.\n\n"
                "You can start a new registration anytime."
            )

        else:

            return (
                "Please type YES to confirm "
                "or NO to cancel."
            )


    # =====================================================
    # COMPLETED
    # =====================================================

    elif state == "completed":

        return (
            "Your registration has already been completed.\n\n"
            "Thank you."
        )


    # =====================================================
    # SAFETY FALLBACK
    # =====================================================

    return (
        "Something went wrong with the registration session. "
        "Please start again."
    )


# =========================================================
# TERMINAL TEST
# =========================================================

if __name__ == "__main__":

    print("\nAI Registration Assistant")
    print("Type 'exit' to stop.\n")

    while True:

        user_message = input("You: ")

        if user_message.strip().lower() == "exit":

            print("Bot: Goodbye.")
            break

        response = chat(user_message)

        print("\nBot:")
        print(response)
        print()