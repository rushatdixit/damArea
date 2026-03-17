"""
Docstring for main
This is the file which runs the project.
"""
import sys
import time
from pipeline.acquisition import acquire_aoi, get_expansion
from pipeline.utilities import adjust_resolution, ensure_utm
from objects import Dam
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from pipeline.data_to_area import get_pixel_area
from pipeline.visuals import show_individual_figures, show_pipeline_overview
from constants import DEFAULT_RESOLUTION, WATER_MASK_THRESHOLD, INITIAL_EXPANSION
from fetch_dam.get_dam import dam_name_to_coords

#set the constants
TIME_INTERVAL = ("2023-01-01", "2023-12-31")

def main():
    resolution = DEFAULT_RESOLUTION
    threshold = WATER_MASK_THRESHOLD
    if len(sys.argv) < 2:
        print("Usage: python3 -m main \"Dam Name\"")
        sys.exit(1)
    dam_name = sys.argv[1]
    print(f"\nRunning pipeline for: {dam_name}\n")

    start = time.time()
    
    # Fetch coordinates first
    coords = dam_name_to_coords(dam_name)
    dam = Dam(name=dam_name, latitude=coords.latitude, longitude=coords.longitude)
    
    EXPANSION_METERS = get_expansion(dam, TIME_INTERVAL, INITIAL_EXPANSION, resolution=500)
    print(f"{EXPANSION_METERS}")
    expanded_dam_bbox = acquire_aoi(dam, EXPANSION_METERS)
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