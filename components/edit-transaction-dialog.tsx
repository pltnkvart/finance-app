"use client"

import type React from "react"

import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { api } from "@/lib/api"

interface Transaction {
  id: number
  amount: number
  description: string
  transaction_date: string
  category_id: number | null
  category_name: string | null
}

interface Category {
  id: number
  name: string
}

interface EditTransactionDialogProps {
  transaction: Transaction
  categories: Category[]
  onClose: () => void
  onUpdate: (transaction: Transaction) => void
}

export function EditTransactionDialog({ transaction, categories, onClose, onUpdate }: EditTransactionDialogProps) {
  const [amount, setAmount] = useState(transaction.amount.toString())
  const [description, setDescription] = useState(transaction.description)
  const [categoryId, setCategoryId] = useState<string>(transaction.category_id?.toString() || "")
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const updatedTransaction = await api.updateTransaction(transaction.id, {
        amount: Number.parseFloat(amount),
        description,
        category_id: categoryId ? Number.parseInt(categoryId) : null,
      })
      onUpdate(updatedTransaction)
      onClose()
    } catch (error) {
      console.error("Ошибка обновления транзакции:", error)
      alert("Не удалось обновить транзакцию")
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Редактировать транзакцию</DialogTitle>
          <DialogDescription>Обновить детали и категорию транзакции</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="amount">Сумма</Label>
            <Input
              id="amount"
              type="number"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Описание</Label>
            <Input id="description" value={description} onChange={(e) => setDescription(e.target.value)} required />
          </div>

          <div className="space-y-2">
            <Label htmlFor="category">Категория</Label>
            <Select value={categoryId} onValueChange={setCategoryId}>
              <SelectTrigger>
                <SelectValue placeholder="Выберите категорию" />
              </SelectTrigger>
              <SelectContent>
                {categories.map((category) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
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
