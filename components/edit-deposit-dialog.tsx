"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { api } from "@/lib/api"
import { toast } from "@/hooks/use-toast"

interface Deposit {
  id: number
  name: string
  amount: number
  interest_rate: number
  end_date: string
  status: string
}

interface EditDepositDialogProps {
  deposit: Deposit
  onClose: () => void
  onUpdate: (deposit: Deposit) => void
}

const statusLabels = {
  active: "Активен",
  completed: "Завершен",
  cancelled: "Отменен",
}

export function EditDepositDialog({ deposit, onClose, onUpdate }: EditDepositDialogProps) {
  const [formData, setFormData] = useState({
    name: deposit.name,
    amount: deposit.amount.toString(),
    interest_rate: deposit.interest_rate.toString(),
    end_date: deposit.end_date.split("T")[0] ?? deposit.end_date,
    status: deposit.status,
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)

    try {
      const updated = await api.updateDeposit(deposit.id, {
        name: formData.name,
        amount: Number.parseFloat(formData.amount),
        interest_rate: Number.parseFloat(formData.interest_rate),
        end_date: formData.end_date,
        status: formData.status,
      })
      toast({
        title: "Вклад обновлен",
        description: updated.name,
      })
      onUpdate(updated)
      onClose()
    } catch (error) {
      console.error("Ошибка обновления вклада:", error)
      toast({
        title: "Не удалось обновить вклад",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Редактировать вклад</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="edit-name">Название</Label>
            <Input
              id="edit-name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-amount">Сумма</Label>
            <Input
              id="edit-amount"
              type="number"
              step="0.01"
              value={formData.amount}
              onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-interest">Процентная ставка (%)</Label>
            <Input
              id="edit-interest"
              type="number"
              step="0.01"
              value={formData.interest_rate}
              onChange={(e) => setFormData({ ...formData, interest_rate: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-end">Дата окончания</Label>
            <Input
              id="edit-end"
              type="date"
              value={formData.end_date}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-status">Статус</Label>
            <Select
              value={formData.status}
              onValueChange={(value) => setFormData({ ...formData, status: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {Object.entries(statusLabels).map(([value, label]) => (
                  <SelectItem key={value} value={value}>
                    {label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex justify-end gap-3">
            <Button type="button" variant="outline" onClick={onClose}>
              Отмена
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "Сохранение..." : "Сохранить"}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  )
}
