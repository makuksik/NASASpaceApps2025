import openrouteservice

client = openrouteservice.Client(key="YOUR_ORS_API_KEY")

def get_route_info(start_coords, end_coords):
    modes = {
        "Pieszo": "foot-walking",
        "Rowerem": "cycling-regular",
        "Samochodem": "driving-car"
    }

    routes = []
    for label, profile in modes.items():
        try:
            route = client.directions(
                coordinates=[start_coords, end_coords],
                profile=profile,
                format="geojson"
            )
            geometry = route["features"][0]["geometry"]
            summary = route["features"][0]["properties"]["summary"]

            route_coords = [[lat, lon] for lon, lat in geometry["coordinates"]]

            routes.append({
                "label": label,
                "duration_min": round(summary["duration"] / 60, 1),
                "distance_km": round(summary["distance"] / 1000, 2),
                "route": route_coords
            })
        except Exception:
            continue

    return routes
