"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Trash2, Pencil, X } from "lucide-react"
import { api } from "@/lib/api"
import { toast } from "@/hooks/use-toast"

interface Category {
  id: number
  name: string
  parent_id: number | null
  parent_name?: string | null
  description?: string | null
}

export function SettingsForm() {
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    parent_id: "none",
  })

  const loadCategories = async () => {
    try {
      const data = await api.getCategories()
      setCategories(data)
    } catch (error) {
      console.error("Ошибка загрузки категорий:", error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadCategories()
  }, [])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()

    const payload = {
      name: formData.name,
      description: formData.description || null,
      parent_id: formData.parent_id === "none" ? null : Number(formData.parent_id),
    }

    try {
      if (editingId) {
        const updated = await api.updateCategory(editingId, payload)
        toast({
          title: "Категория обновлена",
          description: updated.name,
        })
      } else {
        const created = await api.createCategory(payload)
        toast({
          title: "Категория создана",
          description: created.name,
        })
      }
    } catch (error) {
      console.error("Ошибка сохранения категории:", error)
      toast({
        title: "Не удалось сохранить категорию",
        variant: "destructive",
      })
      return
    }

    setFormData({ name: "", description: "", parent_id: "none" })
    setEditingId(null)
    await loadCategories()
  }

  const startEdit = (category: Category) => {
    setEditingId(category.id)
    setFormData({
      name: category.name,
      description: category.description ?? "",
      parent_id: category.parent_id ? String(category.parent_id) : "none",
    })
  }

  const cancelEdit = () => {
    setEditingId(null)
    setFormData({ name: "", description: "", parent_id: "none" })
  }

  const handleDelete = async (category: Category) => {
    if (!confirm(`Удалить категорию "${category.name}"?`)) {
      return
    }

    try {
      await api.deleteCategory(category.id)
      toast({
        title: "Категория удалена",
        description: category.name,
      })
      if (editingId === category.id) {
        cancelEdit()
      }
      await loadCategories()
    } catch (error) {
      console.error("Ошибка удаления категории:", error)
      toast({
        title: "Не удалось удалить категорию",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-2">Категории и подкатегории</h3>
            <p className="text-sm text-muted-foreground">
              Создавайте родительские категории и подкатегории вручную.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="category-name">Название</Label>
              <Input
                id="category-name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Например: Развлечения"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="category-description">Описание</Label>
              <Input
                id="category-description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Опционально"
              />
            </div>

            <div className="space-y-2">
              <Label>Родительская категория</Label>
              <Select
                value={formData.parent_id}
                onValueChange={(value) => setFormData({ ...formData, parent_id: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Без родителя" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="none">Без родителя</SelectItem>
                  {categories
                    .filter((category) => category.parent_id === null)
                    .map((category) => (
                      <SelectItem key={category.id} value={String(category.id)}>
                        {category.name}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>

            <div className="flex justify-end">
              {editingId ? (
                <div className="flex gap-2">
                  <Button type="button" variant="outline" onClick={cancelEdit}>
                    <X className="h-4 w-4 mr-2" />
                    Отмена
                  </Button>
                  <Button type="submit">Сохранить</Button>
                </div>
              ) : (
                <Button type="submit">Добавить категорию</Button>
              )}
            </div>
          </form>

          <div className="space-y-2">
            <h4 className="font-medium text-foreground">Существующие категории</h4>
            {loading ? (
              <div className="h-24 animate-pulse bg-muted rounded" />
            ) : categories.length === 0 ? (
              <p className="text-sm text-muted-foreground">Категорий пока нет.</p>
            ) : (
              <div className="space-y-2">
                {categories.map((category) => (
                  <div key={category.id} className="flex items-center justify-between rounded-lg border border-border p-3">
                    <div>
                      <p className="font-medium text-foreground">{category.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {category.parent_name ? `Родитель: ${category.parent_name}` : "Родитель: нет"}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => startEdit(category)}
                        title="Редактировать"
                      >
                        <Pencil className="h-4 w-4" />
                      </Button>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-destructive hover:text-destructive"
                        onClick={() => handleDelete(category)}
                        title="Удалить"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </Card>

      <Card className="p-6">
        <div className="space-y-4">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-2">Telegram Бот</h3>
            <p className="text-sm text-muted-foreground">Отправляйте транзакции боту используя эти форматы</p>
          </div>

          <div className="space-y-2">
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">100 продукты</div>
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">кофе 5.50</div>
            <div className="p-3 rounded-lg bg-muted/50 font-mono text-sm">25 такси</div>
          </div>
        </div>
      </Card>
    </div>
  )
}
