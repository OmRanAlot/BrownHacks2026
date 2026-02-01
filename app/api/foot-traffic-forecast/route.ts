import { NextResponse } from "next/server"

/**
 * Proxies to the MasterFootTrafficAgent backend.
 * The master agent is the single source of truth; sub-agents (weather, Google traffic, MTA)
 * are never called from the UI—only the backend runs them inside the master agent.
 */
const FOOT_TRAFFIC_API_URL =
  process.env.FOOT_TRAFFIC_API_URL || "http://localhost:8002"

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
