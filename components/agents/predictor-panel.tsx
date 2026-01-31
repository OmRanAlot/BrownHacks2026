"use client"

import { Bot, Cloud, Music, MapPin, TrendingUp } from "lucide-react"

const signals = [
  { id: "1", source: "Weather API", icon: Cloud, value: "Clear, 72°F", weight: "0.25" },
  { id: "2", source: "Events API", icon: Music, value: "Concert at 7pm", weight: "0.35" },
  { id: "3", source: "Maps API", icon: MapPin, value: "+23% activity", weight: "0.25" },
  { id: "4", source: "Historical", icon: TrendingUp, value: "Thursday pattern", weight: "0.15" },
]

const forecasts = [
  { period: "4pm - 5pm", traffic: 78, confidence: 0.85, change: "+18%" },
  { period: "5pm - 6pm", traffic: 92, confidence: 0.82, change: "+31%" },
  { period: "6pm - 7pm", traffic: 98, confidence: 0.80, change: "+40%" },
  { period: "7pm - 8pm", traffic: 95, confidence: 0.78, change: "+36%" },
]

const anomalies = [
  { id: "1", type: "Surge Detected", detail: "Evening traffic 40% above normal", severity: "high" },
  { id: "2", type: "Pattern Break", detail: "Thursday behaving like weekend", severity: "medium" },
]

export function PredictorPanel() {
  return (
    <div className="rounded-xl border border-border bg-card">
      <div className="border-b border-border p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Bot className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-semibold text-foreground">Predictor Agent</h3>
              <p className="text-sm text-primary">Forecaster</p>
            </div>
          </div>
          <span className="rounded-full bg-chart-3/10 px-3 py-1 text-xs font-medium text-chart-3">Processing</span>
        </div>
      </div>

      <div className="space-y-6 p-6">
        {/* Input Signals */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">INPUT SIGNALS</h4>
          <div className="space-y-2">
            {signals.map((signal) => {
              const Icon = signal.icon
              return (
                <div key={signal.id} className="flex items-center justify-between rounded-lg bg-secondary/30 px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Icon className="h-4 w-4 text-primary" />
                    <span className="text-sm text-foreground">{signal.source}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">{signal.value}</span>
                    <span className="font-mono text-xs text-primary">w:{signal.weight}</span>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Forecast Output */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">FORECAST OUTPUT</h4>
          <div className="space-y-2">
            {forecasts.map((forecast) => (
              <div key={forecast.period} className="rounded-lg bg-secondary/30 px-3 py-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-foreground">{forecast.period}</span>
                  <span className="text-sm font-semibold text-accent">{forecast.change}</span>
                </div>
                <div className="mt-1 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Traffic Index:</span>
                    <span className="font-mono text-xs text-foreground">{forecast.traffic}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">Confidence:</span>
                    <span className="font-mono text-xs text-primary">{forecast.confidence}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Anomalies Detected */}
        <div>
          <h4 className="mb-3 text-xs font-medium text-muted-foreground">ANOMALIES DETECTED</h4>
          <div className="space-y-2">
            {anomalies.map((anomaly) => (
              <div
                key={anomaly.id}
                className={`rounded-lg px-3 py-2 ${
                  anomaly.severity === "high" ? "bg-chart-3/10" : "bg-secondary/30"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${anomaly.severity === "high" ? "text-chart-3" : "text-foreground"}`}>
                    {anomaly.type}
                  </span>
                  <span className={`text-xs ${anomaly.severity === "high" ? "text-chart-3" : "text-muted-foreground"}`}>
                    {anomaly.severity}
                  </span>
                </div>
                <p className="mt-1 text-xs text-muted-foreground">{anomaly.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
