"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { TrendingUp } from "lucide-react"
import { api } from "@/lib/api"
import { useDateRange } from "@/components/date-range-context"

interface CategoryData {
  category: string
  total: number
  count: number
}

export function TopCategories() {
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
        const sorted = categoryData.sort((a: CategoryData, b: CategoryData) => b.total - a.total)
        setData(sorted.slice(0, 5))
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [startDate, endDate])

  if (loading) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Топ категории</h2>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 animate-pulse bg-muted rounded" />
          ))}
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Топ категории</h2>
      <div className="space-y-3">
        {data.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">Нет данных по категориям</div>
        ) : (
          data.map((item, index) => (
            <div key={item.category} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center h-8 w-8 rounded-full bg-primary/10 text-primary font-semibold text-sm">
                  {index + 1}
                </div>
                <div>
                  <p className="font-medium text-foreground">{item.category}</p>
                  <p className="text-sm text-muted-foreground">{item.count} транзакций</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-semibold text-foreground">₽{item.total.toFixed(2)}</p>
                <div className="flex items-center gap-1 text-sm text-muted-foreground">
                  <TrendingUp className="h-3 w-3" />
                  <span>{((item.total / data.reduce((sum, d) => sum + d.total, 0)) * 100).toFixed(0)}%</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
