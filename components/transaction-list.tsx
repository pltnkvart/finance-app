"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit, Trash2 } from "lucide-react"
import { api } from "@/lib/api"

interface Transaction {
  id: number
  amount: number
  description: string
  transaction_date: string
  category_name: string | null
}

interface TransactionListProps {
  limit?: number
}

export function TransactionList({ limit }: TransactionListProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getTransactions(limit ? { limit } : undefined)
      .then((data) => {
        setTransactions(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [limit])

  if (loading) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Recent Transactions</h2>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-16 animate-pulse bg-muted rounded" />
          ))}
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">Последние транзакции</h2>
        {limit && (
          <Button variant="ghost" size="sm">
            Показать все
          </Button>
        )}
      </div>

      <div className="space-y-3">
        {transactions.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            Транзакций пока нет. Начните отправлять сообщения в Telegram бот!
          </div>
        ) : (
          transactions.map((transaction) => (
            <div
              key={transaction.id}
              className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent transition-colors"
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <p className="font-medium text-foreground">{transaction.description}</p>
                  <Badge variant="secondary">{transaction.category_name || "Без категории"}</Badge>
                </div>
                <p className="text-sm text-muted-foreground mt-1">
                  {new Date(transaction.transaction_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-lg font-semibold text-foreground">₽{transaction.amount.toFixed(2)}</span>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </Card>
  )
}
