"""
airspace.py — Airspace conflict detection for BVLOS routes.
"""

import math
from typing import List, Dict


def haversine_km(lat1, lon1, lat2, lon2) -> float:
    """Calculate distance in km between two lat/lon points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def check_airspace_conflicts(waypoints: List[Dict], nfz_zones: List[Dict]) -> List[Dict]:
    """
    Check if any waypoint comes within warning distance of a no-fly zone.
    Returns list of conflict dicts.
    """
    conflicts = []
    warning_km = 5.0  # warn if within 5km of NFZ boundary

    for wp in waypoints:
        for zone in nfz_zones:
            dist = haversine_km(wp["lat"], wp["lon"], zone["lat"], zone["lon"])
            zone_radius_km = zone["radius"] / 1000
            buffer = zone_radius_km + warning_km
            if dist < buffer:
                conflicts.append({
                    "waypoint": wp["name"],
                    "zone": zone["name"],
                    "distance_km": round(dist, 2),
                    "zone_radius_km": zone_radius_km,
                    "severity": "Critical" if dist < zone_radius_km else "Warning"
                })

    return conflicts


def get_notam_zones() -> List[Dict]:
    """
    Return example NOTAM-style temporary restricted areas.
    In production this would call the NATS API or CAA NOTAM feed.
    """
    return [
        {
            "name": "Temp Restricted Area RA(T) 001",
            "lat": 52.300,
            "lon": -1.600,
            "radius": 5000,
            "valid_from": "2026-05-01T08:00:00Z",
            "valid_to": "2026-05-01T18:00:00Z",
            "reason": "Military Exercise"
        },
        {
            "name": "UAS Trial Zone — Coventry",
            "lat": 52.408,
            "lon": -1.510,
            "radius": 3000,
            "valid_from": "2026-05-01T06:00:00Z",
            "valid_to": "2026-05-31T20:00:00Z",
            "reason": "Approved BVLOS Trial"
        }
    ]
