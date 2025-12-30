"use client"

import { Card } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"

export function SpendingTrend() {
  // Mock data - in production, fetch from API
  const data = [
    { month: "Jan", amount: 1240 },
    { month: "Feb", amount: 1398 },
    { month: "Mar", amount: 980 },
    { month: "Apr", amount: 1780 },
    { month: "May", amount: 1890 },
    { month: "Jun", amount: 2390 },
  ]

  return (
    <Card className="p-6">
      <h2 className="text-lg font-semibold text-foreground mb-4">Spending Trend</h2>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
          <XAxis dataKey="month" stroke="hsl(var(--muted-foreground))" />
          <YAxis stroke="hsl(var(--muted-foreground))" />
          <Tooltip
            formatter={(value: number) => `$${value.toFixed(2)}`}
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "var(--radius)",
            }}
          />
          <Legend />
          <Bar dataKey="amount" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  )
}
