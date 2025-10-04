import folium
import pandas as pd
from .map_layers import (
    add_zones,
    add_impact_marker,
    add_shelters,
    add_medical_points,
    add_user_location,
    add_evacuation_routes,
    add_aed_locations, add_water_points  # ⬅️ dodane
)

def render_map(
    asteroid_data: dict,
    shelters_df: pd.DataFrame,
    aed_df: pd.DataFrame,
    medical_points_df: pd.DataFrame,
    water_points_df: pd.DataFrame,  # ⬅️ dodane
    user_location=None,
    evacuation_routes=None
):

    """
    Renderuje mapę zagrożenia asteroidą z wszystkimi strefami, markerami i trasami ewakuacyjnymi.

    asteroid_data: dict - wynik calculate_impact_for_location z zagrozenie.py
    shelters_df: pd.DataFrame - lista schronów z kolumnami lat/lng/name
    aed_df: pd.DataFrame - lista AED z kolumnami lat/lng/name/info
    user_location: dict - {'lat': float, 'lng': float}
    evacuation_routes: list - lista tras ewakuacyjnych (każda trasa to lista [lat, lng])
    """
    lat = asteroid_data["impact_coordinates"]["lat"]
    lng = asteroid_data["impact_coordinates"]["lon"]

    m = folium.Map(location=[lat, lng], zoom_start=10)

    # Strefy zagrożenia
    add_zones(m, asteroid_data.get("circles_coordinates", {}))

    # Miejsce uderzenia
    add_impact_marker(m, lat, lng, asteroid_data["asteroid_name"])

    # Schrony
    add_shelters(m, shelters_df)

    # AED
    add_aed_locations(m, aed_df)  # ⬅️ dodane

    add_medical_points(m, medical_points_df)

    add_water_points(m, water_points_df)

    # Lokalizacja użytkownika
    if user_location:
        add_user_location(m, user_location["lat"], user_location["lng"])

    # Trasy ewakuacyjne
    if evacuation_routes:
        add_evacuation_routes(m, evacuation_routes)

    return m
