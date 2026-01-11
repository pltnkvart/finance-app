"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit, Trash2 } from "lucide-react"
import { api } from "@/lib/api"
import { EditTransactionDialog } from "@/components/edit-transaction-dialog"
import { toast } from "@/hooks/use-toast"
import { useDateRange } from "@/components/date-range-context"

interface Transaction {
  id: number
  amount: number
  description: string
  transaction_date: string
  category_id: number | null
  category_name: string | null
  transaction_type: "expense" | "income"
}

interface TransactionListProps {
  limit?: number
}

interface Category {
  id: number
  name: string
}

export function TransactionList({ limit }: TransactionListProps) {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [editingTransaction, setEditingTransaction] = useState<Transaction | null>(null)
  const { startDate, endDate } = useDateRange()

  useEffect(() => {
    const params = {
      ...(limit ? { limit } : {}),
      ...(startDate ? { start_date: startDate } : {}),
      ...(endDate ? { end_date: endDate } : {}),
    }

    Promise.all([api.getTransactions(params), api.getCategories()])
      .then(([transactionsData, categoriesData]) => {
        setTransactions(transactionsData)
        setCategories(categoriesData)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [limit, startDate, endDate])

  const handleDelete = async (transaction: Transaction) => {
    if (!confirm("Удалить транзакцию?")) {
      return
    }

    try {
      await api.deleteTransaction(transaction.id)
      setTransactions(transactions.filter((item) => item.id !== transaction.id))
      toast({
        title: "Транзакция удалена",
        description: transaction.description,
      })
    } catch (error) {
      console.error("Не удалось удалить транзакцию:", error)
      toast({
        title: "Не удалось удалить транзакцию",
        variant: "destructive",
      })
    }
  }

  const handleUpdate = (updated: Transaction) => {
    setTransactions(transactions.map((item) => (item.id === updated.id ? updated : item)))
  }

  if (loading) {
    return (
      <Card className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Последние транзакции</h2>
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
                <span
                  className={`text-lg font-semibold ${
                    transaction.transaction_type === "income" ? "text-emerald-600" : "text-foreground"
                  }`}
                >
                  {transaction.transaction_type === "income" ? "+" : "-"}₽{transaction.amount}
                </span>
                <div className="flex gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={() => setEditingTransaction(transaction)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => handleDelete(transaction)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {editingTransaction && (
        <EditTransactionDialog
          transaction={editingTransaction}
          categories={categories}
          onClose={() => setEditingTransaction(null)}
          onUpdate={handleUpdate}
        />
      )}
    </Card>
  )
}
