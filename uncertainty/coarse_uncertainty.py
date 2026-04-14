import time
from typing import Any, List
from concurrent.futures import ThreadPoolExecutor

from objects import CoarseUncertainty, Dam
from pipeline.acquisition import get_expansion, acquire_aoi
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from pipeline.utilities import ensure_utm, adjust_resolution

def coarse_resolution_sensitivity(
        dam : Dam,
        base_resolution: float,
        time_interval: Any,
        coarse_resolutions: List[float] = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    ) -> CoarseUncertainty:
    """
    Calculates the sensitivity of the initial bounding box expansion and final reservoir area
    to the coarse resolution used in the expansion finding step.
    """
    
    tested_resolutions = []
    bbox_areas_km2 = []
    reservoir_areas_km2 = []
    times_taken = []
    
    def process_coarse_resolution(c_reso: float):
        start_time = time.time()
        # 1. Get expansion using the specified coarse resolution
        expansion = 50000
        # 2. Get the bounding box from this expansion
        bbox = acquire_aoi(dam, expansion)
        end_time = time.time()
        time_taken_val = end_time - start_time
        
        # 3. Calculate BBox area in km2
        bbox_utm = ensure_utm(bbox)
        width_m = bbox_utm.max_x - bbox_utm.min_x
        height_m = bbox_utm.max_y - bbox_utm.min_y
        bbox_area_km2 = (width_m * height_m) / 1e6
        
        # 4. Calculate reservoir area using base resolution
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
                wants_debugs=False
            )
            water = choose_reservoir(
                dam_mask=data.mask,
                expanded_dam_bbox=bbox_utm,
                dam=dam,
                resolution=safe_base_reso,
                min_area_km2=0.01,
                wants_debugs=False
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
        times_taken=times_taken
    )
