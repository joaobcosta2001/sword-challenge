"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Checkbox } from "@/components/ui/checkbox"
import { ToggleSwitch } from "./toggle-switch"
import { Textarea } from "./ui/textarea"
import { generateRecommendation } from "@/lib/recommendations"
import { PatientData, Recommendation } from "@/lib/types"
import { formatDistanceToNow } from "date-fns"

export default function TraditionalForm({ onAddRecommendation }: { onAddRecommendation: (rec: any) => void }) {
  const [name, setName] = useState("")
  const [age, setAge] = useState("")
  const [height, setHeight] = useState("")
  const [weight, setWeight] = useState("")
  const [hadSurgery, setHadSurgery] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [isAIEnabled, setIsAIEnabled] = useState(false)
  const [inputForAI, setInputForAI] = useState("")
  const [generatedRecommendation, setGeneratedRecommendation] = useState<Recommendation|null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")
    setGeneratedRecommendation(null)

    try {
      // Simulate API call

      const patient_data : PatientData = {
        name,
        age: Number(age),
        height: Number(height),
        weight: Number(weight),
        recent_surgery: hadSurgery,
        ai_description: isAIEnabled ? inputForAI : null
      }

      const recommendation:Recommendation|null = await generateRecommendation(patient_data);
      if (!recommendation) {
        throw new Error("Failed to generate recommendation")
      }
      onAddRecommendation(recommendation)
      setGeneratedRecommendation(recommendation)
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>New Clinical Recommendation</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="age">Name</Label>
            <Input
              id="age"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter patient name"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="age">Age (years)</Label>
            <Input
              id="age"
              type="number"
              value={age}
              onChange={(e) => setAge(e.target.value)}
              placeholder="Enter patient age"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="height">Height (cm)</Label>
            <Input
              id="height"
              type="number"
              value={height}
              onChange={(e) => setHeight(e.target.value)}
              placeholder="Enter patient height"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="weight">Weight (kg)</Label>
            <Input
              id="weight"
              type="number"
              value={weight}
              onChange={(e) => setWeight(e.target.value)}
              placeholder="Enter patient weight"
              required
            />
          </div>

          <div className="flex items-center space-x-2 pt-2">
            <Checkbox
              id="surgery"
              checked={hadSurgery}
              onCheckedChange={(checked) => setHadSurgery(checked === true)}
            />
            <Label htmlFor="surgery" className="cursor-pointer">
              Patient had surgery recently
            </Label>
          </div>

          <div className="flex items-center space-x-2 pt-2 text-sm">
            <ToggleSwitch className="mr-4" onToggle={setIsAIEnabled}/>
            Enable AI Recommendations
          </div>

          {isAIEnabled && <div className="flex items-center space-x-2 pt-2 text-sm">
            <Textarea
                value={inputForAI}
                onChange={(e) => setInputForAI(e.target.value)}
                placeholder="Describe the patient's condition..."
                className="min-h-[120px]"
                required
              />
          </div>}

          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">{error}</div>}

          {generatedRecommendation && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-md text-green-600 text-sm space-y-2">
              <div className="flex flex-row">
                Recommendation created successfully!<p className="ml-auto">{formatDistanceToNow(new Date(generatedRecommendation.timestamp), { addSuffix: true })}</p>
              </div>
              <div>
                <b>Recommendation: {generatedRecommendation.recommendation}</b>
              </div>
              <div className="text-xs">
                <p>Recommendation ID: {generatedRecommendation.recommendation_id}</p>
                <p>Patient ID: {generatedRecommendation.patient_id}</p>
              </div>

            </div>
          )}
          <div className="w-full flex flex-row justify-center">
            <Button type="submit" className="w-[300px]" disabled={isSubmitting}>
              {isSubmitting ? "Processing..." : "Submit"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}
