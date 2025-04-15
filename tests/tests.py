import requests

# Define the API endpoints
login_url = "http://localhost:8000/login"
evaluate_url = "http://localhost:8000/evaluate"

# Arrays to track successes and errors
successes = []
errors = []

# Test 1: Attempt to hit /evaluate without login (should fail)
try:
    evaluate_response = requests.post(evaluate_url, json={"patient_data": {}}, headers={"Content-Type": "application/json"})
    if evaluate_response.status_code == 401 or evaluate_response.status_code == 403:  # Unauthorized
        successes.append("Unauthorized access to /evaluate without login blocked")
        print("Unauthorized access to /evaluate without login: Test passed")
    else:
        errors.append("Unexpected success hitting /evaluate without login")
        print("Unexpected success hitting /evaluate without login")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during unauthorized /evaluate test: {e}")
    print("Error during unauthorized /evaluate test:", e)

# Test 2: Login with wrong credentials (should fail)
wrong_login_payload = {
    "username": "wrong_user",
    "password": "wrong_password"
}
try:
    login_response = requests.post(login_url, json=wrong_login_payload)
    if login_response.status_code == 401:  # Unauthorized
        successes.append("Login with wrong credentials (expected failure)")
        print("Login with wrong credentials: Test passed")
    else:
        errors.append("Unexpected success with wrong credentials")
        print("Unexpected success with wrong credentials")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during login with wrong credentials: {e}")
    print("Error during login with wrong credentials:", e)

# Test 3: Login with correct credentials (should succeed)
login_payload = {
    "username": "my_admin",  # Replace with a valid username
    "password": "password123"  # Replace with a valid password
}
try:
    login_response = requests.post(login_url, json=login_payload)
    login_response.raise_for_status()  # Raise an exception for HTTP errors
    token = login_response.json().get("access_token")
    if not token:
        raise ValueError("Failed to retrieve access token")
    successes.append("Login successful")
    print("Successfully retrieved token:", token)
except requests.exceptions.RequestException as e:
    errors.append(f"Error during login: {e}")
    print("Error during login:", e)
    exit(1)

# Test 4: Evaluate endpoint with valid token (should succeed)
evaluate_payload = {
    "patient_data": {
        "name": "John Doe",
        "age": 45,
        "height": 175,
        "weight": 85,
        "recent_surgery": False,
        "ai_description": None
    }
}
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}
try:
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()  # Raise an exception for HTTP errors
    successes.append("Evaluation successful")
    print("Response from /evaluate:", evaluate_response.json())
except requests.exceptions.RequestException as e:
    errors.append(f"Error during evaluation: {e}")
    print("Error during evaluation:", e)


# Test 5: Patient over 65 with chronic pain (should recommend Physical Therapy)
evaluate_payload = {
    "patient_data": {
        "name": "Elderly Patient",
        "age": 70,
        "height": 170,
        "weight": 70,
        "recent_surgery": False,
        "ai_description": "Chronic pain in the lower back"
    }
}
try:
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation = evaluate_response.json().get("recommendation", "")
    if "Physical Therapy" in recommendation:
        successes.append("Recommendation for Physical Therapy for patient over 65 with chronic pain")
        print("Test passed: Physical Therapy recommended for patient over 65 with chronic pain")
    else:
        errors.append("Failed to recommend Physical Therapy for patient over 65 with chronic pain")
        print("Test failed: Physical Therapy not recommended for patient over 65 with chronic pain")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for Physical Therapy recommendation: {e}")
    print("Error during test for Physical Therapy recommendation:", e)

# Test 6: Patient with BMI over 30 (should recommend Weight Management Program)
evaluate_payload = {
    "patient_data": {
        "name": "Overweight Patient",
        "age": 40,
        "height": 160,
        "weight": 100,  # BMI = 39.06
        "recent_surgery": False,
        "ai_description": None
    }
}
try:
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation = evaluate_response.json().get("recommendation", "")
    if "Weight Management Program" in recommendation:
        successes.append("Recommendation for Weight Management Program for patient with BMI over 30")
        print("Test passed: Weight Management Program recommended for patient with BMI over 30")
    else:
        errors.append("Failed to recommend Weight Management Program for patient with BMI over 30")
        print("Test failed: Weight Management Program not recommended for patient with BMI over 30")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for Weight Management Program recommendation: {e}")
    print("Error during test for Weight Management Program recommendation:", e)

# Test 7: Patient with recent surgery (should recommend Post-Op Rehabilitation Plan)
evaluate_payload = {
    "patient_data": {
        "name": "Post-Surgery Patient",
        "age": 50,
        "height": 175,
        "weight": 75,
        "recent_surgery": True,
        "ai_description": None
    }
}
try:
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation = evaluate_response.json().get("recommendation", "")
    if "Post-Op Rehabilitation Plan" in recommendation:
        successes.append("Recommendation for Post-Op Rehabilitation Plan for patient with recent surgery")
        print("Test passed: Post-Op Rehabilitation Plan recommended for patient with recent surgery")
    else:
        errors.append("Failed to recommend Post-Op Rehabilitation Plan for patient with recent surgery")
        print("Test failed: Post-Op Rehabilitation Plan not recommended for patient with recent surgery")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for Post-Op Rehabilitation Plan recommendation: {e}")
    print("Error during test for Post-Op Rehabilitation Plan recommendation:", e)

# Test 8: Patient with no specific conditions (should recommend General Health Checkup)
evaluate_payload = {
    "patient_data": {
        "name": "Healthy Patient",
        "age": 30,
        "height": 175,
        "weight": 70,
        "recent_surgery": False,
        "ai_description": None
    }
}
try:
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation = evaluate_response.json().get("recommendation", "")
    if "General Health Checkup" in recommendation:
        successes.append("Recommendation for General Health Checkup for patient with no specific conditions")
        print("Test passed: General Health Checkup recommended for patient with no specific conditions")
    else:
        errors.append("Failed to recommend General Health Checkup for patient with no specific conditions")
        print("Test failed: General Health Checkup not recommended for patient with no specific conditions")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for General Health Checkup recommendation: {e}")
    print("Error during test for General Health Checkup recommendation:", e)

# Test 9: Retrieve a recommendation by ID (should succeed)
try:
    # Save a recommendation ID from a valid evaluation
    evaluate_payload = {
        "patient_data": {
            "name": "John Doe",
            "age": 45,
            "height": 175,
            "weight": 85,
            "recent_surgery": False,
            "ai_description": None
        }
    }
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation_id = evaluate_response.json().get("recommendation_id")
    
    if not recommendation_id:
        raise ValueError("Failed to retrieve recommendation ID")

    # Use the recommendation ID to hit the /recommendation/{id} endpoint
    recommendation_url = f"http://localhost:8000/recommendation/{recommendation_id}"
    recommendation_response = requests.get(recommendation_url, headers=headers)
    recommendation_response.raise_for_status()

    if recommendation_response.status_code == 200:
        successes.append("Successfully retrieved recommendation by ID")
        print("Test passed: Successfully retrieved recommendation by ID")
    else:
        errors.append("Failed to retrieve recommendation by ID")
        print("Test failed: Failed to retrieve recommendation by ID")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for retrieving recommendation by ID: {e}")
    print("Error during test for retrieving recommendation by ID:", e)

# Test 10: Attempt to access another user's recommendation (should fail)
try:
    # Save a recommendation ID from the current user
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)
    evaluate_response.raise_for_status()
    recommendation_id = evaluate_response.json().get("recommendation_id")

    if not recommendation_id:
        raise ValueError("Failed to retrieve recommendation ID")

    # Login as another user
    other_user_payload = {
        "username": "my_admin2",
        "password": "password123"
    }
    other_user_login_response = requests.post(login_url, json=other_user_payload)
    other_user_login_response.raise_for_status()
    other_user_token = other_user_login_response.json().get("access_token")

    if not other_user_token:
        raise ValueError("Failed to retrieve access token for other user")

    # Attempt to access the recommendation ID with the other user's token
    other_user_headers = {
        "Authorization": f"Bearer {other_user_token}",
        "Content-Type": "application/json"
    }
    recommendation_url = f"http://localhost:8000/recommendation/{recommendation_id}"
    recommendation_response = requests.get(recommendation_url, headers=other_user_headers)

    if recommendation_response.status_code == 403 or recommendation_response.status_code == 401 or recommendation_response.status_code == 404:  # Forbidden or not found
        successes.append("Access to another user's recommendation blocked")
        print("Test passed: Access to another user's recommendation blocked")
    else:
        errors.append("Unexpected success accessing another user's recommendation")
        print("Test failed: Unexpected success accessing another user's recommendation")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for accessing another user's recommendation: {e}")
    print("Error during test for accessing another user's recommendation:", e)

# Test 11: Attempt to retrieve a recommendation with a wrong ID (should fail)
try:
    # Use a non-existent recommendation ID
    wrong_recommendation_id = "123e4567-e89b-12d3-a456-426614174000"  # Example of a UUID that doesn't exist
    recommendation_url = f"http://localhost:8000/recommendation/{wrong_recommendation_id}"
    recommendation_response = requests.get(recommendation_url, headers=headers)

    if recommendation_response.status_code == 404:  # Not Found
        successes.append("Retrieving recommendation with wrong ID blocked")
        print("Test passed: Retrieving recommendation with wrong ID blocked")
    else:
        errors.append("Unexpected success retrieving recommendation with wrong ID")
        print("Test failed: Unexpected success retrieving recommendation with wrong ID")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for retrieving recommendation with wrong ID: {e}")
    print("Error during test for retrieving recommendation with wrong ID:", e)

# Test 12: Attempt to retrieve a recommendation with an invalid ID type (should fail)
try:
    # Use an invalid ID type (e.g., a string that is not a UUID)
    invalid_recommendation_id = "invalid-id"
    recommendation_url = f"http://localhost:8000/recommendation/{invalid_recommendation_id}"
    recommendation_response = requests.get(recommendation_url, headers=headers)

    if recommendation_response.status_code == 400:  # Unprocessable Entity (validation error)
        successes.append("Retrieving recommendation with invalid ID type blocked")
        print("Test passed: Retrieving recommendation with invalid ID type blocked")
    else:
        errors.append("Unexpected success retrieving recommendation with invalid ID type")
        print("Test failed: Unexpected success retrieving recommendation with invalid ID type")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for retrieving recommendation with invalid ID type: {e}")
    print("Error during test for retrieving recommendation with invalid ID type:", e)

# Test 13: Attempt to retrieve a recommendation with a missing ID (should fail)
try:
    # Attempt to hit the endpoint without providing an ID
    recommendation_url = "http://localhost:8000/recommendation/"
    recommendation_response = requests.get(recommendation_url, headers=headers)

    if recommendation_response.status_code == 404:  # Not Found
        successes.append("Retrieving recommendation with missing ID blocked")
        print("Test passed: Retrieving recommendation with missing ID blocked")
    else:
        errors.append("Unexpected success retrieving recommendation with missing ID")
        print("Test failed: Unexpected success retrieving recommendation with missing ID")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for retrieving recommendation with missing ID: {e}")
    print("Error during test for retrieving recommendation with missing ID:", e)

# Test 14: Attempt to evaluate with missing patient_data (should fail)
try:
    # Send a request without the "patient_data" property
    evaluate_payload = {}
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)

    if evaluate_response.status_code == 400:  # Unprocessable Entity (validation error)
        successes.append("Evaluation with missing patient_data blocked")
        print("Test passed: Evaluation with missing patient_data blocked")
    else:
        errors.append("Unexpected success evaluating with missing patient_data")
        print("Test failed: Unexpected success evaluating with missing patient_data")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for evaluation with missing patient_data: {e}")
    print("Error during test for evaluation with missing patient_data:", e)

# Test 15: Attempt to evaluate with invalid data types (should fail)
try:
    # Send a request with invalid data types for patient_data properties
    evaluate_payload = {
        "patient_data": {
            "name": 123,  # Invalid type (should be a string)
            "age": "forty-five",  # Invalid type (should be an integer)
            "height": "one seventy-five",  # Invalid type (should be a number)
            "weight": "eighty-five",  # Invalid type (should be a number)
            "recent_surgery": "no",  # Invalid type (should be a boolean)
            "ai_description": 456  # Invalid type (should be a string or None)
        }
    }
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)

    if evaluate_response.status_code == 400:  # Unprocessable Entity (validation error)
        successes.append("Evaluation with invalid data types blocked")
        print("Test passed: Evaluation with invalid data types blocked")
    else:
        errors.append("Unexpected success evaluating with invalid data types")
        print("Test failed: Unexpected success evaluating with invalid data types")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for evaluation with invalid data types: {e}")
    print("Error during test for evaluation with invalid data types:", e)

# Test 16: Attempt to evaluate with missing required fields (should fail)
try:
    # Send a request with missing required fields in patient_data
    evaluate_payload = {
        "patient_data": {
            "name": "John Doe"  # Only "name" is provided, other fields are missing
        }
    }
    evaluate_response = requests.post(evaluate_url, json=evaluate_payload, headers=headers)

    if evaluate_response.status_code == 400:  # Unprocessable Entity (validation error)
        successes.append("Evaluation with missing required fields blocked")
        print("Test passed: Evaluation with missing required fields blocked")
    else:
        errors.append("Unexpected success evaluating with missing required fields")
        print("Test failed: Unexpected success evaluating with missing required fields")
except requests.exceptions.RequestException as e:
    errors.append(f"Error during test for evaluation with missing required fields: {e}")
    print("Error during test for evaluation with missing required fields:", e)


# Print the summary of successes and errors
print("\nTest Summary:")
print(f"Successes: {len(successes)}")
for success in successes:
    print(f"  - {success}")

print(f"\nErrors: {len(errors)}")
for error in errors:
    print(f"  - {error}")