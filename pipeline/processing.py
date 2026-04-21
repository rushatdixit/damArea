"""
Pipeline processing functions for reservoir selection and bounding box extraction.
"""

import numpy as np
from scipy.ndimage import label
from sentinelhub import BBox, CRS
from processing.select_reservoir import select_reservoir_connected_to_dam
from processing.mask_processing import largest_connected_component
from objects import ReservoirResult, ReservoirSelection, Dam
from constants import MIN_AREA_KM2_PROCESSING


def choose_reservoir(
    dam_mask: np.ndarray,
    expanded_dam_bbox: BBox,
    dam: Dam,
    resolution: float,
    min_area_km2: float = MIN_AREA_KM2_PROCESSING,
    wants_debugs: bool = True,
) -> ReservoirResult:
    """
    Selects the reservoir component closest to the dam and extracts its contour.

    :param dam_mask: Binary water mask (2D).
    :type dam_mask: np.ndarray
    :param expanded_dam_bbox: UTM bounding box corresponding to the mask.
    :type expanded_dam_bbox: BBox
    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param min_area_km2: Minimum area for component filtering.
    :type min_area_km2: float
    :param wants_debugs: Whether to print debug output.
    :type wants_debugs: bool
    :return: Reservoir result containing mask, contour, and area.
    :rtype: ReservoirResult
    """
    assert hasattr(expanded_dam_bbox, 'crs') and expanded_dam_bbox.crs != CRS.WGS84, \
        "choose_reservoir requires UTM bbox"
    assert isinstance(dam, Dam), "dam must be an instance of Dam class"
    assert dam_mask.ndim == 2, "dam_mask must be 2D"
    assert resolution > 0

    selection: ReservoirSelection = select_reservoir_connected_to_dam(
        mask=dam_mask,
        dam=dam,
        bbox_utm=expanded_dam_bbox,
        resolution=resolution,
        min_area_km2=min_area_km2,
        is_debug=wants_debugs,
    )
    selected_contour = largest_connected_component(selection.mask)
    water_pixels = np.sum(selection.mask)
    area_km2 = (water_pixels * resolution * resolution) / 1_000_000
    return ReservoirResult(
        mask=selection.mask,
        contour=selected_contour,
        area_km2=area_km2,
    )


def mask_to_bbox(
    mask: np.ndarray,
    bbox: BBox,
    resolution: float,
    padding_pixels: int = 3,
) -> BBox:
    """
    Converts a binary mask into a geographic bounding box around the largest
    connected component, with optional pixel padding.

    :param mask: Binary mask of reservoir pixels (2D).
    :type mask: np.ndarray
    :param bbox: Original bounding box corresponding to the mask.
    :type bbox: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param padding_pixels: Extra padding in pixels around the detected region.
    :type padding_pixels: int
    :return: Tight bounding box containing the reservoir with padding.
    :rtype: BBox
    """
    assert mask.ndim == 2, "Mask must be 2D"

    labeled, _ = label(mask)

    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0

    largest = sizes.argmax()
    clean_mask = labeled == largest

    ys, xs = np.where(clean_mask)

    if len(xs) == 0:
        raise ValueError("Mask contains no reservoir pixels")

    min_row = ys.min()
    max_row = ys.max()
    min_col = xs.min()
    max_col = xs.max()

    height, width = clean_mask.shape

    bbox_width = bbox.max_x - bbox.min_x
    bbox_height = bbox.max_y - bbox.min_y

    pixel_width = bbox_width / width
    pixel_height = bbox_height / height

    new_min_x = bbox.min_x + min_col * pixel_width
    new_max_x = bbox.min_x + (max_col + 1) * pixel_width

    new_max_y = bbox.max_y - min_row * pixel_height
    new_min_y = bbox.max_y - (max_row + 1) * pixel_height

    padding = padding_pixels * resolution

    new_min_x -= padding
    new_max_x += padding
    new_min_y -= padding
    new_max_y += padding

    return BBox(
        [new_min_x, new_min_y, new_max_x, new_max_y],
        crs=bbox.crs
    )