"""
Dam-to-AOI conversion utility.
"""

from sentinelhub import BBox
from fetch_dam.get_dam import dam_name_to_coords
from sentinel.aoi import bbox_from_coords


def aoi_from_dam_name(name: str) -> BBox:
    """
    Looks up a dam by name and returns a BBox covering its geocoded bounding box.

    :param name: Name of the dam.
    :type name: str
    :return: Bounding box of the dam in WGS84.
    :rtype: BBox
    """
    result = dam_name_to_coords(name)
    bbox = result.bbox

    south, north, west, east = bbox

    coords = [
        (west, south),
        (east, south),
        (east, north),
        (west, north)
    ]

    return bbox_from_coords(coords)