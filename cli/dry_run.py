"""
Dry-run command to preview API operations without execution.
"""

from datetime import datetime, timedelta
from sentinelhub import CRS, transform_point, BBox
from objects import Dam
from fetch_dam.get_dam import dam_name_to_coords, load_database
from pipeline.utilities import adjust_resolution, compute_pixel_dimensions
from utils.logger import get_logger

logger = get_logger(__name__)


def run_dry_run(
    dam_name: str,
    start_date: str,
    end_date: str,
    resolution: float = 10,
    timeseries_step: int = 30,
) -> None:
    """
    Simulates the pipeline execution, reporting estimated geometry, bounds,
    resolutions, and API calls without actually consuming API credits.
    """
    logger.info(f"Running dry-run for: {dam_name}")

    db = load_database()
    key = dam_name.strip().lower()
    source = "Local database (cached)" if key in db else "OpenStreetMap (will fetch)"

    try:
        coords = dam_name_to_coords(dam_name)
    except Exception as e:
        logger.error(f"Failed to geolocate dam '{dam_name}': {e}")
        return

    dam = Dam(name=dam_name, latitude=coords.latitude, longitude=coords.longitude)
    
    utm_crs = CRS.get_utm_from_wgs84(dam.longitude, dam.latitude)
    dam_x, dam_y = transform_point((dam.longitude, dam.latitude), CRS.WGS84, utm_crs)

    expanded_dam_bbox = BBox([dam_x - 25000, dam_y - 25000, dam_x + 25000, dam_y + 25000], crs=utm_crs)
    
    coarse_resolution = 100.0
    coarse_w, coarse_h = compute_pixel_dimensions(expanded_dam_bbox, coarse_resolution)
    coarse_safe = max(coarse_w, coarse_h) <= 2500
    
    # Assume worst case for refined area: a 10km x 10km reservoir
    refined_bbox_width = 10000
    refined_bbox = BBox([dam_x - refined_bbox_width/2, dam_y - refined_bbox_width/2, dam_x + refined_bbox_width/2, dam_y + refined_bbox_width/2], crs=utm_crs)
    refined_safe_res = adjust_resolution(refined_bbox, resolution)
    ref_w, ref_h = compute_pixel_dimensions(refined_bbox, refined_safe_res)
    
    # Uncertainty counts
    unc_thresholds = 10 # (-0.05 to +0.05 / 10) roughly
    unc_resolutions = 4
    unc_coarse = 10

    # Timeseries counts
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    if timeseries_step <= 0:
        timeseries_step = 30
        
    intervals = 0
    curr = start_dt
    while curr < end_dt:
        nxt = curr + timedelta(days=timeseries_step)
        intervals += 1
        curr = nxt
        
    timeseries_min_calls = intervals * 1  # 1 NDWI per interval
    timeseries_max_calls = intervals * 2  # 1 NDWI + 1 SAR failover
    
    total_calls_min = 2 + 2 + (unc_thresholds + unc_resolutions + unc_coarse) * 2 + timeseries_min_calls
    total_calls_max = 2 + 2 + (unc_thresholds + unc_resolutions + unc_coarse) * 2 + timeseries_max_calls

    pu_base = (coarse_w * coarse_h * 3 / (512 * 512)) + (ref_w * ref_h * 3 / (512 * 512))
    total_pu_est_min = pu_base + (intervals * (ref_w * ref_h * 3 / (512 * 512)))
    total_pu_est_max = total_pu_est_min * 1.5

    border = "=" * 50
    print(border)
    print(f"{'DRY RUN SUMMARY':^50}")
    print(border)
    print(f" Dam:           {dam_name}")
    print(f" Coordinates:   {dam.latitude:.4f} N, {dam.longitude:.4f} E")
    print(f" Source:        {source}")
    print("")
    print(" Coarse Scan:")
    print("   BBox:        50 km x 50 km")
    print(f"   Resolution:  {coarse_resolution} m -> {coarse_w} x {coarse_h} px {'[OK]' if coarse_safe else '[TOO LARGE]'}")
    print("   API calls:   2 (NDWI + RGB)")
    print("")
    print(" Refined Scan:")
    print(f"   Resolution:  {refined_safe_res} m (adjusted from {resolution} m)")
    print(f"   Max pixels:  {ref_w} x {ref_h} [OK]")
    print("   API calls:   2 (NDWI + RGB)")
    print("")
    print(" Uncertainty:")
    print(f"   Threshold:   {unc_thresholds} sweeps x 2 calls = {unc_thresholds*2}")
    print(f"   Resolution:  {unc_resolutions} sweeps x 2 calls = {unc_resolutions*2}")
    print(f"   Coarse:      {unc_coarse} sweeps x 2 calls = {unc_coarse*2}")
    print("")
    print(" Timeseries:")
    print(f"   Intervals:   {intervals} (every {timeseries_step} days)")
    print(f"   API calls:   {timeseries_min_calls}-{timeseries_max_calls} (optical + SAR backup)")
    print("   Workers:     5 (parallel)")
    print("")
    print(f" TOTAL ESTIMATED API CALLS: {total_calls_min}-{total_calls_max}")
    print(f" ESTIMATED PROCESSING UNITS: ~{total_pu_est_min:.1f}-{total_pu_est_max:.1f} PU")
    print(border)
