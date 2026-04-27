"""
Water area computation from pixel masks.
"""

import numpy as np
from sentinelhub import BBox
from sentinel.tile_stream import split_bbox_into_tiles
from sentinel.request import request_sentinel_data
from sentinel.ndwi import compute_ndwi, water_mask
from objects import WaterAreaResult
from typing import Tuple


def get_pixel_area(dam_mask: np.ndarray, resolution: float) -> float:
    """
    Computes total water area in square meters from a binary mask.

    :param dam_mask: Binary water mask.
    :type dam_mask: np.ndarray
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :return: Total water area in square meters.
    :rtype: float
    """
    water_pixels = np.sum(dam_mask)
    water_area = water_pixels * resolution * resolution
    return float(water_area)


def recurse_pixel_area(
    expanded_dam_bbox: BBox,
    time_interval: Tuple[str, str],
    resolution: int = 20,
    tile_size_m: int = 2000,
    threshold: float = 0.2,
) -> WaterAreaResult:
    """
    Computes water area by tiling a large bounding box and summing pixel counts.

    :param expanded_dam_bbox: Bounding box to tile and process.
    :type expanded_dam_bbox: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param resolution: Pixel resolution in meters.
    :type resolution: int
    :param tile_size_m: Tile size in meters.
    :type tile_size_m: int
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :return: Water area result containing area in m² and km².
    :rtype: WaterAreaResult
    """
    total_water_pixels: int = 0
    for i, tile in enumerate(split_bbox_into_tiles(expanded_dam_bbox, tile_size_m=tile_size_m)):
        try:
            data = request_sentinel_data(
                aoi=tile,
                time_interval=time_interval,
                resolution=resolution,
            )
        except Exception as e:
            print("Skipping tile due to error:", e)
            continue
        ndwi = compute_ndwi(data)
        mask = water_mask(ndwi, threshold)
        total_water_pixels += np.sum(mask)
    pixel_area = resolution * resolution
    water_area_m2 = float(total_water_pixels * pixel_area)
    water_area_km2 = water_area_m2 / 1_000_000
    return WaterAreaResult(area_m2=water_area_m2, area_km2=water_area_km2)