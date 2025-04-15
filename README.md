# Clinical Recommendation API
This project is a **Clinical Recommendation API** that provides endpoints for evaluating patient data, generating clinical recommendations, and retrieving stored recommendations. It integrates with RabbitMQ for message queuing, PostgreSQL for database storage, Redis for caching, and OpenAI for AI-based recommendations.

## Features
- Patient Evaluation: Accepts patient data and generates clinical recommendations based on predefined rules or AI models.
- Recommendations Storage: Stores recommendations in a PostgreSQL database.
- Message Queuing: Publishes recommendations to RabbitMQ for further processing.
- Caching: Uses Redis to cache recommendations for faster retrieval.
- Authentication: Secures endpoints with JWT-based authentication.
- Frontend Integration: Includes a frontend carousel component for UI interactions.
- Project Structure
├── server.py # FastAPI backend server
├── background-worker.py # Background worker for processing RabbitMQ messages
├── frontend/ # Frontend application
├── data/ # Data files (e.g., event logs)
├── tests/ # Unit tests
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile # Dockerfile for the backend
├── Dockerfile.bg-worker # Dockerfile for the background worker
├── requirements.txt # Python dependencies for the backend
├── requirements-bg-worker.txt # Python dependencies for the background worker
├── init.sql # SQL initialization script for the database
├── .env # Environment variables

## Prerequisites
- Docker and Docker Compose
- Python 3.10+
- PostgreSQL
- RabbitMQ
- Redis

## Setup
1. Clone the Repository:
    - git clone [https://github.com/joaobcosta2001/sword-challenge.git](https://github.com/joaobcosta2001/sword-challenge.git)
    - cd sword-challenge
2. Set Up Environment Variables:
    - Create a .env file in the root directory with the following variables:
        - OPENAI_API_KEY=<your_openai_api_key> (optional)
        - JWT_SECRET=<your_jwt_secret>
3. Build and Start Services:
    - Use Docker Compose to build and start the services:
        - docker-compose up --build
4. Start the frontend app:
    - On a separate terminal execute:
        - cd frontend_app
        - npm run dev
    - Open your browser and access [http://localhost:3000/](http://localhost:3000/)

## API Endpoints

All endpoints are documented in the [OpenAPI Reference file](openapi.json)

1. Evaluate Patient
    - POST /evaluate
    - Description: Evaluates patient data and generates a clinical recommendation.
    - Request Body:
```
{
    {
        "patient_data": {
        "name": "John Doe",
        "age": 45,
        "height": 175,
        "weight": 85,
        "recent_surgery": false,
        "ai_description": "Experiencing mild joint pain"
    }

}
```

   - Response:
```
{
    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
    "recommendation_id": "123e4567-e89b-12d3-a456-426614174001",
    "recommendation": "Weight Management Program",
    "timestamp": "2025-04-15T12:00:00Z"
}
```
2. Retrieve Recommendation
    - GET /recommendation/{recommendation_id}
    - Description: Retrieves a previously generated recommendation by its ID.
    - Response:
```
{
    "patient_id": "123e4567-e89b-12d3-a456-426614174000",
    "recommendation_id": "123e4567-e89b-12d3-a456-426614174001",
    "recommendation": "Weight Management Program",
    "timestamp": "2025-04-15T12:00:00Z"
}
```
3. Login
    - POST /login
    - Description: Authenticates a user and returns a JWT token.
    - Request Body:
```
{
    "username": "my_admin",
    "password": "password123"
}
```

   - Response:
```
{
"access_token": "<jwt_token>",
"token_type": "bearer"
}
```
## Frontend
The frontend application is located in the frontend directory. Even though it was not a requirement, it helps on testing the application

1. Clone the Repository:
    - git clone <repository-url>
    - cd <repository-folder>
2. Set Up Environment Variables:
    - Create a .env file in the root directory with the following variables:
        - OPENAI_API_KEY=<your_openai_api_key> (optional)
        - JWT_SECRET=<your_jwt_secret>

3. Build and Start Services:
    - Use Docker Compose to build and start the services:
        - docker-compose up --build

## Background Worker
The background-worker.py processes messages from RabbitMQ and logs them to an excel file inside the data directory for later analytics

## Testing
Even though some automatic testing is implemented, it is not properly working and due to time constraints it was not fixed. As such, manual testing was extensively conducted
