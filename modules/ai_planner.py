import streamlit as st
from .utils import get_route_info
from .evacuation_planner import haversine

@st.cache_data
def ai_select_evacuation(user_location, shelters_df, impact_lat, impact_lng, shockwave_radius_km, time_to_impact_min, ors_api_key=None):
    """
    Wybiera najlepszą trasę ewakuacyjną na podstawie dystansu, czasu do uderzenia i promienia zagrożenia.

    user_location: dict - {'lat': float, 'lng': float}
    shelters_df: pd.DataFrame - schrony z kolumnami 'lat', 'lng', 'name'
    impact_lat, impact_lng: float - współrzędne uderzenia
    shockwave_radius_km: float - aktualny promień fali uderzeniowej
    time_to_impact_min: int - czas pozostały do uderzenia
    ors_api_key: str - klucz API do OpenRouteService
    """
    candidates = []

    # 🔹 wybierz 5 najbliższych schronów do użytkownika
    shelters_df["dist_to_user"] = shelters_df.apply(
        lambda row: haversine((user_location["lat"], user_location["lng"]), (row["lat"], row["lng"])),
        axis=1
    )
    nearest_shelters = shelters_df.nsmallest(3, "dist_to_user")

    for _, row in nearest_shelters.iterrows():
        shelter_coords = (row["lat"], row["lng"])
        distance_to_impact = haversine(shelter_coords, (impact_lat, impact_lng))

        # Sprawdzamy, czy schron jest poza strefą zagrożenia
        if distance_to_impact > shockwave_radius_km:
            try:
                # Pobieramy możliwe trasy z ORS (z cache)
                routes = get_route_info((user_location["lat"], user_location["lng"]), shelter_coords)
            except:
                continue

            for r in routes:
                # Sprawdzamy, czy czas trasy mieści się w pozostałym czasie
                if r["duration_min"] < time_to_impact_min and r["duration_min"] < 999:
                    # Wyliczamy scoring: im dalej od zagrożenia i szybciej tym lepiej
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

    # Sortujemy po score i zwracamy najlepszą opcję
    candidates.sort(key=lambda x: x["score"], reverse=True)
    if candidates:
        return candidates[0]

    # Fallback: najbliższy schron bez trasy ORS
    if not nearest_shelters.empty:
        nearest = nearest_shelters.iloc[0]
        min_dist = nearest["dist_to_user"]

        return {
            "name": nearest["name"],
            "coords": (nearest["lat"], nearest["lng"]),
            "mode": "On foot" if min_dist < 0.5 else "By car",
            "duration": min_dist * 12 if min_dist < 0.5 else min_dist * 2,
            "distance": min_dist,
            "route": [
                [user_location["lat"], user_location["lng"]],
                [nearest["lat"], nearest["lng"]]
            ],
            "score": 0
        }

    return None
