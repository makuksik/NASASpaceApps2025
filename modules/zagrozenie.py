import math
import json
import requests
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from enum import Enum
import pandas as pd
from datetime import datetime

class ThreatLevel(Enum):
    """Poziomy zagrożenia asteroidą"""
    MINOR = "minor"
    MODERATE = "moderate"
    SEVERE = "severe"
    CATASTROPHIC = "catastrophic"

@dataclass
class Asteroid:
    """Klasa reprezentująca asteroidę z jej parametrami"""
    name: str
    diameter_km: float  # Rozmiar (średnica) w km
    velocity_km_s: float  # Prędkość w km/s
    mass_kg: float  # Masa w kg
    trajectory_angle: float  # Kąt trajektorii (w stopniach, 0-90)
    close_approach_date: str  # Data zbliżenia do Ziemi
    miss_distance_km: float  # Odległość minięcia Ziemi w km
    impact_probability: float  # Prawdopodobieństwo uderzenia (0-1)

    def calculate_kinetic_energy(self) -> float:
        """
        Oblicza energię kinetyczną w megatonach TNT
        E = 0.5 * m * v² - wystarczy bo nam chodzi tylko o jebniecie
        """
        energy_joules = 0.5 * self.mass_kg * (self.velocity_km_s * 1000) ** 2
        # Konwersja na megatony TNT (1 megatona = 4.184 × 10¹⁵ J)
        energy_megatons = energy_joules / (4.184 * 10 ** 15)
        return energy_megatons

    def get_trajectory_info(self) -> str:
        """Zwraca informację o trajektorii"""
        if self.trajectory_angle < 30:
            return "płaska (niebezpieczna - większy zasięg)"
        elif self.trajectory_angle < 60:
            return "umiarkowana"
        else:
            return "stroma (mniejszy zasięg powierzchniowy)"

class ImpactZone:
    """
    Klasa do obliczania okręgów uderzenia i fali uderzeniowej
    dla wybranej lokalizacji
    """

    def __init__(self, asteroid: Asteroid, impact_lat: float, impact_lon: float):
        self.asteroid = asteroid
        self.impact_lat = impact_lat
        self.impact_lon = impact_lon
        self.energy_megatons = asteroid.calculate_kinetic_energy()

    def calculate_crater_radius(self) -> float:
        """
        Oblicza promień krateru w km
        Wzór empiryczny: R = 0.07 * E^0.33 (gdzie E w megatonach) - bardzo ogromne szacowanie
        """
        radius_km = 0.07 * (self.energy_megatons ** 0.33)

        # Modyfikacja na podstawie kąta trajektorii
        # Płytsze uderzenia tworzą większe kratery
        angle_factor = 1 + (90 - self.asteroid.trajectory_angle) / 180
        radius_km *= angle_factor

        return radius_km

    def calculate_blast_radius(self) -> Dict[str, float]:
        """
        Oblicza promienie różnych stref zniszczeń (okręgi uderzenia)
        Zwraca słownik z promieniami w km dla każdej strefy
        """
        crater_radius = self.calculate_crater_radius()

        zones = {
            "crater_km": crater_radius,
            "total_destruction_km": crater_radius * 2,  # Całkowite zniszczenie
            "severe_damage_km": crater_radius * 5,  # Poważne zniszczenia
            "moderate_damage_km": crater_radius * 10,  # Umiarkowane zniszczenia
            "light_damage_km": crater_radius * 20,  # Lekkie zniszczenia
            "shockwave_radius_km": crater_radius * 50  # Fala uderzeniowa
        }
        return zones

    def calculate_affected_area(self) -> float:
        """Oblicza całkowity obszar dotkniętych zniszczeń (km²)"""
        zones = self.calculate_blast_radius()
        area_km2 = math.pi * (zones["shockwave_radius_km"] ** 2)
        return area_km2

    def calculate_zone_coordinates(self, radius_km: float, num_points: int = 360) -> List[Tuple[float, float]]:
        """
        Oblicza współrzędne punktów na okręgu o danym promieniu
        wokół punktu uderzenia (do rysowania na mapie)

        Mozliwe ze to do ZMIANY PAWEŁ !!!

        Args:
            radius_km: promień okręgu w km
            num_points: liczba punktów na okręgu (domyślnie 360 = co 1°)

        Returns:
            Lista tupli (lat, lon)
        """
        earth_radius_km = 6371.0  # Promień Ziemi w km
        points = []

        for i in range(num_points):
            angle = math.radians(i)

            # Oblicz przesunięcie w stopniach
            # Δlat = (radius / earth_radius) * (180 / π)
            delta_lat = (radius_km / earth_radius_km) * (180 / math.pi) * math.cos(angle)
            # Δlon uwzględnia szerokość geograficzną
            delta_lon = (radius_km / earth_radius_km) * (180 / math.pi) * math.sin(angle) / math.cos(
                math.radians(self.impact_lat))

            new_lat = self.impact_lat + delta_lat
            new_lon = self.impact_lon + delta_lon

            points.append((new_lat, new_lon))

        return points

    def get_impact_details(self) -> Dict:
        """
        Zwraca szczegółowe informacje o uderzeniu w formacie JSON-friendly
        Gotowe do użycia przez frontend/Osobę 2
        """
        zones = self.calculate_blast_radius()

        # Przygotuj współrzędne okręgów dla każdej strefy (do map)
        circles_coords = {}
        for zone_name, radius in zones.items():
            circles_coords[zone_name] = self.calculate_zone_coordinates(radius)

        return {
            "asteroid_name": self.asteroid.name,
            "impact_coordinates": {
                "lat": self.impact_lat,
                "lon": self.impact_lon
            },
            "energy_megatons": round(self.energy_megatons, 2),
            "crater_radius_km": round(self.calculate_crater_radius(), 2),
            "trajectory": self.asteroid.get_trajectory_info(),
            "destruction_zones": {k: round(v, 2) for k, v in zones.items()},
            "total_affected_area_km2": round(self.calculate_affected_area(), 2),
            "circles_coordinates": circles_coords  # Współrzędne do rysowania okręgów
        }

class ThreatAnalyzer:
    """Klasa do analizy i kategoryzacji poziomu zagrożenia"""

    @staticmethod
    def categorize_threat(asteroid: Asteroid) -> ThreatLevel:
        """
        Kategoryzuje zagrożenie na podstawie energii i prawdopodobieństwa
        Zwraca: małe / średnie / poważne / katastrofalne
        """
        energy = asteroid.calculate_kinetic_energy()
        probability = asteroid.impact_probability

        # Kategorie oparte na energii i prawdopodobieństwie
        if energy < 1:  # < 1 megatona
            return ThreatLevel.MINOR
        elif energy < 100:  # 1-100 megaton
            if probability > 0.01:
                return ThreatLevel.MODERATE
            return ThreatLevel.MINOR
        elif energy < 10000:  # 100-10,000 megaton
            if probability > 0.001:
                return ThreatLevel.SEVERE
            return ThreatLevel.MODERATE
        else:  # > 10,000 megaton
            return ThreatLevel.CATASTROPHIC

    @staticmethod
    def calculate_risk_score(asteroid: Asteroid) -> float:
        """
        Oblicza wynik ryzyka (0-100) na podstawie wielu czynników
        Używane do rankingu asteroid
        """
        energy = asteroid.calculate_kinetic_energy()
        probability = asteroid.impact_probability

        # Współczynnik ryzyka = energia × prawdopodobieństwo × 100
        risk_score = min(100, energy * probability * 100)

        return round(risk_score, 2)

    @staticmethod
    def compare_to_historical_events(energy_megatons: float) -> str:
        """Porównuje energię z historycznymi wydarzeniami"""
        if energy_megatons < 0.02:
            return "Smaller than the Chelyabinsk meteor (2013)"
        elif energy_megatons < 15:
            return "Similar to the atomic bomb of Hiroshima"
        elif energy_megatons < 50:
            return "Similar to the largest nuclear bombs"
        elif energy_megatons < 1000:
            return "Similar to the Tunguska Event (1908)"
        else:
            return "Extinction event (like the impact that killed the dinosaurs)"


class AsteroidDatabase: # WAZNA KLASA- aktualnie jest 6 asteroid
    """
    Główna baza danych asteroid
    Zarządza danymi, obliczeniami i eksportem
    """

    def __init__(self):
        self.asteroids: List[Asteroid] = []
        self._initialize_known_threats()

    def _initialize_known_threats(self):
        """Inicjalizuje bazę znanymi, potencjalnie niebezpiecznymi asteroidami"""
        known_asteroids = [
            Asteroid(
                name="Apophis",
                diameter_km=0.37,
                velocity_km_s=7.42,
                mass_kg=6.1e10,
                trajectory_angle=45.0,
                close_approach_date="2029-04-13",
                miss_distance_km=31000,
                impact_probability=0.00001
            ),
            Asteroid(
                name="Bennu",
                diameter_km=0.49,
                velocity_km_s=28.0,
                mass_kg=7.8e10,
                trajectory_angle=60.0,
                close_approach_date="2182-09-24",
                miss_distance_km=750000,
                impact_probability=0.00037
            ),
            Asteroid(
                name="1950 DA",
                diameter_km=1.1,
                velocity_km_s=15.0,
                mass_kg=2e12,
                trajectory_angle=30.0,
                close_approach_date="2880-03-16",
                miss_distance_km=5000000,
                impact_probability=0.00033
            ),
            Asteroid(
                name="2023 DW",
                diameter_km=0.05,
                velocity_km_s=18.0,
                mass_kg=1.5e8,
                trajectory_angle=55.0,
                close_approach_date="2046-02-14",
                miss_distance_km=1500000,
                impact_probability=0.00014
            ),
            Asteroid(
                name="2000 SG344",
                diameter_km=0.037,
                velocity_km_s=4.5,
                mass_kg=7.1e7,
                trajectory_angle=70.0,
                close_approach_date="2071-09-21",
                miss_distance_km=500000,
                impact_probability=0.00001
            ),
            Asteroid(
                name="2010 RF12",
                diameter_km=0.007,
                velocity_km_s=12.0,
                mass_kg=5e6,
                trajectory_angle=40.0,
                close_approach_date="2095-09-05",
                miss_distance_km=80000,
                impact_probability=0.000005
            )
        ]
        self.asteroids.extend(known_asteroids)

    def add_asteroid(self, asteroid: Asteroid):
        """Dodaje nową asteroidę do bazy"""
        self.asteroids.append(asteroid)

    def get_most_dangerous(self, top_n: int = 5) -> List[Asteroid]:
        """
        Zwraca n najbardziej niebezpiecznych asteroid
        Sortuje według wyniku ryzyka (energia × prawdopodobieństwo)
        """
        sorted_asteroids = sorted(
            self.asteroids,
            key=lambda a: ThreatAnalyzer.calculate_risk_score(a),
            reverse=True
        )
        return sorted_asteroids[:top_n]

    def filter_by_threat_level(self, level: ThreatLevel) -> List[Asteroid]:
        """Filtruje asteroidy według poziomu zagrożenia"""
        return [a for a in self.asteroids
                if ThreatAnalyzer.categorize_threat(a) == level]

    def to_pandas(self) -> pd.DataFrame:
        """
        Konwertuje bazę danych do pandas DataFrame
        Gotowe do użycia przez frontend (Osobę 2)
        """
        data = []
        for asteroid in self.asteroids:
            threat_level = ThreatAnalyzer.categorize_threat(asteroid)
            energy = asteroid.calculate_kinetic_energy()
            risk_score = ThreatAnalyzer.calculate_risk_score(asteroid)

            data.append({
                "Nazwa": asteroid.name,
                "Średnica (km)": round(asteroid.diameter_km, 3),
                "Prędkość (km/s)": round(asteroid.velocity_km_s, 2),
                "Masa (kg)": f"{asteroid.mass_kg:.2e}",
                "Energia (Mt TNT)": round(energy, 2),
                "Trajektoria (°)": asteroid.trajectory_angle,
                "Data zbliżenia": asteroid.close_approach_date,
                "Odległość (km)": f"{asteroid.miss_distance_km:,.0f}",
                "Prawdopodobieństwo": f"{asteroid.impact_probability:.5f}",
                "Wynik ryzyka": risk_score,
                "Zagrożenie": threat_level.value
            })

        return pd.DataFrame(data)

    def to_json(self, filepath: str = None) -> str:
        """
        Eksportuje wszystkie dane do formatu JSON
        Gotowe do użycia przez frontend
        """
        data = {
            "timestamp": datetime.now().isoformat(),
            "total_asteroids": len(self.asteroids),
            "asteroids": []
        }

        for asteroid in self.asteroids:
            threat_level = ThreatAnalyzer.categorize_threat(asteroid)
            energy = asteroid.calculate_kinetic_energy()
            risk_score = ThreatAnalyzer.calculate_risk_score(asteroid)
            comparison = ThreatAnalyzer.compare_to_historical_events(energy)

            asteroid_data = {
                **asdict(asteroid),
                "energy_megatons": round(energy, 2),
                "risk_score": risk_score,
                "threat_level": threat_level.value,
                "historical_comparison": comparison
            }
            data["asteroids"].append(asteroid_data)

        json_str = json.dumps(data, indent=2, ensure_ascii=False)

        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)

        return json_str

    def calculate_impact_for_location(self,
                                      asteroid: Asteroid,
                                      lat: float,
                                      lon: float) -> Dict:
        """
        Oblicza szczegóły uderzenia dla konkretnej lokalizacji

        Args:
            asteroid: Obiekt Asteroid
            lat: szerokość geograficzna
            lon: długość geograficzna

        Returns:
            Dict z pełnymi szczegółami uderzenia (gotowe dla frontendu)
        """
        impact_zone = ImpactZone(asteroid, lat, lon)
        impact_details = impact_zone.get_impact_details()

        # Dodaj dodatkowe analizy
        threat_level = ThreatAnalyzer.categorize_threat(asteroid)
        risk_score = ThreatAnalyzer.calculate_risk_score(asteroid)
        comparison = ThreatAnalyzer.compare_to_historical_events(
            impact_zone.energy_megatons
        )

        impact_details.update({
            "threat_level": threat_level.value,
            "risk_score": risk_score,
            "historical_comparison": comparison,
            "impact_probability": asteroid.impact_probability,
            "asteroid_info": {
                "name": asteroid.name,
                "diameter_km": asteroid.diameter_km,
                "velocity_km_s": asteroid.velocity_km_s,
                "mass_kg": asteroid.mass_kg,
                "trajectory_angle": asteroid.trajectory_angle
            }
        })

        return impact_details

    def save_to_json_file(self, filepath: str = "data/asteroidy.json"):
        """Zapisuje bazę danych do pliku JSON"""
        json_data = self.to_json()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_data)
        print(f"✅ Data saved to: {filepath}")

    def export_for_frontend(self, output_dir: str = "data/") -> Dict[str, str]:
        """
        Eksportuje wszystkie potrzebne dane dla frontendu

        Returns:
            Dict z ścieżkami do zapisanych plików
        """
        import os
        os.makedirs(output_dir, exist_ok=True)

        # 1. Pełna baza w JSON
        json_path = os.path.join(output_dir, "asteroidy.json")
        self.save_to_json_file(json_path)

        # 2. Tabela do CSV (dla Pandas)
        csv_path = os.path.join(output_dir, "asteroidy.csv")
        df = self.to_pandas()
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ Tabela zapisana do: {csv_path}")

        # 3. Top 10 najbardziej niebezpiecznych
        top_path = os.path.join(output_dir, "top_zagrozen.json")
        top_asteroids = self.get_most_dangerous(10)
        top_data = {
            "top_threats": [asdict(a) for a in top_asteroids]
        }
        with open(top_path, 'w', encoding='utf-8') as f:
            json.dump(top_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Top threats saved to: {top_path}")

        return {
            "json": json_path,
            "csv": csv_path,
            "top_threats": top_path
        }