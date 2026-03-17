import numpy as np
from typing import Any
from sentinelhub import BBox
from sentinel.ndwi import water_mask
from pipeline.processing import choose_reservoir
from pipeline.raw_data import acquire_satellite_data
from pipeline.data_to_area import get_pixel_area
from objects import ThresholdUncertainty
from objects import Dam
def threshold_sensitivity(
        dam_bbox : BBox,
        resolution : float,
        time_interval : Any,
        dam : Dam,
        threshold : float = 0.2,
        epsilon : float = 0.01,
        sampling_density : int = 10
    ) -> ThresholdUncertainty:
    """
    Generates the uncertainty for the ndwi threshold
    """
    n = 2*epsilon/sampling_density
    lst_of_areas = []
    lst_of_thresholds = []

    satellite_data = acquire_satellite_data(
            dam_bbox,
            time_interval=time_interval,
            resolution=resolution,
            threshold=threshold,
            wants_rgb=False,
            wants_mask=False,
            wants_area=False,
            wants_debugs=False
        )

    for i in range(sampling_density+1):
        used_threshold = threshold - epsilon + i*n

        mask = np.array(water_mask(satellite_data.ndwi, threshold=used_threshold))

        selected_reservoir = choose_reservoir(
                dam_mask=mask,
                expanded_dam_bbox=dam_bbox,
                dam=dam,
                resolution=resolution,
                min_area_km2=0.01,
                wants_debugs=False
            )

        area = get_pixel_area(
            selected_reservoir.mask[0],
            resolution=resolution
        )

        lst_of_areas.append(area/1000000)
        lst_of_thresholds.append(used_threshold)
    
    result = ThresholdUncertainty(lst_of_thresholds, lst_of_areas)
    return result