"""
Tile-based streaming water area processor for large bounding boxes.
"""

import numpy as np
from typing import List, Tuple
from sentinelhub import CRS, BBox
from sentinel.request import request_sentinel_data
from sentinel.ndwi import compute_ndwi, water_mask
from objects import WaterAreaResult


def split_bbox_into_tiles(bbox: BBox, tile_size_m: int) -> List[BBox]:
    """
    Splits a bounding box into square tiles in UTM space.

    :param bbox: Bounding box in WGS84 or UTM.
    :type bbox: BBox
    :param tile_size_m: Side length of each tile in meters.
    :type tile_size_m: int
    :return: List of tile bounding boxes in UTM.
    :rtype: List[BBox]
    """
    if bbox.crs == CRS.WGS84:
        center_lon = (bbox.min_x + bbox.max_x) / 2
        center_lat = (bbox.min_y + bbox.max_y) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        bbox = bbox.transform(utm_crs)
    else:
        utm_crs = bbox.crs

    min_x, min_y, max_x, max_y = bbox

    tiles: List[BBox] = []

    x = min_x
    while x < max_x:
        y = min_y
        while y < max_y:
            tile = BBox(
                bbox=[
                    x,
                    y,
                    min(x + tile_size_m, max_x),
                    min(y + tile_size_m, max_y),
                ],
                crs=utm_crs,
            )
            tiles.append(tile)
            y += tile_size_m
        x += tile_size_m

    return tiles


def stream_water_area(
    bbox: BBox,
    time_interval: Tuple[str, str],
    resolution: int = 20,
    tile_size_m: int = 2000,
    threshold: float = 0.2,
) -> WaterAreaResult:
    """
    Streams Sentinel-2 tiles and accumulates total water area.

    :param bbox: Bounding box to process.
    :type bbox: BBox
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
    tiles = split_bbox_into_tiles(bbox, tile_size_m)

    total_water_pixels: int = 0

    print(f"Processing {len(tiles)} tiles...")

    for i, tile in enumerate(tiles):
        print(f"Tile {i+1}/{len(tiles)}")

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
