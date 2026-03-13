from dataclasses import dataclass
from typing import Optional, Any
from sentinelhub import BBox
import numpy as np

@dataclass(frozen=True)
class FetchedDamData:
    latitude : float
    longitude : float
    bbox : BBox | Any

@dataclass(frozen=True)
class SatelliteData:
    """
    Container for satellite-derived products.
    """

    rgb: Optional[np.ndarray]
    ndwi: Optional[np.ndarray]
    mask: Optional[np.ndarray]
    water_area_m2: Optional[float]
    resolution: float

@dataclass(frozen=True)
class ReservoirResult:
    mask: np.ndarray
    contour: np.ndarray
    area_km2: float