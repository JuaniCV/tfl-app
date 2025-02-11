from fastapi import FastAPI
import requests

# TfL API Base URL
BASE_URL = "https://api.tfl.gov.uk"

# Optional: Add your App ID and Key if required
APP_ID = "xxx"
APP_KEY = "xxx"

app = FastAPI()

def search_stop_point(query):
    """Search for a StopPoint ID by name."""
    url = f"{BASE_URL}/StopPoint/Search/{query}"
    params = {"app_id": APP_ID, "app_key": APP_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if not data["matches"]:
            return {"error": "No stops found"}
        
        return [{"name": match["name"], "id": match["id"]} for match in data["matches"]]
    else:
        return {"error": f"API error {response.status_code}"}

@app.get("/search/{query}")
def get_stop_id(query: str):
    return search_stop_point(query)

@app.get("/bus/{stop_id}")
def get_bus_arrivals(stop_id: str):
    """Fetches live bus arrivals for a given stop ID."""
    url = f"{BASE_URL}/StopPoint/{stop_id}/Arrivals"
    params = {"app_id": APP_ID, "app_key": APP_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return sorted(
            [{"line": bus["lineId"], "destination": bus["destinationName"], "arrival_mins": bus["timeToStation"] // 60} 
             for bus in data],
            key=lambda x: x["arrival_mins"]
        )
    else:
        return {"error": f"API error {response.status_code}"}

@app.get("/line_status")
def get_line_status():
    """Fetches the status of all London Underground lines."""
    url = f"{BASE_URL}/Line/Mode/tube/Status"
    params = {"app_id": APP_ID, "app_key": APP_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return {line['name']: line['lineStatuses'][0]['statusSeverityDescription'] for line in data}
    else:
        return {"error": f"API error {response.status_code}"}

@app.get("/journey/{origin}/{destination}")
def get_journey(origin: str, destination: str):
    """Fetches journey planner information between two locations."""
    url = f"{BASE_URL}/Journey/JourneyResults/{origin}/to/{destination}"
    params = {"app_id": APP_ID, "app_key": APP_KEY}
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        journeys = data.get("journeys", [])
        return [
            {
                "journey": i + 1,
                "duration_mins": journey["duration"],
                "steps": [leg["instruction"]["summary"] for leg in journey["legs"]]
            }
            for i, journey in enumerate(journeys[:3])
        ]
    else:
        return {"error": f"API error {response.status_code}"}
