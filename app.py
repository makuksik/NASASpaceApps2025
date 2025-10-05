import requests
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.ai_planner import ai_select_evacuation

ORS_API_KEY = "ORS_API_KEY=eyJvcmciOiI1YjNjZTM1OTc4NTExMTAwMDFjZjYyNDgiLCJpZCI6ImJjNjIwMjM4OGM3MTQyMWNhNDM2NzgxNjJkMjllYTA5IiwiaCI6Im11cm11cjY0In0="

st.set_page_config(
    page_title="Impact Zone",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Ścieżka do folderu z danymi
# -----------------------------
DATA_PATH = r"C:\Users\pawol\NASASpaceApps2025\\"

# -----------------------------
# Wczytanie danych z plików CSV
# -----------------------------
shelters_df = pd.read_csv(DATA_PATH + "shelters.csv")
aed_df = pd.read_csv(DATA_PATH + "aed.csv")
water_points_df = pd.read_csv(DATA_PATH + "water_points.csv")
medical_points_df = pd.read_csv(DATA_PATH + "medical_points.csv")

# -----------------------------
# Inicjalizacja bazy asteroid
# -----------------------------
db = AsteroidDatabase()

st.sidebar.header("⚠️ Impact simulation")
asteroid_names = [a.name for a in db.asteroids]
selected_asteroid_name = st.sidebar.selectbox("Select an asteroid", asteroid_names)

st.sidebar.header("📍 Your location")
user_lat = st.sidebar.number_input("Latitude", value=52.2297)
user_lon = st.sidebar.number_input("Longitude", value=21.0122)
user_location = {"lat": user_lat, "lng": user_lon}


st.sidebar.header("📍 Search location")
with st.sidebar.form("search_form"):
    search_address = st.text_input("Enter address or city")
    search_submitted = st.form_submit_button("Search")

# --- Wyszukiwanie lokalizacji użytkownika ---
st.sidebar.header("📍 Search a location")
with st.sidebar.form("search_form"):
    search_address = st.text_input("Search a location")
    search_submitted = st.form_submit_button("Find")  # Enter lub kliknięcie wyśle formularz

if "user_location" not in st.session_state:
    st.session_state.user_location = user_location

if search_submitted and search_address:
    geocode_url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": ORS_API_KEY, "text": search_address, "size": 1}
    response = requests.get(geocode_url, params=params)
    if response.status_code == 200 and response.json().get("features"):
        feature = response.json()["features"][0]
        coords = feature["geometry"]["coordinates"]
        st.session_state.user_location = {"lat": coords[1], "lng": coords[0]}
        st.sidebar.success(f"Found: {feature['properties']['label']}")
    else:
        st.sidebar.error("Location not found.")

# Geokodowanie po wysłaniu formularza
from modules.utils import client, get_route_info, ORS_API_KEY  # klient ORS już załadowany z ORS_API_KEY

# Geokodowanie po wysłaniu formularza
if "geocode_cache" not in st.session_state:
    st.session_state.geocode_cache = {}

if search_submitted and search_address:
    if search_address in st.session_state.geocode_cache:
        st.session_state.user_location = st.session_state.geocode_cache[search_address]
    else:
        try:
            geocode_result = client.pelias_search(search_address, size=1)
            features = geocode_result.get("features", [])
            if features:
                feature = features[0]
                coords = feature["geometry"]["coordinates"]
                st.session_state.user_location = {"lat": coords[1], "lng": coords[0]}
                st.session_state.geocode_cache[search_address] = st.session_state.user_location
                st.sidebar.success(f"Found: {feature['properties']['label']}")
            else:
                st.sidebar.error("Can't find a location.")
        except Exception as e:
            st.sidebar.error(f"Geocoding error: {e}")


st.sidebar.header("🌋 Impact location")
impact_lat = st.sidebar.number_input("Impact latitude", value=52.2550)
impact_lon = st.sidebar.number_input("Impact longitude", value=21.0400)

time_to_impact_min = st.sidebar.slider("⏱️ Minutes to impact", 0, 60, 15)
time_after_impact_min = st.sidebar.slider("🌪️ Minutes after impact", 0, 300, 0)

selected_asteroid = next(a for a in db.asteroids if a.name == selected_asteroid_name)
impact_details = db.calculate_impact_for_location(selected_asteroid, impact_lat, impact_lon)

max_radius = impact_details["destruction_zones"]["shockwave_radius_km"]
shockwave_speed = max_radius / 300

if time_to_impact_min > 0:
    current_radius = min(max_radius, shockwave_speed * (60 - time_to_impact_min))
else:
    current_radius = min(max_radius, shockwave_speed * time_after_impact_min)

asteroid_data = {
    "asteroid_name": impact_details["asteroid_name"],
    "impact_coordinates": {"lat": impact_lat, "lon": impact_lon},
    "circles_coordinates": impact_details.get("circles_coordinates", {}),
    "destruction_zones": impact_details.get("destruction_zones", {}),
    "threat_level": impact_details.get("threat_level", "unknown"),
    "energy_megatons": impact_details.get("energy_megatons", 0),
    "historical_comparison": impact_details.get("historical_comparison", ""),
    "total_affected_area_km2": impact_details.get("total_affected_area_km2", 0),
    "trajectory": impact_details.get("trajectory", ""),
    "impact_probability": impact_details.get("impact_probability", 0.0),
    "shockwave_radius_km": current_radius
}

# -----------------------------
# AI evacuation route
# -----------------------------
ai_decision = ai_select_evacuation(
    st.session_state.user_location,
    shelters_df,
    impact_lat,
    impact_lon,
    current_radius,
    time_to_impact_min,
    ors_api_key=ORS_API_KEY
)

if ai_decision:
    evacuation_routes = [ai_decision["route"]]
    st.sidebar.success(f"🧠 AI chose: {ai_decision['name']} ({ai_decision['mode']}, {int(ai_decision['duration'])} min)")
else:
    evacuation_routes = []
    st.sidebar.error("❌ No safe route found in time!")

# -----------------------------
# Map rendering
# -----------------------------
st.markdown("### 🗺️ Threat Map")
map_object = render_map(
    asteroid_data,
    shelters_df,
    aed_df,
    medical_points_df,
    water_points_df,
    st.session_state.user_location,
    evacuation_routes
)
st_folium(map_object, use_container_width=True, height=500)

# -----------------------------
# Asteroid info
# -----------------------------
st.markdown("### 💥 Asteroid details")
st.write(f"**Threat level:** {asteroid_data['threat_level']}")
st.write(f"**Impact energy:** {asteroid_data['energy_megatons']} Mt TNT")
st.write(f"**Historical comparison:** {asteroid_data['historical_comparison']}")
st.write(f"**Area of destruction:** {asteroid_data['total_affected_area_km2']:,} km²")
st.write(f"**Trajectory:** {asteroid_data['trajectory']}")
st.write(f"**Impact probability:** {asteroid_data['impact_probability']:.5f}")
st.write(f"**Shockwave radius:** {current_radius:.2f} km")

# -----------------------------
# Evacuation info
# -----------------------------
with st.expander("📋 Evacuation details"):
    if ai_decision:
        st.subheader(f"🏠 {ai_decision['name']}")
        st.write(f"➡️ {ai_decision['mode']}: {int(ai_decision['duration'])} min ({ai_decision['distance']:.2f} km)")
    else:
        st.warning("No escape route available.")

# -----------------------------
# Time warnings
# -----------------------------
if time_to_impact_min > 0:
    st.warning(f"☄️ Impact will occur in {time_to_impact_min} minutes.")
else:
    st.error(f"💥 Impact occurred {time_after_impact_min} minutes ago.")

# -----------------------------
# Post-impact instructions
# -----------------------------
st.markdown("### 🧭 Instructions after impact")
etap = st.selectbox("Select stage", ["⏱️ First hours", "📆 First days", "🗓️ First weeks"])

if etap == "⏱️ First hours":
    with st.expander("Behavior in the first hours (0–6h)", expanded=True):
        st.markdown("""
- **Stay calm.** Don't make hasty decisions.
- **Stay in the shelter.** The shockwave and secondary damage may continue.
- **Avoid windows and open spaces.**
- **Turn off ventilation.** Minimize the risk of air contamination.
- **Secure water and food.**
- **Check the availability of an AED and ventilator.**
""")

elif etap == "📆 First days":
    with st.expander("Behavior in the first days (6h–72h)", expanded=True):
        st.markdown("""
- **Assess the surroundings.** If the shelter is damaged, consider a cautious evacuation.
- **Avoid contact with groundwater.**
- **Monitor messages.** Radio, local network, app.
- **Help others.** Indicate the nearest medical facilities.
- **Do not wander aimlessly.**
""")

elif etap == "🗓️ First weeks":
    with st.expander("Behavior in the first weeks (3–21 days)", expanded=True):
        st.markdown("""
- **Join local survival structures.**
- **Report your position.** If you have internet access.
- **Avoid unorganized gatherings.**
- **Collect data.** Document the state of the environment.
- **Prepare for subsequent waves.** Aftershocks, dust fall.
""")
