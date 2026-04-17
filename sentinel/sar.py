import numpy as np
from typing import List

def sar_water_mask(sar_data: np.ndarray, threshold: float = 0.05) -> np.ndarray:
    """
    Creates a water mask from Sentinel-1 SAR VV backscatter.
    Water has very low backscatter (smooth surface reflects radar away).
    Therefore, water pixels are those BELOW the threshold.
    
    :param sar_data: 2D or 3D numpy array of VV backscatter values.
    :param threshold: Linear backscatter threshold (e.g. 0.05).
    :return: 2D boolean mask where True indicates water.
    """
    arr = np.array(sar_data, dtype=float)
    if arr.ndim == 3:
        arr = arr[:, :, 0] # Extract the single VV band
    
    # Water is dark in SAR (close to 0)
    mask = (arr < threshold) & (~np.isnan(arr)) & (arr > 0)
    
    return mask
