import re
import json
import random


# -------------------------------
# NAME EXTRACTION
# -------------------------------

def extract_name(text):
    patterns = [
        r"my name is ([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"i am ([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"i'm ([A-Za-z]+(?:\s+[A-Za-z]+)?)",
        r"this is ([A-Za-z]+(?:\s+[A-Za-z]+)?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return match.group(1).strip().title()

    return None


# -------------------------------
# EMAIL EXTRACTION
# -------------------------------

def extract_email(text):

    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    match = re.search(pattern, text)

    if match:
        return match.group(0).lower()

    return None


# -------------------------------
# EMAIL VALIDATION
# -------------------------------

def validate_email(email):

    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return bool(re.match(pattern, email))


# -------------------------------
# NAME VALIDATION
# -------------------------------

def validate_name(name):

    return bool(
        re.fullmatch(r"[A-Za-z]+(?:\s+[A-Za-z]+)*", name)
    )


# -------------------------------
# SAVE REGISTRATION
# -------------------------------

def save_registration(user_data):

    try:
        with open("registrations.json", "r", encoding="utf-8") as file:
            registrations = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError):
        registrations = []


    # Generate unique registration ID
    registration_id = "REG-" + str(random.randint(1000, 9999))

    user_data["registration_id"] = registration_id


    registrations.append(user_data)


    with open("registrations.json", "w", encoding="utf-8") as file:
        json.dump(registrations, file, indent=4)


    return registration_id