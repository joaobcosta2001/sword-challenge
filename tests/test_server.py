import unittest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from server import app, db_cursor, db_connection, redis_client
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
import asyncio

# Set up the test client
client = TestClient(app)

# Helper function to generate a JWT token
def generate_token(username: str):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

# Test data
TEST_USER = {
    "username": "my_admin",
    "password": "password123"
}

class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment by creating a test user in the database.
        """
        hashed_password = bcrypt.hashpw(TEST_USER["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        db_cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT DO NOTHING", (TEST_USER["username"], hashed_password))
        db_connection.commit()

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test environment by deleting the test user from the database.
        """
        db_cursor.execute("DELETE FROM users WHERE username = %s", (TEST_USER["username"],))
        db_connection.commit()

    def test_login_success(self):
        """
        Test successful login with valid credentials.
        """
        response = client.post("/login", json=TEST_USER)
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json())

    def test_login_invalid_username(self):
        """
        Test login with an invalid username.
        """
        response = client.post("/login", json={"username": "invaliduser", "password": TEST_USER["password"]})
        self.assertEqual(response.status_code, 401)

    def test_login_invalid_password(self):
        """
        Test login with an invalid password.
        """
        response = client.post("/login", json={"username": TEST_USER["username"], "password": "wrongpassword"})
        self.assertEqual(response.status_code, 401)

    def test_evaluate_patient_success(self):
        """
        Test the /evaluate endpoint with valid patient data.
        """
        token = generate_token(TEST_USER["username"])
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "patient_data": {
                "name": "John Doe",
                "age": 45,
                "height": 175,
                "weight": 85,
                "recent_surgery": False,
                "ai_description": "Experiencing mild joint pain"
            }
        }
        response = client.post("/evaluate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("recommendation", response.json())

    def test_evaluate_patient_missing_data(self):
        """
        Test the /evaluate endpoint with missing patient data.
        """
        token = generate_token(TEST_USER["username"])
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        response = client.post("/evaluate", json=payload, headers=headers)
        self.assertEqual(response.status_code, 400)

    def test_get_recommendation_success(self):
        """
        Test the /recommendation/{recommendation_id} endpoint with a valid recommendation ID.
        """
        token = generate_token(TEST_USER["username"])
        headers = {"Authorization": f"Bearer {token}"}
        # Insert a test recommendation into the database
        recommendation_id = "test-recommendation-id"
        patient_id = "test-patient-id"
        recommendation_text = "Test Recommendation"
        timestamp = datetime.utcnow()
        db_cursor.execute(
            "INSERT INTO recommendations (recommendation_id, patient_id, recommendation, timestamp, created_by) VALUES (%s, %s, %s, %s, %s)",
            (recommendation_id, patient_id, recommendation_text, timestamp, TEST_USER["username"])
        )
        db_connection.commit()

        # Test the endpoint
        response = client.get(f"/recommendation/{recommendation_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["recommendation"], recommendation_text)

        # Cleanup
        db_cursor.execute("DELETE FROM recommendations WHERE recommendation_id = %s", (recommendation_id,))
        db_connection.commit()

    def test_get_recommendation_not_found(self):
        """
        Test the /recommendation/{recommendation_id} endpoint with a nonexistent recommendation ID.
        """
        token = generate_token(TEST_USER["username"])
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("/recommendation/nonexistent-id", headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_recommendation_unauthorized(self):
        """
        Test the /recommendation/{recommendation_id} endpoint with a recommendation created by another user.
        """
        token = generate_token("anotheruser")
        headers = {"Authorization": f"Bearer {token}"}
        recommendation_id = "test-recommendation-id"
        patient_id = "test-patient-id"
        recommendation_text = "Test Recommendation"
        timestamp = datetime.utcnow()
        db_cursor.execute(
            "INSERT INTO recommendations (recommendation_id, patient_id, recommendation, timestamp, created_by) VALUES (%s, %s, %s, %s, %s)",
            (recommendation_id, patient_id, recommendation_text, timestamp, TEST_USER["username"])
        )
        db_connection.commit()

        # Test the endpoint
        response = client.get(f"/recommendation/{recommendation_id}", headers=headers)
        self.assertEqual(response.status_code, 404)

        # Cleanup
        db_cursor.execute("DELETE FROM recommendations WHERE recommendation_id = %s", (recommendation_id,))
        db_connection.commit()

if __name__ == "__main__":
    unittest.main()