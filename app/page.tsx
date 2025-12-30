import { DashboardLayout } from "@/components/dashboard-layout"
import { TransactionList } from "@/components/transaction-list"
import { StatsOverview } from "@/components/stats-overview"
import { CategoryChart } from "@/components/category-chart"

export default function HomePage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">Track your expenses and manage your finances</p>
        </div>

        <StatsOverview />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CategoryChart />
          <TransactionList limit={10} />
        </div>
      </div>
    </DashboardLayout>
  )
}
