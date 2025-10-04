from modules.utils import get_route_info
from modules.evacuation_planner import haversine

def ai_select_evacuation(user_location, shelters_df, impact_lat, impact_lng, shockwave_radius_km, time_to_impact_min):
    candidates = []

    for _, row in shelters_df.iterrows():
        shelter_coords = (row["lat"], row["lng"])
        distance_to_impact = haversine(shelter_coords, (impact_lat, impact_lng))
        distance_to_user = haversine((user_location["lat"], user_location["lng"]), shelter_coords)

        if distance_to_impact > shockwave_radius_km or distance_to_user < 0.2:
            try:
                routes = get_route_info((user_location["lat"], user_location["lng"]), shelter_coords)
            except:
                continue

            for r in routes:
                if r["duration_min"] < time_to_impact_min and r["duration_min"] < 999:
                    score = (distance_to_impact - shockwave_radius_km) * 2 - r["duration_min"]
                    candidates.append({
                        "name": row["name"],
                        "coords": shelter_coords,
                        "mode": r["label"],
                        "duration": r["duration_min"],
                        "distance": r["distance_km"],
                        "route": r["route"],
                        "score": score
                    })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    if candidates:
        return candidates[0]

    for _, row in shelters_df.iterrows():
        dist = haversine((user_location["lat"], user_location["lng"]), (row["lat"], row["lng"]))
        if dist < 0.2:
            return {
                "name": row["name"],
                "coords": (row["lat"], row["lng"]),
                "mode": "Pieszo",
                "duration": 0.1,
                "distance": dist,
                "route": [[user_location["lat"], user_location["lng"]], [row["lat"], row["lng"]]],
                "score": 999
            }

    return None
