import { NextResponse } from "next/server"

// Mock city signals data
const mockSignals = {
  weather: {
    condition: "clear",
    temperature: 72,
    humidity: 45,
    rain_probability: 0,
    description: "Clear · 72°F · No rain",
  },
  events: [
    {
      id: "evt-001",
      name: "Live Concert",
      venue: "Brooklyn Bowl",
      distance_miles: 0.4,
      start_time: "19:00",
      expected_attendance: 3000,
      impact: "high",
    },
  ],
  maps_activity: {
    current_popularity: 1.23,
    average_popularity: 1.0,
    trend: "increasing",
    change_percent: 23,
    description: "Above average (+23%)",
  },
  disruptions: [],
}

export async function GET() {
  return NextResponse.json(mockSignals)
}
