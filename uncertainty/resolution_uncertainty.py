from objects import ResolutionUncertainty
from objects import Dam
from pipeline.acquisition import get_expansion, acquire_aoi
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from typing import Any
from sentinelhub import BBox

def resolution_sensitivity(
        dam : Dam,
        resolution : float,
        dam_bbox : BBox,
        time_interval : Any,
        step : float = 10,
        sampling_density : int = 5
    ) -> ResolutionUncertainty:
    """
    Calculates the sensitivity of a dam to the resolution of the satellite data. It does this by sampling different resolutions around the given resolution and calculating the area for each of those resolutions. The uncertainty is then calculated based on the range of areas obtained from the different resolutions.
    """
    assert resolution > 0, "Resolution must be positive"
    assert step > 0, "Step must be positive"
    assert sampling_density > 0, "Sampling density must be positive"
    assert resolution - step*sampling_density >= 10

    resolutions = [resolution + step * i for i in range(-sampling_density, sampling_density + 1)]
    areas_km2 = []

    from pipeline.utilities import ensure_utm
    aoi = dam_bbox
    aoi = ensure_utm(aoi)

    for reso in resolutions:
        data = acquire_satellite_data(
            expanded_dam_bbox=aoi,
            time_interval=time_interval,
            resolution=reso,
            wants_rgb=False,
            wants_ndwi=False,
            wants_mask=True,
            wants_area=False,
            wants_debugs=False
        )
        water = choose_reservoir(
            dam_mask=data.mask,
            expanded_dam_bbox=aoi,
            dam=dam,
            resolution=reso,
            min_area_km2=0.01,
            wants_debugs=False
        )
        areas_km2.append(water.area_km2) # convert to km2
    return ResolutionUncertainty(resolutions=resolutions, areas_km2=areas_km2)