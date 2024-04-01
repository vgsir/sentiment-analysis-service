# Import necessary libraries
from flask import Flask, request, jsonify
import jwt
import datetime
import os
import requests
from transformers import pipeline
from functools import wraps
import pandas as pd

# Import for accessing Flask and OpenAI secret keys as environment variables
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file, if available
load_dotenv(find_dotenv(), override=True)

# Initialize Flask application
app = Flask(__name__)

# Configure secret key for JWT from environment variables
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")


# Load the dataset
def load_tweets_dataset(csv_path="data/Tweets.csv"):
    try:
        df = pd.read_csv(csv_path, usecols=["text", "airline_sentiment"])
        print("Dataset loaded successfully.")
        return df
    except FileNotFoundError:
        print(f"File not found: {csv_path}")
        return None
    except Exception as e:
        print(f"Error loading the dataset: {e}")
        return None


tweets_df = load_tweets_dataset()

# A mock user database for demonstration purposes
users = {
    "user1": "password1",
}


# Decorator for enforcing authentication
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)

    return decorated


# Decorator for token-based authentication
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers and request.headers[
            "Authorization"
        ].startswith("Bearer "):
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return jsonify({"message": "Token is missing!"}), 403
        try:
            decode_data = jwt.decode(
                token, app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = decode_data["user"]
        except:
            return jsonify({"message": "Token is invalid!"}), 403
        return f(current_user, *args, **kwargs)

    return decorated


# Endpoint for user authentication
@app.route("/auth", methods=["POST"])
@auth_required
def login():
    auth = request.authorization
    if auth:
        token = jwt.encode(
            {
                "user": auth.username,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
            },
            app.config["SECRET_KEY"],
        )
        return jsonify({"token": token})
    else:
        return jsonify({"message": "Authentication required."}), 401


# Endpoint for performing sentiment analysis
@app.route("/sentiment", methods=["POST"])
@token_required
def analyze_sentiment_openai(current_user):
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        return jsonify({"error": "API key not configured"}), 500
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f'Please analyze the sentiment of the following text and provide a sentiment score that reflects the probability of the sentiment being positive or negative, on a scale from -1 to 1. A score closer to 1 indicates a higher probability of the text being positive, a score closer to -1 indicates a higher probability of the text being negative, and a score around 0 suggests neutral sentiment with equal probabilities for both positive and negative sentiments. Calculate and only return this probabilistic sentiment score for the text: "{text}" I only want to see the score',
            }
        ],
        "temperature": 0.7,
    }
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        response_json = response.json()
        sentiment_text = response_json["choices"][0]["message"]["content"]
        return jsonify({"sentiment_value": sentiment_text})
    except Exception as err:
        print(f"Falling back due to error: {err}")
        return analyze_sentiment()


# Fallback sentiment analysis function using Hugging Face's Transformers
sentiment_pipeline = pipeline(
    "sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment"
)


# Fallback sentiment analysis using Hugging Face pipeline.
def analyze_sentiment():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing text in request."}), 400
    text = data["text"]
    result = sentiment_pipeline(text)[0]
    sentiment_value = (
        result["score"] if result["label"] == "POSITIVE" else -result["score"]
    )
    return jsonify({"sentiment_value": sentiment_value})


# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
