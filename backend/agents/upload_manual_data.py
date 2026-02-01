import json
import os
import time
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "manual-foot-traffic-vectors"
path = "C:/Users/omran/code/BrownHacks2026/static_agent_training_data.json"

# 1. Check and Manage Index
existing_indexes = pc.list_indexes().names()

if index_name in existing_indexes:
    # Check if it was created with the wrong setup (e.g., manual vs integrated)
    index_description = pc.describe_index(index_name)
    
    # Optional: If you specifically need to ensure it's using the integrated model
    # and not an old manual index, we check for the 'embed' property.
    if not hasattr(index_description, 'embed'):
        print(f"Index {index_name} exists but isn't configured for integrated embeddings. Rebuilding...")
        pc.delete_index(index_name)
        time.sleep(5)
        existing_indexes = pc.list_indexes().names()

# 2. Create Index (if missing or deleted above)
if index_name not in existing_indexes:
    print(f"Creating integrated index: {index_name}")
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "embedding_text"}
        }
    )
    # Wait for index to be ready
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)

# 3. Process and Upsert Data
index = pc.Index(index_name)

with open(path) as f:
    data = json.load(f)

formatted_records = []
for i, row in enumerate(data):
    # Combine data into a single string for Pinecone to embed internally
    text_to_embed = (
        f"Borough: {row['borough']}, "
        f"Business: {row['business_type']}, "
        f"Weather: {row['weather_condition']}, "
        f"Traffic: {row['foot_traffic']}, "
        f"Events: {row['nearby_events']}, "
        f"Seaso n: {row['season']}, "
        f"Is Holiday: {row['is_holiday']}, "
        f"Temperature: {row['temperature']}, "
        f"Hour: {row['hour']}, "
    )

    # Pinecone metadata must be flat: each key's value must be string, number, boolean, or list of strings
    formatted_records.append({
        "_id": f"vec_{i}",
        "embedding_text": text_to_embed,
        "date": str(row["date"]),
        "borough": row["borough"],
        "foot_traffic": int(row["foot_traffic"]),
    })

# 4. Upsert the data
# Use upsert_records for integrated embedding indexes
index.upsert_records(namespace="traffic-data", records=formatted_records)

print(f"Successfully uploaded {len(formatted_records)} records to Pinecone.")