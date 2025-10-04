import requests
import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from modules.zagrozenie import AsteroidDatabase
from modules.map_renderer import render_map
from modules.utils import ORS_API_KEY
from modules.ai_planner import ai_select_evacuation

# -----------------------------
# Inicjalizacja bazy asteroid
# -----------------------------
db = AsteroidDatabase()

# --- Sidebar: Wybór asteroidy ---
st.sidebar.header("⚠️ Symulacja uderzenia")
asteroid_names = [a.name for a in db.asteroids]
wybrana_asteroida_name = st.sidebar.selectbox("Wybierz asteroidę", asteroid_names)

# --- Wyszukiwanie lokalizacji użytkownika ---
st.sidebar.header("📍 Wyszukaj lokalizację")
with st.sidebar.form("search_form"):
    search_address = st.text_input("Wpisz adres lub miejscowość")
    search_submitted = st.form_submit_button("Szukaj")  # Enter lub kliknięcie wyśle formularz

if "user_location" not in st.session_state:
    st.session_state.user_location = {"lat": 52.2297, "lng": 21.0122}

# Geokodowanie po wysłaniu formularza
if search_submitted and search_address:
    geocode_url = "https://api.openrouteservice.org/geocode/search"
    params = {"api_key": ORS_API_KEY, "text": search_address, "size": 1}
    response = requests.get(geocode_url, params=params)
    if response.status_code == 200 and response.json().get("features"):
        feature = response.json()["features"][0]
        coords = feature["geometry"]["coordinates"]
        st.session_state.user_location = {"lat": coords[1], "lng": coords[0]}
        st.sidebar.success(f"Znaleziono: {feature['properties']['label']}")
    else:
        st.sidebar.error("Nie znaleziono lokalizacji.")

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

water_points_df = pd.DataFrame([
    {"name": "ul. Radiowa 18 (Bemowo)", "lat": 52.2545, "lng": 20.9132},
    {"name": "ul. Powstańców Śląskich 101 (Bemowo)", "lat": 52.2540, "lng": 20.9285},
    {"name": "ul. Kochanowskiego 1 (Bielany)", "lat": 52.2805, "lng": 20.9480},
    {"name": "ul. Daniłowskiego 2 (Bielany)", "lat": 52.2780, "lng": 20.9515},
    {"name": "ul. Wolumen 3 (Bielany)", "lat": 52.2780, "lng": 20.9510},
    {"name": "ul. Puławska 266 (Mokotów)", "lat": 52.2050, "lng": 21.0200},
    {"name": "ul. Dąbrowskiego 75 (Mokotów)", "lat": 52.2100, "lng": 21.0150},
    {"name": "ul. Barska 16/20 (Ochota)", "lat": 52.2190, "lng": 20.9830},
    {"name": "ul. Pasteura 10 (Ochota)", "lat": 52.2180, "lng": 20.9800},
    {"name": "ul. Jagiellońska 56 (Praga Północ)", "lat": 52.2585, "lng": 21.0400},
    {"name": "ul. Targowa 62 (Praga Północ)", "lat": 52.2530, "lng": 21.0450},
    {"name": "ul. Pileckiego 122 (Ursynów)", "lat": 52.1505, "lng": 21.0500},
    {"name": "ul. Dunikowskiego 4 (Ursynów)", "lat": 52.1550, "lng": 21.0450},
    {"name": "ul. Górczewska 200 (Wola)", "lat": 52.2350, "lng": 20.9800},
    {"name": "ul. Młynarska 42 (Wola)", "lat": 52.2370, "lng": 20.9750},
    {"name": "ul. Żelazna 85 (Wola)", "lat": 52.2320, "lng": 20.9840},
    {"name": "ul. Słowackiego 6/8 (Żoliborz)", "lat": 52.2650, "lng": 20.9800},
    {"name": "ul. Broniewskiego 9 (Żoliborz)", "lat": 52.2655, "lng": 20.9755},
    {"name": "ul. Mehoffera 4 (Białołęka)", "lat": 52.3150, "lng": 21.0100},
    {"name": "ul. Świderska 35 (Białołęka)", "lat": 52.3200, "lng": 21.0200},
    {"name": "ul. Głębocka 66 (Targówek)", "lat": 52.2950, "lng": 21.0500},
    {"name": "ul. Kondratowicza 27 (Targówek)", "lat": 52.2900, "lng": 21.0450},
    {"name": "ul. Zawodzie 16 (Wilanów)", "lat": 52.1800, "lng": 21.0800},
    {"name": "ul. Klimczaka 8 (Wilanów)", "lat": 52.1650, "lng": 21.0900},
    {"name": "ul. Komitetu Obrony Robotników 45 (Włochy)", "lat": 52.1850, "lng": 20.9500},
    {"name": "ul. 1 Sierpnia 36 (Włochy)", "lat": 52.1900, "lng": 20.9600},
    {"name": "ul. Cierlicka 15 (Ursus)", "lat": 52.2000, "lng": 20.9200},
    {"name": "ul. Walerego Sławka 5 (Ursus)", "lat": 52.2050, "lng": 20.9300},
    {"name": "ul. Marsa 56 (Rembertów)", "lat": 52.2600, "lng": 21.1100},
    {"name": "ul. Chełmżyńska 180 (Rembertów)", "lat": 52.2650, "lng": 21.1200},
    {"name": "ul. Świętokrzyska 20 (Śródmieście)", "lat": 52.2330, "lng": 21.0100},
    {"name": "ul. Nowowiejska 10 (Śródmieście)", "lat": 52.2250, "lng": 21.0050}
])


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
medical_points_df = pd.DataFrame([
    {"name": "Szpital Bielański", "lat": 52.2830, "lng": 20.9560, "type": "hospital"},
    {"name": "Szpital Czerniakowski", "lat": 52.2080, "lng": 21.0350, "type": "hospital"},
    {"name": "Szpital Grochowski", "lat": 52.2450, "lng": 21.0850, "type": "hospital"},
    {"name": "Szpital Praski", "lat": 52.2540, "lng": 21.0400, "type": "hospital"},
    {"name": "Szpital Południowy", "lat": 52.1500, "lng": 21.0500, "type": "hospital"},
    {"name": "Szpital Wolski", "lat": 52.2350, "lng": 20.9800, "type": "hospital"},
    {"name": "Szpital Świętej Rodziny", "lat": 52.2100, "lng": 21.0200, "type": "hospital"},
    {"name": "Centrum Medyczne Żelazna", "lat": 52.2300, "lng": 20.9950, "type": "hospital"},
    {"name": "Instytut Psychiatrii i Neurologii", "lat": 52.2000, "lng": 21.0300, "type": "hospital"},
    {"name": "Szpital MSWiA", "lat": 52.2100, "lng": 21.0150, "type": "hospital"},
    {"name": "Przychodnia Lekarska Litewska", "lat": 52.2250, "lng": 21.0150, "type": "clinic"},
    {"name": "Przychodnia Klimczaka", "lat": 52.1600, "lng": 21.0700, "type": "clinic"},
    {"name": "Przychodnia Kielecka", "lat": 52.2200, "lng": 21.0100, "type": "clinic"},
    {"name": "Przychodnia Jagiellońska", "lat": 52.2600, "lng": 21.0400, "type": "clinic"},
    {"name": "Przychodnia Radzymińska", "lat": 52.2700, "lng": 21.0600, "type": "clinic"},
    {"name": "Centrum Medyczne Damiana", "lat": 52.2050, "lng": 21.0150, "type": "clinic"},
    {"name": "Centrum Medyczne Mavit", "lat": 52.2800, "lng": 20.9800, "type": "clinic"},
    {"name": "Punkt Medyczny Inflancka", "lat": 52.2500, "lng": 20.9950, "type": "emergency"},
    {"name": "Punkt Medyczny Kopernika", "lat": 52.2300, "lng": 21.0050, "type": "emergency"},
    {"name": "Punkt Medyczny Banacha", "lat": 52.2200, "lng": 21.0000, "type": "emergency"},
    {"name": "Punkt Medyczny Goszczyńskiego", "lat": 52.2150, "lng": 21.0100, "type": "emergency"}
])

# -----------------------------
# AI wybiera trasę ewakuacyjną
# -----------------------------
ai_decision = ai_select_evacuation(
    st.session_state.user_location,
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
map_object = render_map(
    asteroid_data,
    shelters_df,
    aed_df,
    medical_points_df,
    water_points_df,
    st.session_state.user_location,
    evacuation_routes
)

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

st.markdown("## 🧭 Instrukcja postępowania po uderzeniu meteorytu")

etap = st.selectbox("Wybierz etap", ["⏱️ Pierwsze godziny", "📆 Pierwsze dni", "🗓️ Pierwsze tygodnie"])

if etap == "⏱️ Pierwsze godziny":
    with st.expander("Zachowanie w pierwszych godzinach (0–6h)", expanded=True):
        st.markdown("""
- **Zachowaj spokój.** Nie podejmuj pochopnych decyzji.
- **Pozostań w schronie.** Fala uderzeniowa i wtórne zniszczenia mogą trwać.
- **Unikaj okien i otwartych przestrzeni.**
- **Wyłącz wentylację.** Zminimalizuj ryzyko skażenia powietrza.
- **Zabezpiecz wodę i żywność.**
- **Sprawdź dostępność AED i respiratora.**
        """)

elif etap == "📆 Pierwsze dni":
    with st.expander("Zachowanie w pierwszych dniach (6h–72h)", expanded=True):
        st.markdown("""
- **Oceń stan otoczenia.** Jeśli schron jest uszkodzony — rozważ ostrożną ewakuację.
- **Unikaj kontaktu z wodą gruntową.**
- **Monitoruj komunikaty.** Radio, sieć lokalna, aplikacja.
- **Pomagaj innym.** Wskaż najbliższe punkty medyczne.
- **Nie przemieszczaj się bez celu.**
        """)

elif etap == "🗓️ Pierwsze tygodnie":
    with st.expander("Zachowanie w pierwszych tygodniach (3–21 dni)", expanded=True):
        st.markdown("""
- **Dołącz do lokalnych struktur przetrwania.**
- **Zgłaszaj swoją pozycję.** Jeśli masz dostęp do sieci.
- **Unikaj zbiorowisk bez organizacji.**
- **Zbieraj dane.** Dokumentuj stan otoczenia.
- **Przygotuj się na kolejne fale.** Wstrząsy wtórne, opady pyłu.
        """)
