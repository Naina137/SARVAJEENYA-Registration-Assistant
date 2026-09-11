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

with open(
    "intents.json",
    "r",
    encoding="utf-8"
) as file:

    data = json.load(file)


# Prepare training data

sentences = []

labels = []


for intent in data["intents"]:

    for pattern in intent["patterns"]:

        sentences.append(
            preprocess(pattern)
        )

        labels.append(
            intent["tag"]
        )


# TF IDF

vectorizer = TfidfVectorizer()

X = vectorizer.fit_transform(
    sentences
)


# Logistic Regression

model = LogisticRegression()

model.fit(
    X,
    labels
)


def predict_intent(message):

    processed = preprocess(message)

    vector = vectorizer.transform([processed])

    return model.predict(vector)[0]


def get_response(intent):

    for item in data["intents"]:

        if item["tag"] == intent:

            return random.choice(
                item["responses"]
            )


    return "I did not understand that."


# Registration state

user_data = {}

state = "start"


def reset_chat():

    global state
    global user_data

    state = "start"

    user_data.clear()


def is_greeting(message):

    text = message.strip().lower()


    greetings = [

        "hello",
        "hi",
        "hey",
        "namaste",
        "namaskar",
        "नमस्ते",
        "नमस्कार"

    ]


    return text in greetings



def chat(message):

    global state
    global user_data


    message = message.strip()


    # RESTART COMMAND

    if message.lower() in [
        "restart",
        "start again",
        "new registration",
        "reset"
    ]:

        reset_chat()

        state = "name"

        return (
            "Welcome back. "
            "Let's start a new registration. "
            "What is your name?"
        )


    # START

    if state == "start":

        if is_greeting(message):

            state = "name"

            return (
                "Welcome to SARWAJNIY. "
                "Let's begin your registration. "
                "What is your name?"
            )


        intent = predict_intent(message)


        if intent == "greeting":

            state = "name"

            return (
                "Welcome to SARWAJNIY. "
                "What is your name?"
            )


        if intent == "registration":

            state = "name"

            return (
                "Sure. Let's begin your registration. "
                "What is your name?"
            )


        return get_response(intent)


    # NAME

    elif state == "name":

        name = extract_name(message)


        if not name:

            possible_name = message.strip()


            if validate_name(
                possible_name
            ):

                name = possible_name.title()


        if name and validate_name(name):

            user_data["name"] = name

            state = "email"


            return (
                f"Nice to meet you, {name}. "
                "Please enter your email address."
            )


        return (
            "Please enter a valid name. "
            "For example, My name is Naina."
        )


    # EMAIL

    elif state == "email":

        email = extract_email(message)


        if email and validate_email(email):

            user_data["email"] = email

            state = "program"


            return (
                "Your email has been verified. "
                "Which internship or program "
                "would you like to register for?"
            )


        return (
            "Please enter a valid email address."
        )


    # PROGRAM

    elif state == "program":

        program = message.strip()


        if len(program) < 2:

            return (
                "Please enter a valid program name."
            )


        user_data["program"] = program

        state = "confirm"


        return (
            "Please confirm your registration details.\n\n"
            f"Name: {user_data['name']}\n"
            f"Email: {user_data['email']}\n"
            f"Program: {user_data['program']}\n\n"
            "Type YES to confirm or NO to cancel."
        )


    # CONFIRMATION

    elif state == "confirm":

        answer = message.strip().lower()


        if answer in [
            "yes",
            "y",
            "confirm"
        ]:

            registration_id = save_registration(
                user_data
            )


            state = "completed"


            return (
                "Registration successful.\n\n"
                f"Registration ID: {registration_id}\n"
                f"Name: {user_data['name']}\n"
                f"Email: {user_data['email']}\n"
                f"Program: {user_data['program']}\n\n"
                "You can start a new registration "
                "using the Start New Registration button."
            )


        elif answer in [
            "no",
            "n",
            "cancel"
        ]:

            reset_chat()


            return (
                "Registration cancelled. "
                "You can start again anytime."
            )


        else:

            return (
                "Please type YES to confirm "
                "or NO to cancel."
            )


    # COMPLETED

    elif state == "completed":

        if is_greeting(message):

            return (
                "Your registration is already completed. "
                "Use the Start New Registration button "
                "to begin another registration."
            )


        return (
            "Your registration has already been completed. "
            "Use the Start New Registration button "
            "if you want to register again."
        )


# Terminal test

if __name__ == "__main__":

    print()

    print("SARWAJNIY Registration Assistant")

    print("Type exit to stop.")

    print()


    while True:

        user_message = input("You: ")


        if user_message.lower() == "exit":

            print(
                "SARWAJNIY: Goodbye."
            )

            break


        response = chat(
            user_message
        )


        print(
            "SARWAJNIY:",
            response
        )