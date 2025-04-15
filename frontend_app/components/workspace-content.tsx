"use client"

import { useState } from "react"
import TraditionalForm from "@/components/traditional-form"
import RecommendationsList from "@/components/recommendation-search"

type Recommendation = {
  id: string
  type: "traditional" | "ai"
  timestamp: string
  data: any
}

export default function WorkspaceContent() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])


  const handleAddRecommendation = (recommendation: Recommendation) => {
    setRecommendations((prev) => [recommendation, ...prev])
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
      </div>

      <div className="mt-6">
        <TraditionalForm onAddRecommendation={handleAddRecommendation} />
      </div>

      <RecommendationsList recommendations={recommendations} />
    </div>
  )
}
