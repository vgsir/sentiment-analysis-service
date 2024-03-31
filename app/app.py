# Import necessary libraries for the project
from flask import Flask, request, jsonify
import jwt
import datetime
import os
import requests
from transformers import pipeline
from functools import wraps

# Import for accessing Flask and OpenAI secret keys as environment variables
from dotenv import load_dotenv, find_dotenv

# Load environment variables from a .env file, if available
load_dotenv(find_dotenv(), override=True)

# Initialize Flask application
app = Flask(__name__)

# Configure secret key for JWT from environment variables
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

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
        # Extract token from Authorization header
        token = None

        if "Authorization" in request.headers and request.headers[
            "Authorization"
        ].startswith("Bearer "):
            token = request.headers["Authorization"].split(" ")[1]
        
        # If no token found, return error
        if not token:
            return jsonify({"message": "Token is missing!"}), 403

        try:
            # Decode token using the secret key
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
    # Encode a new token for the user
    token = jwt.encode(
        {
            "user": auth.username,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=120),
        },
        app.config["SECRET_KEY"],
    )

    return jsonify({"token": token})

# Endpoint for performing sentiment analysis
@app.route("/sentiment", methods=["POST"])
@token_required
def analyze_sentiment_openai(current_user):
    """Perform sentiment analysis using OpenAI's API or fallback to local model."""
    # Extract text from request body
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Get OpenAI API key from environment variables
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        return jsonify({"error": "API key not configured"}), 500
    
    # Prepare headers and payload for OpenAI API request
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
        # Send request to OpenAI API
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        response_json = response.json()
        # Extract and return sentiment value from the response
        sentiment_text = response_json["choices"][0]["message"]["content"]

        return jsonify({"sentiment_value": sentiment_text})
    except Exception as err:
        # Fallback to local sentiment analysis in case of an error
        print(f"Falling back due to error: {err}")
        return analyze_sentiment()  # Call the fallback method


# Fallback sentiment analysis function using Hugging Face's Transformers - Bert model
sentiment_pipeline = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment",  # Used fine-tuned bert model as local model
)

# Fallback sentiment analysis using Hugging Face pipeline.
def analyze_sentiment():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            return jsonify({"error": "Missing text in request."}), 400

        text = data["text"]

        result = sentiment_pipeline(text)[0]

        # Calculate sentiment value based on the label
        sentiment_value = (
            result["score"] if result["label"] == "POSITIVE" else -result["score"]
        )
        return jsonify({"sentiment_value": sentiment_value})
    except Exception as e:
        # Handle errors and provide feedback
        return (
            jsonify(
                {
                    "error": "An error occurred processing your request.",
                    "details": str(e),
                }
            ),
            500,
        )

# Start the Flask application
if __name__ == "__main__":
    app.run(debug=True)
