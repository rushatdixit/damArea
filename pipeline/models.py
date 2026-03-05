from dataclasses import dataclass
from typing import Optional,List, Any
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

@dataclass
class ThresholdUncertainty:
    thresholds : List[float]
    areas_km2 : List[float]
    @property
    def mean_km2(self) -> float:
        return float(np.mean(self.areas_km2))

    @property
    def min_km2(self) -> float:
        return float(np.min(self.areas_km2))

    @property
    def max_km2(self) -> float:
        return float(np.max(self.areas_km2))

    @property
    def range_km2(self) -> float:
        return self.max_km2 - self.min_km2

    @property
    def relative_range_percent(self) -> float:
        return 100 * self.range_km2 / self.mean_km2