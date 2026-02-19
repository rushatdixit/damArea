import numpy as np
from typing import List


def compute_ndwi(data: List[List[List[float]]]) -> List[List[float]]:
    """
    data: 3D list -> [row][col][band]
          band 0 = Green (B03)
          band 1 = NIR (B08)

    returns: 2D list of NDWI values
    """
    arr = np.array(data, dtype=float)

    green = arr[:, :, 0] / 10000.0
    nir = arr[:, :, 1] / 10000.0
    scl = arr[:, :, 2]

    ndwi = (green - nir) / (green + nir + 1e-10)

    # Cloud mask
    cloud_classes = [3, 8, 9, 10, 11]
    cloud_mask = np.isin(scl, cloud_classes)

    # Remove cloudy pixels
    ndwi[cloud_mask] = np.nan

    return ndwi.tolist()


def water_mask(ndwi: List[List[float]], threshold: float = 0.2) -> List[List[bool]]:
    """
    ndwi: 2D list
    returns: 2D list of booleans
    """

    arr = np.array(ndwi, dtype=float)
    mask = (arr > threshold) & (~np.isnan(arr))

    return mask.tolist()
