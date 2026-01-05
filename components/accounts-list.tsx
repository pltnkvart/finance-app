"use client"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Wallet, CreditCard, Banknote, TrendingUp, Edit, Trash2 } from "lucide-react"
import { api } from "@/lib/api"

interface Account {
  id: number
  name: string
  description: string
  account_type: string
  currency: string
  balance: number
  created_at: string
  updated_at: string
}

const accountTypeIcons = {
  checking: Wallet,
  savings: TrendingUp,
  credit_card: CreditCard,
  cash: Banknote,
  investment: TrendingUp,
}

const accountTypeLabels = {
  checking: "Текущий счет",
  savings: "Накопительный",
  credit_card: "Кредитная карта",
  cash: "Наличные",
  investment: "Инвестиционный",
}

export function AccountsList() {
  const [accounts, setAccounts] = useState<Account[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api
      .getAccounts()
      .then((data) => {
        setAccounts(data)
        setLoading(false)
      })
      .catch(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="p-4">
            <div className="h-20 animate-pulse bg-muted rounded" />
          </Card>
        ))}
      </div>
    )
  }

  if (accounts.length === 0) {
    return (
      <Card className="p-8 text-center">
        <p className="text-muted-foreground">Нет счетов. Создайте первый счет.</p>
      </Card>
    )
  }

  return (
    <div className="space-y-3">
      {accounts.map((account) => {
        const Icon = accountTypeIcons[account.account_type as keyof typeof accountTypeIcons] || Wallet
        return (
          <Card key={account.id} className="p-4 hover:bg-accent transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground">{account.name}</h3>
                  <p className="text-sm text-muted-foreground">
                    {accountTypeLabels[account.account_type as keyof typeof accountTypeLabels]}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-lg font-bold text-foreground">₽{Number(account.balance).toFixed(2)}</p>
                  <p className="text-xs text-muted-foreground">{account.currency}</p>
                </div>
                <div className="flex gap-1">
                  <Button variant="ghost" size="icon">
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}
