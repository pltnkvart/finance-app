"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { api } from "@/lib/api"
import { authStorage, isAuthenticated } from "@/lib/auth"
import { useToast } from "@/hooks/use-toast"

export default function RegisterPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [step, setStep] = useState<"form" | "link">("form")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [linkLoading, setLinkLoading] = useState(false)
  const [linkCode, setLinkCode] = useState<string | null>(null)
  const [linkExpires, setLinkExpires] = useState<string | null>(null)
  const [linked, setLinked] = useState(false)

  useEffect(() => {
    if (isAuthenticated() && step === "form") {
      router.replace("/")
    }
  }, [router, step])

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoading(true)
    try {
      await api.register({ email, password })
      const login = await api.login({ email, password })
      authStorage.setToken(login.access_token)
      const code = await api.getTelegramLinkCode()
      setLinkCode(code.code)
      setLinkExpires(code.expires_at)
      setStep("link")
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Не удалось зарегистрироваться",
        description: error instanceof Error ? error.message : "Проверьте данные и попробуйте снова",
      })
    } finally {
      setLoading(false)
    }
  }

  const refreshLinkCode = async () => {
    setLinkLoading(true)
    try {
      const code = await api.getTelegramLinkCode()
      setLinkCode(code.code)
      setLinkExpires(code.expires_at)
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Не удалось получить код",
        description: error instanceof Error ? error.message : "Попробуйте позже",
      })
    } finally {
      setLinkLoading(false)
    }
  }

  const checkLinkStatus = async () => {
    setLinkLoading(true)
    try {
      const me = await api.getMe()
      if (me.telegram_user_id) {
        setLinked(true)
        router.push("/")
        return
      }
      toast({
        variant: "destructive",
        title: "Telegram не привязан",
        description: "Отправьте код боту и попробуйте снова.",
      })
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Не удалось проверить",
        description: error instanceof Error ? error.message : "Попробуйте позже",
      })
    } finally {
      setLinkLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      <Card className="w-full max-w-md p-8 space-y-6">
        {step === "form" ? (
          <>
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold text-foreground">Создать аккаунт</h1>
              <p className="text-sm text-muted-foreground">Создайте учетную запись, чтобы начать работу.</p>
            </div>

            <form className="space-y-4" onSubmit={handleSubmit}>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Пароль</Label>
                <Input
                  id="password"
                  type="password"
                  autoComplete="new-password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={8}
                  maxLength={72}
                />
              </div>

              <Button className="w-full" type="submit" disabled={loading}>
                {loading ? "Создаем..." : "Зарегистрироваться"}
              </Button>
            </form>

            <p className="text-sm text-muted-foreground">
              Уже есть аккаунт?{" "}
              <Link href="/login" className="text-primary hover:underline">
                Войти
              </Link>
            </p>
          </>
        ) : (
          <>
            <div className="space-y-2">
              <h1 className="text-2xl font-semibold text-foreground">Привяжите Telegram</h1>
              <p className="text-sm text-muted-foreground">
                Отправьте боту код, чтобы связать аккаунт и создавать транзакции.
              </p>
            </div>

            <div className="rounded-lg border border-border p-4 space-y-3">
              <div className="text-sm text-muted-foreground">Бот:</div>
              <a
                className="text-primary hover:underline"
                href="https://t.me/finance_tracker_ai_bot"
                target="_blank"
                rel="noreferrer"
              >
                @finance_tracker_ai_bot
              </a>
              <div className="text-sm text-muted-foreground">Код:</div>
              <div className="text-lg font-semibold text-foreground tracking-widest">{linkCode || "—"}</div>
              {linkExpires ? (
                <div className="text-xs text-muted-foreground">Действителен до: {new Date(linkExpires).toLocaleString()}</div>
              ) : null}
            </div>

            <div className="space-y-3">
              <Button className="w-full" onClick={checkLinkStatus} disabled={linkLoading || !linkCode}>
                {linkLoading ? "Проверяем..." : linked ? "Привязано" : "Проверить привязку"}
              </Button>
              <Button className="w-full" variant="outline" onClick={refreshLinkCode} disabled={linkLoading}>
                Получить новый код
              </Button>
            </div>
          </>
        )}
      </Card>
    </div>
  )
}
