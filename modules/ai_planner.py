from .utils import get_route_info
from .evacuation_planner import haversine

def ai_select_evacuation(user_location, shelters_df, impact_lat, impact_lng, shockwave_radius_km, time_to_impact_min):
    """
    Wybiera najlepszą trasę ewakuacyjną na podstawie dystansu, czasu do uderzenia i promienia zagrożenia.

    user_location: dict - {'lat': float, 'lng': float}
    shelters_df: pd.DataFrame - schrony z kolumnami 'lat', 'lng', 'name'
    impact_lat, impact_lng: float - współrzędne uderzenia
    shockwave_radius_km: float - aktualny promień fali uderzeniowej
    time_to_impact_min: int - czas pozostały do uderzenia
    """
    candidates = []

    for _, row in shelters_df.iterrows():
        shelter_coords = (row["lat"], row["lng"])
        distance_to_impact = haversine(shelter_coords, (impact_lat, impact_lng))
        distance_to_user = haversine((user_location["lat"], user_location["lng"]), shelter_coords)

        # Sprawdzamy, czy schron jest poza strefą zagrożenia
        if distance_to_impact > shockwave_radius_km:
            try:
                # Pobieramy możliwe trasy
                routes = get_route_info((user_location["lat"], user_location["lng"]), shelter_coords)
            except:
                continue

            for r in routes:
                # Sprawdzamy, czy czas trasy mieści się w pozostałym czasie
                if r["duration_min"] < time_to_impact_min and r["duration_min"] < 999:
                    # Wyliczamy prosty scoring: odległość od zagrożenia + czas trasy
                    score = (distance_to_impact - shockwave_radius_km) * 2 - r["duration_min"]
                    candidates.append({
                        "name": row["name"],
                        "coords": shelter_coords,
                        "mode": r["label"],  # pieszo, rowerem, samochodem
                        "duration": r["duration_min"],
                        "distance": r["distance_km"],
                        "route": r["route"],
                        "score": score
                    })

    # Sortujemy po score i zwracamy najlepszą opcję
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if candidates:
        return candidates[0]

    # Jeśli żaden schron poza zagrożeniem nie jest dostępny, szukamy najbliższego
    min_dist = float("inf")
    nearest_shelter = None
    for _, row in shelters_df.iterrows():
        dist = haversine((user_location["lat"], user_location["lng"]), (row["lat"], row["lng"]))
        if dist < min_dist:
            min_dist = dist
            nearest_shelter = row

    if nearest_shelter is not None:
        return {
            "name": nearest_shelter["name"],
            "coords": (nearest_shelter["lat"], nearest_shelter["lng"]),
            "mode": "On foot" if min_dist < 0.5 else "By car",
            "duration": min_dist * 12 if min_dist < 0.5 else min_dist * 2,  # przybliżone czasy w min
            "distance": min_dist,
            "route": [
                [user_location["lat"], user_location["lng"]],
                [nearest_shelter["lat"], nearest_shelter["lng"]]
            ],
            "score": 0
        }

    return None
