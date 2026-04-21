"""
AOI acquisition and expansion optimization for dam detection.
"""

import numpy as np
from typing import Tuple
from sentinelhub import BBox
from fetch_dam.get_dam import dam_name_to_bbox
from sentinel.aoi import expand_bbox_meters
from sentinel.request import request_sentinel_data
from sentinel.ndwi import water_mask
from objects import Dam
from constants import INITIAL_EXPANSION, BREAKING_EXPANSION, BOUNDARY_PIXELS_THRESHOLD


def acquire_aoi(dam: Dam, expansion: int) -> BBox:
    """
    Creates an expanded bounding box around the dam coordinates.

    :param dam: Dam object with name and coordinates.
    :type dam: Dam
    :param expansion: Expansion distance in meters on all sides.
    :type expansion: int
    :return: Expanded bounding box in WGS84.
    :rtype: BBox
    """
    dam_bbox = dam_name_to_bbox(dam.name)
    expanded_dam_bbox = expand_bbox_meters(dam_bbox, expansion)
    return expanded_dam_bbox


def get_expansion(
    dam: Dam,
    time_interval: Tuple[str, str],
    initial_expansion: int = INITIAL_EXPANSION,
    resolution: int = 500,
    threshold: int = BOUNDARY_PIXELS_THRESHOLD,
    breaking_expansion: int = BREAKING_EXPANSION,
) -> float:
    """
    Finds the optimal expansion distance by iteratively checking whether
    water pixels touch the bounding box border.

    :param dam: Dam object to build the AOI around.
    :type dam: Dam
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param initial_expansion: Starting expansion in meters.
    :type initial_expansion: int
    :param resolution: Coarse resolution in meters for the border check.
    :type resolution: int
    :param threshold: Minimum boundary water pixels to trigger expansion.
    :type threshold: int
    :param breaking_expansion: Maximum expansion before giving up.
    :type breaking_expansion: int
    :return: Optimal expansion distance in meters.
    :rtype: float
    """
    initial_bbox = acquire_aoi(dam=dam, expansion=initial_expansion)
    bbox = initial_bbox

    from pipeline.utilities import ensure_utm, adjust_resolution
    while True:
        bbox_utm = ensure_utm(bbox)
        safe_resolution = adjust_resolution(bbox_utm, resolution)

        ndwi_bands = request_sentinel_data(
            aoi=bbox,
            time_interval=time_interval,
            resolution=safe_resolution,
        )

        mask = water_mask(ndwi_bands)
        mask = np.array(mask)

        top = mask[0, :]
        bottom = mask[-1, :]
        left = mask[:, 0]
        right = mask[:, -1]

        boundary_pixels = (
            top.sum() +
            bottom.sum() +
            left.sum() +
            right.sum()
        )

        if boundary_pixels < threshold:
            break

        initial_expansion += 2000
        if initial_expansion > breaking_expansion:
            break

        bbox = expand_bbox_meters(initial_bbox, initial_expansion)

    return initial_expansion + initial_expansion / 10