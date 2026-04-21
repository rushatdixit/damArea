"""
Dam Area Measurement Pipeline — CLI Entry Point

Runs area estimation, uncertainty analysis, timeseries tracking, and
extrema diagnostics for a specified dam using Sentinel satellite imagery.
"""

import os
import sys
import time
import shutil
import argparse
from typing import Optional

from objects import Dam
from constants import WATER_MASK_THRESHOLD
from fetch_dam.get_dam import dam_name_to_coords

from pipeline.orchestration import (
    run_area_estimation,
    run_uncertainty_analysis,
    run_timeseries,
    run_extrema_analysis,
)
from pipeline.visuals import show_pipeline_overview
from uncertainty.visuals import show_analysis_overview, show_extrema_dashboard


def main() -> None:
    """
    Parses CLI arguments and runs the dam area pipeline.
    """
    parser = argparse.ArgumentParser(description="Dam Area Pipeline")
    parser.add_argument("dam_name", type=str, help="Name of the dam to process")
    parser.add_argument("--start-date", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")

    parser.add_argument("--area", type=str, choices=['y', 'n'], default='y', help="Run Area Estimation phase (y/n)")
    parser.add_argument("--unc", type=str, choices=['y', 'n'], default='y', help="Run Uncertainty Analysis phase (y/n)")
    parser.add_argument("--time", type=str, choices=['y', 'n'], default='y', help="Run Timeseries phase (y/n)")

    parser.add_argument("--sar", type=str, choices=['y', 'n'], default='y', help="Allows automatic Sentinel-1 SAR Cloud Failovers (y/n)")
    parser.add_argument("--extrema", type=str, choices=['y', 'n'], default='n', help="Show full Optical+SAR diagnostic for global min/max area dates (y/n)")
    parser.add_argument("--timeseries-step", type=int, default=30, help="Interval size in days for Timeseries scans")
    parser.add_argument("--resolution", type=int, default=10, help="Optical target resolution in meters")
    parser.add_argument("--verbose", type=str, choices=['y', 'n'], default='n', help="Enable deep debug logging (y/n)")
    parser.add_argument("--debug", type=str, choices=['y', 'n'], default='n', help="Export RGB debug images")
    parser.add_argument("--delete-debug", type=str, choices=['y', 'n'], default='n', help="Delete generated debug directories")

    args = parser.parse_args()

    if args.delete_debug == 'y':
        target_dirs = [d for d in ["debug", "deep_debug"] if os.path.exists(d)]
        if not target_dirs:
            print("No debug directories found.")
            sys.exit(0)

        print("\n[WARNING] The following directories and all their contents will be permanently deleted:")
        for d in target_dirs:
            print(f" - {os.path.abspath(d)}")

        confirmation = input("\nAre you sure you want to proceed? [y/N]: ")
        if confirmation.lower() in ('y', 'yes'):
            for d in target_dirs:
                shutil.rmtree(d)
                print(f"Deleted {d}/")
            print("Debug cache cleared.")
        else:
            print("Deletion aborted.")
        sys.exit(0)

    dam_name: str = args.dam_name
    time_interval = (args.start_date, args.end_date)
    threshold: float = WATER_MASK_THRESHOLD

    do_area: bool = args.area == 'y'
    do_unc: bool = args.unc == 'y'
    do_time: bool = args.time == 'y'

    use_sar: bool = args.sar == 'y'
    resolution: float = float(args.resolution)
    interval_days: int = args.timeseries_step

    if args.debug == 'y':
        os.environ["DAM_DEBUG_DIR"] = "debug"
        os.makedirs("debug", exist_ok=True)
    if args.verbose == 'y':
        os.environ["DAM_VERBOSE_DIR"] = "deep_debug"
        os.makedirs("deep_debug", exist_ok=True)

    print(f"\nRunning pipeline for: {dam_name}\n")
    start = time.time()

    coords = dam_name_to_coords(dam_name)
    dam = Dam(name=dam_name, latitude=coords.latitude, longitude=coords.longitude)

    area_res = None
    unc_res = None
    timeseries_data = None

    if do_area:
        area_res = run_area_estimation(dam_name, dam, time_interval, 100.0, threshold)

    if do_unc:
        if area_res is not None:
            unc_res = run_uncertainty_analysis(dam, area_res.reservoir_bbox, resolution, time_interval, threshold)
            print("\n-----------------------------------")
            print(f"Final Area: {area_res.area_km2:.4f} ± {unc_res.total_unc if unc_res else 0.0:.4f} km²")
            print("-----------------------------------")
        else:
            print("\nSkipping Uncertainty Analysis because Area Estimation was not run.")

    if do_time:
        if area_res is not None:
            start_bbox = area_res.reservoir_bbox
            expected_area: Optional[float] = area_res.area_km2
        else:
            from sentinelhub import CRS, transform_point, BBox
            utm_crs = CRS.get_utm_from_wgs84(dam.longitude, dam.latitude)
            dam_x, dam_y = transform_point((dam.longitude, dam.latitude), CRS.WGS84, utm_crs)
            start_bbox = BBox([dam_x - 5000, dam_y - 5000, dam_x + 5000, dam_y + 5000], crs=utm_crs)
            expected_area = None

        timeseries_data = run_timeseries(
            dam, start_bbox, time_interval, threshold,
            resolution=resolution, interval_days=interval_days,
            allow_sar=use_sar, expected_area_km2=expected_area,
        )

    end = time.time()
    print(f"\nTime elapsed: {end - start:.2f} seconds")

    if area_res is not None:
        show_pipeline_overview(
            rgb=area_res.refined_data.rgb,
            ndwi=area_res.refined_data.ndwi,
            full_mask=area_res.refined_data.mask,
            selected_mask=area_res.refined_reservoir.mask[0],
            contour_pixels=area_res.refined_reservoir.contour,
            area_km2=area_res.area_km2,
            uncertainty_km2=unc_res.total_unc if unc_res else 0.0,
            coarse_mask=area_res.coarse_data.mask,
            coarse_selected_mask=area_res.coarse_reservoir.mask[0],
        )

    if unc_res is not None or timeseries_data is not None:
        show_analysis_overview(unc_res=unc_res, timeseries_data=timeseries_data, dam_name=dam_name)

    if args.extrema == 'y' and timeseries_data is not None:
        if timeseries_data.min_date_str or timeseries_data.max_date_str:
            if area_res is not None:
                extrema_bbox = area_res.reservoir_bbox
                extrema_res = area_res.resolution
            else:
                extrema_bbox = start_bbox
                extrema_res = resolution
            extrema_result = run_extrema_analysis(
                dam=dam,
                reservoir_bbox=extrema_bbox,
                timeseries_data=timeseries_data,
                resolution=extrema_res,
                threshold=threshold,
            )
            if extrema_result.min_extrema is not None and extrema_result.max_extrema is not None:
                show_extrema_dashboard(extrema_result.min_extrema, extrema_result.max_extrema, dam_name=dam_name)
            else:
                print("Could not generate extrema dashboard (missing min or max data).")
        else:
            print("No extrema date information available from timeseries.")

    print("Pipeline complete.")


if __name__ == "__main__":
    main()