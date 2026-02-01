from openai import OpenAI
from dotenv import load_dotenv
import asyncio
from typing import Dict, Any
import json
import math
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load .env from project root (parent of backend/)
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
load_dotenv(os.path.join(project_root, ".env"))
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

from mta import run_mta_forecast
from nearbycongestion import forecast_extra_customers
from predictor_agent import predict_for_datetime



# -----------------------------
# Normalization helpers
# -----------------------------

def normalize_weather_event(out: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": "weather_event",
        "extra_customers_per_hour": out.get("predicted_traffic", 0),
        "confidence": out.get("confidence", 0.5),
        "explanation": out.get("reasoning", ""),
    }


def normalize_google_traffic(out: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": "google_traffic",
        "extra_customers_per_hour": out.get("expected_extra_customers_per_hour", 0),
        "confidence": out.get("confidence_0_to_1", 0.5),
        "explanation": "; ".join(out.get("rationale_bullets", [])),
    }


def normalize_mta(out: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "source": "mta_subway",
        # convert 30 min → hourly equivalent
        "extra_customers_per_hour": out.get("expected_extra_customers_next_30_min", 0) * 2,
        "confidence": out.get("confidence_0_to_1", 0.5),
        "explanation": "; ".join(out.get("main_drivers", [])),
    }


# -----------------------------
# Master Agent
# -----------------------------

class MasterFootTrafficAgent:
    def __init__(self, baseline_customers_per_hour: float):
        self.baseline = baseline_customers_per_hour

    async def run(self, date=None, time=None) -> Dict[str, Any]:
        """
        Orchestrates all sub-agents and returns a unified forecast.
        """

        # --- Run sub-agents (parallel where possible) ---
        weather_task = asyncio.to_thread(
            predict_for_datetime,
            date=date,
            time=time,
            business_type="cafe"
        )

        dataset_path = os.path.join(project_root, "detailed_cafe_congestion.json")
        google_task = asyncio.to_thread(
            forecast_extra_customers,
            dataset_path,
            self.baseline
        )

        mta_task = asyncio.to_thread(
            run_mta_forecast
        )

        weather_out, google_out, mta_out = await asyncio.gather(
            weather_task,
            google_task,
            mta_task
        )

        # --- Normalize outputs ---
        signals = [
            normalize_weather_event(weather_out),
            normalize_google_traffic(google_out),
            normalize_mta(mta_out),
        ]

        # --- Combine conservatively ---
        combined = self.combine_signals(signals)

        return {
            "baseline_customers_per_hour": self.baseline,
            "signals": signals,
            "final_forecast": combined,
        }

    def combine_signals(self, signals):
        """
        Weighted average using confidence as weight.
        """
        weighted_sum = 0.0
        weight_total = 0.0
        explanations = []

        for s in signals:
            w = max(0.05, s["confidence"])
            weighted_sum += s["extra_customers_per_hour"] * w
            weight_total += w
            explanations.append(f"[{s['source']}] {s['explanation']}")

        extra_customers = weighted_sum / weight_total if weight_total > 0 else 0.0

        # Guardrails (single cafe)
        extra_customers = max(-0.5 * self.baseline, min(extra_customers, 1.5 * self.baseline))

        return {
            "expected_extra_customers_per_hour": round(extra_customers, 1),
            "expected_total_customers_per_hour": round(self.baseline + extra_customers, 1),
            "confidence": round(min(1.0, weight_total / len(signals)), 2),
            "summary": explanations[:5],
        }


# -----------------------------
# Demo / CLI
# -----------------------------

if __name__ == "__main__":
    agent = MasterFootTrafficAgent(baseline_customers_per_hour=42.0)

    result = asyncio.run(agent.run(time=18))  # 6 PM demo
    import json
    print(json.dumps(result, indent=2))

