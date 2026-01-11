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

interface Account {
  id: number
  name: string
  description: string
  account_type: string
  currency: string
  balance: number
}

interface EditAccountDialogProps {
  account: Account
  onClose: () => void
  onUpdate: (account: Account) => void
}

export function EditAccountDialog({ account, onClose, onUpdate }: EditAccountDialogProps) {
  const [formData, setFormData] = useState({
    name: account.name,
    description: account.description || "",
    account_type: account.account_type,
    currency: account.currency,
    balance: account.balance.toString(),
  })
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)

    try {
      const updated = await api.updateAccount(account.id, {
        ...formData,
        balance: Number.parseFloat(formData.balance),
      })
      toast({
        title: "Счет обновлен",
        description: updated.name,
      })
      onUpdate(updated)
      onClose()
    } catch (error) {
      console.error("Ошибка обновления счета:", error)
      toast({
        title: "Не удалось обновить счет",
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
          <DialogTitle>Редактировать счет</DialogTitle>
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
            <Label htmlFor="edit-description">Описание</Label>
            <Input
              id="edit-description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Основной счет для расходов"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-account-type">Тип счета</Label>
            <Select
              value={formData.account_type}
              onValueChange={(value) => setFormData({ ...formData, account_type: value })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="checking">Текущий счет</SelectItem>
                <SelectItem value="savings">Накопительный</SelectItem>
                <SelectItem value="credit_card">Кредитная карта</SelectItem>
                <SelectItem value="cash">Наличные</SelectItem>
                <SelectItem value="investment">Инвестиционный</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-currency">Валюта</Label>
            <Input
              id="edit-currency"
              value={formData.currency}
              onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="edit-balance">Баланс</Label>
            <Input
              id="edit-balance"
              type="number"
              step="0.01"
              value={formData.balance}
              onChange={(e) => setFormData({ ...formData, balance: e.target.value })}
            />
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
