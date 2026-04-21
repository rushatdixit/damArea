"""
Dam geocoding and local database caching.
"""

import requests
import json
import time
from typing import Dict, Optional
from pathlib import Path
from functools import lru_cache
from sentinelhub import BBox, CRS
from objects import FetchedDamData

DATABASE_PATH: Path = Path(__file__).parent / "dam_database.json"
_DB_CACHE: Optional[Dict] = None


def load_database() -> Dict:
    """
    Loads the local dam coordinate database from disk, using an in-memory cache.

    :return: Dictionary mapping dam name keys to coordinate records.
    :rtype: Dict
    """
    global _DB_CACHE

    if _DB_CACHE is not None:
        return _DB_CACHE

    if DATABASE_PATH.exists():
        try:
            with open(DATABASE_PATH, "r") as f:
                _DB_CACHE = json.load(f)
        except json.JSONDecodeError:
            _DB_CACHE = {}
    else:
        _DB_CACHE = {}

    return _DB_CACHE


def save_database(db: Dict) -> None:
    """
    Persists the dam coordinate database to disk and updates the in-memory cache.

    :param db: Dictionary of dam coordinate records to save.
    :type db: Dict
    """
    global _DB_CACHE

    _DB_CACHE = db

    with open(DATABASE_PATH, "w") as f:
        json.dump(db, f, indent=4)


@lru_cache
def dam_name_to_coords(dam_name: str) -> FetchedDamData:
    """
    Resolves a dam name to geographic coordinates via local database or OpenStreetMap.

    Checks the local database first. If not found, queries the Nominatim API
    with multiple query strategies and caches the result locally.

    :param dam_name: Human-readable name of the dam.
    :type dam_name: str
    :return: Geocoded dam data with latitude, longitude, and bounding box.
    :rtype: FetchedDamData
    :raises ValueError: If no results are found for any query strategy.
    """
    url = "https://nominatim.openstreetmap.org/search"
    key = dam_name.strip().lower()
    queries = [
        f"{dam_name} Dam",
        f"{dam_name} Reservoir",
        dam_name,
        f"{dam_name.split()[0]} Dam",
    ]

    db = load_database()

    if key in db:
        print("Found dam in database. Skipping openstreetmap query.")
        coords = db[key]
        return FetchedDamData(coords["latitude"], coords["longitude"], coords["bbox"])

    headers = {
        "User-Agent": "DamAreaMeasure/0.1 (research project)"
    }
    for query in queries:
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)
        print("Searching for:", params["q"])
        time.sleep(1)

        response.raise_for_status()
        data = response.json()
        print("Raw response: ", data)

        if len(data) > 0:
            result = data[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            bbox = [float(x) for x in result["boundingbox"]]
            db[key] = {
                "latitude": lat,
                "longitude": lon,
                "bbox": bbox,
            }
            save_database(db)
            return FetchedDamData(lat, lon, bbox)

    raise ValueError("Dam not found using any query strategy")


def dam_name_to_bbox(name: str) -> BBox:
    """
    Resolves a dam name to a geographic bounding box in WGS84.

    :param name: Human-readable name of the dam.
    :type name: str
    :return: Bounding box of the dam location.
    :rtype: BBox
    """
    result = dam_name_to_coords(name)
    bb = result.bbox

    min_lat = float(bb[0])
    max_lat = float(bb[1])
    min_lon = float(bb[2])
    max_lon = float(bb[3])

    return BBox(
        bbox=[min_lon, min_lat, max_lon, max_lat],
        crs=CRS.WGS84,
    )
