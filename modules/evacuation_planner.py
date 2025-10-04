from math import radians, cos, sin, asin, sqrt

def haversine(coord1, coord2):
    """
    Oblicza odległość w kilometrach między dwoma punktami (lat, lon)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    # konwersja stopni na radiany
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # wzór haversine
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # promień Ziemi w km
    return c * r
