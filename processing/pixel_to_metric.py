"""
This converts pixels represented in [row, col] to real world metric coords (UTM) (x, y)
"""

import numpy as np
from typing import List
from sentinelhub import BBox

def contour_pixels_to_metric(
        contour : List[np.ndarray], 
        bbox_utm : BBox, 
        resolution : float
        ) -> np.ndarray:
    """
    Convert pixel contour coords to real world metric based coords (UTM)
    
    :param contour: Nx2 array of (row, col) in pixel space
    :type contour: List[np.ndarray]
    :param bbox_utm: Sentinel Hub Bounding box in UTM
    :type bbox_utm: BBox
    :param resolution: Meters per pixel
    :type resolution: float
    :return: Array of coords of vertices of the largest continuous polygon in the contour
    :rtype: ndarray[_AnyShape, dtype[Any]]
    """

    contour = np.array(contour)
    min_x = bbox_utm.min_x
    max_y = bbox_utm.max_y

    rows = contour[:,0]
    cols = contour[:,1]

    x = min_x + cols * resolution
    y = max_y - rows * resolution

    metric_coords = np.column_stack((x, y))

    return metric_coords