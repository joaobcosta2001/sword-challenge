from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from uuid import uuid4, UUID
from datetime import datetime
import pika  # RabbitMQ library
import time
import psycopg2  # PostgreSQL library
import bcrypt
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import redis
from openai import AsyncOpenAI


load_dotenv()

app = FastAPI(
    title="Clinical Recommendation API",
    description="This API provides endpoints for evaluating patient data, generating clinical recommendations, and retrieving stored recommendations.",
    version="1.0.0",
    contact={
        "name": "João Costa",
        "email": "joaoassuncaoecosta@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

security = HTTPBearer()


# In-memory storage for recommendations

# RabbitMQ connection setup
RABBITMQ_HOST = "rabbitmq"  # Change to your RabbitMQ host if needed
QUEUE_NAME = "recommendations_queue"

DATABASE_URL = "postgresql://secret_admin123:verynotsecurepassword@postgres:5432/main_db"

def get_db_connection():
    """
    Attempts to establish a connection to the database with retries.
    """
    max_retries = 5
    retry_delay = 5  # seconds

    for attempt in range(max_retries):
        try:
            connection = psycopg2.connect(DATABASE_URL)
            print("Database connection established.")
            return connection
        except psycopg2.OperationalError as e:
            print(f"Database connection failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not connect to the database.")
                raise


db_connection = get_db_connection()
db_cursor = db_connection.cursor()


openai_key = os.getenv("OPENAI_API_KEY")

if not openai_key:
    openai_key = ""

openai_client = AsyncOpenAI(
    api_key = openai_key,
)


redis_client = redis.StrictRedis(host="redis", port=6379, decode_responses=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific origins for better security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies the validity of the JWT token provided in the Authorization header.
    """
    print(f"Received token: {credentials.credentials}")  # Debugging line
    token = credentials.credentials
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"])
        print(f"Decoded JWT payload: {payload}")  # Debugging line
        return payload  # Return the decoded payload if the token is valid
    except jwt.ExpiredSignatureError:
        print("Token has expired")  # Debugging line
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        print("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")



def get_rabbitmq_channel():
    for _ in range(10):  # Retry up to 10 times
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME)
            return connection, channel
        except pika.exceptions.AMQPConnectionError:
            print("Failed to connect to RabbitMQ. Retrying in 5 seconds...")
            time.sleep(5)
    raise Exception("Could not connect to RabbitMQ after multiple attempts.")

rabbitmq_connection, rabbitmq_channel = get_rabbitmq_channel()

# Establish RabbitMQ connection
def publish_to_rabbitmq(message: dict):
    max_retries = 5
    retry_delay = 5  # seconds
    global rabbitmq_connection, rabbitmq_channel
    for attempt in range(max_retries):
        try:
            if rabbitmq_channel.is_closed:
                print("RabbitMQ channel is closed. Reconnecting...")
                rabbitmq_connection, rabbitmq_channel = get_rabbitmq_channel()

            # Serialize the message dictionary to a JSON string
            message_body = json.dumps(message)

            rabbitmq_channel.basic_publish(
                exchange="",
                routing_key=QUEUE_NAME,
                body=message_body  # Pass the serialized JSON string
            )
            return  # Exit the function if the message is successfully published
        except Exception as e:
            print(f"Error publishing to RabbitMQ (attempt {attempt + 1}/{max_retries}): {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Could not publish message to RabbitMQ.")
                raise HTTPException(status_code=500, detail="Failed to publish message to RabbitMQ")


class PatientData(BaseModel):
    """
    Model for patient data used in the `/evaluate` endpoint.
    """
    name: str  # Patient's name
    age: int  # Patient's age
    height: int  # Patient's height in centimeters
    weight: int  # Patient's weight in kilograms
    recent_surgery: bool  # Whether the patient had recent surgery
    ai_description: Optional[str] = None  # Additional description for AI-based recommendations


class Recommendation(BaseModel):
    """
    Model for the recommendation response.
    """
    patient_id: str  # Unique ID for the patient
    recommendation_id: str  # Unique ID for the recommendation
    recommendation: str  # The generated recommendation
    timestamp: str  # Timestamp of when the recommendation was created

@app.post("/evaluate", response_model=Recommendation)
async def evaluate_patient(payload: dict, token: dict = Depends(verify_token)):
    """
    Evaluate patient data and generate a clinical recommendation.

    This endpoint accepts patient data, validates it, and generates a clinical recommendation
    based on predefined rules or using an AI model. The recommendation is stored in the database
    and published to RabbitMQ.

    **Request Body**:
    - `payload`: A dictionary containing the `patient_data` property.

    **Example**:
    ```json
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

    **Response**:
    - Returns a recommendation object containing:
        - [patient_id](http://_vscodecontentref_/0): Unique ID for the patient.
        - [recommendation_id](http://_vscodecontentref_/1): Unique ID for the recommendation.
        - [recommendation](http://_vscodecontentref_/2): The generated recommendation.
        - [timestamp](http://_vscodecontentref_/3): The timestamp of when the recommendation was created.

    **Example**:
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "recommendation_id": "123e4567-e89b-12d3-a456-426614174001",
        "recommendation": "Weight Management Program",
        "timestamp": "2025-04-15T12:00:00Z"
    }
    ```

    **Errors**:
    - `400 Bad Request`: If [patient_data](http://_vscodecontentref_/4) is missing or invalid.
    - `401 Unauthorized`: If the JWT token is invalid or expired.
    - `500 Internal Server Error`: If there is an issue with RabbitMQ or the database.
    """

    # Extract the 'patient_data' property from the payload
    patient_data = payload.get("patient_data")

    print("Received payload:", payload)  # Debugging line
    print("Extracted patient_data:", patient_data)  # Debugging line	


    if not patient_data:
        print("Missing 'patient_data' in the request body")
        raise HTTPException(status_code=400, detail="Missing 'patient_data' in the request body")

    # Validate the extracted data against the PatientData model
    try:
        data = PatientData(**patient_data)
    except Exception as e:
        print(f"Error validating patient_data: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid 'patient_data': {str(e)}")
    
    bmi = data.weight/((data.height/100.0) ** 2)

    recommendation_text = ""

    if data.ai_description != None:
        # Use OpenAI's API to generate the recommendation
        try:
            response = await openai_client.responses.create(
                model="gpt-4o",
                instructions="You are a medical assistant, that suggests clinical recommendations based on patient data. You are not a real doctor, as such do not propose very exagerated, expensive or invasive procedures. Do not repeat back the instructions or patient data",
                input=  f"Follow these rules:\n"
                        f"1. If patient is over 65 years old and has chronic pain, recommend Physical Therapy\n"
                        f"2. If patient has a BMI over 30, recommend Weight Management Program\n"
                        f"3. If patient has had recent surgery, recommend Post-Op Rehabilitation Plan\n"
                        f"Generate a medical recommendation based on the following patient data:\n\n"
                        f"Name: {data.name}\n"
                        f"Age: {data.age}\n"
                        f"Height: {data.height} cm\n"
                        f"Weight: {data.weight} kg\n"
                        f"BMI: {bmi:.2f}\n"
                        f"Recent Surgery: {'Yes' if data.recent_surgery else 'No'}\n"
                        f"AI Description: {data.ai_description or 'None'}\n\n"
                        f"Recommendation:"
            )
            recommendation_text = response.output_text.strip()
        except Exception as e:
            print(f"Error generating recommendation using OpenAI API: {str(e)}")
        
    if recommendation_text == "":
        # Generate a mock recommendation
        # Generate a recommendation based on the patient's data
        recommendations_list = []


        # Logic for generating recommendations
        if data.age >= 65 and "chronic pain" in (data.ai_description or "").lower():
            recommendations_list.append("Physical Therapy")
        if bmi >= 30:
            recommendations_list.append("Weight Management Program")
        if data.recent_surgery:
            recommendations_list.append("Post-Op Rehabilitation Plan")

        # If no specific recommendation is generated, provide a generic one
        if not recommendations_list:
            recommendations_list.append("General Health Checkup")

        # Combine recommendations into a single text
        recommendation_text = ". ".join(recommendations_list) + "."

    # Create a timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"


    
    recommendation_id = str(uuid4())
    patient_id = str(uuid4())

    # Store the recommendation
    recommendation = {
        "patient_id": patient_id,
        "recommendation_id": recommendation_id,
        "recommendation": recommendation_text,
        "timestamp": timestamp
    }

    # Publish the recommendation to RabbitMQ
    try:
        publish_to_rabbitmq(recommendation)
    except pika.exceptions.ChannelClosedByBroker:
        raise HTTPException(status_code=500, detail="Failed to publish message to RabbitMQ")
    try:
        db_cursor.execute(
            """
            INSERT INTO recommendations (recommendation_id, patient_id, recommendation, timestamp, created_by)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (recommendation_id, patient_id, recommendation_text, timestamp, token["sub"])
        )
        db_connection.commit()
    except Exception as e:
        print(f"Error saving recommendation to the database: {str(e)}")
        db_connection.rollback()
        raise HTTPException(status_code=500, detail="Failed to save recommendation to the database")

    return recommendation











@app.get("/recommendation/{recommendation_id}", response_model=Recommendation)
async def get_recommendation(recommendation_id: str, token: dict = Depends(verify_token)):
    """
    Retrieve a previously generated recommendation by its ID.

    This endpoint retrieves a recommendation from the Redis cache or the database
    using the provided [recommendation_id](http://_vscodecontentref_/5). If the recommendation is found, it is returned.
    Unauthorized users cannot access recommendations created by others.

    **Path Parameter**:
    - [recommendation_id](http://_vscodecontentref_/6): The unique ID of the recommendation to retrieve.

    **Response**:
    - Returns a recommendation object containing:
        - [patient_id](http://_vscodecontentref_/7): Unique ID for the patient.
        - [recommendation_id](http://_vscodecontentref_/8): Unique ID for the recommendation.
        - [recommendation](http://_vscodecontentref_/9): The generated recommendation.
        - [timestamp](http://_vscodecontentref_/10): The timestamp of when the recommendation was created.

    **Example**:
    ```json
    {
        "patient_id": "123e4567-e89b-12d3-a456-426614174000",
        "recommendation_id": "123e4567-e89b-12d3-a456-426614174001",
        "recommendation": "Weight Management Program",
        "timestamp": "2025-04-15T12:00:00Z"
    }
    ```

    **Errors**:
    - `400 Bad Request`: If the [recommendation_id](http://_vscodecontentref_/11) is not a valid UUID.
    - `401 Unauthorized`: If the JWT token is invalid or expired.
    - `404 Not Found`: If the recommendation does not exist or the user is unauthorized to access it.
    - `500 Internal Server Error`: If there is an issue retrieving the recommendation.
    """
    try:

        try:
           UUID(recommendation_id, version=4)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid recommendation_id format. Must be a valid UUID. Received: " + recommendation_id)
    

        # Check if the recommendation is in the Redis cache
        cached_recommendation = redis_client.get(recommendation_id)
        if cached_recommendation:
            print(f"Cache hit for recommendation_id: {recommendation_id}")
            if token["sub"] != json.loads(cached_recommendation)["created_by"]:
                # Send 404 because we dont want unauthorized people to know that that recommendation exists ;)
                raise HTTPException(status_code=404, detail="Recommendation not found")
            return json.loads(cached_recommendation)

        print(f"Cache miss for recommendation_id: {recommendation_id}")

        # If not in cache, retrieve from the database
        db_cursor.execute(
            "SELECT patient_id, recommendation, timestamp, created_by FROM recommendations WHERE recommendation_id = %s",
            (recommendation_id,)
        )
        result = db_cursor.fetchone()
        if not result:
            print(f"Recommendation with ID {recommendation_id} not found in the database")
            raise HTTPException(status_code=404, detail="Recommendation not found")

        print("Recommendation retrieved from database:", result)  # Debugging line

        patient_id, recommendation_text, timestamp, created_by = result

        if token["sub"] != created_by:
            # Send 404 because we dont want unauthorized people to know that that recommendation exists ;)
            raise HTTPException(status_code=404, detail="Recommendation not found")

        recommendation_to_store = {
            "patient_id": patient_id,
            "recommendation_id": recommendation_id,
            "recommendation": recommendation_text,
            "timestamp": timestamp.isoformat(),
            "created_by": created_by
        }

        # Store the recommendation in Redis cache
        redis_client.set(recommendation_id, json.dumps(recommendation_to_store), ex=3600)  # Cache for 1 hour

        return {
            "patient_id": patient_id,
            "recommendation_id": recommendation_id,
            "recommendation": recommendation_text,
            "timestamp": timestamp.isoformat(),
        }
    except HTTPException as http_exc:
        # Re-raise the original HTTPException
        raise http_exc
    except Exception as e:
        print(f"Error retrieving recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve recommendation")





# Request model for login
class LoginRequest(BaseModel):
    username: str
    password: str

# Response model for JWT token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    """
    Authenticate a user and return a JWT token.

    This endpoint validates the user's credentials (username and password) against the database.
    If the credentials are valid, a JWT token is generated and returned.

    **Request Body**:
    - [data](http://_vscodecontentref_/12): A dictionary containing the user's [username](http://_vscodecontentref_/13) and [password](http://_vscodecontentref_/14).

    **Example**:
    ```json
    {
        "username": "my_admin",
        "password": "password123"
    }
    ```

    **Response**:
    - Returns a JWT token object containing:
        - [access_token](http://_vscodecontentref_/15): The generated JWT token.
        - [token_type](http://_vscodecontentref_/16): The type of token (e.g., "bearer").

    **Example**:
    ```json
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }
    ```

    **Errors**:
    - `401 Unauthorized`: If the username or password is invalid.
    """
    # Query the database for the user
    db_cursor.execute("SELECT password FROM users WHERE username = %s", (data.username,))
    result = db_cursor.fetchone()

    if not result:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    stored_hashed_password = result[0]

    # Verify the password

    expected_password = bcrypt.hashpw(data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


    if not bcrypt.checkpw(data.password.encode('utf-8'), stored_hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate a JWT token
    payload = {
        "sub": data.username,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    }

    token = jwt.encode(payload, os.getenv("JWT_SECRET"), algorithm="HS256")

    return {"access_token": token, "token_type": "bearer"}





@app.on_event("shutdown")
async def shutdown_event():
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        rabbitmq_connection.close()