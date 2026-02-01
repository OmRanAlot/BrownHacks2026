import os
import json
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuration
PINECONE_INDEX = "manual-foot-traffic-vectors"
NAMESPACE = "traffic-data"

# 1. Initialize Clients
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(PINECONE_INDEX)
openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
gemini = os.getenv("GEMINI_API_KEY")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=gemini,
)


def predict_missing_metrics(target_ids):
    """
    Iterates through IDs that lack foot_traffic and predicts them.
    """
    for record_id in target_ids:
        # A. Fetch the 'Future' record details from Pinecone
        # We need the embedding_text to use as a query for the past
        target_record = index.fetch(ids=[record_id], namespace=NAMESPACE)
        record = target_record["vectors"].get(record_id)
        if not record:
            print(f"Record {record_id} not found, skipping.")
            continue
        # Records use flat fields; embedding_text may be in metadata or at top level
        meta = getattr(record, "metadata", None) or {}
        query_text = meta.get("embedding_text") if isinstance(meta, dict) else None
        query_text = query_text or getattr(record, "embedding_text", None)
        if not query_text:
            print(f"Record {record_id} has no embedding_text, skipping.")
            continue

        print(f"--- Predicting for {record_id} ---")
        print(f"Target Context: {query_text}")

        # B. RAG: Search for 3 HISTORICAL matches in the same index
        # Metadata filter ensures we only get records with ACTUAL foot_traffic
        search_results = index.search(
            namespace=NAMESPACE,
            query={
                "inputs": {"text": query_text},
                "top_k": 3,
                "filter": {"foot_traffic": {"$exists": True}},
            },
            fields=["embedding_text", "foot_traffic"],
        )

        # C. Format historical grounding for Gemini (new API: result.hits, each hit has .fields)
        historical_context = ""
        result = search_results.result
        hits = result.hits if hasattr(result, "hits") else []
        for hit in hits:
            fields = getattr(hit, "fields", None) or {}
            emb = fields.get("embedding_text", "")
            traffic = fields.get("foot_traffic", "?")
            historical_context += f"- Past Record: {emb} | ACTUAL TRAFFIC: {traffic}\n"

        # D. The Prediction Prompt
        prompt = f"""
        You are an NYC Foot Traffic AI. Predict traffic for the 'Target' based on 'History'.
        
        HISTORY:
        {historical_context if historical_context else "No direct history found. Use NYC logic."}
        
        TARGET EVENT:
        {query_text}

        Return ONLY a JSON object:
        {{
            "predicted_traffic": (number),
            "reasoning": (one sentence explaining why based on weather/event)
        }}
        """

        # E. Generate and Save
        response = client.chat.completions.create(
            model="google/gemini-3-flash-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        print(response.choices[0].message.content)
        exit()
# --- EXECUTION ---
# You can pass a list of IDs from your screenshot (e.g., ["event_896004"])
predict_missing_metrics(["event_896004"])

# {"predicted_traffic": 100, "reasoning": "The weather was sunny and the event was a concert."}