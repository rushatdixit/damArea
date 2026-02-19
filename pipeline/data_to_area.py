import numpy as np
from typing import Tuple
from sentinelhub import BBox
from sentinel.tile_stream import split_bbox_into_tiles
from sentinel.request2 import request_sentinel_data
from sentinel.ndwi import compute_ndwi, water_mask

def get_pixel_area(
        dam_mask : np.ndarray,
        resolution : float
    ) -> float:
    water_pixels = np.sum(dam_mask)
    water_area = water_pixels*resolution*resolution
    return water_area

def recurse_pixel_area(
        expanded_dam_bbox: BBox,
        time_interval,
        resolution: int = 20,
        tile_size_m: int = 2000,
        threshold: float = 0.2,
    ) -> Tuple[float, float]:
    total_water_pixels = 0
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
    water_area_m2 = total_water_pixels * pixel_area
    water_area_km2 = water_area_m2 / 1_000_000
    return (water_area_m2, water_area_km2)