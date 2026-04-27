"""
Sentinel Hub API request functions with caching and retry logic.
"""

from sentinelhub import SentinelHubRequest, DataCollection, MimeType, CRS, BBox
from sentinel.config import get_sh_config
from sentinel.evalscripts import NDWI_EVALSCRIPT, RGB_EVALSCRIPT, SAR_VV_EVALSCRIPT
from constants import DEFAULT_RESOLUTION
import numpy as np
import time
import os
from typing import Tuple
from functools import wraps

from joblib import Memory
from utils.logger import get_logger

logger = get_logger(__name__)


class NoImageryFoundError(Exception):
    """Raised when a Sentinel Hub request returns empty or all-zero data."""
    pass


cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.cache')
memory = Memory(cache_dir, verbose=0)


def retry_with_backoff(retries: int = 5, backoff_in_seconds: int = 2):
    """
    Decorator that retries a function with exponential backoff on failure.

    :param retries: Maximum number of retry attempts.
    :type retries: int
    :param backoff_in_seconds: Base delay in seconds (doubled each retry).
    :type backoff_in_seconds: int
    :return: Decorated function.
    :rtype: callable
    """
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if isinstance(e, NoImageryFoundError):
                        raise e
                    if x == retries:
                        logger.error(f"Failed after {retries} retries.")
                        raise e
                    sleep_time = (backoff_in_seconds * 2 ** x)
                    logger.warning(f"Request failed: {e}. Retrying in {sleep_time} seconds (Attempt {x+1}/{retries})...")
                    time.sleep(sleep_time)
                    x += 1
        return wrapped
    return wrapper


@memory.cache
@retry_with_backoff()
def request_sentinel_data(
    aoi: BBox,
    time_interval: Tuple[str, str],
    resolution: float = DEFAULT_RESOLUTION,
) -> np.ndarray:
    """
    Fetches Sentinel-2 NDWI bands (Green, NIR, SCL) from the Sentinel Hub API.

    :param aoi: Bounding box for the area of interest (WGS84 or UTM).
    :type aoi: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :return: 3D array of shape (H, W, 3) with Green, NIR, SCL bands.
    :rtype: np.ndarray
    :raises NoImageryFoundError: If no valid data is returned.
    """
    config = get_sh_config()

    if aoi.crs == CRS.WGS84:
        min_lon, min_lat, max_lon, max_lat = aoi
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        bbox_utm = aoi.transform(utm_crs)
    else:
        bbox_utm = aoi

    request = SentinelHubRequest(
        evalscript=NDWI_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                maxcc=0.2,
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        bbox=bbox_utm,
        resolution=(resolution, resolution),
        config=config,
    )

    data = request.get_data()
    if not data or np.all(data[0] == 0):
        raise NoImageryFoundError(f"No Sentinel data found for interval {time_interval}")
    return data[0]


@memory.cache
@retry_with_backoff()
def request_rgb_data(
    aoi: BBox,
    time_interval: Tuple[str, str],
    resolution: float = DEFAULT_RESOLUTION,
    maxcc: float = 0.2,
) -> np.ndarray:
    """
    Fetches Sentinel-2 RGB composite (B04, B03, B02) from the Sentinel Hub API.

    :param aoi: Bounding box for the area of interest (WGS84 or UTM).
    :type aoi: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param maxcc: Maximum cloud cover fraction (0.0 to 1.0).
    :type maxcc: float
    :return: 3D array of shape (H, W, 3) with R, G, B bands.
    :rtype: np.ndarray
    :raises NoImageryFoundError: If no valid data is returned.
    """
    config = get_sh_config()

    if aoi.crs == CRS.WGS84:
        min_lon, min_lat, max_lon, max_lat = aoi
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        bbox_utm = aoi.transform(utm_crs)
    else:
        bbox_utm = aoi

    request = SentinelHubRequest(
        evalscript=RGB_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                maxcc=maxcc,
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        bbox=bbox_utm,
        resolution=(resolution, resolution),
        config=config,
    )

    data = request.get_data()
    if not data or np.all(data[0] == 0):
        raise NoImageryFoundError(f"No RGB data found for interval {time_interval}")
    return data[0]


@memory.cache
@retry_with_backoff()
def request_sar_data(
    aoi: BBox,
    time_interval: Tuple[str, str],
    resolution: float = DEFAULT_RESOLUTION,
) -> np.ndarray:
    """
    Fetches Sentinel-1 SAR VV backscatter from the Sentinel Hub API.

    :param aoi: Bounding box for the area of interest (WGS84 or UTM).
    :type aoi: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :return: 2D or 3D array of VV backscatter values (linear scale).
    :rtype: np.ndarray
    :raises NoImageryFoundError: If no valid data is returned.
    """
    config = get_sh_config()

    if aoi.crs == CRS.WGS84:
        min_lon, min_lat, max_lon, max_lat = aoi
        center_lon = (min_lon + max_lon) / 2
        center_lat = (min_lat + max_lat) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        bbox_utm = aoi.transform(utm_crs)
    else:
        bbox_utm = aoi

    request = SentinelHubRequest(
        evalscript=SAR_VV_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL1_IW,
                time_interval=time_interval,
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        bbox=bbox_utm,
        resolution=(resolution, resolution),
        config=config,
    )

    data = request.get_data()
    if not data or np.all(data[0] == 0):
        raise NoImageryFoundError(f"No SAR data found for interval {time_interval}")
    return data[0]