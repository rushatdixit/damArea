"""
This file handles acquiring the lat,lon coords of the dam
It contains two functions:
    1. dam_name_to_coords
    2. dam_name_to_bbox
"""

import requests
from typing import Dict
from sentinelhub import BBox, CRS

def dam_name_to_coords(dam_name) -> Dict:
    """
    Given a dam name returns a dict with all the relevant information \n
    Uses openstreetmap

    :param dam_name: Name of the dam
    :type dam_name: str
    """
    url = "https://nominatim.openstreetmap.org/search"
    queries = {
        f"{dam_name} Dam",
        f"{dam_name} Reservoir",
        dam_name,
        f"{dam_name.split()[0]} Dam" #first word + dam
    }
    for query in queries:
        params = {
            "q": query,
            "format": "json",
            "limit": 1,
            "countrycodes": "in"
        }
        headers = {
            "User-Agent": "DamAreaMeasure/0.1 (research project)"
        }

        response = requests.get(url, params=params, headers=headers)
        print("Searching for:", params["q"])

        response.raise_for_status()
        data = response.json()
        print("Raw response: ", data)

        if len(data) > 0:
            result = data[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            bbox = [float(x) for x in result["boundingbox"]]
            return {
                "latitude": lat,
                "longitude": lon,
                "bounding_box": bbox
            }
        
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
    bb = result["bounding_box"]

    min_lat = float(bb[0])
    max_lat = float(bb[1])
    min_lon = float(bb[2])
    max_lon = float(bb[3])

    return BBox(
        bbox=[min_lon, min_lat, max_lon, max_lat],
        crs=CRS.WGS84
    )
