"""
Spatial resolution sensitivity analysis.
"""

from typing import Tuple, List, Optional
from sentinelhub import BBox
from concurrent.futures import ThreadPoolExecutor
from objects import ResolutionUncertainty, Dam
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir


def resolution_sensitivity(
    dam: Dam,
    resolution: float,
    dam_bbox: BBox,
    time_interval: Tuple[str, str],
    step: float = 10,
    sampling_density: int = 5,
) -> ResolutionUncertainty:
    """
    Measures how reservoir area changes when the spatial resolution is varied.

    Sweeps resolution from ``resolution - step*sampling_density``
    to ``resolution + step*sampling_density`` and records the detected area
    at each value. Skips resolutions that exceed the Sentinel API pixel limit.

    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param resolution: Centre resolution in meters.
    :type resolution: float
    :param dam_bbox: UTM bounding box of the reservoir.
    :type dam_bbox: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param step: Resolution increment in meters.
    :type step: float
    :param sampling_density: Number of steps above and below centre.
    :type sampling_density: int
    :return: Resolution uncertainty containing tested resolutions and areas.
    :rtype: ResolutionUncertainty
    """
    assert resolution > 0, "Resolution must be positive"
    assert step > 0, "Step must be positive"
    assert sampling_density > 0, "Sampling density must be positive"
    assert resolution - step * sampling_density >= 10

    resolutions = [resolution + step * i for i in range(-sampling_density, sampling_density + 1)]

    from pipeline.utilities import ensure_utm, adjust_resolution
    aoi = ensure_utm(dam_bbox)

    def process_resolution(reso: float) -> Optional[Tuple[float, float]]:
        """
        Processes a single resolution sample.

        :param reso: Resolution to test in meters.
        :type reso: float
        :return: Tuple of (resolution, area_km2) or None if skipped.
        :rtype: Optional[Tuple[float, float]]
        """
        if adjust_resolution(aoi, resolution=reso) != reso:
            print(f"Skipping {reso}m resolution (exceeds Sentinel API 2500x2500 limit).")
            return None

        data = acquire_satellite_data(
            expanded_dam_bbox=aoi,
            time_interval=time_interval,
            resolution=reso,
            wants_rgb=False,
            wants_ndwi=False,
            wants_mask=True,
            wants_area=False,
            wants_debugs=False,
        )
        water = choose_reservoir(
            dam_mask=data.mask,
            expanded_dam_bbox=aoi,
            dam=dam,
            resolution=reso,
            min_area_km2=0.01,
            wants_debugs=False,
        )
        return (reso, water.area_km2)

    tested_resolutions: List[float] = []
    areas_km2: List[float] = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_resolution, resolutions)

    for res in results:
        if res is not None:
            tested_resolutions.append(res[0])
            areas_km2.append(res[1])

    return ResolutionUncertainty(resolutions=tested_resolutions, areas_km2=areas_km2)