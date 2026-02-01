/**
 * Type for the MasterFootTrafficAgent payload.
 * Single source of truth: do not reshape or recompute in the UI.
 */
export interface FootTrafficSignal {
  source: string
  extra_customers_per_hour: number
  confidence: number
  explanation: string
}

export interface FootTrafficFinalForecast {
  expected_extra_customers_per_hour: number
  expected_total_customers_per_hour: number
  confidence: number
  summary: string[]
}

export interface FootTrafficForecastPayload {
  baseline_customers_per_hour: number
  signals: FootTrafficSignal[]
  final_forecast: FootTrafficFinalForecast
  /** LLM-generated plain-language bullets for business owners */
  business_insights?: string[]
}
