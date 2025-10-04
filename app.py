import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.utils import get_route_info
from modules.ai_planner import ai_select_evacuation

# -----------------------------
# Inicjalizacja bazy asteroid
# -----------------------------
db = AsteroidDatabase()

# --- Sidebar: Wybór asteroidy ---
st.sidebar.header("⚠️ Symulacja uderzenia")
asteroid_names = [a.name for a in db.asteroids]
wybrana_asteroida_name = st.sidebar.selectbox("Wybierz asteroidę", asteroid_names)

# --- Lokalizacja użytkownika ---
st.sidebar.header("📍 Twoja lokalizacja")
user_lat = st.sidebar.number_input("Szerokość geograficzna użytkownika", value=52.2297)
user_lon = st.sidebar.number_input("Długość geograficzna użytkownika", value=21.0122)
user_location = {"lat": user_lat, "lng": user_lon}

# --- Lokalizacja uderzenia asteroidy ---
st.sidebar.header("🌋 Lokalizacja uderzenia")
impact_lat = st.sidebar.number_input("Szerokość geograficzna uderzenia", value=52.2550)
impact_lon = st.sidebar.number_input("Długość geograficzna uderzenia", value=21.0400)

# --- Suwaki czasowe ---
time_to_impact_min = st.sidebar.slider("⏱️ Minuty do uderzenia", 0, 60, 15)
time_after_impact_min = st.sidebar.slider("🌪️ Minuty po uderzeniu", 0, 300, 0)

# --- Dane asteroid i uderzenia ---
wybrana_asteroida = next(a for a in db.asteroids if a.name == wybrana_asteroida_name)
impact_details = db.calculate_impact_for_location(wybrana_asteroida, impact_lat, impact_lon)

max_shockwave_radius = impact_details["destruction_zones"]["shockwave_radius_km"]
shockwave_speed_km_per_min = max_shockwave_radius / 300

# 🔁 Obliczenie aktualnego promienia fali uderzeniowej
if time_to_impact_min > 0:
    current_shockwave_radius = min(max_shockwave_radius, shockwave_speed_km_per_min * (60 - time_to_impact_min))
else:
    current_shockwave_radius = min(max_shockwave_radius, shockwave_speed_km_per_min * time_after_impact_min)

# --- Przygotowanie danych do render_map ---
asteroid_data = {
    "asteroid_name": impact_details["asteroid_name"],
    "impact_coordinates": {"lat": impact_lat, "lon": impact_lon},
    "circles_coordinates": impact_details.get("circles_coordinates", {}),
    "destruction_zones": impact_details.get("destruction_zones", {}),
    "threat_level": impact_details.get("threat_level", "nieznany"),
    "energy_megatons": impact_details.get("energy_megatons", 0),
    "historical_comparison": impact_details.get("historical_comparison", ""),
    "total_affected_area_km2": impact_details.get("total_affected_area_km2", 0),
    "trajectory": impact_details.get("trajectory", ""),
    "impact_probability": impact_details.get("impact_probability", 0.0),
    "shockwave_radius_km": current_shockwave_radius
}

# -----------------------------
# Dane schronów
# -----------------------------
shelters_df = pd.DataFrame([
    {"name": "Schron Alfa (ul. Kozielska 4)", "lat": 52.2785, "lng": 20.9812},
    {"name": "Schron Huta Warszawa (Młociny)", "lat": 52.2921, "lng": 20.9357},
    {"name": "Schron Bielany (osiedlowy)", "lat": 52.2840, "lng": 20.9560},
    {"name": "Schron Wola (podziemia biurowca)", "lat": 52.2350, "lng": 20.9800},
    {"name": "Schron Mokotów (garaż podziemny)", "lat": 52.2000, "lng": 21.0200},
    {"name": "Schron Ursynów (garaż podziemny)", "lat": 52.1500, "lng": 21.0500},
    {"name": "Schron Praga Północ (piwnica szkoły)", "lat": 52.2580, "lng": 21.0400},
    {"name": "Schron Żerań (zakład przemysłowy)", "lat": 52.2950, "lng": 21.0200},
    {"name": "Schron Marymont (piwnica techniczna)", "lat": 52.2780, "lng": 20.9800}
])

# -----------------------------
# Dane AED
# -----------------------------
aed_df = pd.DataFrame([
    {"name": "AED Metro Centrum", "lat": 52.2298, "lng": 21.0118, "info": "AED przy wejściu głównym, brak respiratora"},
    {"name": "AED Metro Politechnika", "lat": 52.2193, "lng": 21.0182, "info": "AED + respirator w punkcie medycznym"},
    {"name": "AED Metro Świętokrzyska", "lat": 52.2335, "lng": 21.0106, "info": "AED przy kasach, brak respiratora"},
    {"name": "AED Metro Ratusz Arsenał", "lat": 52.2430, "lng": 21.0045, "info": "AED + respirator w dyżurce ochrony"},
    {"name": "AED Pałac Kultury", "lat": 52.2319, "lng": 21.0059, "info": "AED w recepcji, brak respiratora"},
    {"name": "AED Hala Torwar", "lat": 52.2220, "lng": 21.0450, "info": "AED + respirator w punkcie medycznym"},
    {"name": "AED Biblioteka UW", "lat": 52.2405, "lng": 21.0205, "info": "AED przy wejściu głównym, brak respiratora"},
    {"name": "AED Złote Tarasy", "lat": 52.2305, "lng": 21.0030, "info": "AED + respirator w punkcie ochrony"},
    {"name": "AED Stadion Narodowy", "lat": 52.2390, "lng": 21.0450, "info": "AED + respirator w punkcie medycznym"},
    {"name": "AED Lotnisko Chopina", "lat": 52.1650, "lng": 20.9670, "info": "AED + respirator w strefie kontroli bezpieczeństwa"}
])

# -----------------------------
# AI wybiera trasę ewakuacyjną
# -----------------------------
ai_decision = ai_select_evacuation(
    user_location,
    shelters_df,
    impact_lat,
    impact_lon,
    current_shockwave_radius,
    time_to_impact_min
)

if ai_decision:
    st.sidebar.success(f"🧠 AI wybrało: {ai_decision['name']} ({ai_decision['mode']}, {int(ai_decision['duration'])} min)")
    evacuation_routes = [ai_decision["route"]]
else:
    st.sidebar.error("❌ AI nie znalazło bezpiecznej trasy w czasie!")
    evacuation_routes = None

# -----------------------------
# Renderowanie mapy
# -----------------------------
map_object = render_map(asteroid_data, shelters_df, aed_df, user_location, evacuation_routes)
st.title("🗺️ Mapa zagrożenia")
st_folium(map_object, width=700, height=500)

# -----------------------------
# Informacje o asteroidzie
# -----------------------------
st.subheader(f"💥 Asteroida: {asteroid_data['asteroid_name']}")
st.write(f"**Stopień zagrożenia:** {asteroid_data['threat_level']}")
st.write(f"**Energia uderzenia:** {asteroid_data['energy_megatons']} Mt TNT")
st.write(f"**Porównanie historyczne:** {asteroid_data['historical_comparison']}")
st.write(f"**Obszar zniszczeń:** {asteroid_data['total_affected_area_km2']:,} km²")
st.write(f"**Trajektoria uderzenia:** {asteroid_data['trajectory']}")
st.write(f"**Prawdopodobieństwo uderzenia:** {asteroid_data['impact_probability']:.5f}")
st.write(f"**Promień fali uderzeniowej:** {current_shockwave_radius:.2f} km")

# -----------------------------
# Informacje o trasie
# -----------------------------
with st.expander("📋 Szczegóły ewakuacji"):
    if ai_decision:
        st.subheader(f"🏠 {ai_decision['name']}")
        st.write(f"➡️ {ai_decision['mode']}: {int(ai_decision['duration'])} min ({ai_decision['distance']:.2f} km)")
    else:
        st.warning("Brak dostępnej trasy ewakuacyjnej.")

# -----------------------------
# Ostrzeżenia czasowe
# -----------------------------
if time_to_impact_min > 0:
    st.warning(f"☄️ Uderzenie nastąpi za {time_to_impact_min} minut.")
else:
    st.error(f"💥 Uderzenie nastąpiło {time_after_impact_min} minut temu.")