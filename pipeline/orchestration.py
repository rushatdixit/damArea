"""
Pipeline orchestration: area estimation, uncertainty analysis, timeseries, and extrema.
"""

import time
import numpy as np
from typing import Tuple, Optional
from sentinelhub import CRS, transform_point, BBox
from scipy.ndimage import label as scipy_label

from objects import (
    Dam, TimeSeries, AreaEstimationResult, UncertaintyAnalysisResult,
    ExtremaResult, ExtremaAnalysisResult,
)
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir, mask_to_bbox
from pipeline.data_to_area import get_pixel_area
from pipeline.utilities import adjust_resolution
from constants import DEFAULT_RESOLUTION, WATER_MASK_THRESHOLD
from utils.logger import get_logger

logger = get_logger(__name__)

def run_area_estimation(
    dam_name: str,
    dam: Dam,
    time_interval: Tuple[str, str],
    coarse_resolution: float,
    threshold: float = WATER_MASK_THRESHOLD,
) -> AreaEstimationResult:
    """
    Computes reservoir surface area via coarse-then-refined satellite acquisition.

    Performs a 50 km × 50 km coarse scan to locate the reservoir, refines the
    bounding box, then re-acquires at optimal resolution for the final estimate.

    :param dam_name: Human-readable name of the dam.
    :type dam_name: str
    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param coarse_resolution: Resolution in meters for the initial coarse scan.
    :type coarse_resolution: float
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :return: Area estimation result with all intermediate data.
    :rtype: AreaEstimationResult
    """
    logger.info("Initial 50km x 50km bounds selected.")
    utm_crs = CRS.get_utm_from_wgs84(dam.longitude, dam.latitude)
    dam_x, dam_y = transform_point((dam.longitude, dam.latitude), CRS.WGS84, utm_crs)

    expanded_dam_bbox = BBox([dam_x - 25000, dam_y - 25000, dam_x + 25000, dam_y + 25000], crs=utm_crs)

    coarse_data = acquire_satellite_data(
        expanded_dam_bbox,
        resolution=coarse_resolution,
        time_interval=time_interval,
        threshold=threshold,
        wants_rgb=False,
        wants_ndwi=True,
        wants_mask=True,
    )

    coarse_reservoir = choose_reservoir(
        dam_mask=coarse_data.mask,
        expanded_dam_bbox=expanded_dam_bbox,
        dam=dam,
        resolution=coarse_resolution,
    )

    reservoir_bbox = mask_to_bbox(
        coarse_reservoir.mask,
        expanded_dam_bbox,
        resolution=coarse_resolution,
    )

    resolution = adjust_resolution(reservoir_bbox, resolution=DEFAULT_RESOLUTION)
    logger.info(f"Optimal resolution for reservoir AOI: {resolution}")

    refined_data = acquire_satellite_data(
        reservoir_bbox,
        resolution=resolution,
        time_interval=time_interval,
        threshold=threshold,
    )

    refined_reservoir = choose_reservoir(
        dam_mask=refined_data.mask,
        expanded_dam_bbox=reservoir_bbox,
        dam=dam,
        resolution=resolution,
    )

    area_m2 = get_pixel_area(
        refined_reservoir.mask,
        resolution=resolution,
    )

    area_km2 = area_m2 / 1e6
    logger.info(f"Best Area Estimate: {area_km2:.4f} km²")

    return AreaEstimationResult(
        area_km2=area_km2,
        reservoir_bbox=reservoir_bbox,
        resolution=resolution,
        refined_data=refined_data,
        refined_reservoir=refined_reservoir,
        coarse_data=coarse_data,
        coarse_reservoir=coarse_reservoir,
    )


def run_uncertainty_analysis(
    dam: Dam,
    reservoir_bbox: BBox,
    resolution: float,
    time_interval: Tuple[str, str],
    threshold: float = WATER_MASK_THRESHOLD,
) -> UncertaintyAnalysisResult:
    """
    Executes threshold, resolution, and coarse sensitivity analyses.

    Computes individual uncertainty ranges and combines them via
    root-sum-of-squares into a total uncertainty bound.

    :param dam: Dam object being analyzed.
    :type dam: Dam
    :param reservoir_bbox: Tight bounding box around the detected reservoir.
    :type reservoir_bbox: BBox
    :param resolution: Optimal resolution used for the area estimate.
    :type resolution: float
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param threshold: Base NDWI threshold.
    :type threshold: float
    :return: Combined uncertainty analysis results.
    :rtype: UncertaintyAnalysisResult
    """
    from uncertainty.threshold_uncertainty import threshold_sensitivity
    from uncertainty.resolution_uncertainty import resolution_sensitivity
    from uncertainty.coarse_uncertainty import coarse_resolution_sensitivity

    threshold_unc = threshold_sensitivity(
        dam_bbox=reservoir_bbox,
        resolution=resolution,
        time_interval=time_interval,
        dam=dam,
        threshold=threshold,
        epsilon=0.05,
        sampling_density=10,
    )

    resolution_unc = resolution_sensitivity(
        dam=dam,
        resolution=30,
        dam_bbox=reservoir_bbox,
        time_interval=time_interval,
        step=5,
        sampling_density=4,
    )

    logger.info("Computing Coarse Resolution Uncertainty...")
    coarse_unc = coarse_resolution_sensitivity(
        dam=dam,
        base_resolution=resolution,
        time_interval=time_interval,
        coarse_resolutions=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
    )

    threshold_range = threshold_unc.range_km2
    resolution_range = resolution_unc.range_km2
    total_unc = (threshold_range**2 + resolution_range**2) ** 0.5

    return UncertaintyAnalysisResult(
        total_unc=total_unc,
        threshold_unc=threshold_unc,
        resolution_unc=resolution_unc,
        coarse_unc=coarse_unc,
    )


def run_timeseries(
    dam: Dam,
    reservoir_bbox: BBox,
    time_interval: Tuple[str, str],
    threshold: float = WATER_MASK_THRESHOLD,
    resolution: float = 10,
    interval_days: int = 30,
    allow_sar: bool = True,
    expected_area_km2: Optional[float] = None,
) -> TimeSeries:
    """
    Computes reservoir surface area at regular intervals over a time span.

    :param dam: Dam object being analyzed.
    :type dam: Dam
    :param reservoir_bbox: Bounding box of the reservoir.
    :type reservoir_bbox: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param interval_days: Step size in days between measurements.
    :type interval_days: int
    :param allow_sar: Whether to allow SAR failover on cloudy intervals.
    :type allow_sar: bool
    :param expected_area_km2: Expected area for cloud-detection heuristic.
    :type expected_area_km2: Optional[float]
    :return: Timeseries of area measurements.
    :rtype: TimeSeries
    """
    from uncertainty.timeseries_analysis import compute_timeseries

    logger.info(f"Computing Area over Time for interval {time_interval}...")
    timeseries_data = compute_timeseries(
        dam=dam,
        resolution=resolution,
        dam_bbox=reservoir_bbox,
        time_interval=time_interval,
        threshold=threshold,
        interval_days=interval_days,
        allow_sar=allow_sar,
        expected_area_km2=expected_area_km2,
    )
    return timeseries_data


def run_extrema_analysis(
    dam: Dam,
    reservoir_bbox: BBox,
    timeseries_data: TimeSeries,
    resolution: float = 10,
    threshold: float = WATER_MASK_THRESHOLD,
) -> ExtremaAnalysisResult:
    """
    Fetches full optical and SAR diagnostic data for the global min and max
    area dates identified by the timeseries analysis.

    For each extremum date, acquires RGB, NDWI, optical mask, and SAR
    backscatter, then selects the largest connected water component.

    :param dam: Dam object being analyzed.
    :type dam: Dam
    :param reservoir_bbox: Bounding box of the reservoir.
    :type reservoir_bbox: BBox
    :param timeseries_data: Timeseries with identified min/max date strings.
    :type timeseries_data: TimeSeries
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :return: Extrema analysis result with min and max diagnostic data.
    :rtype: ExtremaAnalysisResult
    """
    from sentinel.request import request_rgb_data, request_sar_data, request_sentinel_data
    from sentinel.ndwi import compute_ndwi, water_mask
    from sentinel.sar import sar_water_mask

    def fetch_extrema_for_interval(date_str: str) -> ExtremaResult:
        """
        Fetches all diagnostic layers for a single extremum interval.

        :param date_str: Comma-separated start,end date string.
        :type date_str: str
        :return: Diagnostic data for this interval.
        :rtype: ExtremaResult
        """
        start_str, end_str = date_str.split(",")
        interval = (start_str, end_str)
        logger.info(f"Fetching Extrema Context for {interval}")

        rgb = None
        ndwi = None
        opt_mask = None
        opt_sel = None
        sar_raw = None
        sar_sel = None

        try:
            rgb = request_rgb_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution, maxcc=1.0)
        except Exception as e:
            logger.warning(f"RGB fetch failed: {e}")

        try:
            ndwi_bands = request_sentinel_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution)
            ndwi = np.array(compute_ndwi(ndwi_bands))
            opt_mask = np.array(water_mask(ndwi.tolist(), threshold))

            labeled, num = scipy_label(opt_mask)
            if num > 0:
                sizes = np.bincount(labeled.ravel())
                sizes[0] = 0
                opt_sel = (labeled == sizes.argmax()).astype(int)
            else:
                opt_sel = opt_mask
        except Exception as e:
            logger.warning(f"Optical processing failed: {e}")

        try:
            sar_raw = request_sar_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution)
            sar_mask_arr = sar_water_mask(sar_raw)

            labeled, num = scipy_label(sar_mask_arr)
            if num > 0:
                sizes = np.bincount(labeled.ravel())
                sizes[0] = 0
                sar_sel = (labeled == sizes.argmax()).astype(int)
            else:
                sar_sel = sar_mask_arr.astype(int)
        except Exception as e:
            logger.warning(f"SAR processing failed: {e}")

        return ExtremaResult(
            date_str=start_str,
            rgb=rgb,
            ndwi=ndwi,
            opt_mask=opt_mask,
            opt_sel=opt_sel,
            sar=sar_raw,
            sar_sel=sar_sel,
        )

    min_extrema: Optional[ExtremaResult] = None
    max_extrema: Optional[ExtremaResult] = None

    if timeseries_data.min_date_str:
        logger.info("Processing Global MINIMUM area date...")
        min_extrema = fetch_extrema_for_interval(timeseries_data.min_date_str)

    if timeseries_data.max_date_str:
        logger.info("Processing Global MAXIMUM area date...")
        max_extrema = fetch_extrema_for_interval(timeseries_data.max_date_str)

    return ExtremaAnalysisResult(
        min_extrema=min_extrema,
        max_extrema=max_extrema,
    )
