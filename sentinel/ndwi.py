"""
NDWI computation and water mask generation from Sentinel-2 bands.
"""

import numpy as np
from typing import List


def compute_ndwi(data: List[List[List[float]]]) -> List[List[float]]:
    """
    Computes the Normalized Difference Water Index from Sentinel-2 bands.

    Uses Green (B03) and NIR (B08) bands. Cloud-contaminated pixels identified
    by the Scene Classification Layer (SCL) are masked to NaN.

    :param data: 3D list [row][col][band] where band 0=Green, band 1=NIR, band 2=SCL.
    :type data: List[List[List[float]]]
    :return: 2D list of NDWI values in range [-1, 1], with NaN for cloud pixels.
    :rtype: List[List[float]]
    """
    arr = np.array(data, dtype=float)

    green = arr[:, :, 0] / 10000.0
    nir = arr[:, :, 1] / 10000.0
    scl = arr[:, :, 2]

    ndwi = (green - nir) / (green + nir + 1e-10)

    cloud_classes = [3, 8, 9, 10, 11]
    cloud_mask = np.isin(scl, cloud_classes)
    ndwi[cloud_mask] = np.nan

    return ndwi.tolist()


def water_mask(ndwi: List[List[float]], threshold: float = 0.2) -> List[List[bool]]:
    """
    Generates a binary water mask by thresholding NDWI values.

    :param ndwi: 2D list of NDWI values.
    :type ndwi: List[List[float]]
    :param threshold: NDWI value above which a pixel is classified as water.
    :type threshold: float
    :return: 2D boolean mask where True indicates water.
    :rtype: List[List[bool]]
    """
    arr = np.array(ndwi, dtype=float)
    mask = (arr > threshold) & (~np.isnan(arr))

    return mask.tolist()
