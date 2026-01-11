"use client"

import type React from "react"

import { createContext, useContext, useMemo, useState } from "react"
import { format } from "date-fns"

export type DateRangeType = "last30" | "last90" | "last365" | "custom" | "all"

interface DateRangeContextValue {
  range: DateRangeType
  startDate: string | null
  endDate: string | null
  setRange: (range: DateRangeType) => void
  customStart: string | null
  customEnd: string | null
  setCustomRange: (start: string | null, end: string | null) => void
}

const DateRangeContext = createContext<DateRangeContextValue | undefined>(undefined)

function formatDate(date: Date): string {
  return format(date, "yyyy-MM-dd")
}

export function DateRangeProvider({ children }: { children: React.ReactNode }) {
  const [range, setRange] = useState<DateRangeType>("last30")
  const [customStart, setCustomStart] = useState<string | null>(null)
  const [customEnd, setCustomEnd] = useState<string | null>(null)

  const { startDate, endDate } = useMemo(() => {
    if (range === "all") {
      return { startDate: null, endDate: null }
    }
    if (range === "custom") {
      return { startDate: customStart, endDate: customEnd }
    }

    const today = new Date()
    const end = formatDate(today)
    const start = new Date(today)
    const daysMap: Record<DateRangeType, number> = {
      last30: 30,
      last90: 90,
      last365: 365,
      custom: 0,
      all: 0,
    }
    start.setDate(start.getDate() - (daysMap[range] - 1))

    return {
      startDate: formatDate(start),
      endDate: end,
    }
  }, [range, customStart, customEnd])

  const setCustomRange = (start: string | null, end: string | null) => {
    setCustomStart(start)
    setCustomEnd(end)
  }

  return (
    <DateRangeContext.Provider
      value={{ range, startDate, endDate, setRange, customStart, customEnd, setCustomRange }}
    >
      {children}
    </DateRangeContext.Provider>
  )
}

export function useDateRange() {
  const context = useContext(DateRangeContext)
  if (!context) {
    throw new Error("useDateRange must be used within DateRangeProvider")
  }
  return context
}
