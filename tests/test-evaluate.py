import requests

# Define the base URL of the FastAPI application
BASE_URL = "http://127.0.0.1:8000"

# Define the payload for the /evaluate endpoint
payload = {
    "patient_id": 123,
    "name": "John Doe",
    "age": 45,
    "symptoms": ["fever", "cough", "fatigue"],
    "bmi": 24.5,
    "date_of_last_surgery": "2023-05-10"
}

# Send a POST request to the /evaluate endpoint
response = requests.post(f"{BASE_URL}/evaluate", json=payload)

# Print the response
if response.status_code == 200:
    print("Response from /evaluate endpoint:")
    print(response.json())
else:
    print(f"Failed to call /evaluate endpoint. Status code: {response.status_code}")
    print(response.text)