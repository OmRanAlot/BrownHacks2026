import { NextResponse } from "next/server"

// Mock data - in production this would call the Python FastAPI backend
const mockPrediction = {
  location_id: "loc-001",
  date: new Date().toISOString().split("T")[0],
  traffic_index: 85,
  confidence: 0.82,
  demand_level: "High",
  traffic_change: "+18%",
  primary_driver: "Local concert + clear weather",
  hourly_forecasts: [
    { hour: "6am", baseline: 20, predicted: 22, low: 18, high: 26 },
    { hour: "7am", baseline: 35, predicted: 38, low: 32, high: 44 },
    { hour: "8am", baseline: 55, predicted: 58, low: 50, high: 66 },
    { hour: "9am", baseline: 65, predicted: 62, low: 55, high: 69 },
    { hour: "10am", baseline: 50, predicted: 52, low: 45, high: 59 },
    { hour: "11am", baseline: 55, predicted: 58, low: 50, high: 66 },
    { hour: "12pm", baseline: 75, predicted: 82, low: 72, high: 92 },
    { hour: "1pm", baseline: 80, predicted: 85, low: 75, high: 95 },
    { hour: "2pm", baseline: 65, predicted: 68, low: 60, high: 76 },
    { hour: "3pm", baseline: 55, predicted: 60, low: 52, high: 68 },
    { hour: "4pm", baseline: 60, predicted: 78, low: 68, high: 88 },
    { hour: "5pm", baseline: 70, predicted: 92, low: 82, high: 102 },
    { hour: "6pm", baseline: 75, predicted: 98, low: 88, high: 108 },
    { hour: "7pm", baseline: 65, predicted: 95, low: 85, high: 105 },
    { hour: "8pm", baseline: 55, predicted: 88, low: 78, high: 98 },
    { hour: "9pm", baseline: 40, predicted: 65, low: 55, high: 75 },
    { hour: "10pm", baseline: 25, predicted: 35, low: 28, high: 42 },
  ],
}

export async function GET() {
  // In production, this would call: await fetch('http://localhost:8000/api/predict')
  return NextResponse.json(mockPrediction)
}

export async function POST(request: Request) {
  const body = await request.json()
  
  // In production, forward to FastAPI backend
  // const response = await fetch('http://localhost:8000/api/predict', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify(body),
  // })
  
  return NextResponse.json({
    ...mockPrediction,
    location_id: body.location_id || mockPrediction.location_id,
  })
}
