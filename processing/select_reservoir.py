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
from typing import Tuple
from scipy.ndimage import label
from sentinelhub import CRS, transform_point, BBox
from objects.dam import Dam
from constants import MIN_AREA_KM2_SELECTION

def select_reservoir_connected_to_dam(
        mask: np.ndarray,
        dam: Dam,
        bbox_utm: BBox,
        resolution: float,
        min_area_km2: float = MIN_AREA_KM2_SELECTION,
        is_debug : bool = True
    ) -> Tuple[np.ndarray, float]:
    """
    Parameters
    mask : binary water mask
    dam : Dam object containing location (WGS84)
    bbox_utm : bounding box in UTM
    resolution : meters per pixel
    min_area_km2 : ignore components smaller than this

    Returns
    selected_mask : binary mask of chosen reservoir
    area_km2 : computed area using pixel area
    """

    mask = np.asarray(mask).astype(bool)
    labeled, num_features = label(mask)

    if num_features == 0:
        raise ValueError("No water components found.")
    #included for debugging purposes
    if is_debug:
        print(f"Found {num_features} water components.")

    utm_crs = bbox_utm.crs
    dam_x, dam_y = transform_point(
        (dam.longitude, dam.latitude),
        CRS.WGS84,
        utm_crs
    )

    min_distance = np.inf
    selected_component_id = None
    pixel_area_m2 = resolution * resolution
    
    min_x, max_y = bbox_utm.min_x, bbox_utm.max_y
    for component_id in range(1, num_features + 1):
        component_mask = labeled == component_id
        pixel_count = np.sum(component_mask)

        area_km2 = (pixel_count * pixel_area_m2) / 1_000_000
        # Ignore tiny components
        if area_km2 < min_area_km2:
            continue

        # Get pixel indices (row, col) which map to (y, x)
        ys, xs = np.where(component_mask)
        
        # Convert pixel coordinates to metric coordinates
        # BBox min_x is Left, max_y is Top.
        # Moving right (increasing x pixel) increases easting (min_x + ...).
        # Moving down (increasing y pixel) decreases northing (max_y - ...).
        component_x = min_x + (xs * resolution)
        component_y = max_y - (ys * resolution)

        # Compute minimum boundary distance vectorized
        distances = np.sqrt((component_x - dam_x) ** 2 +
                            (component_y - dam_y) ** 2)

        boundary_distance = np.min(distances)
        if boundary_distance < min_distance:
            min_distance = boundary_distance
            selected_component_id = component_id

    if selected_component_id is None:
        raise ValueError("No valid reservoir component selected.")

    selected_mask = labeled == selected_component_id
    selected_pixels = np.sum(selected_mask)
    selected_area_km2 = (selected_pixels * pixel_area_m2) / 1_000_000

    print(f"Selected reservoir area: {selected_area_km2:.4f} km²")
    print(f"Boundary distance to dam: {min_distance:.2f} meters")

    return (selected_mask.astype(int), selected_area_km2)
