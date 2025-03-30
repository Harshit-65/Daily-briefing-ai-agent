import os
import requests
from dotenv import load_dotenv

load_dotenv()

class TrafficService:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.base_url = "https://maps.googleapis.com/maps/api/directions/json"
    
    def get_traffic_info(self, origin, destination):
        """Get traffic information between two locations."""
        params = {
            "origin": origin,
            "destination": destination,
            "departure_time": "now",
            "alternatives": "true",
            "key": self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if data["status"] == "OK":
                # Extract relevant traffic information
                route = data["routes"][0]
                leg = route["legs"][0]
                
                duration = leg["duration"]["text"]
                duration_in_traffic = leg.get("duration_in_traffic", {}).get("text", "N/A")
                distance = leg["distance"]["text"]
                
                # Calculate traffic delay if available
                traffic_delay = ""
                if "duration_in_traffic" in leg:
                    normal_seconds = leg["duration"]["value"]
                    traffic_seconds = leg["duration_in_traffic"]["value"]
                    delay = traffic_seconds - normal_seconds
                    
                    if delay > 0:
                        delay_minutes = delay // 60
                        traffic_delay = f" (delay of {delay_minutes} minutes due to traffic)"
                
                return {
                    "distance": distance,
                    "duration": duration,
                    "duration_in_traffic": duration_in_traffic,
                    "traffic_delay": traffic_delay,
                    "start_address": leg["start_address"],
                    "end_address": leg["end_address"]
                }
            else:
                print(f"Error: {data['status']}")
                return None
        else:
            print(f"Error: {response.status_code}")
            return None
