import folium
import pandas as pd

def add_zones(map_object, circles_coordinates: dict):
    for zone_name, coords in circles_coordinates.items():
        if not coords:
            continue
        if "crater" in zone_name or "destruction" in zone_name or "severe" in zone_name:
            color = "red"
            fill_opacity = 0.3
        elif "moderate" in zone_name:
            color = "orange"
            fill_opacity = 0.2
        elif "light" in zone_name:
            color = "yellow"
            fill_opacity = 0.1
        elif "shockwave" in zone_name:
            color = "blue"
            fill_opacity = 0.05
        else:
            color = "gray"
            fill_opacity = 0.1

        folium.Polygon(
            locations=coords,
            color=color,
            fill=True,
            fill_opacity=fill_opacity,
            popup=zone_name.replace("_", " ").capitalize()
        ).add_to(map_object)

def add_impact_marker(map_object, lat, lng, asteroid_name):
    folium.Marker(
        location=[lat, lng],
        popup=f"Uderzenie asteroidy: {asteroid_name}",
        icon=folium.Icon(color="red", icon="asterisk")
    ).add_to(map_object)

def add_shelters(map_object, shelters_df: pd.DataFrame):
    for _, row in shelters_df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color="green", icon="home")
        ).add_to(map_object)

def add_aed_locations(map_object, aed_df: pd.DataFrame):
    for _, row in aed_df.iterrows():
        if not all(k in row for k in ["lat", "lng", "name", "info"]):
            continue

        info_lower = row["info"].lower()
        if "respirator" in info_lower:
            icon_color = "darkred"
            icon_type = "plus"
        else:
            icon_color = "orange"
            icon_type = "medkit"

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=f"{row['name']}<br>{row['info']}",
            icon=folium.Icon(color=icon_color, icon=icon_type, prefix="fa")
        ).add_to(map_object)

def add_medical_points(map_object, medical_points_df: pd.DataFrame):
    for _, row in medical_points_df.iterrows():
        if not all(k in row for k in ["lat", "lng", "name", "type"]):
            continue

        point_type = row["type"].lower()
        if point_type == "hospital":
            icon_color = "red"
            icon_type = "plus"
        elif point_type == "clinic":
            icon_color = "green"
            icon_type = "stethoscope"
        elif point_type == "emergency":
            icon_color = "orange"
            icon_type = "exclamation-triangle"
        else:
            icon_color = "gray"
            icon_type = "question"

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color=icon_color, icon=icon_type, prefix="fa")
        ).add_to(map_object)

def add_user_location(map_object, lat, lng):
    folium.Marker(
        location=[lat, lng],
        popup="Twoja lokalizacja",
        icon=folium.Icon(color="blue", icon="user")
    ).add_to(map_object)

def add_evacuation_routes(map_object, routes: list):
    for route in routes:
        folium.PolyLine(
            locations=route,
            color="purple",
            weight=3,
            opacity=0.7,
            popup="Trasa ewakuacyjna"
        ).add_to(map_object)

def add_medical_points(map_object, medical_points_df: pd.DataFrame):
    for _, row in medical_points_df.iterrows():
        if not all(k in row for k in ["lat", "lng", "name", "type"]):
            continue

        point_type = row["type"].lower()
        if point_type == "hospital":
            icon_color = "red"
            icon_type = "plus"
        elif point_type == "clinic":
            icon_color = "green"
            icon_type = "stethoscope"
        elif point_type == "emergency":
            icon_color = "orange"
            icon_type = "exclamation-triangle"
        else:
            icon_color = "gray"
            icon_type = "question"

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color=icon_color, icon=icon_type, prefix="fa")
        ).add_to(map_object)


def add_water_points(map_object, water_points_df: pd.DataFrame):
    for _, row in water_points_df.iterrows():
        if not all(k in row for k in ["lat", "lng", "name"]):
            continue

        folium.Marker(
            location=[row["lat"], row["lng"]],
            popup=row["name"],
            icon=folium.Icon(color="blue", icon="tint", prefix="fa")
        ).add_to(map_object)
