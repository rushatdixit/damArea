import time
from typing import Tuple
from objects import Dam, TimeSeries, AreaEstimationResult, UncertaintyAnalysisResult
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir, mask_to_bbox
from pipeline.data_to_area import get_pixel_area
from pipeline.utilities import adjust_resolution
from constants import DEFAULT_RESOLUTION, WATER_MASK_THRESHOLD
from sentinelhub import CRS, transform_point, BBox

def run_area_estimation(
    dam_name: str, 
    dam: Dam, 
    time_interval: Tuple[str, str], 
    coarse_resolution: float, 
    threshold: float = WATER_MASK_THRESHOLD
) -> AreaEstimationResult:
    """
    Computes the surface area of a dam reservoir by performing a coarse scale
    search followed by a refined high-resolution border extraction.

    Args:
        dam_name (str): The name of the dam.
        dam (Dam): The Dam object containing coordinates.
        time_interval (Tuple[str, str]): Start and end dates (YYYY-MM-DD, YYYY-MM-DD).
        coarse_resolution (float): The resolution in meters for the initial lookup.
        threshold (float): The NDWI threshold to filter water pixels.

    Returns:
        AreaEstimationResult: A dataclass containing the estimated area, bounding
        box, calculated optimal resolution, and the generated raw satellite and
        reservoir masking data for both coarse and refined scales.
    """
    print("Initial 50km x 50km bounds selected.")
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
        wants_mask=True
    )

    coarse_reservoir = choose_reservoir(
        dam_mask=coarse_data.mask,
        expanded_dam_bbox=expanded_dam_bbox,
        dam=dam,
        resolution=coarse_resolution,
    )
    
    reservoir_bbox = mask_to_bbox(
        coarse_reservoir.mask[0],
        expanded_dam_bbox,
        resolution=coarse_resolution
    )

    resolution = adjust_resolution(reservoir_bbox, resolution=DEFAULT_RESOLUTION)
    print(f"Optimal resolution for reservoir AOI: {resolution}")

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
        refined_reservoir.mask[0],
        resolution=resolution
    )

    area_km2 = area_m2 / 1e6
    print(f"\nBest Area Estimate: {area_km2:.4f} km²")

    return AreaEstimationResult(
        area_km2=area_km2, 
        reservoir_bbox=reservoir_bbox, 
        resolution=resolution, 
        refined_data=refined_data, 
        refined_reservoir=refined_reservoir, 
        coarse_data=coarse_data, 
        coarse_reservoir=coarse_reservoir
    )

def run_uncertainty_analysis(
    dam: Dam, 
    reservoir_bbox: BBox, 
    resolution: float, 
    time_interval: Tuple[str, str], 
    threshold: float = WATER_MASK_THRESHOLD
) -> UncertaintyAnalysisResult:
    """
    Executes various sensitivity analyses to calculate algorithmic uncertainty bounds
    for the estimated reservoir area.

    Args:
        dam (Dam): The Dam object being analyzed.
        reservoir_bbox (BBox): The bounding box encapsulating the refined reservoir.
        resolution (float): The optimal resolution used in the final estimation.
        time_interval (Tuple[str, str]): Start and end dates.
        threshold (float): The base NDWI threshold used.

    Returns:
        UncertaintyAnalysisResult: A dataclass grouping total aggregated uncertainty 
        along with the raw sensitivity results.
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
        sampling_density=10
    )

    resolution_unc = resolution_sensitivity(
        dam=dam,
        resolution=30,
        dam_bbox=reservoir_bbox,
        time_interval=time_interval,
        step=5,
        sampling_density=4
    )

    print("\nComputing Coarse Resolution Uncertainty...")
    coarse_unc = coarse_resolution_sensitivity(
        dam=dam,
        base_resolution=resolution,
        time_interval=time_interval,
        coarse_resolutions=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    )

    threshold_range = threshold_unc.range_km2
    resolution_range = resolution_unc.range_km2
    total_unc = (threshold_range**2 + resolution_range**2) ** 0.5

    return UncertaintyAnalysisResult(
        total_unc=total_unc,
        threshold_unc=threshold_unc,
        resolution_unc=resolution_unc,
        coarse_unc=coarse_unc
    )

def run_timeseries(
    dam: Dam, 
    reservoir_bbox: BBox, 
    time_interval: Tuple[str, str], 
    threshold: float = WATER_MASK_THRESHOLD,
    resolution: float = 10,
    interval_days: int = 30,
    allow_sar: bool = True,
    expected_area_km2: float = None
) -> TimeSeries:
    """
    Computes the surface area of the reservoir over intervals inside the provided
    time span to create a timeseries.
    """
    from uncertainty.timeseries_analysis import compute_timeseries

    print(f"\nComputing Area over Time for interval {time_interval}...")
    timeseries_data = compute_timeseries(
        dam=dam,
        resolution=resolution,
        dam_bbox=reservoir_bbox,
        time_interval=time_interval,
        threshold=threshold,
        interval_days=interval_days,
        allow_sar=allow_sar,
        expected_area_km2=expected_area_km2
    )
    return timeseries_data

def run_extrema_analysis(
    dam: Dam,
    reservoir_bbox: BBox,
    timeseries_data: TimeSeries,
    resolution: float = 10,
    threshold: float = WATER_MASK_THRESHOLD,
):
    """
    Fetches full optical and SAR diagnostic data for the global min and max
    area dates identified by the timeseries analysis.
    Returns a tuple of (min_extrema, max_extrema) ExtremaResult objects.
    """
    from objects import ExtremaResult
    from sentinel.request import request_rgb_data, request_sar_data
    from sentinel.ndwi import compute_ndwi, water_mask
    from sentinel.sar import sar_water_mask
    from sentinel.request import request_sentinel_data
    import numpy as np

    def fetch_extrema_for_interval(date_str):
        start_str, end_str = date_str.split(",")
        interval = (start_str, end_str)
        print(f"\n--- Fetching Extrema Context for {interval} ---")

        rgb = None
        ndwi = None
        opt_mask = None
        opt_sel = None
        sar_raw = None
        sar_sel = None

        try:
            rgb = request_rgb_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution, maxcc=1.0)
        except Exception as e:
            print(f"  RGB fetch failed: {e}")

        try:
            ndwi_bands = request_sentinel_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution)
            ndwi = np.array(compute_ndwi(ndwi_bands))
            opt_mask = np.array(water_mask(ndwi.tolist(), threshold))

            from scipy.ndimage import label as scipy_label
            labeled, num = scipy_label(opt_mask)
            if num > 0:
                sizes = np.bincount(labeled.ravel())
                sizes[0] = 0
                opt_sel = (labeled == sizes.argmax()).astype(int)
            else:
                opt_sel = opt_mask
        except Exception as e:
            print(f"  Optical processing failed: {e}")

        try:
            sar_raw = request_sar_data(aoi=reservoir_bbox, time_interval=interval, resolution=resolution)
            sar_mask = sar_water_mask(sar_raw)

            from scipy.ndimage import label as scipy_label
            labeled, num = scipy_label(sar_mask)
            if num > 0:
                sizes = np.bincount(labeled.ravel())
                sizes[0] = 0
                sar_sel = (labeled == sizes.argmax()).astype(int)
            else:
                sar_sel = sar_mask.astype(int)
        except Exception as e:
            print(f"  SAR processing failed: {e}")

        return ExtremaResult(
            date_str=start_str,
            rgb=rgb,
            ndwi=ndwi,
            opt_mask=opt_mask,
            opt_sel=opt_sel,
            sar=sar_raw,
            sar_sel=sar_sel,
        )

    min_extrema = None
    max_extrema = None

    if timeseries_data.min_date_str:
        print("\nProcessing Global MINIMUM area date...")
        min_extrema = fetch_extrema_for_interval(timeseries_data.min_date_str)

    if timeseries_data.max_date_str:
        print("\nProcessing Global MAXIMUM area date...")
        max_extrema = fetch_extrema_for_interval(timeseries_data.max_date_str)

    return min_extrema, max_extrema
