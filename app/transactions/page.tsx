import { DashboardLayout } from "@/components/dashboard-layout"
import { TransactionsTable } from "@/components/transactions-table"

export default function TransactionsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Транзакции</h1>
          <p className="text-muted-foreground mt-1">Управляйте своими транзакциями</p>
        </div>

        <TransactionsTable />
      </div>
    </DashboardLayout>
  )
}
