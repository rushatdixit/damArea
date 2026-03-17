import numpy as np
from sentinelhub import BBox, CRS
from processing.select_reservoir import select_reservoir_connected_to_dam
from processing.mask_processing import largest_connected_component
from objects import ReservoirResult
from objects import Dam
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

import numpy as np
from scipy.ndimage import label
from sentinelhub import BBox


def mask_to_bbox(
        mask: np.ndarray,
        bbox: BBox,
        resolution: float,
        padding_pixels: int = 3
    ) -> BBox:
    """
    Converts a binary mask into a geographic bounding box corresponding
    to the largest connected component.

    Parameters
    ----------
    mask : np.ndarray
        Binary mask of reservoir pixels.
    bbox : BBox
        Original bbox corresponding to the mask.
    resolution : float
        Pixel resolution in meters.
    padding_pixels : int
        Extra padding around the reservoir.

    Returns
    -------
    BBox
        Refined bounding box containing the reservoir.
    """

    assert mask.ndim == 2, "Mask must be 2D"

    # -------------------------------------------------
    # 1. Remove tiny islands
    # -------------------------------------------------

    labeled, _ = label(mask)

    sizes = np.bincount(labeled.ravel())
    sizes[0] = 0

    largest = sizes.argmax()
    clean_mask = labeled == largest

    # -------------------------------------------------
    # 2. Find bounding pixels
    # -------------------------------------------------

    ys, xs = np.where(clean_mask)

    if len(xs) == 0:
        raise ValueError("Mask contains no reservoir pixels")

    min_row = ys.min()
    max_row = ys.max()

    min_col = xs.min()
    max_col = xs.max()

    height, width = clean_mask.shape

    # -------------------------------------------------
    # 3. Convert pixels → coordinates
    # -------------------------------------------------

    bbox_width = bbox.max_x - bbox.min_x
    bbox_height = bbox.max_y - bbox.min_y

    pixel_width = bbox_width / width
    pixel_height = bbox_height / height

    new_min_x = bbox.min_x + min_col * pixel_width
    new_max_x = bbox.min_x + (max_col + 1) * pixel_width

    new_max_y = bbox.max_y - min_row * pixel_height
    new_min_y = bbox.max_y - (max_row + 1) * pixel_height

    # -------------------------------------------------
    # 4. Padding
    # -------------------------------------------------

    padding = padding_pixels * resolution

    new_min_x -= padding
    new_max_x += padding
    new_min_y -= padding
    new_max_y += padding

    # -------------------------------------------------
    # 5. Return refined bbox
    # -------------------------------------------------

    return BBox(
        [new_min_x, new_min_y, new_max_x, new_max_y],
        crs=bbox.crs
    )