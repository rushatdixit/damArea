"""
Docstring for main
This is the file which runs the project.
"""
import time
import argparse
from objects import Dam
from constants import WATER_MASK_THRESHOLD
from fetch_dam.get_dam import dam_name_to_coords

from pipeline.orchestration import (
    run_area_estimation,
    run_uncertainty_analysis,
    run_timeseries
)
from pipeline.visuals import show_pipeline_overview
from uncertainty.visuals import show_analysis_overview

def main():
    parser = argparse.ArgumentParser(description="Dam Area Pipeline")
    parser.add_argument("dam_name", type=str, help="Name of the dam to process")
    parser.add_argument("--start-date", type=str, default="2023-01-01", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
    parser.add_argument("--coarse-res", type=float, default=100.0, help="Coarse resolution in meters")
    args = parser.parse_args()

    dam_name = args.dam_name
    time_interval = (args.start_date, args.end_date)
    coarse_resolution = args.coarse_res
    threshold = WATER_MASK_THRESHOLD

    print(f"\nRunning pipeline for: {dam_name}\n")
    start = time.time()
    
    coords = dam_name_to_coords(dam_name)
    dam = Dam(name=dam_name, latitude=coords.latitude, longitude=coords.longitude)

    area_res = None
    unc_res = None
    timeseries_data = None

    # Phase 1: Area Estimation
    area_res = run_area_estimation(dam_name, dam, time_interval, coarse_resolution, threshold)

    # Phase 2: Uncertainty Analysis
    if area_res is not None:
        unc_res = run_uncertainty_analysis(dam, area_res.reservoir_bbox, area_res.resolution, time_interval, threshold)

        print("\n-----------------------------------")
        print(f"Final Area: {area_res.area_km2:.4f} ± {unc_res.total_unc if unc_res else 0.0:.4f} km²")
        print("-----------------------------------")

    # Phase 3: Timeseries
    if area_res is not None:
        timeseries_data = run_timeseries(dam, area_res.reservoir_bbox, time_interval, threshold)

    end = time.time()
    print(f"\nTime elapsed: {end - start:.2f} seconds")

    # Plotting
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
            coarse_selected_mask=area_res.coarse_reservoir.mask[0]
        )

    if unc_res is not None or timeseries_data is not None:
        show_analysis_overview(unc_res=unc_res, timeseries_data=timeseries_data, dam_name=dam_name)

    print("Pipeline complete.")

if __name__ == "__main__":
    main()