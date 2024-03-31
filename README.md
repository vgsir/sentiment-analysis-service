# Sentiment Analysis Service

This project implements a sentiment analysis service using Flask, JWT for authentication, and the Transformers library for processing natural language data. It supports sentiment analysis via both OpenAI's API and a fallback local model powered by Hugging Face's Transformers.

## Features

- Authentication: Secure access with JWT tokens.
- OpenAI API Integration: Leverages OpenAI's GPT-3.5 for sentiment analysis.
- Local Fallback: Utilizes a BERT model from Hugging Face's Transformers library for sentiment analysis without relying on external APIs.
- Environment Variable Management: Uses python-dotenv for secure handling of secrets and configurations.

## Prerequisites

- Python 3.6+
- Flask
- PyJWT
- requests
- transformers
- python-dotenv

## Installation

1. ### Clone the Repository

git clone https://github.com/vgsir/sentiment-analysis-service.git

cd sentiment-analysis-service

2. ### Set up a Virtual Environment

python -m venv venv

source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. ### Install Dependencies

pip install -r requirements.txt

4. ### Environment Variables

- Create a .env file in the root directory.
- Add your FLASK_SECRET_KEY and OPENAI_API_KEY:

FLASK_SECRET_KEY=your_secret_key_here

OPENAI_API_KEY=your_openai_api_key_here

## Usage

To run the Flask application:

flask run

## API Endpoints

POST /auth: Authenticate and receive a JWT token.

POST /sentiment: Perform sentiment analysis on provided text. Requires JWT authentication.