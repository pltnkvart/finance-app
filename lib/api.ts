import { authStorage } from "@/lib/auth"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function apiRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_URL}${endpoint}`
  const token = authStorage.getToken()

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options?.headers,
      },
    })

    if (!response.ok) {
      const payload = await response.json().catch(() => null)
      const message = payload?.detail || response.statusText
      throw new Error(`API Error: ${message}`)
    }

    return await response.json()
  } catch (error) {
    console.error("[v0] API request failed:", url, error)
    throw error
  }
}

export const api = {
  // Auth
  register: (data: { email: string; password: string }) =>
    apiRequest<{ id: number; email: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  login: (data: { email: string; password: string }) =>
    apiRequest<{ access_token: string; token_type: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getMe: () => apiRequest<{ id: number; email: string; telegram_user_id?: string }>("/api/auth/me"),
  getTelegramLinkCode: () => apiRequest<{ code: string; expires_at: string }>("/api/auth/telegram-link-code", {
    method: "POST",
  }),

  // Statistics
  getStatistics: (params?: { start_date?: string; end_date?: string }) => {
    const query = params ? `?${new URLSearchParams(params as any).toString()}` : ""
    return apiRequest<any>(`/api/statistics/summary${query}`)
  },
  getCategoryStats: (params?: { start_date?: string; end_date?: string }) => {
    const query = params ? `?${new URLSearchParams(params as any).toString()}` : ""
    return apiRequest<any>(`/api/statistics/by-category${query}`)
  },
  getSpendingTrend: (params?: { start_date?: string; end_date?: string }) => {
    const query = params ? `?${new URLSearchParams(params as any).toString()}` : ""
    return apiRequest<any>(`/api/statistics/trend${query}`)
  },

  // Transactions
  getTransactions: (params?: { limit?: number; skip?: number; start_date?: string; end_date?: string }) => {
    const query = params ? `?${new URLSearchParams(params as any).toString()}` : ""
    return apiRequest<any>(`/api/transactions${query}`)
  },
  updateTransaction: (id: number, data: any) =>
    apiRequest<any>(`/api/transactions/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteTransaction: (id: number) =>
    apiRequest<any>(`/api/transactions/${id}`, {
      method: "DELETE",
    }),

  // Categories
  getCategories: () => apiRequest<any>("/api/categories"),
  createCategory: (data: any) =>
    apiRequest<any>("/api/categories", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateCategory: (id: number, data: any) =>
    apiRequest<any>(`/api/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteCategory: (id: number) =>
    apiRequest<any>(`/api/categories/${id}`, {
      method: "DELETE",
    }),

  // Accounts
  getAccounts: () => apiRequest<any>("/api/accounts"),
  createAccount: (data: any) =>
    apiRequest<any>("/api/accounts", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateAccount: (id: number, data: any) =>
    apiRequest<any>(`/api/accounts/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteAccount: (id: number) =>
    apiRequest<any>(`/api/accounts/${id}`, {
      method: "DELETE",
    }),

  // Deposits
  getDeposits: () => apiRequest<any>("/api/deposits"),
  createDeposit: (data: any) =>
    apiRequest<any>("/api/deposits", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateDeposit: (id: number, data: any) =>
    apiRequest<any>(`/api/deposits/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  deleteDeposit: (id: number) =>
    apiRequest<any>(`/api/deposits/${id}`, {
      method: "DELETE",
    }),

  // Export
  exportCSV: (params: { start_date?: string; end_date?: string; category_id?: number }) => {
    const query = new URLSearchParams(params as any).toString()
    const token = authStorage.getToken()
    return fetch(`${API_URL}/api/export/csv?${query}`, {
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    }).then((res) => res.blob())
  },
}
