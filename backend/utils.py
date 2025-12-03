# backend/utils.py
import math

# -------------------------
# Helper functions
# -------------------------

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate distance in meters between two lat/lng points
    """
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    meters = R * c
    return meters


def nearest_stores(lat, lng, stores_list, max_results=3):
    """
    Return nearest stores with distance calculated
    stores_list: list of dicts with 'lat', 'lng', 'name', 'promos'
    """
    for store in stores_list:
        store_lat = store.get("lat")
        store_lng = store.get("lng")
        store["distance_m"] = int(haversine(lat, lng, store_lat, store_lng))

    # sort by distance
    sorted_stores = sorted(stores_list, key=lambda x: x["distance_m"])
    return sorted_stores[:max_results]
