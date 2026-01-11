"use client"

import type React from "react"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Menu, X, LayoutDashboard, Receipt, PieChart, Download, Settings, Bot, Wallet } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { format } from "date-fns"
import { ru } from "date-fns/locale"
import { RangeCalendar } from "@gravity-ui/date-components"
import { dateTimeParse } from "@gravity-ui/date-utils"
import { cn } from "@/lib/utils"
import { DateRangeProvider, useDateRange } from "@/components/date-range-context"
import { authStorage, isAuthenticated } from "@/lib/auth"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const router = useRouter()

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login")
    }
  }, [router])

  const navigation = [
    { name: "Главная", href: "/", icon: LayoutDashboard },
    { name: "Транзакции", href: "/transactions", icon: Receipt },
    { name: "Счета", href: "/accounts", icon: Wallet },
    { name: "Аналитика", href: "/analytics", icon: PieChart },
    { name: "Экспорт", href: "/export", icon: Download },
    { name: "Настройки", href: "/settings", icon: Settings },
  ]

  return (
    <DateRangeProvider>
      <LayoutShell
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        navigation={navigation}
      >
        {children}
      </LayoutShell>
    </DateRangeProvider>
  )
}

function LayoutShell({
  sidebarOpen,
  setSidebarOpen,
  navigation,
  children,
}: {
  sidebarOpen: boolean
  setSidebarOpen: (open: boolean) => void
  navigation: { name: string; href: string; icon: React.ComponentType<{ className?: string }> }[]
  children: React.ReactNode
}) {
  const { range, setRange, customStart, customEnd, setCustomRange } = useDateRange()
  const router = useRouter()

  const handleLogout = () => {
    authStorage.clearToken()
    router.replace("/login")
  }

  const rangeLabelMap: Record<string, string> = {
    last30: "Последние 30 дней",
    last90: "Последние 90 дней",
    last365: "Последний год",
    custom: "Произвольный диапазон",
    all: "Все время",
  }

  const rangeValue = {
    from: customStart ? new Date(customStart) : undefined,
    to: customEnd ? new Date(customEnd) : undefined,
  }

  const startValue = customStart ? dateTimeParse(customStart) : undefined
  const endValue = customEnd ? dateTimeParse(customEnd) : undefined
  const calendarValue = startValue && endValue ? { start: startValue, end: endValue } : null

  const rangeLabel =
    rangeValue.from && rangeValue.to
      ? `${format(rangeValue.from, "dd.MM.yyyy", { locale: ru })} - ${format(rangeValue.to, "dd.MM.yyyy", {
          locale: ru,
        })}`
      : "Выберите даты"

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed top-0 left-0 h-full w-64 bg-card border-r border-border z-50 transition-transform duration-200 lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center gap-2">
              <Bot className="h-6 w-6 text-primary" />
              <span className="text-xl font-semibold text-foreground">FinTrack</span>
            </div>
            <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(false)}>
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navigation.map((item) => (
              <Link
                key={item.name}
                href={item.href}
                className="flex items-center gap-3 px-3 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-accent rounded-md transition-colors"
              >
                <item.icon className="h-5 w-5" />
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Footer */}
          <div className="p-4 border-t border-border">
            <div className="text-xs text-muted-foreground">Подключено к Telegram</div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 flex items-center justify-between h-16 px-6 bg-card border-b border-border">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setSidebarOpen(true)}>
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-4">
            <Select value={range} onValueChange={(value) => setRange(value as typeof range)}>
              <SelectTrigger className="w-[190px]" aria-label="Диапазон">
                <SelectValue>{rangeLabelMap[range]}</SelectValue>
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="last30">Последние 30 дней</SelectItem>
                <SelectItem value="last90">Последние 90 дней</SelectItem>
                <SelectItem value="last365">Последний год</SelectItem>
                <SelectItem value="custom">Произвольный</SelectItem>
                <SelectItem value="all">Все время</SelectItem>
              </SelectContent>
            </Select>
            {range === "custom" ? (
              <Popover>
                <PopoverTrigger asChild>
                  <Button variant="outline" size="sm">
                    {rangeLabel}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="p-4" align="end">
                  <RangeCalendar
                    value={calendarValue}
                    onUpdate={(value) => {
                      setCustomRange(
                        value.start.format("YYYY-MM-DD"),
                        value.end.format("YYYY-MM-DD")
                      )
                    }}
                  />
                </PopoverContent>
              </Popover>
            ) : null}
          </div>
          <Button variant="ghost" onClick={handleLogout}>
            Выйти
          </Button>
        </header>

        {/* Page content */}
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
