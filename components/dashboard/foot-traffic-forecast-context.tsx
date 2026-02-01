"use client"

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
  type ReactNode,
} from "react"
import type { FootTrafficForecastPayload } from "@/lib/foot-traffic-forecast"

/**
 * Fetched once on dashboard load. Master agent is the single source of truth;
 * sub-agents are never called from the UI.
 */
type ForecastState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: FootTrafficForecastPayload }
  | { status: "error"; error: string }

const FootTrafficForecastContext = createContext<ForecastState>({
  status: "idle",
})

const fetchedRef = { current: false }

export function FootTrafficForecastProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<ForecastState>({ status: "idle" })

  useEffect(() => {
    // Only fetch once per app session to avoid repeated calls on rerenders.
    if (fetchedRef.current) return
    fetchedRef.current = true

    setState({ status: "loading" })
    fetch("/api/foot-traffic-forecast")
      .then((res) => {
        if (!res.ok) return res.json().then((b) => Promise.reject(b.error || b.detail || res.statusText))
        return res.json()
      })
      .then((data: FootTrafficForecastPayload) => {
        setState({ status: "success", data })
      })
      .catch((err) => {
        setState({
          status: "error",
          error: typeof err === "string" ? err : err?.message ?? "Failed to load forecast",
        })
      })
  }, [])

  return (
    <FootTrafficForecastContext.Provider value={state}>
      {children}
    </FootTrafficForecastContext.Provider>
  )
}

export function useFootTrafficForecast(): ForecastState {
  return useContext(FootTrafficForecastContext)
}
