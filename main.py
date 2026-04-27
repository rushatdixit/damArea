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

#first run check
def _check_first_run():
    flag_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".damArea_initialized")
    if not os.path.exists(flag_file):
        try:
            from preliminary_tests import run_preliminary_tests
        except ImportError:
            print("Error: Could not import preliminary_tests.py")
            sys.exit(1)
            
        print("First time running damArea! Running preliminary tests...\n")
        passed = run_preliminary_tests()
        if passed:
            with open(flag_file, 'w') as f:
                f.write('initialized')
            print("\nPreliminary tests passed. Proceeding with your command...\n")
        else:
            print("\nPlease install the required dependencies and fix the issues above before using damArea.")
            sys.exit(1)

_check_first_run()


from cli.doctor import run_doctor_checks
from cli.cache import purge_cache, list_cache_entries, display_cache_size
from cli.dry_run import run_dry_run
from cli.config_cmd import show_config
from cli.inspect_data import inspect_bbox, inspect_mask, inspect_ndwi, inspect_sar, inspect_compare
from cli.validate import validate_outputs
from cli.rate_status import show_rate_status
from utils.logger import configure_logging, get_logger

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


logger = get_logger(__name__)

def run_pipeline(args: argparse.Namespace) -> None:
    """
    Runs the main dam area pipeline.
    """

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
            selected_mask=area_res.refined_reservoir.mask,
            contour_pixels=area_res.refined_reservoir.contour,
            area_km2=area_res.area_km2,
            uncertainty_km2=unc_res.total_unc if unc_res else 0.0,
            coarse_mask=area_res.coarse_data.mask,
            coarse_selected_mask=area_res.coarse_reservoir.mask,
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

def main() -> None:
    """
    Parses CLI arguments and routes to the appropriate subcommand.
    """
    parser = argparse.ArgumentParser(description="Dam Area Pipeline with Debugging Tools")
    parser.add_argument("--log-level", type=str, default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Set the logging level")
    parser.add_argument("--log-file", type=str, default=None, help="Output logs to a JSON file")
    
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")
    
    # RUN command
    parser_run = subparsers.add_parser("run", help="Run the dam area pipeline")
    parser_run.add_argument("dam_name", type=str, help="Name of the dam to process")
    parser_run.add_argument("--start-date", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser_run.add_argument("--end-date", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
    parser_run.add_argument("--area", type=str, choices=['y', 'n'], default='y', help="Run Area Estimation phase (y/n)")
    parser_run.add_argument("--unc", type=str, choices=['y', 'n'], default='y', help="Run Uncertainty Analysis phase (y/n)")
    parser_run.add_argument("--time", type=str, choices=['y', 'n'], default='y', help="Run Timeseries phase (y/n)")
    parser_run.add_argument("--sar", type=str, choices=['y', 'n'], default='y', help="Allows automatic Sentinel-1 SAR Cloud Failovers (y/n)")
    parser_run.add_argument("--extrema", type=str, choices=['y', 'n'], default='n', help="Show full Optical+SAR diagnostic for global min/max area dates (y/n)")
    parser_run.add_argument("--timeseries-step", type=int, default=30, help="Interval size in days for Timeseries scans")
    parser_run.add_argument("--resolution", type=int, default=10, help="Optical target resolution in meters")
    parser_run.add_argument("--verbose", type=str, choices=['y', 'n'], default='n', help="Enable deep debug logging (y/n)")
    parser_run.add_argument("--debug", type=str, choices=['y', 'n'], default='n', help="Export RGB debug images")
    parser_run.add_argument("--delete-debug", type=str, choices=['y', 'n'], default='n', help="Delete generated debug directories")

    # DOCTOR command
    parser_doctor = subparsers.add_parser("doctor", help="API health checks and credential validation")
    
    # CACHE command
    parser_cache = subparsers.add_parser("cache", help="Inspect and purge the joblib cache")
    parser_cache.add_argument("action", type=str, choices=["list", "size", "purge"], help="Cache action to perform")
    parser_cache.add_argument("--dry-run", action="store_true", help="Simulate purge without deleting")
    
    # DRY-RUN command
    parser_dry = subparsers.add_parser("dry-run", help="Validate inputs and preview API calls without executing them")
    parser_dry.add_argument("dam_name", type=str, help="Name of the dam to process")
    parser_dry.add_argument("--start-date", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser_dry.add_argument("--end-date", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
    parser_dry.add_argument("--resolution", type=float, default=10, help="Optical target resolution in meters")
    parser_dry.add_argument("--timeseries-step", type=int, default=30, help="Interval size in days for Timeseries scans")
    
    # CONFIG command
    parser_config = subparsers.add_parser("config", help="Audit and display resolved configuration")
    parser_config.add_argument("action", type=str, choices=["show"], default="show", nargs="?", help="Config action to perform")
    parser_config.add_argument("--json", action="store_true", help="Output config in JSON format")
    
    # INSPECT command
    parser_inspect = subparsers.add_parser("inspect", help="Visualize bounding boxes, masks, and intermediate arrays")
    inspect_sub = parser_inspect.add_subparsers(dest="inspect_cmd", help="Inspect action")
    
    inspect_bbox_parser = inspect_sub.add_parser("bbox", help="Inspect bounding box for a dam")
    inspect_bbox_parser.add_argument("dam_name", type=str)
    inspect_bbox_parser.add_argument("--resolution", type=float, default=10)
    
    inspect_mask_parser = inspect_sub.add_parser("mask", help="Inspect binary mask")
    inspect_mask_parser.add_argument("path", type=str)
    
    inspect_ndwi_parser = inspect_sub.add_parser("ndwi", help="Inspect NDWI array")
    inspect_ndwi_parser.add_argument("path", type=str)
    inspect_ndwi_parser.add_argument("--threshold", type=float, default=0.2)
    
    inspect_sar_parser = inspect_sub.add_parser("sar", help="Inspect SAR array")
    inspect_sar_parser.add_argument("path", type=str)
    inspect_sar_parser.add_argument("--threshold", type=float, default=0.09)
    
    inspect_compare_parser = inspect_sub.add_parser("compare", help="Compare optical and SAR masks")
    inspect_compare_parser.add_argument("opt_path", type=str)
    inspect_compare_parser.add_argument("sar_path", type=str)
    
    # VALIDATE command
    parser_validate = subparsers.add_parser("validate", help="Data integrity checks on pipeline outputs")
    parser_validate.add_argument("dam_name", type=str)
    parser_validate.add_argument("--outputs-dir", type=str, default="./outputs")
    parser_validate.add_argument("--strict", action="store_true")
    
    # RATE-STATUS command
    parser_rate = subparsers.add_parser("rate-status", help="Show Sentinel Hub rate limit consumption")
    parser_rate.add_argument("--json", action="store_true", help="Output in JSON format")
    parser_rate.add_argument("--watch", action="store_true", help="Live monitor dashboard")
    
    args = parser.parse_args()
    
    configure_logging(level=args.log_level, log_file=args.log_file)
    
    # Optional backward compatibility wrapper if no subcommand given
    # Defaults to parser.print_help() if nothing matched
    if not args.subcommand:
        # Check if the user passed positional arguments directly (legacy mode)
        if len(sys.argv) > 1 and sys.argv[1] not in ["run", "doctor", "cache", "dry-run", "config", "-h", "--help"]:
            # Inject "run" into sys.argv and re-parse
            sys.argv.insert(1, "run")
            args = parser.parse_args()
        else:
            parser.print_help()
            sys.exit(0)

    if args.subcommand == "run":
        run_pipeline(args)
    elif args.subcommand == "doctor":
        run_doctor_checks()
    elif args.subcommand == "cache":
        if args.action == "list":
            list_cache_entries()
        elif args.action == "size":
            display_cache_size()
        elif args.action == "purge":
            purge_cache(dry_run=args.dry_run)
    elif args.subcommand == "dry-run":
        run_dry_run(
            dam_name=args.dam_name,
            start_date=args.start_date,
            end_date=args.end_date,
            resolution=args.resolution,
            timeseries_step=args.timeseries_step,
        )
    elif args.subcommand == "config":
        if args.action == "show":
            show_config(json_format=args.json)
    elif args.subcommand == "inspect":
        if args.inspect_cmd == "bbox":
            inspect_bbox(args.dam_name, args.resolution)
        elif args.inspect_cmd == "mask":
            inspect_mask(args.path)
        elif args.inspect_cmd == "ndwi":
            inspect_ndwi(args.path, args.threshold)
        elif args.inspect_cmd == "sar":
            inspect_sar(args.path, args.threshold)
        elif args.inspect_cmd == "compare":
            inspect_compare(args.opt_path, args.sar_path)
        else:
            parser_inspect.print_help()
    elif args.subcommand == "validate":
        validate_outputs(args.dam_name, args.outputs_dir, args.strict)
    elif args.subcommand == "rate-status":
        show_rate_status(json_format=args.json, watch=args.watch)


if __name__ == "__main__":
    main()