import folium
from modules.map_layers import (
    draw_impact_zone,
    draw_shockwave_zone,
    add_impact_marker,
    add_shelters,
    add_user_location,
    add_evacuation_routes
)

def render_map(asteroid_data, shelters_df, user_location, evacuation_routes=None):
    m = folium.Map(location=[asteroid_data["impact_lat"], asteroid_data["impact_lng"]], zoom_start=12)

    # 🔴 Krater
    draw_impact_zone(m, asteroid_data["impact_lat"], asteroid_data["impact_lng"], asteroid_data["impact_radius_km"])

    # 🟡 Fala uderzeniowa
    try:
        radius = float(asteroid_data["shockwave_radius_km"])
        if radius > 0:
            draw_shockwave_zone(m, asteroid_data["impact_lat"], asteroid_data["impact_lng"], radius)
    except:
        pass

    # 📍 Marker uderzenia
    add_impact_marker(m, asteroid_data["impact_lat"], asteroid_data["impact_lng"], asteroid_data["name"])

    # 🏠 Schrony
    add_shelters(m, shelters_df)

    # 👤 Lokalizacja użytkownika
    add_user_location(m, user_location["lat"], user_location["lng"])

    # 🔵 Trasa ewakuacyjna
    if evacuation_routes:
        add_evacuation_routes(m, evacuation_routes)

    return m
