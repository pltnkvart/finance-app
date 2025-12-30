"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Download } from "lucide-react"

export function ExportForm() {
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [loading, setLoading] = useState(false)

  const handleExport = async () => {
    setLoading(true)

    try {
      const params = new URLSearchParams()
      if (startDate) params.append("start_date", startDate)
      if (endDate) params.append("end_date", endDate)

      const response = await fetch(`http://localhost:8000/api/export/csv?${params.toString()}`)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `transactions_${new Date().toISOString().split("T")[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Export failed:", error)
      alert("Failed to export transactions")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 max-w-2xl">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-foreground mb-2">Export Parameters</h3>
          <p className="text-sm text-muted-foreground">
            Select a date range to filter transactions, or leave empty to export all.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="start-date">Start Date</Label>
            <Input id="start-date" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="end-date">End Date</Label>
            <Input id="end-date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
        </div>

        <Button onClick={handleExport} disabled={loading} className="w-full md:w-auto">
          <Download className="h-4 w-4 mr-2" />
          {loading ? "Exporting..." : "Export to CSV"}
        </Button>

        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium text-foreground mb-2">CSV Format</h4>
          <p className="text-sm text-muted-foreground">
            The exported file will contain: ID, Date, Amount, Description, and Category for each transaction.
          </p>
        </div>
      </div>
    </Card>
  )
}
