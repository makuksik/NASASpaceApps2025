import openrouteservice
import requests

def get_client(api_key: str):
    """
    Tworzy klienta ORS na podstawie przekazanego klucza.
    """
    return openrouteservice.Client(key=api_key)

def get_route_info(client, start_coords, end_coords):
    """
    Zwraca trasy piesze, rowerowe i samochodowe między dwoma punktami.
    start_coords, end_coords: (lat, lng)
    """
    modes = {
        "On foot": "foot-walking",
        "By bike": "cycling-regular",
        "By car": "driving-car"
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

def get_realistic_route(start: dict, end: dict, ors_api_key: str):
    """
    Pobiera trasę samochodową z ORS jako listę punktów [lat, lng].
    """
    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {"Authorization": ors_api_key}
    body = {
        "coordinates": [
            [start["lng"], start["lat"]],
            [end["lng"], end["lat"]]
        ]
    }

    response = requests.post(url, json=body, headers=headers)
    if response.status_code != 200:
        raise Exception(f"ORS error: {response.status_code} {response.text}")

    data = response.json()
    geometry = data["features"][0]["geometry"]["coordinates"]
    return [[lat, lng] for lng, lat in geometry]
