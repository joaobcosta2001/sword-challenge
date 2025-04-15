"use client"

import type React from "react"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function AIForm({ onAddRecommendation }: { onAddRecommendation: (rec: any) => void }) {
  const [input, setInput] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState<{ id: string } | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError("")
    setSuccess(null)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))

      // 10% chance of failure for demo purposes
      if (Math.random() < 0.1) {
        throw new Error("Failed to process AI request")
      }

      // Generate a random recommendation ID
      const recommendationId = `AI-${Math.floor(Math.random() * 10000)
        .toString()
        .padStart(4, "0")}`

      const recommendation = {
        id: recommendationId,
        type: "ai",
        timestamp: new Date().toISOString(),
        data: { input },
      }

      onAddRecommendation(recommendation)
      setSuccess({ id: recommendationId })
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Describe the patient's condition..."
              className="min-h-[120px]"
              required
            />
          </div>

          {error && <div className="p-3 bg-red-50 border border-red-200 rounded-md text-red-600 text-sm">{error}</div>}

          {success && (
            <div className="p-3 bg-green-50 border border-green-200 rounded-md text-green-600 text-sm">
              Recommendation created successfully! ID: {success.id}
            </div>
          )}

          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? "Processing..." : "Submit"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
