"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { ArrowUpRight, ArrowDownRight, Receipt, TrendingUp, Wallet } from "lucide-react"
import { api } from "@/lib/api"
import { useDateRange } from "@/components/date-range-context"

interface Stats {
  total_amount: number
  transaction_count: number
  total_balance?: number
  income_total?: number
  expense_total?: number
}

export function StatsOverview() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [baselineStats, setBaselineStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const { range, startDate, endDate } = useDateRange()

  useEffect(() => {
    const loadStats = async () => {
      try {
        if (range !== "all" && startDate && endDate) {
          const [current, baseline] = await Promise.all([
            api.getStatistics({ start_date: startDate, end_date: endDate }),
            api.getStatistics({ start_date: startDate, end_date: startDate }),
          ])
          setStats(current)
          setBaselineStats(baseline)
        } else if (range === "all") {
          const current = await api.getStatistics()
          setStats(current)
          setBaselineStats(null)
        } else {
          setStats(null)
          setBaselineStats(null)
        }
      } catch (error) {
        console.error("Failed to load statistics:", error)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
  }, [range, startDate, endDate])

  const buildDelta = (current?: number, baseline?: number) => {
    if (baseline === undefined || baseline === null || current === undefined || current === null) {
      return null
    }
    if (baseline === 0) {
      if (current === 0) {
        return { text: "—", tone: "neutral" as const }
      }
      return null
    }

    const delta = ((current - baseline) / Math.abs(baseline)) * 100
    const sign = delta >= 0 ? "+" : ""
    return {
      text: `${sign}${delta.toFixed(1)}% к концу периода`,
      tone: delta >= 0 ? "positive" as const : "negative" as const,
    }
  }

  const expenseTotal = stats ? stats.expense_total ?? stats.total_amount : 0
  const incomeTotal = stats ? stats.income_total ?? 0 : 0
  const netFlow = incomeTotal - expenseTotal

  const baselineExpense = baselineStats ? baselineStats.expense_total ?? baselineStats.total_amount : undefined
  const baselineIncome = baselineStats ? baselineStats.income_total ?? 0 : undefined
  const baselineNet = baselineStats
    ? (baselineStats.income_total ?? 0) - (baselineStats.expense_total ?? baselineStats.total_amount)
    : undefined

  const cards = [
    {
      title: "Общий баланс",
      value: stats?.total_balance ? `₽${stats.total_balance.toFixed(2)}` : "₽0.00",
      icon: Wallet,
      delta: null,
    },
    {
      title: "Всего потрачено",
      value: stats ? `₽${expenseTotal.toFixed(2)}` : "₽0.00",
      icon: TrendingUp,
      delta: buildDelta(expenseTotal, baselineExpense),
    },
    {
      title: "Доходы",
      value: stats ? `₽${incomeTotal.toFixed(2)}` : "₽0.00",
      icon: ArrowDownRight,
      delta: buildDelta(incomeTotal, baselineIncome),
    },
    {
      title: "Чистый доход",
      value: stats ? `₽${netFlow.toFixed(2)}` : "₽0.00",
      icon: ArrowUpRight,
      delta: buildDelta(netFlow, baselineNet),
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
              {card.delta ? (
                <div className="flex items-center gap-1 mt-2">
                  {card.delta.tone === "positive" ? (
                    <ArrowUpRight className="h-4 w-4 text-emerald-600" />
                  ) : card.delta.tone === "negative" ? (
                    <ArrowDownRight className="h-4 w-4 text-rose-500" />
                  ) : null}
                  <span
                    className={`text-sm font-medium ${
                      card.delta.tone === "positive"
                        ? "text-emerald-600"
                        : card.delta.tone === "negative"
                          ? "text-rose-500"
                          : "text-muted-foreground"
                    }`}
                  >
                    {card.delta.text}
                  </span>
                </div>
              ) : null}
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
