"""
Streaming tile-based Sentinel water area processor
"""

import numpy as np
from sentinelhub import CRS, BBox
from sentinelhub import transform_point

from sentinel.request import request_sentinel_data
from sentinel.ndwi import compute_ndwi, water_mask


def split_bbox_into_tiles(bbox: BBox, tile_size_m: int):
    """
    Splits a bbox into square tiles in meters (UTM space).
    Accepts bbox in either WGS84 or UTM.
    """

    if bbox.crs == CRS.WGS84:

        center_lon = (bbox.min_x + bbox.max_x) / 2
        center_lat = (bbox.min_y + bbox.max_y) / 2

        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)

        bbox = bbox.transform(utm_crs)

    else:
        utm_crs = bbox.crs

    min_x, min_y, max_x, max_y = bbox

    tiles = []

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
    time_interval,
    resolution: int = 20,
    tile_size_m: int = 2000,
    threshold: float = 0.2,
):
    """
    Streams Sentinel tiles and accumulates water area.
    """

    tiles = split_bbox_into_tiles(bbox, tile_size_m)

    total_water_pixels = 0

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
    water_area_m2 = total_water_pixels * pixel_area
    water_area_km2 = water_area_m2 / 1_000_000

    return water_area_m2, water_area_km2
