import os
import requests
import geocoder
from geopy.distance import geodesic

# =========================
# GET CURRENT LOCATION
# =========================
def get_current_location():
    try:
        g = geocoder.ip('me')

        if g.ok and g.latlng:
            lat, lng = g.latlng
            address = g.address or "Unknown Location"
            return lat, lng, address

    except Exception as e:
        print("Location error:", e)

    # Fallback (Delhi)
    return 28.6139, 77.2090, "New Delhi, India"


# =========================
# GET NEAREST POLICE
# =========================
def get_nearest_police_stations(lat, lng):
    api_key = os.getenv('GOOGLE_MAPS_API_KEY')

    # Fallback if no API
    if not api_key:
        return [
            {"name": "Emergency Helpline", "distance": "Call 112", "phone": "112"},
            {"name": "Police Control Room", "distance": "Call 100", "phone": "100"}
        ]

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

    params = {
        "location": f"{lat},{lng}",
        "radius": 5000,
        "keyword": "police",
        "key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if data.get("status") != "OK":
# sourcery skip: raise-specific-error
# sourcery skip: raise-specific-error
            raise Exception("Google API error")

        stations = []
        user_loc = (lat, lng)

        for place in data.get("results", [])[:3]:
            try:
                place_lat = place["geometry"]["location"]["lat"]
                place_lng = place["geometry"]["location"]["lng"]

                distance = geodesic(user_loc, (place_lat, place_lng)).km

                stations.append({
                    "name": place.get("name", "Police Station"),
                    "distance": f"{distance:.1f} km",
                    "phone": "112",  # Google API doesn't give phone here
                    "lat": place_lat,
                    "lng": place_lng
                })

            except Exception:
                continue

        return stations or [
                           {"name": "Emergency", "distance": "Call 112", "phone": "112"}
                       ]

    except Exception as e:
        print("Police API error:", e)

        return [
            {"name": "Emergency", "distance": "Call 112", "phone": "112"}
        ]