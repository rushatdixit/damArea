from dataclasses import dataclass
from typing import List
from datetime import datetime
import numpy as np

@dataclass
class TimeSeries:
    times: List[datetime]
    areas_km2: List[float]

    @property
    def start_time(self) -> datetime:
        return min(self.times)

    @property
    def end_time(self) -> datetime:
        return max(self.times)

    @property
    def duration_days(self) -> int:
        return (self.end_time - self.start_time).days

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
        if self.mean_km2 == 0:
            return 0.0
        return 100 * self.range_km2 / self.mean_km2
