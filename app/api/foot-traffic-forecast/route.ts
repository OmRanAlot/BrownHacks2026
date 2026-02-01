import { NextResponse } from "next/server"

/**
 * Proxies to the MasterFootTrafficAgent backend.
 * Falls back to mock data when backend is unreachable (e.g. ECONNREFUSED).
 */
const FOOT_TRAFFIC_API_URL =
  process.env.FOOT_TRAFFIC_API_URL || "http://localhost:8002"

/** Mock forecast when backend is down — lets dashboard render without errors */
const MOCK_FORECAST = {
  baseline_customers_per_hour: 42,
  signals: [
    {
      source: "weather_event",
      extra_customers_per_hour: 3.2,
      confidence: 0.75,
      explanation: "Mild weather favors walk-in traffic.",
    },
    {
      source: "google_traffic",
      extra_customers_per_hour: -1.5,
      confidence: 0.6,
      explanation: "Moderate congestion; slight drag on foot traffic.",
    },
    {
      source: "mta_subway",
      extra_customers_per_hour: 2.0,
      confidence: 0.7,
      explanation: "Average subway busyness near station exits.",
    },
  ],
  final_forecast: {
    expected_extra_customers_per_hour: 2.5,
    expected_total_customers_per_hour: 44.5,
    confidence: 0.68,
    summary: ["On par with usual"],
  },
  business_insights: [
    "Weather is favorable—mild temps tend to bring more walk-in traffic.",
    "Road congestion is moderate with slight drag on foot traffic.",
    "Subway conditions are average near station exits.",
  ],
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const baseline = searchParams.get("baseline")
    const date = searchParams.get("date")
    const time = searchParams.get("time")
    const params = new URLSearchParams()
    if (baseline != null) params.set("baseline", baseline)
    if (date != null) params.set("date", date)
    if (time != null) params.set("time", time)
    const qs = params.toString()
    const url = `${FOOT_TRAFFIC_API_URL}/api/foot-traffic-forecast${qs ? `?${qs}` : ""}`
    const res = await fetch(url, {
      next: { revalidate: 60 },
      signal: AbortSignal.timeout(8000),
    })
    if (!res.ok) {
      const text = await res.text()
      return NextResponse.json(
        { error: "Foot traffic backend error", detail: text },
        { status: res.status }
      )
    }
    const data = await res.json()
    return NextResponse.json(data)
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err)
    const cause = (err as { cause?: { code?: string } })?.cause
    const code = typeof cause?.code === "string" ? cause.code : ""
    // Backend unreachable (ECONNREFUSED, timeout, etc.) — return mock data so dashboard still works
    if (
      code === "ECONNREFUSED" ||
      code === "ETIMEDOUT" ||
      code === "ENOTFOUND" ||
      message.toLowerCase().includes("fetch failed")
    ) {
      return NextResponse.json({
        ...MOCK_FORECAST,
        _fallback: true,
        _message: `Backend unreachable. Using demo data. Start with: cd backend && uvicorn main:app --port 8002`,
      })
    }
    return NextResponse.json(
      {
        error: "Failed to fetch foot traffic forecast",
        detail: message,
        hint: "Start the backend: cd backend && uvicorn main:app --port 8002",
      },
      { status: 502 }
    )
  }
}
