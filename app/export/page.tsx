import { DashboardLayout } from "@/components/dashboard-layout"
import { ExportForm } from "@/components/export-form"

export default function ExportPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Export Data</h1>
          <p className="text-muted-foreground mt-1">Download your transaction data as CSV</p>
        </div>

        <ExportForm />
      </div>
    </DashboardLayout>
  )
}
