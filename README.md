#Sentiment Analysis Service

This project implements a sentiment analysis service using Flask, JWT for authentication, and the Transformers library for processing natural language data. It supports sentiment analysis via both OpenAI's API and a fallback local model powered by Hugging Face's Transformers.

Features

Authentication: Secure access with JWT tokens.
OpenAI API Integration: Leverages OpenAI's GPT-3.5 for sentiment analysis.
Local Fallback: Utilizes a BERT model from Hugging Face's Transformers library for sentiment analysis without relying on external APIs.
Environment Variable Management: Uses python-dotenv for secure handling of secrets and configurations.
Prerequisites

Python 3.6+
Flask
PyJWT
requests
transformers
python-dotenv
Installation

Clone the Repository
bash
Copy code
git clone https://github.com/vgsir/sentiment-analysis-service.git
cd sentiment-analysis-service
Set up a Virtual Environment (optional but recommended)
bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
Install Dependencies
bash
Copy code
pip install -r requirements.txt
Environment Variables
Create a .env file in the root directory.
Add your FLASK_SECRET_KEY and OPENAI_API_KEY:
makefile
Copy code
FLASK_SECRET_KEY=your_secret_key_here
OPENAI_API_KEY=your_openai_api_key_here
Usage

To run the Flask application:

bash
Copy code
flask run
API Endpoints

POST /auth: Authenticate and receive a JWT token.
POST /sentiment: Perform sentiment analysis on provided text. Requires JWT authentication.
Contributing

Contributions to the project are welcome! Please fork the repository and submit a pull request with your changes or improvements.