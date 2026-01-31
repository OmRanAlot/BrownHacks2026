import requests
import os
import json
from dotenv import load_dotenv

# 1. Setup your information
API_KEY = os.getenv('GOOGLE_API_KEY')
LOCATION = '45.523062,-122.676482' # Latitude and Longitude (this is Portland, OR)
RADIUS = '1500' # Distance in meters
PLACE_TYPE = 'restaurant' # What kind of places you want

# 2. Build the URL (The "Address" we are asking for data from)
url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={LOCATION}&radius={RADIUS}&type={PLACE_TYPE}&key={API_KEY}"

# 3. Make the request
response = requests.get(url)

# 4. Print the results to the console for testing
if response.status_code == 200:
    data = response.json()
    
    # This takes the data and makes it look "pretty" with indenting
    # otherwise, it would be one giant block of text that's hard to read
    pretty_data = json.dumps(data, indent=4)
    
    print(pretty_data)
else:
    print(f"Failed! Status Code: {response.status_code}")
    print(response.text) # This will tell you WHY it failed (like an invalid key)