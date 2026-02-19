"""
Area of interest builder
We are creating:
    - Axis aligned Bounding Box
    - Polygon geometry
"""

from typing import List, Tuple
from sentinelhub import BBox, CRS, Geometry
from sentinelhub import BBoxSplitter

def expand_bbox_meters(bbox: BBox, expansion_m: float) -> BBox:
    """
    Expands WGS84 BBox by expansion_m meters on all sides.
    Works with all sentinelhub versions.
    """

    min_lon, min_lat, max_lon, max_lat = bbox

    # Compute centroid manually
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2

    utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)

    # Transform to UTM
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

    # Transform back to WGS84
    return expanded_utm.transform(CRS.WGS84)

def bbox_from_coords(coords : List[Tuple[float, float]]) -> BBox:
    lons = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]

    return BBox(
        bbox = [min(lons), min(lats), max(lons), max(lats)],
        crs = CRS.WGS84
    )

def geometry_from_geojson(geojson : dict) -> Geometry:
    return Geometry(geojson, CRS.WGS84)