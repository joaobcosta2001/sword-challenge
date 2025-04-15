import { getToken } from "./auth";
import { PatientData, Recommendation } from "./types";

const backendUrl = process.env.BACKEND_URL || "http://localhost:8000"


export async function generateRecommendation(patient_data:PatientData): Promise<Recommendation | null> {
  // Send login request to the server

  const token = await getToken()

  const response = await fetch(backendUrl + "/evaluate", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token,
    },
    body: JSON.stringify({patient_data}),
  })

  if (!response.ok) {
    return null
  }

  const result = await response.json()

  // Check if the server returned a valid token
  if (!result || typeof result !== "object") {
    return null
  }

  return result as Recommendation
}

export async function getRecommendation(id:string): Promise<Recommendation|null> {
  
  const token = await getToken()
  try{
    const response = await fetch(backendUrl + "/recommendation/"+id, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token,
      },
    })

    if (!response.ok) {
      console.error("Error fetching recommendation:", response.statusText)
      return null
    }

    //Not found
    if(response.status === 404){
      return null
    }

    const result = await response.json()

    // Check if the server returned a valid token
    if (!result || typeof result !== "object") {
      console.error("Invalid recommendation format")
    }

    return result as Recommendation
  }catch (error) {
    console.error("Error fetching recommendation:", error)
    return null
  }
}