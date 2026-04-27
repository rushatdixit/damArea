"""
Satellite data acquisition pipeline with SAR failover and debug logging.
"""

import os
import numpy as np
from typing import Tuple, List
from sentinelhub import CRS, BBox
from sentinel.ndwi import compute_ndwi, water_mask
from sentinel.request import request_rgb_data, request_sentinel_data, request_sar_data
from sentinel.sar import sar_water_mask
from sentinel.tile_stream import split_bbox_into_tiles
from objects import SatelliteData
from utils.logger import get_logger

logger = get_logger(__name__)


def acquire_satellite_data(
    expanded_dam_bbox: BBox,
    time_interval: Tuple[str, str],
    resolution: float = 10,
    threshold: float = 0.3,
    wants_rgb: bool = True,
    wants_ndwi: bool = True,
    wants_mask: bool = True,
    wants_area: bool = False,
    wants_debugs: bool = True,
    use_sar: bool = False,
) -> SatelliteData:
    """
    Acquires and processes satellite imagery from Sentinel Hub.

    Supports both optical (Sentinel-2) and SAR (Sentinel-1) modes.
    When debug/verbose environment variables are set, saves intermediate
    diagnostic images to the corresponding directories.

    :param expanded_dam_bbox: UTM bounding box of the area of interest.
    :type expanded_dam_bbox: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :param wants_rgb: Whether to fetch RGB composite.
    :type wants_rgb: bool
    :param wants_ndwi: Whether to compute NDWI.
    :type wants_ndwi: bool
    :param wants_mask: Whether to generate water mask.
    :type wants_mask: bool
    :param wants_area: Whether to compute total water area.
    :type wants_area: bool
    :param wants_debugs: Whether to print debug statements.
    :type wants_debugs: bool
    :param use_sar: Whether to use SAR instead of optical.
    :type use_sar: bool
    :return: Container with satellite-derived products.
    :rtype: SatelliteData
    """
    rgb = None
    ndwi_arr = None
    mask_arr = None
    water_area = None

    assert expanded_dam_bbox.crs != CRS.WGS84, "acquire_satellite_data requires UTM bbox"
    assert resolution > 0, "Resolution must be positive"

    debug_dir = os.environ.get("DAM_DEBUG_DIR")
    verbose_dir = os.environ.get("DAM_VERBOSE_DIR")
    is_log = bool(debug_dir or verbose_dir)

    if is_log:
        import time
        import matplotlib.pyplot as plt
        from pipeline.visuals import normalize_rgb

        time.sleep(1.5)
        if wants_debugs:
            logger.info("Applying 1.5s Rate Limiter to protect Sentinel Hub API limits.")

        if not use_sar:
            wants_rgb = True

        try:
            start_str, end_str = time_interval
            interval_stamp = f"{start_str}_to_{end_str}"
        except:
            interval_stamp = str(time_interval).replace('/', '-')

    if use_sar:
        if wants_debugs:
            logger.info("Fetching SAR Radar Data...")
        sar_bands = request_sar_data(
            aoi=expanded_dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
        )
        if is_log and verbose_dir and np.array(sar_bands).size > 0:
            plt.figure(figsize=(8, 8))
            plt.imshow(normalize_rgb(np.array(sar_bands)), cmap="gray")
            plt.title(f"SAR VV Backscatter - {interval_stamp}")
            plt.savefig(os.path.join(verbose_dir, f"SAR_VV_{interval_stamp}.png"))
            plt.close()

        if wants_mask or wants_area:
            mask_arr = sar_water_mask(sar_bands)

            if is_log and verbose_dir and np.array(mask_arr).size > 0:
                plt.figure(figsize=(8, 8))
                plt.imshow(mask_arr, cmap="Blues")
                plt.title(f"SAR Water Mask - {interval_stamp}")
                plt.savefig(os.path.join(verbose_dir, f"SAR_Mask_{interval_stamp}.png"))
                plt.close()

            if wants_area:
                water_pixels = np.sum(mask_arr)
                water_area = float(water_pixels * resolution * resolution)

        return SatelliteData(
            rgb=None,
            ndwi=None,
            mask=mask_arr,
            sar=sar_bands,
            water_area_m2=water_area,
            resolution=resolution,
        )

    if wants_rgb:
        if wants_debugs:
            logger.info("Fetching RGB Data...")
        rgb = request_rgb_data(
            aoi=expanded_dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
        )
        if is_log and rgb is not None:
            rgb_arr = np.array(rgb)
            if rgb_arr.size > 0 and rgb_arr.shape[0] > 0 and rgb_arr.shape[1] > 0:
                plt.figure(figsize=(8, 8))
                plt.imshow(normalize_rgb(rgb_arr))
                plt.title(f"Optical RGB - {interval_stamp}")
                if debug_dir:
                    plt.savefig(os.path.join(debug_dir, f"RGB_{interval_stamp}.png"))
                if verbose_dir:
                    plt.savefig(os.path.join(verbose_dir, f"RGB_{interval_stamp}.png"))
                plt.close()

    needs_ndwi = wants_ndwi or wants_mask or wants_area
    if needs_ndwi:
        if wants_debugs:
            logger.info("Getting NDWI bands...")
        ndwi_bands = request_sentinel_data(
            aoi=expanded_dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
        )
        if wants_debugs:
            logger.info("Computing NDWI...")
        ndwi_arr = np.array(compute_ndwi(ndwi_bands))

        if is_log and verbose_dir and ndwi_arr.size > 0 and ndwi_arr.shape[0] > 0:
            plt.figure(figsize=(8, 8))
            plt.imshow(ndwi_arr, cmap="viridis")
            plt.title(f"NDWI Computed - {interval_stamp}")
            plt.savefig(os.path.join(verbose_dir, f"NDWI_{interval_stamp}.png"))
            plt.close()

    if wants_mask or wants_area:
        if wants_debugs:
            logger.info("Applying water threshold to NDWI...")
        mask_arr = np.array(water_mask(ndwi_arr.tolist(), threshold))

        if is_log and verbose_dir and mask_arr.size > 0 and mask_arr.shape[0] > 0:
            plt.figure(figsize=(8, 8))
            plt.imshow(mask_arr, cmap="Blues")
            plt.title(f"Optical Water Mask - {interval_stamp}")
            plt.savefig(os.path.join(verbose_dir, f"Optical_Mask_{interval_stamp}.png"))
            plt.close()

        if wants_area:
            water_pixels = np.sum(mask_arr)
            water_area = float(water_pixels * resolution * resolution)

    return SatelliteData(
        rgb=rgb,
        ndwi=ndwi_arr,
        mask=mask_arr,
        sar=None,
        water_area_m2=water_area,
        resolution=resolution,
    )


def make_grid(expanded_dam_bbox: BBox, tile_size: int = 2000) -> List[BBox]:
    """
    Splits a bounding box into a grid of tiles.

    :param expanded_dam_bbox: Bounding box to split.
    :type expanded_dam_bbox: BBox
    :param tile_size: Tile side length in meters.
    :type tile_size: int
    :return: List of tile bounding boxes.
    :rtype: List[BBox]
    """
    tiles = split_bbox_into_tiles(expanded_dam_bbox, tile_size_m=tile_size)
    return tiles
