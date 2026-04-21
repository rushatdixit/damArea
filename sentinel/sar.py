"""
SAR water mask extraction from Sentinel-1 VV backscatter.
"""

import numpy as np
from scipy.ndimage import median_filter
from constants import SAR_THRESHOLD, SAR_SPECKLE_KERNEL


def sar_water_mask(
    sar_data: np.ndarray,
    threshold: float = SAR_THRESHOLD,
    speckle_kernel: int = SAR_SPECKLE_KERNEL,
) -> np.ndarray:
    """
    Creates a binary water mask from Sentinel-1 SAR VV backscatter.

    Applies a median filter to suppress speckle noise, then thresholds
    the smoothed backscatter. Water surfaces produce specular reflection
    resulting in very low return signal (dark pixels).

    :param sar_data: 2D or 3D array of VV backscatter values (linear scale).
    :type sar_data: np.ndarray
    :param threshold: Backscatter threshold below which pixels are classified as water.
    :type threshold: float
    :param speckle_kernel: Size of the median filter kernel for speckle suppression.
    :type speckle_kernel: int
    :return: 2D boolean mask where True indicates water.
    :rtype: np.ndarray
    """
    arr = np.array(sar_data, dtype=float)
    if arr.ndim == 3:
        arr = arr[:, :, 0]

    arr = median_filter(arr, size=speckle_kernel)

    mask = (arr < threshold) & (~np.isnan(arr)) & (arr > 0)

    return mask
