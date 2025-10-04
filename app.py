import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.utils import get_route_info

# -----------------------------
# Inicjalizacja bazy asteroid
# -----------------------------
db = AsteroidDatabase()

# -----------------------------
# Sidebar – wybór asteroidy i lokalizacji
# -----------------------------
st.sidebar.header("Ustawienia zagrożenia")
asteroid_names = [a.name for a in db.asteroids]
wybrana_asteroida_name = st.sidebar.selectbox("Wybierz asteroidę", asteroid_names)
lat = st.sidebar.number_input("Szerokość geograficzna", value=52.2297)
lon = st.sidebar.number_input("Długość geograficzna", value=21.0122)

# Stan przycisku
if "show_impact" not in st.session_state:
    st.session_state.show_impact = False

if st.sidebar.button("Pokaż zagrożenie"):
    st.session_state.show_impact = True

# -----------------------------
# Dane schronów
# -----------------------------
shelters_df = pd.DataFrame([
    {"name": "Schron Warszawa Centrum", "lat": 52.2300, "lng": 21.0100},
    {"name": "Schron Praga", "lat": 52.2550, "lng": 21.0400},
    {"name": "Schron Mokotów", "lat": 52.2000, "lng": 21.0200},
])

# Lokalizacja użytkownika (przykładowa)
user_location = {"lat": 52.2400, "lng": 21.0300}

# -----------------------------
# Wyświetlanie mapy i informacji o zagrożeniu
# -----------------------------
if st.session_state.show_impact:
    # Pobieramy asteroidę z bazy
    wybrana_asteroida = next(a for a in db.asteroids if a.name == wybrana_asteroida_name)
    asteroid_data = db.calculate_impact_for_location(wybrana_asteroida, lat, lon)

    # -----------------------------
    # Sidebar – wybór trasy ewakuacyjnej
    # -----------------------------
    st.sidebar.header("🧭 Wybierz trasę ewakuacyjną")
    selected_shelter_name = st.sidebar.selectbox("Schron:", shelters_df["name"].tolist())
    selected_mode_label = st.sidebar.radio("Tryb transportu:", ["Pieszo", "Rowerem", "Samochodem"])

    selected_shelter = shelters_df[shelters_df["name"] == selected_shelter_name].iloc[0]
    shelter_coords = (selected_shelter["lat"], selected_shelter["lng"])

    # Klucz sesji dla trasy
    session_key = f"{selected_shelter_name}_{selected_mode_label}"
    if session_key not in st.session_state:
        st.session_state[session_key] = get_route_info(
            (user_location["lat"], user_location["lng"]),
            shelter_coords
        )

    route_info = st.session_state[session_key]
    selected_route_data = next((r for r in route_info if r["label"] == selected_mode_label), None)
    evacuation_routes = [selected_route_data["route"]] if selected_route_data else None

    # -----------------------------
    # Renderowanie mapy
    # -----------------------------
    map_object = render_map(asteroid_data, shelters_df, user_location, evacuation_routes)
    st.title("🗺️ Mapa zagrożenia")
    st_folium(map_object, width=700, height=500)

    # -----------------------------
    # Informacje o asteroidzie
    # -----------------------------
    st.subheader(f"💥 Asteroida: {asteroid_data['asteroid_name']}")
    st.write(f"**Stopień zagrożenia:** {asteroid_data['threat_level']}")
    st.write(f"**Energia uderzenia:** {asteroid_data['energy_megatons']} Mt TNT")
    st.write(f"**Porównanie historyczne:** {asteroid_data['historical_comparison']}")
    st.write(f"**Całkowity obszar dotknięty zniszczeniem:** {asteroid_data['total_affected_area_km2']:,} km²")
    st.write(f"**Trajektoria uderzenia:** {asteroid_data['trajectory']}")
    st.write(f"**Prawdopodobieństwo uderzenia:** {asteroid_data['impact_probability']:.5f}")

    # -----------------------------
    # Informacje o trasie
    # -----------------------------
    with st.expander("📋 Szczegóły trasy"):
        st.subheader(f"🏠 {selected_shelter_name}")
        if selected_route_data:
            st.write(f"➡️ {selected_mode_label}: {selected_route_data['duration_min']} min ({selected_route_data['distance_km']} km)")
        else:
            st.warning("Brak danych dla wybranego trybu.")
