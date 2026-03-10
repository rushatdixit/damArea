from fetch_dam.get_dam import dam_name_to_coords
from sentinel.aoi import bbox_from_coords

def aoi_from_dam_name(name):
    result = dam_name_to_coords(name)
    bbox = result["bounding_box"]

    south, north, west, east = bbox

    coords = [
        (west, south),
        (east, south),
        (east, north),
        (west, north)
    ]

    return bbox_from_coords(coords)