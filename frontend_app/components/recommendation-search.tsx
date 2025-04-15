"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { formatDistanceToNow } from "date-fns"
import { Search, Loader2 } from "lucide-react"
import { getRecommendation } from "@/lib/recommendations"
import { Recommendation } from "@/lib/types"

export default function RecommendationsSearch() {
  const [searchQuery, setSearchQuery] = useState("")
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Recommendation | null>(null)

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()

    if (!searchQuery.trim()) {
      setSearchResults(null)
      return
    }

    setIsSearching(true)

    const recommendation = await getRecommendation(searchQuery)

    setSearchResults(recommendation)
    setIsSearching(false)
  }

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-col space-y-4">
        <CardTitle>Search for Recommendations</CardTitle>
        <form onSubmit={handleSearch} className="flex flex-col w-full max-w-sm mt-8 space-y-2">
          <p className="text-xs">Recommendation ID</p>
          <div className="flex flex-row">
            <Input
              placeholder="Recommendation ID"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="max-w-[400px]"
            />
            <Button type="submit" size="sm" disabled={isSearching} className="h-10 ml-2">
              {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
              <span className="ml-2">Search</span>
            </Button>
          </div>
        </form>
      </CardHeader>
      <CardContent>
        {isSearching ? (
          <div className="flex justify-center items-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <span className="ml-2">Searching database...</span>
          </div>
        ) : (!searchResults)? (
          <p className="text-gray-500 text-center py-4">
            No results found
          </p>
        ) : (
          <div className="space-y-4">
            {searchResults && (
              <div className="p-3 bg-green-50 border border-green-200 rounded-md text-green-600 text-sm space-y-2">
                <div className="flex flex-row">
                  Recommendation created successfully!<p className="ml-auto">{formatDistanceToNow(new Date(searchResults.timestamp), { addSuffix: true })}</p>
                </div>
                <div>
                  <b>Recommendation: {searchResults.recommendation}</b>
                </div>
                <div className="text-xs">
                  <p>Recommendation ID: {searchResults.recommendation_id}</p>
                  <p>Patient ID: {searchResults.patient_id}</p>
                </div>
  
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
