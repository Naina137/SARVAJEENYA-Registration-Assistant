import re
import nltk

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


# Download required NLTK data
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")


lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))


def preprocess(text):
    """
    Clean and preprocess user text.
    """

    # Convert to lowercase
    text = text.lower()

    # Remove unwanted special characters
    text = re.sub(r"[^a-zA-Z0-9@\.\s]", "", text)

    # Split into words
    words = text.split()

    # Remove stopwords and perform lemmatization
    words = [
        lemmatizer.lemmatize(word)
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)