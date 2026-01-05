"use client"

import { useState, useEffect } from "react"
import { DashboardLayout } from "@/components/dashboard-layout"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Wallet, TrendingUp, PiggyBank } from "lucide-react"
import { CreateAccountDialog } from "@/components/create-account-dialog"
import { AccountsList } from "@/components/accounts-list"
import { DepositsList } from "@/components/deposits-list"
import { api } from "@/lib/api"

export default function AccountsPage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [totalBalance, setTotalBalance] = useState(0)

  useEffect(() => {
    api
      .getStatistics()
      .then((data) => setTotalBalance(data.total_balance || 0))
      .catch(() => {})
  }, [])

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-semibold text-foreground">Счета и вклады</h1>
            <p className="text-muted-foreground mt-1">Управляйте своими счетами и депозитами</p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Добавить счет
          </Button>
        </div>

        <Card className="p-6">
          <div className="flex items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Wallet className="h-8 w-8 text-primary" />
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Общий баланс</p>
              <h2 className="text-4xl font-bold text-foreground">₽{totalBalance.toFixed(2)}</h2>
            </div>
          </div>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">Счета</h2>
            </div>
            <AccountsList />
          </div>

          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <PiggyBank className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold text-foreground">Вклады</h2>
            </div>
            <DepositsList />
          </div>
        </div>

        <CreateAccountDialog open={showCreateDialog} onOpenChange={setShowCreateDialog} />
      </div>
    </DashboardLayout>
  )
}
