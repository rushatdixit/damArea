"""
Area of Interest (AOI) construction utilities.
"""

from typing import List, Tuple
from sentinelhub import BBox, CRS, Geometry


def expand_bbox_meters(bbox: BBox, expansion_m: float) -> BBox:
    """
    Expands a WGS84 BBox by a given number of meters on all sides.

    Transforms to UTM, applies metric expansion, then transforms back to WGS84.

    :param bbox: Original bounding box in WGS84.
    :type bbox: BBox
    :param expansion_m: Expansion distance in meters.
    :type expansion_m: float
    :return: Expanded bounding box in WGS84.
    :rtype: BBox
    """
    min_lon, min_lat, max_lon, max_lat = bbox

    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)

    bbox_utm = bbox.transform(utm_crs)
    minx, miny, maxx, maxy = bbox_utm

    expanded_utm = BBox(
        bbox=[
            minx - expansion_m,
            miny - expansion_m,
            maxx + expansion_m,
            maxy + expansion_m,
        ],
        crs=utm_crs,
    )

    return expanded_utm.transform(CRS.WGS84)


def bbox_from_coords(coords: List[Tuple[float, float]]) -> BBox:
    """
    Creates a WGS84 BBox from a list of (lon, lat) coordinate pairs.

    :param coords: List of (longitude, latitude) tuples.
    :type coords: List[Tuple[float, float]]
    :return: Bounding box enclosing all coordinates.
    :rtype: BBox
    """
    lons = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]

    return BBox(
        bbox=[min(lons), min(lats), max(lons), max(lats)],
        crs=CRS.WGS84
    )


def geometry_from_geojson(geojson: dict) -> Geometry:
    """
    Creates a Sentinel Hub Geometry from a GeoJSON dictionary.

    :param geojson: GeoJSON geometry dictionary.
    :type geojson: dict
    :return: Sentinel Hub Geometry in WGS84.
    :rtype: Geometry
    """
    return Geometry(geojson, CRS.WGS84)