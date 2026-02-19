"""
We have a mask converted to 1's and 0's 
We need to convert that to a contour for using greens theorem

"""

import numpy as np
from skimage import measure
from typing import List

def extract_contours(mask : np.ndarray) -> List[np.ndarray]:
    """
    Extracts continuous contours from a binary mask
    
    :param mask: Please convert the water mask to np.ndarray before passing
    :type mask: np.ndarray
    :return: List of np.ndarrays
    :rtype: List[ndarray[_AnyShape, dtype[Any]]]
    """

    mask = np.array(mask, dtype=float)
    contours = measure.find_contours(mask, level=0.5)
    return contours
