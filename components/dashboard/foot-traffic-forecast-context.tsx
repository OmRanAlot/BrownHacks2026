"use client"

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useMemo,
  type ReactNode,
} from "react"
import type {
  FootTrafficForecastPayload,
  FootTrafficSignal,
} from "@/lib/foot-traffic-forecast"
import { useEventSurge } from "@/components/event-surge-context"

/**
 * Fetches forecast on dashboard load. Uses localStorage for instant display when returning.
 * Backend caches results so repeat fetches are fast.
 * When simulated event is active: weather_event extra -50%, other sources 0.
 */
const STORAGE_KEY = "foot_traffic_forecast_cache"

const SURGE_PREDICTED_CUSTOMERS_PER_HOUR = 20
const SURGE_CONFIDENCE = 0.95

function applySurgeAdjustment(payload: FootTrafficForecastPayload): FootTrafficForecastPayload {
  const baseline = payload.baseline_customers_per_hour
  const expectedTotal = SURGE_PREDICTED_CUSTOMERS_PER_HOUR
  const expectedExtra = expectedTotal - baseline

  const adjustedSignals: FootTrafficSignal[] = payload.signals.map((s) => {
    if (s.source === "weather_event") {
      return {
        ...s,
        extra_customers_per_hour: expectedExtra, // weather is primary driver
        explanation: "Weather is historically poor for cafe foot traffic; rainy or stormy conditions reduce walk-in visits.",
      }
    }
    return {
      ...s,
      extra_customers_per_hour: 0,
      explanation: "Simulated event: impact set to 0 people/hr",
    }
  })

  return {
    ...payload,
    signals: adjustedSignals,
    final_forecast: {
      ...payload.final_forecast,
      expected_extra_customers_per_hour: expectedExtra,
      expected_total_customers_per_hour: expectedTotal,
      confidence: SURGE_CONFIDENCE,
      summary: ["Weather"],
    },
  }
}

type ForecastState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "success"; data: FootTrafficForecastPayload }
  | { status: "error"; error: string }

const FootTrafficForecastContext = createContext<ForecastState>({
  status: "idle",
})

function loadCached(): FootTrafficForecastPayload | null {
  if (typeof window === "undefined") return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const { data } = JSON.parse(raw) as {
      data: FootTrafficForecastPayload
      timestamp: number
    }
    return data
  } catch {
    return null
  }
}

function saveCached(data: FootTrafficForecastPayload) {
  if (typeof window === "undefined") return
  try {
    localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ data, timestamp: Date.now() })
    )
  } catch {
    /* ignore */
  }
}

export function FootTrafficForecastProvider({ children }: { children: ReactNode }) {
  const { isSurgeActive } = useEventSurge()
  const [state, setState] = useState<ForecastState>(() => {
    const cached = loadCached()
    if (cached) return { status: "success" as const, data: cached }
    return { status: "idle" }
  })

  useEffect(() => {
    const cached = loadCached()
    if (!cached) setState({ status: "loading" })

    fetch("/api/foot-traffic-forecast")
      .then((res) => {
        if (!res.ok) return res.json().then((b) => Promise.reject(b.error || b.detail || res.statusText))
        return res.json()
      })
      .then((data: FootTrafficForecastPayload) => {
        saveCached(data)
        setState({ status: "success", data })
      })
      .catch((err) => {
        // Keep showing cached data if fetch fails but we had it
        const fallback = loadCached()
        if (fallback) {
          setState({ status: "success", data: fallback })
        } else {
          setState({
            status: "error",
            error: typeof err === "string" ? err : err?.message ?? "Failed to load forecast",
          })
        }
      })
  }, [])

  const displayState = useMemo(() => {
    if (state.status !== "success" || !isSurgeActive) return state
    return {
      ...state,
      data: applySurgeAdjustment(state.data),
    }
  }, [state, isSurgeActive])

  return (
    <FootTrafficForecastContext.Provider value={displayState}>
      {children}
    </FootTrafficForecastContext.Provider>
  )
}

export function useFootTrafficForecast(): ForecastState {
  return useContext(FootTrafficForecastContext)
}
