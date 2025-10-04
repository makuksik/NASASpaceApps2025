import openrouteservice
import os
from dotenv import load_dotenv

load_dotenv()
ORS_API_KEY = os.getenv("ORS_API_KEY")
client = openrouteservice.Client(key=ORS_API_KEY)

def get_route_info(origin, destination):
    """
    Zwraca czasy przejścia pieszo, rowerem i samochodem oraz trasę.
    origin, destination: tuple (lat, lng)
    """
    profiles = {
        "foot-walking": "Pieszo",
        "cycling-regular": "Rowerem",
        "driving-car": "Samochodem"
    }

    results = []

    for profile, label in profiles.items():
        coords = [[origin[1], origin[0]], [destination[1], destination[0]]]  # ORS używa [lng, lat]
        try:
            route = client.directions(coordinates=coords, profile=profile, format='geojson')
            summary = route['features'][0]['properties']['summary']
            duration_sec = summary['duration']
            distance_m = summary['distance']
            points = route['features'][0]['geometry']['coordinates']
            formatted = [[lat, lng] for lng, lat in points]

            results.append({
                "label": label,
                "duration_min": round(duration_sec / 60, 1),
                "distance_km": round(distance_m / 1000, 2),
                "route": formatted
            })
        except Exception as e:
            print(f"Błąd dla profilu {label}:", e)

    return results
