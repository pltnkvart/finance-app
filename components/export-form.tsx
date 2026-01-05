"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Download } from "lucide-react"
import { api } from "@/lib/api"

export function ExportForm() {
  const [startDate, setStartDate] = useState("")
  const [endDate, setEndDate] = useState("")
  const [loading, setLoading] = useState(false)

  const handleExport = async () => {
    setLoading(true)

    try {
      const blob = await api.exportCSV({
        start_date: startDate || undefined,
        end_date: endDate || undefined,
      })

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `transactions_${new Date().toISOString().split("T")[0]}.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error("Ошибка экспорта:", error)
      alert("Не удалось экспортировать транзакции")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Card className="p-6 max-w-2xl">
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-medium text-foreground mb-2">Параметры экспорта</h3>
          <p className="text-sm text-muted-foreground">
            Выберите диапазон дат для фильтрации транзакций или оставьте пустым для экспорта всех данных.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="start-date">Начальная дата</Label>
            <Input id="start-date" type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
          </div>

          <div className="space-y-2">
            <Label htmlFor="end-date">Конечная дата</Label>
            <Input id="end-date" type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
          </div>
        </div>

        <Button onClick={handleExport} disabled={loading} className="w-full md:w-auto">
          <Download className="h-4 w-4 mr-2" />
          {loading ? "Экспорт..." : "Экспортировать в CSV"}
        </Button>

        <div className="p-4 bg-muted rounded-lg">
          <h4 className="font-medium text-foreground mb-2">Формат CSV</h4>
          <p className="text-sm text-muted-foreground">
            Экспортированный файл будет содержать: ID, Дата, Сумма, Описание и Категория для каждой транзакции.
          </p>
        </div>
      </div>
    </Card>
  )
}
