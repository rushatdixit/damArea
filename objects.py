"""
Data structures for representing dams, reservoirs, satellite products,
uncertainty metrics, timeseries, and extrema diagnostics.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Any, List, Union, Tuple
from datetime import datetime
from sentinelhub import BBox


@dataclass
class Dam:
    """
    Represents a dam with its geographical coordinates.

    :param name: Human-readable name of the dam.
    :type name: str
    :param latitude: Latitude in WGS84 decimal degrees.
    :type latitude: float
    :param longitude: Longitude in WGS84 decimal degrees.
    :type longitude: float
    """
    name: str
    latitude: float
    longitude: float


@dataclass
class Reservoir:
    """
    Represents an extracted reservoir from satellite data with derived measurements.

    :param mask: Binary water mask array.
    :type mask: np.ndarray
    :param ndwi: NDWI values array.
    :type ndwi: np.ndarray
    :param bbox: Bounding box of the reservoir in UTM.
    :type bbox: BBox
    :param resolution: Pixel resolution in meters.
    :type resolution: float
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
    Geocoded dam data fetched from OpenStreetMap or local database.

    :param latitude: Latitude in WGS84 decimal degrees.
    :type latitude: float
    :param longitude: Longitude in WGS84 decimal degrees.
    :type longitude: float
    :param bbox: Raw bounding box from geocoding response.
    :type bbox: Union[BBox, Any]
    """
    latitude: float
    longitude: float
    bbox: Union[BBox, Any]


@dataclass(frozen=True)
class SatelliteData:
    """
    Container for satellite-derived products from a single acquisition.

    :param rgb: RGB composite array, or None if not requested.
    :type rgb: Optional[np.ndarray]
    :param ndwi: NDWI array, or None if not requested.
    :type ndwi: Optional[np.ndarray]
    :param mask: Binary water mask, or None if not requested.
    :type mask: Optional[np.ndarray]
    :param sar: SAR VV backscatter array, or None if optical mode.
    :type sar: Optional[np.ndarray]
    :param water_area_m2: Total water area in square meters, or None.
    :type water_area_m2: Optional[float]
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    """
    rgb: Optional[np.ndarray]
    ndwi: Optional[np.ndarray]
    mask: Optional[np.ndarray]
    sar: Optional[np.ndarray]
    water_area_m2: Optional[float]
    resolution: float


@dataclass(frozen=True)
class ReservoirResult:
    """
    Result of connected-component reservoir selection.

    :param mask: Binary mask of the selected reservoir component.
    :type mask: np.ndarray
    :param contour: Pixel coordinates of the reservoir contour.
    :type contour: np.ndarray
    :param area_km2: Surface area of the selected component in km².
    :type area_km2: float
    """
    mask: np.ndarray
    contour: np.ndarray
    area_km2: float


@dataclass(frozen=True)
class ReservoirSelection:
    """
    Output of the reservoir selection algorithm.

    :param mask: Binary mask of the selected water component.
    :type mask: np.ndarray
    :param area_km2: Surface area of the selected component in km².
    :type area_km2: float
    """
    mask: np.ndarray
    area_km2: float


@dataclass(frozen=True)
class WaterAreaResult:
    """
    Result of a water area computation.

    :param area_m2: Water surface area in square meters.
    :type area_m2: float
    :param area_km2: Water surface area in square kilometers.
    :type area_km2: float
    """
    area_m2: float
    area_km2: float


@dataclass(frozen=True)
class PolarCoordinates:
    """
    Polar coordinate representation of a 2D point.

    :param radius: Distance from origin.
    :type radius: float
    :param angle: Angle in radians from the positive x-axis.
    :type angle: float
    """
    radius: float
    angle: float


@dataclass
class ThresholdUncertainty:
    """
    Uncertainty metrics from sweeping NDWI thresholds.

    :param thresholds: List of tested NDWI threshold values.
    :type thresholds: List[float]
    :param areas_km2: Corresponding reservoir areas in km².
    :type areas_km2: List[float]
    """
    thresholds: List[float]
    areas_km2: List[float]

    @property
    def mean_km2(self) -> float:
        """Mean area across all tested thresholds."""
        return float(np.mean(self.areas_km2))

    @property
    def min_km2(self) -> float:
        """Minimum area across all tested thresholds."""
        return float(np.min(self.areas_km2))

    @property
    def max_km2(self) -> float:
        """Maximum area across all tested thresholds."""
        return float(np.max(self.areas_km2))

    @property
    def range_km2(self) -> float:
        """Range of areas across all tested thresholds."""
        return self.max_km2 - self.min_km2

    @property
    def relative_range_percent(self) -> float:
        """Range as a percentage of the mean area."""
        return 100 * self.range_km2 / self.mean_km2


@dataclass
class ResolutionUncertainty:
    """
    Uncertainty metrics from sweeping spatial resolutions.

    :param resolutions: List of tested resolutions in meters.
    :type resolutions: List[float]
    :param areas_km2: Corresponding reservoir areas in km².
    :type areas_km2: List[float]
    """
    resolutions: List[float]
    areas_km2: List[float]

    @property
    def mean_km2(self) -> float:
        """Mean area across all tested resolutions."""
        return float(np.mean(self.areas_km2))

    @property
    def min_km2(self) -> float:
        """Minimum area across all tested resolutions."""
        return float(np.min(self.areas_km2))

    @property
    def max_km2(self) -> float:
        """Maximum area across all tested resolutions."""
        return float(np.max(self.areas_km2))

    @property
    def range_km2(self) -> float:
        """Range of areas across all tested resolutions."""
        return self.max_km2 - self.min_km2

    @property
    def relative_range_percent(self) -> float:
        """Range as a percentage of the mean area."""
        return 100 * self.range_km2 / self.mean_km2


@dataclass
class CoarseUncertainty:
    """
    Uncertainty metrics from sweeping coarse scan resolutions.

    :param coarse_resolutions: List of tested coarse resolutions in meters.
    :type coarse_resolutions: List[float]
    :param bbox_areas_km2: BBox areas in km² for each coarse resolution.
    :type bbox_areas_km2: List[float]
    :param reservoir_areas_km2: Reservoir areas in km² for each coarse resolution.
    :type reservoir_areas_km2: List[float]
    :param times_taken: Time taken in seconds for each coarse resolution.
    :type times_taken: List[float]
    """
    coarse_resolutions: List[float]
    bbox_areas_km2: List[float]
    reservoir_areas_km2: List[float]
    times_taken: List[float]


@dataclass
class ExtremaResult:
    """
    Full diagnostic data for a single extremum date (global min or max area).

    :param date_str: Start date string of the extremum interval (YYYY-MM-DD).
    :type date_str: str
    :param rgb: RGB composite, or None if fetch failed.
    :type rgb: Optional[np.ndarray]
    :param ndwi: NDWI array, or None if fetch failed.
    :type ndwi: Optional[np.ndarray]
    :param opt_mask: Optical water mask, or None if fetch failed.
    :type opt_mask: Optional[np.ndarray]
    :param opt_sel: Largest connected optical water component, or None.
    :type opt_sel: Optional[np.ndarray]
    :param sar: SAR VV backscatter array, or None if fetch failed.
    :type sar: Optional[np.ndarray]
    :param sar_sel: Largest connected SAR water component, or None.
    :type sar_sel: Optional[np.ndarray]
    """
    date_str: str
    rgb: Optional[np.ndarray]
    ndwi: Optional[np.ndarray]
    opt_mask: Optional[np.ndarray]
    opt_sel: Optional[np.ndarray]
    sar: Optional[np.ndarray]
    sar_sel: Optional[np.ndarray]


@dataclass
class ExtremaAnalysisResult:
    """
    Combined result of extrema analysis for both global min and max.

    :param min_extrema: Diagnostic data for the global minimum area date, or None.
    :type min_extrema: Optional[ExtremaResult]
    :param max_extrema: Diagnostic data for the global maximum area date, or None.
    :type max_extrema: Optional[ExtremaResult]
    """
    min_extrema: Optional[ExtremaResult]
    max_extrema: Optional[ExtremaResult]


@dataclass
class TimeSeries:
    """
    Timeseries of reservoir area measurements.

    :param df: DataFrame indexed by date with an 'area_km2' column.
    :type df: pd.DataFrame
    :param min_date_str: Comma-separated start,end date string of the minimum area interval.
    :type min_date_str: Optional[str]
    :param max_date_str: Comma-separated start,end date string of the maximum area interval.
    :type max_date_str: Optional[str]
    """
    df: pd.DataFrame
    min_date_str: Optional[str] = None
    max_date_str: Optional[str] = None

    @property
    def times(self) -> List[datetime]:
        """List of datetime indices from the timeseries."""
        return self.df.index.tolist() if not self.df.empty else []

    @property
    def areas_km2(self) -> List[float]:
        """List of area values in km²."""
        return self.df['area_km2'].tolist() if not self.df.empty else []

    @property
    def start_time(self) -> datetime:
        """Earliest date in the timeseries."""
        return self.df.index.min()

    @property
    def end_time(self) -> datetime:
        """Latest date in the timeseries."""
        return self.df.index.max()

    @property
    def duration_days(self) -> int:
        """Total span of the timeseries in days."""
        if self.df.empty:
            return 0
        return (self.end_time - self.start_time).days

    @property
    def mean_km2(self) -> float:
        """Mean reservoir area in km²."""
        return float(self.df['area_km2'].mean()) if not self.df.empty else 0.0

    @property
    def min_km2(self) -> float:
        """Minimum reservoir area in km²."""
        return float(self.df['area_km2'].min()) if not self.df.empty else 0.0

    @property
    def max_km2(self) -> float:
        """Maximum reservoir area in km²."""
        return float(self.df['area_km2'].max()) if not self.df.empty else 0.0

    @property
    def range_km2(self) -> float:
        """Range of reservoir area in km²."""
        return self.max_km2 - self.min_km2

    @property
    def relative_range_percent(self) -> float:
        """Range as a percentage of the mean area."""
        if self.mean_km2 == 0:
            return 0.0
        return 100 * self.range_km2 / self.mean_km2


@dataclass
class AreaEstimationResult:
    """
    Result container for the area estimation pipeline phase.

    :param area_km2: Best estimated reservoir area in km².
    :type area_km2: float
    :param reservoir_bbox: Tight bounding box around the detected reservoir.
    :type reservoir_bbox: BBox
    :param resolution: Optimal resolution used for refinement in meters.
    :type resolution: float
    :param refined_data: Satellite data from the refined acquisition.
    :type refined_data: SatelliteData
    :param refined_reservoir: Reservoir selection from the refined data.
    :type refined_reservoir: ReservoirResult
    :param coarse_data: Satellite data from the initial coarse acquisition.
    :type coarse_data: SatelliteData
    :param coarse_reservoir: Reservoir selection from the coarse data.
    :type coarse_reservoir: ReservoirResult
    """
    area_km2: float
    reservoir_bbox: BBox
    resolution: float
    refined_data: SatelliteData
    refined_reservoir: ReservoirResult
    coarse_data: SatelliteData
    coarse_reservoir: ReservoirResult


@dataclass
class UncertaintyAnalysisResult:
    """
    Combined result of all uncertainty sensitivity analyses.

    :param total_unc: Root-sum-of-squares combined uncertainty in km².
    :type total_unc: float
    :param threshold_unc: NDWI threshold sensitivity results.
    :type threshold_unc: ThresholdUncertainty
    :param resolution_unc: Spatial resolution sensitivity results.
    :type resolution_unc: ResolutionUncertainty
    :param coarse_unc: Coarse resolution sensitivity results.
    :type coarse_unc: CoarseUncertainty
    """
    total_unc: float
    threshold_unc: ThresholdUncertainty
    resolution_unc: ResolutionUncertainty
    coarse_unc: CoarseUncertainty
