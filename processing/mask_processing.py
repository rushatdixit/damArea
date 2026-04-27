"""
It converts the water mask into multiple polygons, from which it selects
the largest polygon.
If we assume the reservoir of interest is centered on the mask, and the mask encloses
the reservoir with suitable tightness, this will always return the polygon of interest.

SciPy is a scientific computing library built on NumPy.
It contains:
    -Optimization
    -Integration
    -Linear algebra
    -Signal processing
    -Image processing
ndimage stands for n dimensional image processing, it works on numpy arrays and treats
them as images. our water mask is just an np.ndarray of shape (H,W)
label() is the function we use :
    - it takes an array
    - and uses 8-connectivity to distinguish neighbours
    - for example an array of:
    1 1 1 0 0
    1 1 1 0 1
    1 1 1 0 1
    0 0 0 0 1
    - will return :
    1 1 1 0 0
    1 1 1 0 0
    1 1 1 0 2
    0 0 0 0 2
    - thereby distinguishing the connected 1's with the disconnected 1's
    - if it had return :
    0 1 0 0 0
    1 1 1 0 0
    0 1 0 0 2
    0 0 0 0 2
    - that would have been 4 connectivity, not 8 connectivity.
"""

import numpy as np
from scipy.ndimage import label
from skimage import measure
from sentinelhub import BBox, CRS, transform_point
from typing import Tuple


def largest_connected_component(mask: np.ndarray) -> np.ndarray:
    """
    Keeps only the largest 8-connected component in a binary mask.

    :param mask: Binary water mask.
    :type mask: np.ndarray
    :return: Boolean mask with only the largest component retained.
    :rtype: np.ndarray
    """
    mask = np.asarray(mask).astype(bool)

    structure = np.ones((3, 3), dtype=int)
    labeled, num_features = label(mask, structure=structure)

    if num_features == 0:
        return mask

    component_sizes = np.bincount(labeled.ravel())
    component_sizes[0] = 0

    if len(component_sizes) <= 1:
        return np.zeros_like(labeled, dtype=bool)
    largest_label = component_sizes.argmax()
    return labeled == largest_label


def select_closest_component(
    mask: np.ndarray,
    dam_coords_wgs84: Tuple[float, float],
    bbox_utm: BBox,
    resolution: float,
) -> np.ndarray:
    """
    Selects the water component whose centroid is closest to the dam coordinates.

    :param mask: Binary water mask.
    :type mask: np.ndarray
    :param dam_coords_wgs84: Dam coordinates as (latitude, longitude) in WGS84.
    :type dam_coords_wgs84: Tuple[float, float]
    :param bbox_utm: UTM bounding box corresponding to the mask.
    :type bbox_utm: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :return: Binary mask of the selected component.
    :rtype: np.ndarray
    :raises ValueError: If no water bodies are found.
    """
    mask = np.array(mask).astype(bool)
    labeled = measure.label(mask)
    regions = measure.regionprops(labeled)

    if len(regions) == 0:
        raise ValueError("No water bodies found.")

    lat, lon = dam_coords_wgs84
    utm_crs = bbox_utm.crs
    dam_x, dam_y = transform_point(
        (lon, lat),
        CRS.WGS84,
        utm_crs,
    )

    min_dist = np.inf
    selected_label = None
    for region in regions:
        row, col = region.centroid
        x = bbox_utm.min_x + col * resolution
        y = bbox_utm.max_y - row * resolution
        distance = np.sqrt((x - dam_x) ** 2 + (y - dam_y) ** 2)
        if distance < min_dist:
            min_dist = distance
            selected_label = region.label
    selected_mask = labeled == selected_label
    return selected_mask
