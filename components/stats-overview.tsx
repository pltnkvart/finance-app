"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, Receipt, TrendingUp, Wallet } from "lucide-react"

interface Stats {
  total_amount: number
  transaction_count: number
  total_balance?: number
}

export function StatsOverview() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch("http://localhost:8000/api/statistics/summary")
      .then((res) => res.json())
      .then((data) => {
        setStats(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  const cards = [
    {
      title: "Общий баланс",
      value: stats?.total_balance ? `₽${stats.total_balance.toFixed(2)}` : "₽0.00",
      icon: Wallet,
      change: "+2.5%",
      positive: true,
    },
    {
      title: "Всего потрачено",
      value: stats ? `₽${stats.total_amount.toFixed(2)}` : "₽0.00",
      icon: TrendingUp,
      change: "+12.5%",
      positive: false,
    },
    {
      title: "Транзакций",
      value: stats ? stats.transaction_count.toString() : "0",
      icon: Receipt,
      change: "+8",
      positive: true,
    },
    {
      title: "Средний расход",
      value:
        stats && stats.transaction_count > 0
          ? `₽${(stats.total_amount / stats.transaction_count).toFixed(2)}`
          : "₽0.00",
      icon: ArrowUpRight,
      change: "+4.2%",
      positive: true,
    },
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-6">
            <div className="h-24 animate-pulse bg-muted rounded" />
          </Card>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <Card key={card.title} className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{card.title}</p>
              <h3 className="text-2xl font-semibold text-foreground mt-2">{card.value}</h3>
              <div className="flex items-center gap-1 mt-2">
                {card.positive ? (
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-500" />
                )}
                <span className={cn("text-sm font-medium", card.positive ? "text-green-500" : "text-red-500")}>
                  {card.change}
                </span>
                <span className="text-sm text-muted-foreground">за месяц</span>
              </div>
            </div>
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center">
              <card.icon className="h-6 w-6 text-primary" />
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

function cn(...classes: string[]) {
  return classes.filter(Boolean).join(" ")
}
