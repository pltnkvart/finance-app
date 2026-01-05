"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { RefreshCw } from "lucide-react"
import { api } from "@/lib/api"

interface CategorizationStats {
  rule_based: {
    total_rules: number
    average_confidence: number
  }
  machine_learning: {
    is_trained: boolean
    num_categories: number
    total_samples: number
  }
  user_corrections: number
  threshold: number
}

export function SettingsForm() {
  const [stats, setStats] = useState<CategorizationStats | null>(null)
  const [training, setTraining] = useState(false)
  const [loading, setLoading] = useState(true)

  const loadStats = async () => {
    try {
      const data = await api.getCategorizationStats()
      setStats(data)
      setLoading(false)
    } catch (error) {
      console.error("Ошибка загрузки статистики:", error)
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  const handleTrain = async () => {
    setTraining(true)

    try {
      const result = await api.trainCategorization()

      if (result.success) {
        alert("Модель успешно обучена!")
        loadStats()
      } else {
        alert(result.message)
      }
    } catch (error) {
      console.error("Ошибка обучения:", error)
      alert("Не удалось обучить модель")
    } finally {
      setTraining(false)
    }
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="h-64 animate-pulse bg-muted rounded" />
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-medium text-foreground mb-2">Движок категоризации</h3>
            <p className="text-sm text-muted-foreground">
              Обучите модель машинного обучения для улучшения автоматической категоризации
            </p>
          </div>

          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium text-muted-foreground">Статус ML модели</p>
                  <Badge variant={stats.machine_learning.is_trained ? "default" : "secondary"}>
                    {stats.machine_learning.is_trained ? "Обучена" : "Не обучена"}
                  </Badge>
                </div>
                <p className="text-2xl font-semibold text-foreground">
                  {stats.machine_learning.num_categories} категорий
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  {stats.machine_learning.total_samples} обучающих примеров
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">Система правил</p>
                <p className="text-2xl font-semibold text-foreground">{stats.rule_based.total_rules} правил</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {(stats.rule_based.average_confidence * 100).toFixed(0)}% средняя точность
                </p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">Исправления пользователя</p>
                <p className="text-2xl font-semibold text-foreground">{stats.user_corrections}</p>
                <p className="text-sm text-muted-foreground mt-1">Учусь на ваших правках</p>
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <p className="text-sm font-medium text-muted-foreground mb-2">Порог схожести</p>
                <p className="text-2xl font-semibold text-foreground">{(stats.threshold * 100).toFixed(0)}%</p>
                <p className="text-sm text-muted-foreground mt-1">Минимальная требуемая уверенность</p>
              </div>
            </div>
          )}

          <Button onClick={handleTrain} disabled={training}>
            <RefreshCw className={`h-4 w-4 mr-2 ${training ? "animate-spin" : ""}`} />
            {training ? "Обучение модели..." : "Обучить ML модель"}
          </Button>

          <div className="p-4 bg-muted rounded-lg">
            <h4 className="font-medium text-foreground mb-2">О процессе обучения</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Требуется минимум 3 транзакции на категорию</li>
              <li>• Использует TF-IDF векторизацию и косинусное сходство</li>
              <li>• Учится на ваших ручных исправлениях категорий</li>
              <li>• Переобучайте периодически для лучших результатов</li>
            </ul>
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
