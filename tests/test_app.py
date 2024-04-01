import unittest
import app
import json
import os
import sys

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir, "app"))
)
from app import app


class SentimentAnalysisServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        self.app.testing = True

    def test_auth_endpoint(self):
        response = self.app.post("/auth", auth=("user1", "password1"))
        self.assertEqual(response.status_code, 200)
        # Further assertions as needed

    def test_sentiment_endpoint(self):
        # Authenticate to obtain a token
        auth_response = self.app.post("/auth", auth=("user1", "password1"))
        self.assertEqual(auth_response.status_code, 200)
        token_data = json.loads(auth_response.data.decode("utf-8"))
        token = token_data.get("token")

        # Now use the token to test the /sentiment endpoint
        if token:
            response = self.app.post(
                "/sentiment",
                headers={"Authorization": f"Bearer {token}"},
                json={"text": "I love this service!"},
            )
            self.assertEqual(response.status_code, 200)
            # Add further assertions here
        else:
            self.fail("Authentication failed, token was not obtained.")


if __name__ == "__main__":
    unittest.main()
