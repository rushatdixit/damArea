"""
This file handles acquiring the lat,lon coords of the dam
It contains two functions:
    1. dam_name_to_coords
    2. dam_name_to_bbox
"""

import requests
import json
import time
from pathlib import Path
from functools import lru_cache
from sentinelhub import BBox, CRS
from objects.results import FetchedDamData

DATABASE_PATH = Path(__file__).parent / "dam_database.json"
_DB_CACHE = None

def load_database():
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


def save_database(db):
    global _DB_CACHE

    _DB_CACHE = db

    with open(DATABASE_PATH, "w") as f:
        json.dump(db, f, indent=4)

@lru_cache
def dam_name_to_coords(dam_name : str) -> FetchedDamData:
    """
    Given a dam name returns a dict with all the relevant information \n
    Uses openstreetmap

    :param dam_name: Name of the dam
    :type dam_name: str
    """

    url = "https://nominatim.openstreetmap.org/search"
    key = dam_name.strip().lower()
    queries = [
        f"{dam_name} Dam",
        f"{dam_name} Reservoir",
        dam_name,
        f"{dam_name.split()[0]} Dam" #first word + dam
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
            db[key]= {
                "latitude" : lat,
                "longitude" : lon,
                "bbox" : bbox
            }
            save_database(db)
            return FetchedDamData(lat, lon, bbox)
        
    raise ValueError("Dam not found using any query strategy")

def dam_name_to_bbox(name: str) -> BBox:
    """
    Gets the Bounding box of the dam \n
    Broadly, this function returns the BBox of any location

    :param name: Name of the dam
    :type name: str
    :return: Bounding box of the dam
    :rtype: sentinelhub.BBox
    """

    result = dam_name_to_coords(name)
    bb = result.bbox

    min_lat = float(bb[0])
    max_lat = float(bb[1])
    min_lon = float(bb[2])
    max_lon = float(bb[3])

    return BBox(
        bbox=[min_lon, min_lat, max_lon, max_lat],
        crs=CRS.WGS84
    )
