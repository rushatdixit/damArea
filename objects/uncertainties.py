from dataclasses import dataclass
from typing import List
import numpy as np

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
    
@dataclass
class ResolutionUncertainty:
    resolutions : List[float]
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