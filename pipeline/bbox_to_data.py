import numpy as np
from sentinelhub import CRS, BBox
from sentinel.ndwi import compute_ndwi, water_mask
from sentinel.request2 import request_rgb_data, request_sentinel_data
from pipeline.utilities import ensure_utm, adjust_resolution
from pipeline.models import SatelliteData
def acquire_satellite_data(
            expanded_dam_bbox : BBox,
            time_interval,
            resolution : float = 10,
            threshold : float = 0.3,
            wants_rgb : bool = True,
            wants_ndwi : bool = True,
            wants_mask : bool = True,
            wants_area : bool = False,
            wants_debugs : bool = True
            ) -> SatelliteData:
    """
    Acquires satellite data via sentinel hub.
    
    :param expanded_dam_bbox: The Expanded Bounding Box of the dam.
    :type expanded_dam_bbox: BBox
    :param resolution: resolution
    :type resolution: float
    :param time_interval: time_interval in dates for ex. 23/1/23 to 25/3/23 (not in this syntax)
    :param threshold: The ndwi threshold above which water pixels will be counted, should be 0.2 or 0.3
    :type threshold: float
    :param wants_rgb: If you want rgb data
    :type wants_rgb: bool
    :param wants_ndwi: If you want ndwi data (will be calculated anyways)
    :type wants_ndwi: bool
    :param wants_mask: If you want mask from ndwi
    :type wants_mask: bool
    :param wants_area: If you want area from water pixels only
    :type wants_area: bool
    :param wants_debugs: Will include debugging statements
    :type wants_debugs: bool
    :return: This tuple ---> (rgb, (ndwi, ndwi_arr), (mask, mask_arr), water_area), they will return None if corresponding bool is False
    :rtype: tuple
    """
    rgb = None
    ndwi = None
    ndwi_arr = None
    mask = None
    mask_arr = None
    water_pixels = 0
    water_area = 0
    #conversion to utm

    assert expanded_dam_bbox.crs != CRS.WGS84, \
    "acquire_satellite_data requires UTM bbox"
    assert resolution > 0, \
        "Resolution must be positive"
    
    if wants_rgb:
        print("Fetching RGB Data...")
        rgb = request_rgb_data(
            aoi=expanded_dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
        )
        if wants_debugs:
            print(f"RGB received | Shape: {np.array(rgb).shape}")

    needs_ndwi = wants_ndwi or wants_mask or wants_area
    if needs_ndwi:
        print("Getting NDWI bands...")
        ndwi_bands = request_sentinel_data(
            aoi=expanded_dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
        )
        print("Computing NDWI...")
        ndwi = compute_ndwi(ndwi_bands)
        ndwi_arr = np.array(ndwi)
        if wants_debugs and wants_ndwi:
            print(f"NDWI range: {np.nanmin(ndwi_arr):.3f} to {np.nanmax(ndwi_arr):.3f}")

    if wants_mask or wants_area:
        print("Applying water threshold to NDWI...")
        mask = water_mask(ndwi, threshold)
        mask_arr = np.array(mask)

    if wants_area:
        water_pixels = np.sum(mask_arr)
        water_area = water_pixels * resolution * resolution
        if wants_debugs:
            print(f"Water pixels: {water_pixels}")

    return SatelliteData(
    rgb=rgb,
    ndwi=ndwi_arr,
    mask=mask_arr,
    water_area_m2=water_area if wants_area else None,
    resolution=resolution,
)


from sentinel.tile_stream import split_bbox_into_tiles
def make_grid(
        expanded_dam_bbox : BBox,
        tile_size : int = 2000,
    ) -> list:
    tiles = split_bbox_into_tiles(expanded_dam_bbox, tile_size_m=tile_size)
    return tiles
