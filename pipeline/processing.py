import numpy as np
from sentinelhub import BBox, CRS
from processing.select_reservoir import select_reservoir_connected_to_dam
from processing.mask_processing import largest_connected_component
from objects.results import ReservoirResult
from objects.dam import Dam
from constants import MIN_AREA_KM2_PROCESSING

def choose_reservoir(
        dam_mask : np.ndarray,
        expanded_dam_bbox : BBox,
        dam : Dam,
        resolution : float,
        min_area_km2 : float = MIN_AREA_KM2_PROCESSING,
        wants_debugs : bool = True
    ) -> ReservoirResult:

    assert hasattr(expanded_dam_bbox, 'crs') and expanded_dam_bbox.crs != CRS.WGS84, \
        "choose_reservoir requires UTM bbox"
    assert isinstance(dam, Dam), "dam must be an instance of Dam class"
    assert dam_mask.ndim == 2, \
        "dam_mask must be 2D"
    assert resolution > 0

    selected_mask = select_reservoir_connected_to_dam(
        mask=dam_mask,
        dam=dam,
        bbox_utm=expanded_dam_bbox,
        resolution=resolution,
        min_area_km2=min_area_km2,
        is_debug=wants_debugs
        )
    selected_contour = largest_connected_component(selected_mask[0])
    water_pixels = np.sum(selected_mask[0])
    area_km2 = (water_pixels * resolution * resolution) / 1_000_000
    return ReservoirResult(
        mask = selected_mask,
        contour = selected_contour,
        area_km2 = area_km2
        )
