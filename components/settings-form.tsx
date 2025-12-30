"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RefreshCw } from "lucide-react"

interface CategorizationStats {
  rule_based: {
    total_rules: number
    average_confidence: number
  }
  machine_learning: {
    is_trained: boolean
    num_categories: number
    total_samples: number
  }
  user_corrections: number
  threshold: number
}

export function SettingsForm() {
  const [stats, setStats] = useState<CategorizationStats | null>(null)
  const [training, setTraining] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadStats = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/categorization/stats")
      const data = await response.json()
      setStats(data)
      setLoading(false)
    } catch (error) {
      console.error("Failed to load stats:", error)
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  const handleTrain = async () => {
    setTraining(true)

    try {
      const response = await fetch("http://localhost:8000/api/categorization/train", {
        method: "POST",
      })
      const result = await response.json()

      if (result.success) {
        alert("Model trained successfully!")
        loadStats()
      } else {
        alert(result.message)
      }
    } catch (error) {
      console.error("Training failed:", error)
      alert("Failed to train model")
    } finally {
      setTraining(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="h-64 animate-pulse bg-muted rounded" />
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-2">Categorization Engine</h3>
            <p className="text-sm text-muted-foreground">
              Train the machine learning model to improve automatic categorization
            </p>
          </div>

          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">ML Model Status</p>
                  <Badge variant={stats.machine_learning.is_trained ? "default" : "secondary"}>
                    {stats.machine_learning.is_trained ? "Trained" : "Not Trained"}
                  </Badge>
                </div>
                <p className="text-2xl font-semibold text-foreground">
                  {stats.machine_learning.num_categories} categories
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {stats.machine_learning.total_samples} training samples
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">Rule-Based System</p>
                <p className="text-2xl font-semibold text-foreground">{stats.rule_based.total_rules} rules</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {(stats.rule_based.average_confidence * 100).toFixed(0)}% avg confidence
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">User Corrections</p>
                <p className="text-2xl font-semibold text-foreground">{stats.user_corrections}</p>
                <p className="text-sm text-muted-foreground mt-1">Learning from your edits</p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">Similarity Threshold</p>
                <p className="text-2xl font-semibold text-foreground">{(stats.threshold * 100).toFixed(0)}%</p>
                <p className="text-sm text-muted-foreground mt-1">Minimum confidence required</p>
              </div>
            </div>
          )}

          <Button onClick={handleTrain} disabled={training}>
            <RefreshCw className={`h-4 w-4 mr-2 ${training ? "animate-spin" : ""}`} />
            {training ? "Training Model..." : "Train ML Model"}
          </Button>

          <div className="p-4 bg-muted rounded-lg">
            <h4 className="font-medium text-foreground mb-2">About Training</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Requires at least 3 transactions per category</li>
              <li>• Uses TF-IDF vectorization and cosine similarity</li>
              <li>• Learns from your manual category corrections</li>
              <li>• Retrain periodically for best results</li>
            </ul>
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-2">Telegram Bot</h3>
            <p className="text-sm text-muted-foreground">Send transactions to your bot using these formats</p>
          </div>

          <div className="space-y-2">
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">100 groceries</div>
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">coffee 5.50</div>
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">25 taxi ride</div>
          </div>
        </div>
      </Card>
    </div>
  )
}
