"""
This is the file which actually extracts data from sentinel hub by sending a request
SENTINEL_L2A = surface reflectance which is atmostpherically corrected
maxcc = maximum fraction of cloud coverage 
time interval = date range 
"""

from sentinelhub import SentinelHubRequest, DataCollection
from sentinelhub import MimeType
from sentinelhub import CRS, Geometry

from sentinel.config import get_sh_config
from sentinel.evalscripts import NDWI_EVALSCRIPT, RGB_EVALSCRIPT

def request_sentinel_data(aoi, time_interval, resolution=10):
    centroid = aoi.geometry.centroid
    lon = centroid.x
    lat = centroid.y
    utm_crs = CRS.get_utm_from_wgs84(lon, lat)
    aoi_utm = aoi.transform(utm_crs)

    config = get_sh_config()

    request = SentinelHubRequest(
        evalscript=NDWI_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                maxcc=0.2
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        geometry=aoi_utm,
        config=config,
        resolution=(resolution,resolution)
    )

    return request.get_data()[0]

def request_rgb_data(aoi, time_interval, resolution):
    centroid = aoi.geometry.centroid
    lon = centroid.x
    lat = centroid.y
    utm_crs = CRS.get_utm_from_wgs84(lon, lat)
    aoi_utm = aoi.transform(utm_crs)

    config = get_sh_config()

    request = SentinelHubRequest(
        evalscript=RGB_EVALSCRIPT,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L2A,
                time_interval=time_interval,
                maxcc=0.2
            )
        ],
        responses=[
            SentinelHubRequest.output_response("default", MimeType.TIFF)
        ],
        geometry=aoi_utm,   # <-- match NDWI request
        resolution=(resolution, resolution),
        config=config
    )

    return request.get_data()[0]
