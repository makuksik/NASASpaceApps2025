import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.utils import get_route_info

# Inicjalizacja bazy asteroid
db = AsteroidDatabase()

# --- Sidebar ---
st.sidebar.header("⚠️ Ustawienia zagrożenia")

# Wybór asteroidy
asteroid_names = [a.name for a in db.asteroids]
wybrana_asteroida_name = st.sidebar.selectbox("Wybierz asteroidę", asteroid_names)

# Lokalizacja użytkownika
user_lat = st.sidebar.number_input("Twoja szerokość geograficzna", value=52.2297)
user_lon = st.sidebar.number_input("Twoja długość geograficzna", value=21.0122)
user_location = {"lat": user_lat, "lng": user_lon}

# Wczytaj dane asteroid
asteroid = next(a for a in db.asteroids if a.name == wybrana_asteroida_name)
impact_details = db.calculate_impact_for_location(asteroid, user_lat, user_lon)

asteroid_data = {
    "name": impact_details["asteroid_name"],
    "impact_lat": impact_details["impact_coordinates"]["lat"],
    "impact_lng": impact_details["impact_coordinates"]["lon"],
    "impact_radius_km": impact_details["destruction_zones"]["crater_km"],
    "shockwave_radius_km": impact_details["destruction_zones"]["shockwave_radius_km"],
    "severity": impact_details["threat_level"]
}

# --- Dane schronów ---
try:
    shelters_df = pd.read_csv("data/schrony.csv")  # kolumny: name, lat, lng
except:
    shelters_df = pd.DataFrame([
        {"name": "Schron Warszawa Centrum", "lat": 52.2300, "lng": 21.0100},
        {"name": "Schron Praga", "lat": 52.2550, "lng": 21.0400},
        {"name": "Schron Mokotów", "lat": 52.2000, "lng": 21.0200},
    ])

# --- Sidebar wybór schronu i transportu ---
st.sidebar.header("🧭 Ewakuacja")
selected_shelter_name = st.sidebar.selectbox("Wybierz schron:", shelters_df["name"].tolist())
selected_mode_label = st.sidebar.radio("Tryb transportu:", ["Pieszo", "Rowerem", "Samochodem"])

# Pobierz dane schronu
selected_shelter = shelters_df[shelters_df["name"] == selected_shelter_name].iloc[0]
shelter_coords = (selected_shelter["lat"], selected_shelter["lng"])

# Klucz sesji (cache trasy)
session_key = f"{selected_shelter_name}_{selected_mode_label}"
if session_key not in st.session_state:
    st.session_state[session_key] = get_route_info((user_lat, user_lon), shelter_coords)

# Wybór trasy
route_info = st.session_state[session_key]
selected_route_data = next((r for r in route_info if r["label"] == selected_mode_label), None)
evacuation_routes = [selected_route_data["route"]] if selected_route_data else None

# --- Wyświetlanie ---
st.title("🌍 Symulacja uderzenia asteroidy")

# Szczegóły asteroidy
st.subheader(f"☄️ Asteroida: {asteroid_data['name']}")
st.write(f"**Stopień zagrożenia:** {asteroid_data['severity']}")
st.write(f"**Energia uderzenia:** {impact_details['energy_megatons']} Mt TNT")
st.write(f"**Porównanie historyczne:** {impact_details['historical_comparison']}")
st.write(f"**Obszar zniszczeń:** {impact_details['total_affected_area_km2']:,} km²")

# Render mapy
map_object = render_map(asteroid_data, shelters_df, user_location, evacuation_routes)
st_folium(map_object, width=700, height=500)

# Szczegóły trasy
with st.expander("📋 Szczegóły ewakuacji"):
    st.subheader(f"🏠 {selected_shelter_name}")
    if selected_route_data:
        st.write(f"➡️ {selected_mode_label}: {selected_route_data['duration_min']} min ({selected_route_data['distance_km']} km)")
    else:
        st.warning("Brak danych dla wybranego trybu.")
