"use server"

import { cookies } from "next/headers"
import jwt from "jsonwebtoken";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"

// Authenticate the user and store the JWT token in a cookie
export async function authenticate(username: string, password: string): Promise<boolean> {
  // Send login request to the server
  const response = await fetch(backendUrl + "/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
  })

  if (!response.ok) {
    return false
  }

  const result = await response.json()

  // Check if the server returned a valid token
  if (!result.access_token) {
    return false
  }

  // Store the JWT token in an HttpOnly, Secure cookie
  const cookieStore = await cookies();
  cookieStore.set("token", result.access_token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    maxAge: 60 * 60 * 24, // 1 day
    path: "/",
  })

  console.log("Token set in cookie:", result.access_token)

  return true
}

// Retrieve the user from the JWT token stored in the cookie

export async function getUser(): Promise<string | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;

  if (!token) {
    return null;
  }

  try {
    // Decode the JWT token to extract the username
    const decoded = jwt.decode(token) as { sub?: string };
    console.log("Decoded token:", decoded);

    // Return the username (sub claim) if it exists
    return decoded?.sub || null;
  } catch (error) {
    console.error("Failed to decode token:", error);
    return null;
  }
}

export async function getToken(): Promise<string | null> {
  const cookieStore = await cookies();
  const token = cookieStore.get("token")?.value;
  return token || null;
}

// Logout the user by deleting the JWT token cookie
export async function logout(): Promise<void> {
  const cookieStore = await cookies();
  cookieStore.delete("token");
}