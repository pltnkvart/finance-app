import { DashboardLayout } from "@/components/dashboard-layout"
import { SettingsForm } from "@/components/settings-form"

export default function SettingsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Настройки</h1>
          <p className="text-muted-foreground mt-1">Категории, счета и Telegram-бот</p>
        </div>

        <SettingsForm />
      </div>
    </DashboardLayout>
  )
}
