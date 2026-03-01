import numpy as np
from sentinelhub import BBox, CRS
from processing.select_reservoir import select_reservoir_connected_to_dam
from processing.mask_processing import largest_connected_component
from pipeline.models import ReservoirResult

def choose_reservoir(
        dam_mask : np.ndarray,
        expanded_dam_bbox : BBox,
        dam_lat : float,
        dam_lon : float,
        resolution : float,
        min_area_km2 : float = 0.01,
        wants_debugs : bool = True
    ) -> ReservoirResult:

    assert expanded_dam_bbox.crs != CRS.WGS84, \
        "choose_reservoir requires UTM bbox"
    assert isinstance(dam_lat, float)
    assert isinstance(dam_lon, float)
    assert dam_mask.ndim == 2, \
        "dam_mask must be 2D"
    assert resolution > 0

    selected_mask = select_reservoir_connected_to_dam(
        dam_mask,
        dam_lat,
        dam_lon,
        expanded_dam_bbox,
        resolution,
        min_area_km2,
        wants_debugs
        )
    selected_contour = largest_connected_component(selected_mask[0])
    water_pixels = np.sum(selected_mask[0])
    area_km2 = (water_pixels * resolution * resolution) / 1_000_000
    return ReservoirResult(
        mask = selected_mask,
        contour = selected_contour,
        area_km2 = area_km2
        )
