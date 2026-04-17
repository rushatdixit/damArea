from sentinelhub import SentinelHubRequest, DataCollection, MimeType, CRS
from sentinel.config import get_sh_config
from sentinel.evalscripts import NDWI_EVALSCRIPT, RGB_EVALSCRIPT
from constants import DEFAULT_RESOLUTION
import time
from functools import wraps
import os

class NoImageryFoundError(Exception):
    pass

from joblib import Memory

cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.cache')
memory = Memory(cache_dir, verbose=0)

def retry_with_backoff(retries=5, backoff_in_seconds=2):
    """
    Retry decorator with exponential backoff.
    """
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        print(f"Failed after {retries} retries.")
                        raise e
                    sleep_time = (backoff_in_seconds * 2 ** x)
                    print(f"Request failed: {e}. Retrying in {sleep_time} seconds (Attempt {x+1}/{retries})...")
                    time.sleep(sleep_time)
                    x += 1
        return wrapped
    return wrapper

@memory.cache
@retry_with_backoff()
def request_sentinel_data(aoi, time_interval, resolution=DEFAULT_RESOLUTION):

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
    if not data:
        raise NoImageryFoundError(f"No Sentinel data found for interval {time_interval}")
    return data[0]

@memory.cache
@retry_with_backoff()
def request_rgb_data(aoi, time_interval, resolution=DEFAULT_RESOLUTION):

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
    if not data:
        raise NoImageryFoundError(f"No RGB data found for interval {time_interval}")
    return data[0]