import numpy as np
from typing import List
from scipy.ndimage import median_filter

def sar_water_mask(sar_data: np.ndarray, threshold: float = 0.09, speckle_kernel: int = 5) -> np.ndarray:
    """
    Creates a water mask from Sentinel-1 SAR VV backscatter.
    Water has very low backscatter (smooth surface reflects radar away).
    Therefore, water pixels are those BELOW the threshold.

    Applies a median filter first to suppress SAR speckle noise,
    which otherwise fragments water bodies into disconnected components.
    
    :param sar_data: 2D or 3D numpy array of VV backscatter values.
    :param threshold: Linear backscatter threshold (e.g. 0.09).
    :param speckle_kernel: Size of the median filter kernel for speckle suppression.
    :return: 2D boolean mask where True indicates water.
    """
    arr = np.array(sar_data, dtype=float)
    if arr.ndim == 3:
        arr = arr[:, :, 0]

    arr = median_filter(arr, size=speckle_kernel)

    mask = (arr < threshold) & (~np.isnan(arr)) & (arr > 0)

    return mask

