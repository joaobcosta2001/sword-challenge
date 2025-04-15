export  type PatientData ={
    name: string
    age: number
    height: number
    weight: number
    recent_surgery: boolean
    ai_description: string | null
}


export type Recommendation = {
    recommendation_id: string
    patient_id: string
    recommendation: string
    timestamp: Date
}