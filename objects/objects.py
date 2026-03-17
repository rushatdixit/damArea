"""
Data structures for representing dams, reservoirs, and uncertainty metrics.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional, Any, List
from sentinelhub import BBox

@dataclass
class Dam:
    """
    Represents a dam with its geographical coordinates.
    """
    name: str
    latitude: float
    longitude: float

@dataclass
class Reservoir:
    """
    Represents the extracted reservoir from the satellite data.
    Contains the processed mask and derived measurements.
    """
    mask: np.ndarray
    ndwi: np.ndarray
    bbox: BBox
    resolution: float

    @property
    def pixel_area(self) -> float:
        """Area of a single pixel in square meters."""
        return self.resolution ** 2

    @property
    def water_pixels(self) -> int:
        """Number of water pixels in the reservoir mask."""
        return int(np.sum(self.mask))

    @property
    def area_m2(self) -> float:
        """Reservoir surface area in square meters."""
        return self.water_pixels * self.pixel_area

    @property
    def area_km2(self) -> float:
        """Reservoir surface area in square kilometers."""
        return self.area_m2 / 1e6

@dataclass(frozen=True)
class FetchedDamData:
    """
    Data fetched for a specific dam including its bounding box.
    """
    latitude: float
    longitude: float
    bbox: BBox | Any

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
    """
    Results from processing a reservoir, including the mask and contour.
    """
    mask: np.ndarray
    contour: np.ndarray
    area_km2: float

@dataclass
class ThresholdUncertainty:
    """
    Uncertainty metrics calculated across different thresholds.
    """
    thresholds: List[float]
    areas_km2: List[float]
    
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
    """
    Uncertainty metrics calculated across different resolutions.
    """
    resolutions: List[float]
    areas_km2: List[float]
    
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