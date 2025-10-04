import folium

def draw_impact_zone(map_obj, lat, lon, radius_km):
    folium.Circle(
        location=[lat, lon],
        radius=radius_km * 1000,
        color="red",
        fill=True,
        fill_opacity=0.4,
        weight=2,
        tooltip="Strefa krateru"
    ).add_to(map_obj)

def draw_shockwave_zone(map_obj, lat, lon, radius_km):
    folium.Circle(
        location=[lat, lon],
        radius=radius_km * 1000,
        color="yellow",
        fill=True,
        fill_opacity=0.2,
        weight=2,
        tooltip="Fala uderzeniowa"
    ).add_to(map_obj)

def add_impact_marker(map_obj, lat, lon, name):
    folium.Marker(
        location=[lat, lon],
        popup=f"Uderzenie: {name}",
        icon=folium.Icon(color="red", icon="warning-sign")
    ).add_to(map_obj)

def add_shelters(map_obj, shelters_df):
    for _, row in shelters_df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color="green", icon="home")
        ).add_to(map_obj)

def add_user_location(map_obj, lat, lon):
    folium.Marker(
        location=[lat, lon],
        popup="Twoja lokalizacja",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(map_obj)

def add_evacuation_routes(map_obj, routes):
    for route in routes:
        folium.PolyLine(
            locations=route,
            color="blue",
            weight=4,
            opacity=0.8,
            tooltip="Trasa ewakuacji"
        ).add_to(map_obj)
