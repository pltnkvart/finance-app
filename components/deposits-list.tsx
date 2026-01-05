"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PiggyBank, Plus } from "lucide-react"
import { CreateDepositDialog } from "@/components/create-deposit-dialog"

interface Deposit {
  id: number
  account_id: number
  name: string
  amount: number
  interest_rate: number
  start_date: string
  end_date: string
  status: string
  created_at: string
  updated_at: string
}

const statusLabels = {
  active: "Активен",
  completed: "Завершен",
  cancelled: "Отменен",
}

const statusColors = {
  active: "bg-green-500/10 text-green-500",
  completed: "bg-blue-500/10 text-blue-500",
  cancelled: "bg-red-500/10 text-red-500",
}

export function DepositsList() {
  const [deposits, setDeposits] = useState<Deposit[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateDialog, setShowCreateDialog] = useState(false)

  useEffect(() => {
    fetch("http://localhost:8000/api/deposits")
      .then((res) => res.json())
      .then((data) => {
        setDeposits(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2].map((i) => (
          <Card key={i} className="p-4">
            <div className="h-24 animate-pulse bg-muted rounded" />
          </Card>
        ))}
      </div>
    )
  }

  if (deposits.length === 0) {
    return (
      <Card className="p-8 text-center space-y-4">
        <p className="text-muted-foreground">Нет вкладов. Создайте первый вклад.</p>
        <Button onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Создать вклад
        </Button>
        <CreateDepositDialog open={showCreateDialog} onOpenChange={setShowCreateDialog} />
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {deposits.map((deposit) => (
        <Card key={deposit.id} className="p-4 hover:bg-accent transition-colors">
          <div className="flex items-start justify-between">
            <div className="flex items-start gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <PiggyBank className="h-5 w-5 text-primary" />
              </div>
              <div className="space-y-1">
                <h3 className="font-semibold text-foreground">{deposit.name}</h3>
                <div className="flex items-center gap-2">
                  <Badge className={statusColors[deposit.status as keyof typeof statusColors]}>
                    {statusLabels[deposit.status as keyof typeof statusLabels]}
                  </Badge>
                  <span className="text-sm text-muted-foreground">{deposit.interest_rate}% годовых</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {new Date(deposit.start_date).toLocaleDateString("ru-RU")} -{" "}
                  {new Date(deposit.end_date).toLocaleDateString("ru-RU")}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-lg font-bold text-foreground">₽{deposit.amount.toFixed(2)}</p>
            </div>
          </div>
        </Card>
      ))}
      <Button variant="outline" className="w-full bg-transparent" onClick={() => setShowCreateDialog(true)}>
        <Plus className="h-4 w-4 mr-2" />
        Добавить вклад
      </Button>
      <CreateDepositDialog open={showCreateDialog} onOpenChange={setShowCreateDialog} />
    </div>
  )
}
