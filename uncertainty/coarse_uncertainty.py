"""
Coarse resolution sensitivity analysis for bounding box acquisition.
"""

import time
from typing import Tuple, List, Optional
from concurrent.futures import ThreadPoolExecutor

from objects import CoarseUncertainty, Dam
from pipeline.acquisition import acquire_aoi
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from pipeline.utilities import ensure_utm, adjust_resolution


def coarse_resolution_sensitivity(
    dam: Dam,
    base_resolution: float,
    time_interval: Tuple[str, str],
    coarse_resolutions: List[float] = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
) -> CoarseUncertainty:
    """
    Measures how the bounding box size and detected reservoir area vary
    with the coarse resolution used during the initial expansion scan.

    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param base_resolution: Resolution in meters for the final area computation.
    :type base_resolution: float
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param coarse_resolutions: List of coarse resolutions to test.
    :type coarse_resolutions: List[float]
    :return: Coarse uncertainty containing tested resolutions, bbox areas, reservoir areas, and timings.
    :rtype: CoarseUncertainty
    """
    tested_resolutions: List[float] = []
    bbox_areas_km2: List[float] = []
    reservoir_areas_km2: List[float] = []
    times_taken: List[float] = []

    def process_coarse_resolution(c_reso: float) -> Optional[Tuple[float, float, float, float]]:
        """
        Processes a single coarse resolution sample.

        :param c_reso: Coarse resolution to test in meters.
        :type c_reso: float
        :return: Tuple of (resolution, bbox_area_km2, reservoir_area_km2, time_taken) or None.
        :rtype: Optional[Tuple[float, float, float, float]]
        """
        start_time = time.time()
        expansion = 50000
        bbox = acquire_aoi(dam, expansion)
        end_time = time.time()
        time_taken_val = end_time - start_time

        bbox_utm = ensure_utm(bbox)
        width_m = bbox_utm.max_x - bbox_utm.min_x
        height_m = bbox_utm.max_y - bbox_utm.min_y
        bbox_area_km2 = (width_m * height_m) / 1e6

        try:
            safe_base_reso = adjust_resolution(bbox_utm, base_resolution)
            data = acquire_satellite_data(
                expanded_dam_bbox=bbox_utm,
                time_interval=time_interval,
                resolution=safe_base_reso,
                wants_rgb=False,
                wants_ndwi=False,
                wants_mask=True,
                wants_area=False,
                wants_debugs=False,
            )
            water = choose_reservoir(
                dam_mask=data.mask,
                expanded_dam_bbox=bbox_utm,
                dam=dam,
                resolution=safe_base_reso,
                min_area_km2=0.01,
                wants_debugs=False,
            )
            water_area_km2 = water.area_km2
        except Exception as e:
            print(f"Error processing reservoir for coarse resolution {c_reso}: {e}")
            water_area_km2 = None

        return (c_reso, bbox_area_km2, water_area_km2, time_taken_val)

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_coarse_resolution, coarse_resolutions)

    for res in results:
        if res is not None and res[2] is not None:
            tested_resolutions.append(res[0])
            bbox_areas_km2.append(res[1])
            reservoir_areas_km2.append(res[2])
            times_taken.append(res[3])

    return CoarseUncertainty(
        coarse_resolutions=tested_resolutions,
        bbox_areas_km2=bbox_areas_km2,
        reservoir_areas_km2=reservoir_areas_km2,
        times_taken=times_taken,
    )
