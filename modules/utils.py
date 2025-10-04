# utils.py
import os
import openrouteservice
from dotenv import load_dotenv

# Ładowanie zmiennych środowiskowych tylko tutaj
load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")

# Tworzymy klienta ORS raz
client = openrouteservice.Client(key=ORS_API_KEY)

def get_route_info(start_coords, end_coords):
    """
    start_coords, end_coords: (lat, lng)
    """
    modes = {
        "Pieszo": "foot-walking",
        "Rowerem": "cycling-regular",
        "Samochodem": "driving-car"
    }

    routes = []
    coords = [[start_coords[1], start_coords[0]], [end_coords[1], end_coords[0]]]  # lon, lat

    for label, profile in modes.items():
        try:
            route = client.directions(coordinates=coords, profile=profile, format="geojson")
            summary = route["features"][0]["properties"]["summary"]
            points = route["features"][0]["geometry"]["coordinates"]
            route_coords = [[lat, lon] for lon, lat in points]

            routes.append({
                "label": label,
                "duration_min": round(summary["duration"] / 60, 1),
                "distance_km": round(summary["distance"] / 1000, 2),
                "route": route_coords
            })
        except Exception as e:
            print("Błąd ORS:", e)
            continue

    return routes
