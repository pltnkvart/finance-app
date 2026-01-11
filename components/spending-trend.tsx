"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { api } from "@/lib/api"
import { useDateRange } from "@/components/date-range-context"

export function SpendingTrend() {
  const [data, setData] = useState<{ month: string; amount: number }[]>([])
  const [loading, setLoading] = useState(true)
  const { startDate, endDate } = useDateRange()

  useEffect(() => {
    api
      .getSpendingTrend({
        ...(startDate ? { start_date: startDate } : {}),
        ...(endDate ? { end_date: endDate } : {}),
      })
      .then((trendData) => {
        const mapped = trendData.map((item: { month: string; total: number }) => ({
          month: item.month,
          amount: item.total,
        }))
        setData(mapped)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [startDate, endDate])

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Динамика расходов</h2>
      {loading ? (
        <div className="h-64 animate-pulse bg-muted rounded" />
      ) : data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-muted-foreground">Нет данных за выбранный период</div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
            <YAxis stroke="hsl(var(--muted-foreground))" />
            <Tooltip
              formatter={(value: number) => `₽${value.toFixed(2)}`}
              contentStyle={{
                backgroundColor: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "var(--radius)",
              }}
            />
            <Legend />
            <Bar dataKey="amount" name="Расходы" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      )}
    </Card>
  )
}
