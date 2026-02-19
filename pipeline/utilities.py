from sentinelhub import CRS, BBox
import numpy as np


def ensure_utm(bbox: BBox) -> BBox:
    assert isinstance(bbox, BBox)
    if bbox.crs == CRS.WGS84:
        center_lon = (bbox.min_x + bbox.max_x) / 2
        center_lat = (bbox.min_y + bbox.max_y) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        return bbox.transform(utm_crs)
    return bbox


def adjust_resolution(bbox: BBox, resolution: float, max_pixels: int = 2500) -> float:
    assert resolution > 0
    assert max_pixels > 0
    width_m = bbox.max_x - bbox.min_x
    height_m = bbox.max_y - bbox.min_y
    max_dimension_m = max(width_m, height_m)

    if max_dimension_m / resolution > max_pixels:
        resolution = int(np.ceil(max_dimension_m / max_pixels))

    return resolution
