"""
Reservoir Selection Logic

Selects the water component physically connected to the dam wall.

Selection Criteria:
1. Ignore tiny noise components.
2. For each remaining component:
   - Extract x,y coordinates for all pixels in the mask in metric format
   - Compute minimum distance from dam point to the component pixels
3. Select component with smallest distance.
"""

import numpy as np
from scipy.ndimage import label
from sentinelhub import CRS, transform_point, BBox
from objects import Dam, ReservoirSelection
from constants import MIN_AREA_KM2_SELECTION


def select_reservoir_connected_to_dam(
    mask: np.ndarray,
    dam: Dam,
    bbox_utm: BBox,
    resolution: float,
    min_area_km2: float = MIN_AREA_KM2_SELECTION,
    is_debug: bool = True,
) -> ReservoirSelection:
    """
    Selects the water body component closest to the dam coordinates.

    Performs connected-component labeling on the binary mask, filters out
    components smaller than a minimum area, and selects the component whose
    nearest pixel is closest to the dam's projected UTM coordinates.

    :param mask: Binary water mask (2D).
    :type mask: np.ndarray
    :param dam: Dam object with WGS84 coordinates.
    :type dam: Dam
    :param bbox_utm: Bounding box in UTM corresponding to the mask.
    :type bbox_utm: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param min_area_km2: Minimum area threshold to filter noise components.
    :type min_area_km2: float
    :param is_debug: Whether to print debug information.
    :type is_debug: bool
    :return: Selected reservoir mask and its area in km².
    :rtype: ReservoirSelection
    :raises ValueError: If no water components are found or none pass filtering.
    """
    mask = np.asarray(mask).astype(bool)
    labeled, num_features = label(mask)

    if num_features == 0:
        raise ValueError("No water components found.")
    if is_debug:
        print(f"Found {num_features} water components.")

    utm_crs = bbox_utm.crs
    dam_x, dam_y = transform_point(
        (dam.longitude, dam.latitude),
        CRS.WGS84,
        utm_crs
    )

    min_distance_sq = np.inf
    selected_component_id = None
    pixel_area_m2 = resolution * resolution

    min_x, max_y = bbox_utm.min_x, bbox_utm.max_y
    for component_id in range(1, num_features + 1):
        component_mask = labeled == component_id
        pixel_count = np.sum(component_mask)

        area_km2 = (pixel_count * pixel_area_m2) / 1_000_000
        if area_km2 < min_area_km2:
            continue

        ys, xs = np.where(component_mask)

        component_x = min_x + (xs * resolution)
        component_y = max_y - (ys * resolution)

        distances_sq = (component_x - dam_x) ** 2 + (component_y - dam_y) ** 2

        boundary_distance_sq = np.min(distances_sq)
        if boundary_distance_sq < min_distance_sq:
            min_distance_sq = boundary_distance_sq
            selected_component_id = component_id

    if selected_component_id is None:
        raise ValueError("No valid reservoir component selected.")

    min_distance = np.sqrt(min_distance_sq)

    selected_mask = labeled == selected_component_id
    selected_pixels = np.sum(selected_mask)
    selected_area_km2 = (selected_pixels * pixel_area_m2) / 1_000_000

    print(f"Selected reservoir area: {selected_area_km2:.4f} km²")
    print(f"Boundary distance to dam: {min_distance:.2f} meters")

    return ReservoirSelection(
        mask=selected_mask.astype(int),
        area_km2=selected_area_km2,
    )
