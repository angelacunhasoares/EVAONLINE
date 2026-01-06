"""
Geographic utilities for distance and coordinate calculations.

Provides optimized Haversine distance calculations for both scalar and
vectorized (NumPy array) operations.
"""

import math
from typing import Tuple, Union

import numpy as np


def haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate distance between two points using Haversine formula.

    Args:
        lat1, lon1: First coordinate (degrees)
        lat2, lon2: Second coordinate (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in km

    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def haversine_distance_vectorized(
    lat1: Union[np.ndarray, float],
    lon1: Union[np.ndarray, float],
    lat2: Union[np.ndarray, float],
    lon2: Union[np.ndarray, float],
) -> Union[np.ndarray, float]:
    """
    Vectorized Haversine for multiple pairs (fast for large arrays).

    Args:
        lat1, lon1, lat2, lon2: NumPy arrays or floats of lat/lon (degrees).

    Returns:
        Array of distances in km (or float if inputs are floats).
    """
    # Convert to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    # Earth radius in km
    R = 6371.0

    return R * c


def detect_geographic_region(lat: float, lon: float) -> str:
    """
    Detect geographic region based on coordinates.

    Returns one of: brasil, usa, europe, africa, asia, oceania, global
    """
    # Brasil (approximate bounds)
    if -35 <= lat <= 5 and -75 <= lon <= -30:
        return "brasil"
    # USA Continental
    elif 24 <= lat <= 50 and -125 <= lon <= -66:
        return "usa"
    # Europe
    elif 35 <= lat <= 72 and -10 <= lon <= 40:
        return "europe"
    # Africa
    elif -35 <= lat <= 37 and -20 <= lon <= 55:
        return "africa"
    # Asia
    elif 0 <= lat <= 80 and 40 <= lon <= 180:
        return "asia"
    # Australia/Oceania
    elif -50 <= lat <= 0 and 100 <= lon <= 180:
        return "oceania"
    else:
        return "global"


def is_same_hemisphere(
    lat1: float, lat2: float, tolerance: float = 5.0
) -> bool:
    """
    Check if two latitudes are in the same hemisphere.

    Args:
        lat1, lat2: Latitudes in degrees
        tolerance: Degrees near equator to consider as "same hemisphere"

    Returns:
        True if both are in the same hemisphere
    """
    # Same sign means same hemisphere
    if lat1 * lat2 > 0:
        return True

    # Near equator is considered compatible with both hemispheres
    if abs(lat1) < tolerance and abs(lat2) < tolerance:
        return True

    return False


def calculate_bounding_box(
    lat: float, lon: float, distance_km: float
) -> Tuple[float, float, float, float]:
    """
    Calculate a bounding box around a point.

    Args:
        lat, lon: Center coordinates (degrees)
        distance_km: Distance from center to edge (km)

    Returns:
        Tuple of (min_lat, max_lat, min_lon, max_lon)
    """
    # Approximate degrees per km
    lat_delta = distance_km / 111.0  # ~111 km per degree latitude
    lon_delta = distance_km / (111.0 * math.cos(math.radians(lat)))

    return (
        lat - lat_delta,
        lat + lat_delta,
        lon - lon_delta,
        lon + lon_delta,
    )
