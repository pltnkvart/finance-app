"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts"
import { api } from "@/lib/api"
import { useDateRange } from "@/components/date-range-context"

interface CategoryData {
  category: string
  total: number
  count: number
}

const COLORS = [
  "var(--chart-1)",
  "var(--chart-2)",
  "var(--chart-3)",
  "var(--chart-4)",
  "var(--chart-5)",
]

export function CategoryChart() {
  const [data, setData] = useState<CategoryData[]>([])
  const [loading, setLoading] = useState(true)
  const { startDate, endDate } = useDateRange()

  useEffect(() => {
    api
      .getCategoryStats({
        ...(startDate ? { start_date: startDate } : {}),
        ...(endDate ? { end_date: endDate } : {}),
      })
      .then((categoryData) => {
        setData(categoryData)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [startDate, endDate])

  if (loading) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Расходы по категориям</h2>
        <div className="h-64 animate-pulse bg-muted rounded" />
      </Card>
    )
  }

  if (data.length === 0) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Расходы по категориям</h2>
        <div className="h-64 flex items-center justify-center text-muted-foreground">Нет данных по категориям</div>
      </Card>
    )
  }

  const chartData = data.map((item) => ({
    name: item.category,
    value: item.total,
  }))

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Расходы по категориям</h2>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={(entry) => `₽${entry.value.toFixed(0)}`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => `₽${value.toFixed(2)}`}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "var(--radius)",
            }}
          />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Card>
  )
}
