"""
Symbolises a water body and not just the dam
"""

import numpy as np
from dataclasses import dataclass
from sentinelhub import BBox

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