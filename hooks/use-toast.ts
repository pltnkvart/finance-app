"use client"

import * as React from "react"

type ToastActionElement = React.ReactElement

type ToastItem = ToastProps & {
  id: string
  title?: string
  description?: string
  action?: ToastActionElement
}

type State = {
  toasts: ToastItem[]
}

type ToastAction =
  | { type: "ADD_TOAST"; toast: ToastItem }
  | { type: "UPDATE_TOAST"; toast: Partial<ToastItem> }
  | { type: "DISMISS_TOAST"; toastId?: string }
  | { type: "REMOVE_TOAST"; toastId?: string }

const TOAST_LIMIT = 3
const TOAST_REMOVE_DELAY = 4000

let count = 0

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER
  return count.toString()
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>()

const reducer = (state: State, action: ToastAction): State => {
  switch (action.type) {
    case "ADD_TOAST":
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      }
    case "UPDATE_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((toast) =>
          toast.id === action.toast.id ? { ...toast, ...action.toast } : toast
        ),
      }
    case "DISMISS_TOAST":
      return {
        ...state,
        toasts: state.toasts.map((toast) =>
          toast.id === action.toastId || action.toastId === undefined
            ? {
                ...toast,
                open: false,
              }
            : toast
        ),
      }
    case "REMOVE_TOAST":
      if (action.toastId === undefined) {
        return {
          ...state,
          toasts: [],
        }
      }

      return {
        ...state,
        toasts: state.toasts.filter((toast) => toast.id !== action.toastId),
      }
  }
}

const listeners: Array<(state: State) => void> = []

let memoryState: State = { toasts: [] }

function dispatch(action: ToastAction) {
  memoryState = reducer(memoryState, action)
  listeners.forEach((listener) => listener(memoryState))
}

function toast({ ...props }: Omit<ToastItem, "id">) {
  const id = genId()

  const update = (props: ToastItem) =>
    dispatch({
      type: "UPDATE_TOAST",
      toast: { ...props, id },
    })

  const dismiss = () => dispatch({ type: "DISMISS_TOAST", toastId: id })

  dispatch({
    type: "ADD_TOAST",
    toast: {
      ...props,
      id,
      open: true,
      onOpenChange: (open) => {
        if (!open) dismiss()
      },
    },
  })

  if (toastTimeouts.has(id)) {
    clearTimeout(toastTimeouts.get(id))
  }

  toastTimeouts.set(
    id,
    setTimeout(() => {
      toastTimeouts.delete(id)
      dispatch({ type: "REMOVE_TOAST", toastId: id })
    }, TOAST_REMOVE_DELAY)
  )

  return {
    id,
    dismiss,
    update,
  }
}

function useToast() {
  const [state, setState] = React.useState<State>(memoryState)

  React.useEffect(() => {
    listeners.push(setState)
    return () => {
      const index = listeners.indexOf(setState)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }, [])

  return {
    ...state,
    toast,
    dismiss: (toastId?: string) => dispatch({ type: "DISMISS_TOAST", toastId }),
  }
}

export type ToastProps = {
  variant?: "default" | "destructive"
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export { toast, useToast }
