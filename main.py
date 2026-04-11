"""
Docstring for main
This is the file which runs the project.
"""
import sys
import time
from pipeline.acquisition import acquire_aoi, get_expansion
from pipeline.utilities import adjust_resolution, ensure_utm
from objects import Dam, TimeSeries
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir, mask_to_bbox
from pipeline.data_to_area import get_pixel_area
from pipeline.visuals import show_individual_figures, show_pipeline_overview
from constants import DEFAULT_RESOLUTION, WATER_MASK_THRESHOLD, INITIAL_EXPANSION
from fetch_dam.get_dam import dam_name_to_coords
from uncertainty.visuals import plot_resolution_uncertainty, plot_threshold_uncertainty, plot_timeseries

TIME_INTERVAL = ("2023-01-01", "2023-12-31")


def main():
    resolution = DEFAULT_RESOLUTION
    threshold = WATER_MASK_THRESHOLD
    expansion = INITIAL_EXPANSION

    if len(sys.argv) < 2:
        print("Usage: python3 -m main \"Dam Name\"")
        sys.exit(1)
    dam_name = sys.argv[1]
    print(f"\nRunning pipeline for: {dam_name}\n")

    start = time.time()
    
    coords = dam_name_to_coords(dam_name)
    dam = Dam(name=dam_name, latitude=coords.latitude, longitude=coords.longitude)
    
    EXPANSION_METERS = get_expansion(dam, TIME_INTERVAL, INITIAL_EXPANSION, resolution=500)
    print(f"{EXPANSION_METERS}")
    expanded_dam_bbox = acquire_aoi(dam, expansion)
    assert -90 <= dam.latitude <= 90
    assert -180 <= dam.longitude <= 180

    expanded_dam_bbox = ensure_utm(expanded_dam_bbox)
    resolution = adjust_resolution(expanded_dam_bbox, resolution=resolution)
    print(f"Adjusted resolution to : {resolution}")
    data = acquire_satellite_data(
        expanded_dam_bbox,
        resolution=resolution,
        time_interval=TIME_INTERVAL,
        threshold=threshold,
        )

    reservoir = choose_reservoir(
            dam_mask=data.mask,
            expanded_dam_bbox=expanded_dam_bbox,
            dam=dam,
            resolution=resolution,
            )
    
    reservoir_bbox = mask_to_bbox(
        reservoir.mask[0],
        expanded_dam_bbox,
        resolution=resolution
    )

    resolution = adjust_resolution(reservoir_bbox, resolution=DEFAULT_RESOLUTION)
    print(f"Optimal resolution for reservoir AOI: {resolution}")

    refined_data = acquire_satellite_data(
        reservoir_bbox,
        resolution=resolution,
        time_interval=TIME_INTERVAL,
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

    from uncertainty.threshold_uncertainty import threshold_sensitivity

    threshold_unc = threshold_sensitivity(
        dam_bbox=reservoir_bbox,
        resolution=resolution,
        time_interval=TIME_INTERVAL,
        dam=dam,
        threshold=threshold,
        epsilon=0.05,
        sampling_density=10
    )

    from uncertainty.resolution_uncertainty import resolution_sensitivity

    resolution_unc = resolution_sensitivity(
        dam=dam,
        resolution=30,
        dam_bbox=reservoir_bbox,
        time_interval=TIME_INTERVAL,
        step=5,
        sampling_density=4
    )

    from uncertainty.timeseries_analysis import compute_timeseries
    print(f"\nComputing Area over Time for interval {TIME_INTERVAL}...")
    timeseries_data = compute_timeseries(
        dam=dam,
        resolution=50,
        dam_bbox=reservoir_bbox,
        time_interval=TIME_INTERVAL,
        threshold=threshold,
        interval_days=30
    )

    threshold_range = threshold_unc.range_km2
    resolution_range = resolution_unc.range_km2

    total_unc = (threshold_range**2 + resolution_range**2) ** 0.5

    print("\n-----------------------------------")
    print(f"Final Area: {area_km2:.4f} ± {total_unc:.4f} km²")
    print("-----------------------------------")

    end = time.time()
    print(f"\nTime elapsed: {end - start:.2f} seconds")

    show_pipeline_overview(
        rgb=refined_data.rgb,
        ndwi=refined_data.ndwi,
        full_mask=refined_data.mask,
        selected_mask=refined_reservoir.mask[0],
        contour_pixels=refined_reservoir.contour,
        area_km2=area_km2,
        uncertainty_km2=total_unc
    )

    plot_threshold_uncertainty(threshold_unc)
    plot_resolution_uncertainty(resolution_unc)
    plot_timeseries(timeseries_data, dam_name=dam_name)

    print("Pipeline complete.")

if __name__ == "__main__":
    main()