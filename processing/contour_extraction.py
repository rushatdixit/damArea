"""
Contour extraction from binary water masks.
"""

import numpy as np
from skimage import measure
from typing import List


def extract_contours(mask: np.ndarray) -> List[np.ndarray]:
    """
    Extracts continuous contours from a binary mask using marching squares.

    :param mask: Binary water mask as a numpy array.
    :type mask: np.ndarray
    :return: List of contour arrays, each with shape (N, 2) in (row, col) format.
    :rtype: List[np.ndarray]
    """
    mask = np.array(mask, dtype=float)
    contours = measure.find_contours(mask, level=0.5)
    return contours
