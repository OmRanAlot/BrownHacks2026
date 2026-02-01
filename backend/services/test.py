import requests
import json
import time
import os
import dotenv

# --- CONFIGURATION ---
dotenv.load_dotenv()
API_KEY = os.getenv("TOMTOM_API_KEY")
OUTPUT_FILE = "detailed_cafe_congestion.json"

poi_list = [
    # --- IMMEDIATE AREA (Within 0.2 miles) ---
    {"name": "Cafe Aroma", "lat": 40.7709, "lon": -73.9818, "weight": 1.0},
    {"name": "Lincoln Center / W 64th St", "lat": 40.7725, "lon": -73.9835, "weight": 0.9},
    {"name": "Columbus Circle / 8th Ave", "lat": 40.7681, "lon": -73.9819, "weight": 0.95},

    # --- MID-RANGE FEEDERS (0.5 - 0.8 miles) ---
    {"name": "Apple Store Upper West Side", "lat": 40.7744, "lon": -73.9821, "weight": 0.7},
    {"name": "W 72nd St Subway Hub", "lat": 40.7788, "lon": -73.9823, "weight": 0.8},
    {"name": "Museum of Natural History", "lat": 40.7813, "lon": -73.9740, "weight": 0.6},
    {"name": "Central Park South / 7th Ave", "lat": 40.7659, "lon": -73.9790, "weight": 0.75},

    # --- MAJOR INFLOW HUBS (1.0 - 1.5 miles) ---
    {"name": "Times Square / Broadway", "lat": 40.7580, "lon": -73.9855, "weight": 0.85},
    {"name": "Port Authority Bus Terminal", "lat": 40.7568, "lon": -73.9910, "weight": 0.9},
    {"name": "West Side Highway at 57th St", "lat": 40.7720, "lon": -73.9930, "weight": 0.5},
    {"name": "Rockefeller Center", "lat": 40.7587, "lon": -73.9787, "weight": 0.7}
]

def get_detailed_flow(lat, lon):
    # Note: absolute/10 refers to the zoom level for road segment detail
    url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json"
    params = {
        "key": API_KEY,
        "point": f"{lat},{lon}",
        "unit": "mph",
        "thickness": 10
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
    return None

def main():
    final_dataset = {
        "metadata": {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "target_location": "1873 Broadway, NY",
            "hack_context": "BrownHacks2026_Predictive_Model"
        },
        "points_of_interest": []
    }

    for poi in poi_list:
        print(f"🚦 Requesting: {poi['name']}...")
        raw_data = get_detailed_flow(poi["lat"], poi["lon"])
        
        if raw_data and "flowSegmentData" in raw_data:
            print(f"   ✅ flowSegmentData found! Speed: {raw_data['flowSegmentData']['currentSpeed']} mph")
            entry = {
                "poi_name": poi["name"],
                "input_coordinates": {"lat": poi["lat"], "lon": poi["lon"]},
                "traffic_data": raw_data["flowSegmentData"]
            }
            final_dataset["points_of_interest"].append(entry)
        else:
            print(f"   ❌ No segment data found for {poi['name']}.")
        
        time.sleep(0.5) # Avoid rate limits during the hackathon

    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_dataset, f, indent=4)
    
    print(f"\n🚀 Done! {len(final_dataset['points_of_interest'])} points captured in {OUTPUT_FILE}")

if __name__ == "__main__":
    main()