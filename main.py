"""
Docstring for main
This is the file which runs the project.
"""
import sys
import time
from pipeline.acquisition import acquire_aoi, get_expansion
from pipeline.utilities import adjust_resolution, ensure_utm
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from pipeline.data_to_area import get_pixel_area
from pipeline.visuals import show_individual_figures, show_pipeline_overview

#set the constants
TIME_INTERVAL = ("2023-01-01", "2023-12-31")
EXPANSION_METERS = float(input("Expansion : "))
RESOLUTION = int(input("Set your resolution: "))

def main():
    resolution = RESOLUTION
    threshold = 0.2
    if len(sys.argv) < 2:
        print("Usage: python3 -m main \"Dam Name\"")
        sys.exit(1)
    dam_name = sys.argv[1]
    print(f"\nRunning pipeline for: {dam_name}\n")

    start = time.time()
    EXPANSION_METERS = get_expansion(dam_name, TIME_INTERVAL, 2000, resolution=500)
    print(f"{EXPANSION_METERS}")
    expanded_dam_bbox = acquire_aoi(dam_name, EXPANSION_METERS)
    dam_lon = (expanded_dam_bbox.min_x + expanded_dam_bbox.max_x) / 2
    dam_lat = (expanded_dam_bbox.min_y + expanded_dam_bbox.max_y) / 2
    assert -90 <= dam_lat <= 90
    assert -180 <= dam_lon <= 180

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
            dam_lat=dam_lat,
            dam_lon=dam_lon,
            resolution=resolution,
            )
    
    area_m2 = get_pixel_area(
        dam_mask=reservoir.mask[0],
        resolution=resolution
        )
    area_km2 = area_m2/1e6

    end = time.time()
    print(f"Time elapsed : {end - start}")

    show_pipeline_overview(
        rgb=data.rgb,
        ndwi=data.ndwi,
        full_mask=data.mask,
        selected_mask=reservoir.mask[0],
        contour_pixels=reservoir.contour,
        area_km2=area_km2
        )
    
    show_individual_figures(
        rgb=data.rgb,
        ndwi=data.ndwi,
        full_mask=data.mask,
        selected_mask=reservoir.mask[0]
    )
    print("Pipeline complete.")

if __name__ == "__main__":
    main()