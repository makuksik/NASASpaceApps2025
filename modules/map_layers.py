import folium

def draw_impact_zone(map_object, lat, lng, radius_km):
    folium.Circle(
        radius=radius_km * 1000,
        location=[lat, lng],
        popup="Strefa uderzenia",
        color="red",
        fill=True,
        fill_opacity=0.4
    ).add_to(map_object)

def draw_shockwave_zone(map_object, lat, lng, radius_km):
    folium.Circle(
        radius=radius_km * 1000,
        location=[lat, lng],
        popup="Strefa fali uderzeniowej",
        color="orange",
        fill=True,
        fill_opacity=0.2
    ).add_to(map_object)

def add_impact_marker(map_object, lat, lng, asteroid_name):
    folium.Marker(
        location=[lat, lng],
        popup=f"Uderzenie asteroidy: {asteroid_name}",
        icon=folium.Icon(color="red", icon="asterisk")
    ).add_to(map_object)

def add_shelters(map_object, shelters_df):
    for _, row in shelters_df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color="green", icon="home")
        ).add_to(map_object)

def add_user_location(map_object, lat, lng):
    folium.Marker(
        location=[lat, lng],
        popup="Twoja lokalizacja",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(map_object)

def add_evacuation_routes(map_object, routes):
    for route in routes:
        folium.PolyLine(
            locations=route,
            color="purple",
            weight=3,
            opacity=0.7,
            popup="Trasa ewakuacyjna"
        ).add_to(map_object)
