import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.map_renderer import render_map
from modules.utils import get_route_info

# Dane asteroidy
asteroid_data = {
    "name": "Apophis",
    "impact_lat": 52.2297,
    "impact_lng": 21.0122,
    "impact_radius_km": 50,
    "shockwave_radius_km": 100,
    "severity": "katastrofalne"
}

# Dane schronów
shelters_df = pd.DataFrame([
    {"name": "Schron Warszawa Centrum", "lat": 52.2300, "lng": 21.0100},
    {"name": "Schron Praga", "lat": 52.2550, "lng": 21.0400},
    {"name": "Schron Mokotów", "lat": 52.2000, "lng": 21.0200},
])

# Lokalizacja użytkownika
user_location = {"lat": 52.2400, "lng": 21.0300}

# Interfejs wyboru
with st.sidebar:
    st.header("🧭 Wybierz trasę ewakuacyjną")
    selected_shelter_name = st.selectbox("Schron:", shelters_df["name"].tolist())
    selected_mode_label = st.radio("Tryb transportu:", ["Pieszo", "Rowerem", "Samochodem"])

# Pobierz dane schronu
selected_shelter = shelters_df[shelters_df["name"] == selected_shelter_name].iloc[0]
shelter_coords = (selected_shelter["lat"], selected_shelter["lng"])

# Klucz sesji
session_key = f"{selected_shelter_name}_{selected_mode_label}"

# Generuj trasę tylko jeśli nie ma jej w sesji
if session_key not in st.session_state:
    st.session_state[session_key] = get_route_info((user_location["lat"], user_location["lng"]), shelter_coords)

# Pobierz dane trasy
route_info = st.session_state[session_key]
selected_route_data = next((r for r in route_info if r["label"] == selected_mode_label), None)

# Renderuj mapę
evacuation_routes = [selected_route_data["route"]] if selected_route_data else None
map_object = render_map(asteroid_data, shelters_df, user_location, evacuation_routes)

# Wyświetlenie mapy
st.title("🗺️ Mapa zagrożenia")
st_folium(map_object, width=700, height=500)

# Informacje o trasie
with st.expander("📋 Szczegóły trasy"):
    st.subheader(f"🏠 {selected_shelter_name}")
    if selected_route_data:
        st.write(f"➡️ {selected_mode_label}: {selected_route_data['duration_min']} min ({selected_route_data['distance_km']} km)")
    else:
        st.warning("Brak danych dla wybranego trybu.")
