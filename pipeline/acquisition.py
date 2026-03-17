from typing import Any
import numpy as np
from sentinelhub import BBox
from fetch_dam.get_dam import dam_name_to_bbox
from sentinel.aoi import expand_bbox_meters
from sentinel.request import request_sentinel_data
from sentinel.ndwi import water_mask
from sentinelhub import CRS, BBox
from objects.dam import Dam
from constants import INITIAL_EXPANSION, BREAKING_EXPANSION, BOUNDARY_PIXELS_THRESHOLD

def acquire_aoi(dam : Dam, expansion : int) -> BBox:
    """
    Given a Dam and an expansion, gives you the dam bbox expanded by "expansion" meters on all sides.
    
    :param dam: The Dam object
    :type dam: Dam
    :param expansion: Expansion in metres
    :type expansion: int
    :return: Expanded dam bbox
    :rtype: BBox
    """
    dam_bbox = dam_name_to_bbox(dam.name)
    expanded_dam_bbox = expand_bbox_meters(dam_bbox, expansion)
    return expanded_dam_bbox

def get_expansion(
        dam : Dam,
        time_interval : Any,       
        initial_expansion : int = INITIAL_EXPANSION, 
        resolution : int = 500, 
        threshold : int = BOUNDARY_PIXELS_THRESHOLD,
        breaking_expansion : int = BREAKING_EXPANSION
        ) -> int:
    """
    Given a dam name, finds the optimal expansion. \n ie. you don't have to guess the expansion anymore.

    :param dam: The Dam object
    :type dam: Dam
    :param initial_expansion: Initial BBox obtained, set to 2Kms
    :type initial_expansion: int
    :param threshold: Minimum number of water pixels which touch the BBox
    :type threshold: int
    """

    initial_bbox = acquire_aoi(dam=dam, expansion=initial_expansion)
    bbox = initial_bbox

    from pipeline.utilities import ensure_utm, adjust_resolution
    while True:

        # API resolution limit check (Needs UTM to calculate Max Pixels correctly)
        bbox_utm = ensure_utm(bbox)
        safe_resolution = adjust_resolution(bbox_utm, resolution)

        ndwi_bands = request_sentinel_data(
            aoi=bbox,
            time_interval=time_interval,
            resolution=safe_resolution
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
    
    return initial_expansion+initial_expansion/10