import json
import random
from datetime import datetime, timedelta

def generate_nuanced_data(num_entries=50):
    # Contextual variables specific to 1.5 miles of Lincoln Center
    weather_types = ["Clear", "Cloudy", "Rainy", "Snowy", "Frigid/Windy"]
    events_pool = [
        "NY Philharmonic: David Geffen Hall (7:30 PM)",
        "Met Opera: I Puritani (7:00 PM)",
        "Broadway: Ragtime at Vivian Beaumont",
        "Juilliard School Masterclass",
        "Farmers Market at Richard Tucker Square",
        "Lincoln Center Matinee (2:00 PM)",
        "None"
    ]
    
    data = []
    # Start on New Year's Day 2026 (confirmed snow squall in NYC records)
    start_date = datetime(2026, 1, 1, 8, 0) 

    for i in range(num_entries):
        current_date = start_date + timedelta(hours=i * 4) # Spread over ~8 days
        hour = current_date.hour
        day = current_date.strftime("%A")
        
        # Determine Nuance: Weather/Season
        weather = random.choice(weather_types)
        temp = random.randint(15, 38) # NYC Jan 2026 was historically cold
        
        # Determine Nuance: Events
        # Logic: Events mostly happen in evening or weekend afternoons
        if (18 <= hour <= 20) or (day in ["Saturday", "Sunday"] and 13 <= hour <= 15):
            event = random.choice(events_pool[:-1])
        else:
            event = "None"

        # Logic: Foot Traffic Calculation
        base_traffic = 150 # Quiet baseline
        
        # Time Multipliers
        if 8 <= hour <= 10: base_traffic *= 4.5 # Morning caffeine rush
        elif 12 <= hour <= 14: base_traffic *= 3.0 # Lunch
        elif 18 <= hour <= 20: base_traffic *= 5.0 # Pre-theater peak
        
        # Weather & Event Nuance
        if event != "None": base_traffic += 400
        if weather in ["Rainy", "Snowy", "Frigid/Windy"]:
            # Paradox: Bad weather often INCREASES cafe traffic near theaters 
            # as people seek shelter before doors open.
            base_traffic *= 1.2 
        
        entry = {
            "date": current_date.strftime("%Y-%m-%d %H:%M"),
            "day_of_week": day,
            "hour": hour,
            "weather_condition": weather,
            "temperature": temp,
            "borough": "Manhattan",
            "nearby_events": event,
            "business_type": "cafe",
            "season": "Winter",
            "is_holiday": current_date.day == 1, # Jan 1
            "foot_traffic": int(base_traffic + random.randint(-50, 50))
        }
        data.append(entry)

    return data

# Generate and Save
final_data = generate_nuanced_data(50)
with open("aroma_cafe_training_data.json", "w") as f:
    json.dump(final_data, f, indent=4)

print("Generated 50 realistic entries for Lincoln Center area.")