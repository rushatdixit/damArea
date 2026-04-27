"""
Utility functions for coordinate transformations and API constraint checks.
"""

import numpy as np
from sentinelhub import CRS, BBox


def ensure_utm(bbox: BBox) -> BBox:
    """
    Ensures a bounding box is in UTM projection, transforming from WGS84 if needed.

    :param bbox: Input bounding box in any CRS.
    :type bbox: BBox
    :return: Bounding box in UTM.
    :rtype: BBox
    """
    assert isinstance(bbox, BBox)
    if bbox.crs == CRS.WGS84:
        center_lon = (bbox.min_x + bbox.max_x) / 2
        center_lat = (bbox.min_y + bbox.max_y) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        return bbox.transform(utm_crs)
    return bbox


def adjust_resolution(bbox: BBox, resolution: float, max_pixels: int = 2500) -> float:
    """
    Adjusts resolution if the resulting image dimensions would exceed API limits.

    If the bounding box divided by the resolution produces more than ``max_pixels``
    pixels along any axis, the resolution is increased to stay within the limit.

    :param bbox: Bounding box in UTM (meters).
    :type bbox: BBox
    :param resolution: Desired pixel resolution in meters.
    :type resolution: float
    :param max_pixels: Maximum allowed pixels per axis (Sentinel Hub limit).
    :type max_pixels: int
    :return: Safe resolution that stays within pixel limits.
    :rtype: float
    """
    assert resolution > 0
    assert max_pixels > 0
    width_m = bbox.max_x - bbox.min_x
    height_m = bbox.max_y - bbox.min_y
    max_dimension_m = max(width_m, height_m)

    if max_dimension_m / resolution > max_pixels:
        resolution = float(int(np.ceil(max_dimension_m / max_pixels)))

    return resolution


def compute_pixel_dimensions(bbox: BBox, resolution: float) -> tuple[int, int]:
    """
    Computes the width and height in pixels for a given BBox and resolution.

    :param bbox: Bounding box in UTM (meters).
    :type bbox: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :return: Width and height in pixels as a tuple (width, height).
    :rtype: tuple[int, int]
    """
    width_m = bbox.max_x - bbox.min_x
    height_m = bbox.max_y - bbox.min_y
    return int(np.ceil(width_m / resolution)), int(np.ceil(height_m / resolution))
