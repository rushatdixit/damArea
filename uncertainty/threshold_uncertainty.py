"""
Threshold sensitivity analysis for NDWI water classification.
"""

import numpy as np
from typing import Tuple
from sentinelhub import BBox
from sentinel.ndwi import water_mask
from pipeline.processing import choose_reservoir
from pipeline.raw_data import acquire_satellite_data
from pipeline.data_to_area import get_pixel_area
from objects import ThresholdUncertainty, Dam


def threshold_sensitivity(
    dam_bbox: BBox,
    resolution: float,
    time_interval: Tuple[str, str],
    dam: Dam,
    threshold: float = 0.2,
    epsilon: float = 0.01,
    sampling_density: int = 10,
) -> ThresholdUncertainty:
    """
    Measures how reservoir area changes when the NDWI threshold is varied.

    Sweeps the threshold from ``threshold - epsilon`` to ``threshold + epsilon``
    in ``sampling_density`` steps and records the detected area at each value.

    :param dam_bbox: UTM bounding box of the reservoir.
    :type dam_bbox: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param threshold: Centre NDWI threshold value.
    :type threshold: float
    :param epsilon: Half-width of the threshold sweep range.
    :type epsilon: float
    :param sampling_density: Number of threshold steps to evaluate.
    :type sampling_density: int
    :return: Threshold uncertainty containing tested thresholds and areas.
    :rtype: ThresholdUncertainty
    """
    n = 2 * epsilon / sampling_density
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
        wants_debugs=False,
    )

    for i in range(sampling_density + 1):
        used_threshold = threshold - epsilon + i * n

        mask = np.array(water_mask(satellite_data.ndwi, threshold=used_threshold))

        selected_reservoir = choose_reservoir(
            dam_mask=mask,
            expanded_dam_bbox=dam_bbox,
            dam=dam,
            resolution=resolution,
            min_area_km2=0.01,
            wants_debugs=False,
        )

        area = get_pixel_area(
            selected_reservoir.mask[0],
            resolution=resolution,
        )

        lst_of_areas.append(area / 1000000)
        lst_of_thresholds.append(used_threshold)

    return ThresholdUncertainty(thresholds=lst_of_thresholds, areas_km2=lst_of_areas)