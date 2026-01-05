import { DashboardLayout } from "@/components/dashboard-layout"
import { CategoryChart } from "@/components/category-chart"
import { SpendingTrend } from "@/components/spending-trend"
import { TopCategories } from "@/components/top-categories"

export default function AnalyticsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Аналитика</h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CategoryChart />
          <TopCategories />
        </div>

        <SpendingTrend />
      </div>
    </DashboardLayout>
  )
}
