-- Enable pgcrypto extension for password hashing
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the recommendations table
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    patient_id UUID NOT NULL,
    recommendation_id UUID NOT NULL,
    recommendation TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    created_by TEXT NOT NULL
);

-- Create the users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Insert the admin user with a hashed password
INSERT INTO users (username, password)
VALUES ('my_admin', crypt('password123', gen_salt('bf')));

INSERT INTO users (username, password)
VALUES ('my_admin2', crypt('password123', gen_salt('bf')));