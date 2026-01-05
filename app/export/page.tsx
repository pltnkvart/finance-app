import { DashboardLayout } from "@/components/dashboard-layout"
import { ExportForm } from "@/components/export-form"

export default function ExportPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Экспорт данных</h1>
        </div>

        <ExportForm />
      </div>
    </DashboardLayout>
  )
}
