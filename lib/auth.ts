const TOKEN_KEY = "fintrack_token"

export const authStorage = {
  getToken: () => {
    if (typeof window === "undefined") {
      return null
    }
    return window.localStorage.getItem(TOKEN_KEY)
  },
  setToken: (token: string) => {
    if (typeof window === "undefined") {
      return
    }
    window.localStorage.setItem(TOKEN_KEY, token)
  },
  clearToken: () => {
    if (typeof window === "undefined") {
      return
    }
    window.localStorage.removeItem(TOKEN_KEY)
  },
}

export const isAuthenticated = () => Boolean(authStorage.getToken())
