import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.utils import get_route_info
from modules.ai_planner import ai_select_evacuation

# Inicjalizacja bazy asteroid
db = AsteroidDatabase()

# --- Sidebar: Ustawienia zagrożenia ---
st.sidebar.header("⚠️ Symulacja uderzenia")

asteroid_names = [a.name for a in db.asteroids]
wybrana_asteroida_name = st.sidebar.selectbox("Wybierz asteroidę", asteroid_names)

# Lokalizacja użytkownika
st.sidebar.header("📍 Twoja lokalizacja")
user_lat = st.sidebar.number_input("Szerokość geograficzna użytkownika", value=52.2297)
user_lon = st.sidebar.number_input("Długość geograficzna użytkownika", value=21.0122)
user_location = {"lat": user_lat, "lng": user_lon}

# Lokalizacja uderzenia asteroidy
st.sidebar.header("🌋 Lokalizacja uderzenia")
impact_lat = st.sidebar.number_input("Szerokość geograficzna uderzenia", value=52.2550)
impact_lon = st.sidebar.number_input("Długość geograficzna uderzenia", value=21.0400)

# Suwak: ile minut zostało do uderzenia
time_to_impact_min = st.sidebar.slider("⏱️ Minuty do uderzenia", min_value=0, max_value=60, value=15, step=1)

# Suwak: ile minut minęło od uderzenia
time_after_impact_min = st.sidebar.slider("🌪️ Minuty po uderzeniu", min_value=0, max_value=300, value=0, step=1)

# --- Dane asteroid i uderzenia ---
asteroid = next(a for a in db.asteroids if a.name == wybrana_asteroida_name)
impact_details = db.calculate_impact_for_location(asteroid, impact_lat, impact_lon)

max_shockwave_radius = impact_details["destruction_zones"]["shockwave_radius_km"]
shockwave_speed_km_per_min = max_shockwave_radius / 300

# 🔁 Fala uderzeniowa rośnie przed i po uderzeniu
if time_to_impact_min > 0:
    current_shockwave_radius = min(max_shockwave_radius, shockwave_speed_km_per_min * (60 - time_to_impact_min))
else:
    current_shockwave_radius = min(max_shockwave_radius, shockwave_speed_km_per_min * time_after_impact_min)

asteroid_data = {
    "name": impact_details["asteroid_name"],
    "impact_lat": impact_lat,
    "impact_lng": impact_lon,
    "impact_radius_km": impact_details["destruction_zones"]["crater_km"],
    "shockwave_radius_km": current_shockwave_radius,
    "severity": impact_details["threat_level"]
}

# --- Dane schronów ---
try:
    shelters_df = pd.read_csv("data/schrony.csv")
except:
    shelters_df = pd.DataFrame([
        {"name": "Schron Warszawa Centrum", "lat": 52.2300, "lng": 21.0100},
        {"name": "Schron Praga", "lat": 52.2550, "lng": 21.0400},
        {"name": "Schron Mokotów", "lat": 52.2000, "lng": 21.0200},
    ])

# --- AI wybiera trasę ewakuacyjną ---
ai_decision = ai_select_evacuation(user_location, shelters_df,
                                    impact_lat,
                                    impact_lon,
                                    current_shockwave_radius,
                                    time_to_impact_min)

if ai_decision:
    st.sidebar.success(f"🧠 AI wybrało: {ai_decision['name']} ({ai_decision['mode']}, {ai_decision['duration']} min)")
    evacuation_routes = [ai_decision["route"]]
else:
    st.sidebar.error("❌ AI nie znalazło bezpiecznej trasy w czasie!")
    evacuation_routes = None

# --- Wyświetlanie ---
st.title("🌍 Symulacja uderzenia asteroidy")

if time_to_impact_min > 0:
    st.warning(f"☄️ Uderzenie nastąpi za {time_to_impact_min} minut.")
else:
    st.error(f"💥 Uderzenie nastąpiło {time_after_impact_min} minut temu.")

st.write(f"**Promień fali uderzeniowej:** {current_shockwave_radius:.2f} km")

st.subheader(f"☄️ Asteroida: {asteroid_data['name']}")
st.write(f"**Stopień zagrożenia:** {asteroid_data['severity']}")
st.write(f"**Energia uderzenia:** {impact_details['energy_megatons']} Mt TNT")
st.write(f"**Porównanie historyczne:** {impact_details['historical_comparison']}")
st.write(f"**Obszar zniszczeń:** {impact_details['total_affected_area_km2']:,} km²")

map_object = render_map(asteroid_data, shelters_df, user_location, evacuation_routes)
st_folium(map_object, width=700, height=500)

# Szczegóły trasy
with st.expander("📋 Szczegóły ewakuacji"):
    if ai_decision:
        st.subheader(f"🏠 {ai_decision['name']}")
        st.write(f"➡️ {ai_decision['mode']}: {ai_decision['duration']} min ({ai_decision['distance']} km)")
    else:
        st.warning("Brak dostępnej trasy ewakuacyjnej.")
