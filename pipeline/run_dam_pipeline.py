"""
Full Dam Water Extraction Pipeline

Usage:
    python3 -m sentinel.run_dam_pipeline "Khadakwasla Dam"
"""

import sys
import numpy as np
import matplotlib.pyplot as plt

from sentinel.tile_stream import stream_water_area
from sentinelhub import CRS, BBox

from fetch_dam.get_dam import dam_name_to_coords, dam_name_to_bbox
from sentinel.aoi import bbox_from_coords, expand_bbox_meters
from sentinel.request2 import request_sentinel_data, request_rgb_data
from sentinel.ndwi import compute_ndwi, water_mask


# --------------------------------------------
# CONFIG
# --------------------------------------------

TIME_INTERVAL = ("2023-01-01", "2023-12-31")
EXPANSION_METERS = 2000  # expand bbox by 5km
RESOLUTION = 10

# --------------------------------------------
# VISUAL DEBUG
# --------------------------------------------

def visual_debug(rgb, ndwi, mask, threshold):
    rgb = np.array(rgb)
    ndwi_arr = np.array(ndwi)
    mask_arr = np.array(mask)
    print("\n--- DEBUG INFO ---")
    print("RGB min/max:", np.min(rgb), np.max(rgb))
    print("NDWI nan count:", np.isnan(ndwi_arr).sum())
    print("Mask true count:", np.sum(mask_arr))
    print("Mask shape:", mask_arr.shape)
    print("------------------\n")
    plt.figure(figsize=(16, 6))

    # RGB
    plt.subplot(1, 4, 1)
    plt.title("True Color (RGB)")
    rgb = rgb.astype(float)
    # Compute percentiles
    p2 = np.percentile(rgb, 2)
    p98 = np.percentile(rgb, 98)
    rgb = (rgb - p2) / (p98 - p2)
    rgb = np.clip(rgb, 0, 1)
    plt.imshow(rgb)
    plt.axis("off")

    # NDWI
    plt.subplot(1, 4, 2)
    plt.title("NDWI")
    im = plt.imshow(ndwi, cmap="RdBu")
    plt.colorbar(im)
    plt.axis("off")

    # Histogram
    plt.subplot(1, 4, 3)
    plt.title("NDWI Histogram")
    plt.hist(ndwi[~np.isnan(ndwi)], bins=100)
    plt.axvline(threshold, color="red", linestyle="--")
    plt.xlabel("NDWI")
    plt.ylabel("Pixel Count")

    # Mask
    plt.subplot(1, 4, 4)
    plt.title("Water Mask")
    plt.imshow(mask, cmap="Blues")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

def visual_showcase(rgb, ndwi, mask, threshold):
    """
    Displays RGB, NDWI, Histogram, and Mask
    as separate full-sized figures.
    """

    rgb = np.array(rgb).astype(float)
    ndwi_arr = np.array(ndwi)
    mask_arr = np.array(mask)

    # -----------------------------
    # RGB (percentile stretch)
    # -----------------------------
    p2 = np.percentile(rgb, 2)
    p98 = np.percentile(rgb, 98)

    rgb = (rgb - p2) / (p98 - p2)
    rgb = np.clip(rgb, 0, 1)

    plt.figure(figsize=(10, 8))
    plt.title("True Color (RGB)")
    plt.imshow(rgb)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # NDWI
    # -----------------------------
    plt.figure(figsize=(10, 8))
    plt.title("NDWI")
    im = plt.imshow(ndwi_arr, cmap="RdBu")
    plt.colorbar(im, fraction=0.046, pad=0.04)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # NDWI Histogram
    # -----------------------------
    plt.figure(figsize=(10, 6))
    plt.title("NDWI Histogram")
    plt.hist(ndwi_arr[~np.isnan(ndwi_arr)], bins=100)
    plt.axvline(threshold, color="red", linestyle="--")
    plt.xlabel("NDWI")
    plt.ylabel("Pixel Count")
    plt.tight_layout()
    plt.show()

    # -----------------------------
    # Water Mask
    # -----------------------------
    plt.figure(figsize=(10, 8))
    plt.title("Water Mask")
    plt.imshow(mask_arr, cmap="Blues")
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# --------------------------------------------
# MAIN PIPELINE
# --------------------------------------------

def main():
    resolution = RESOLUTION
    if len(sys.argv) < 2:
        print("Usage: python3 -m sentinel.run_dam_pipeline \"Dam Name\"")
        sys.exit(1)

    dam_name = sys.argv[1]

    print(f"\nRunning pipeline for: {dam_name}\n")

    # ----------------------------------------
    # Fetch bounding box from geocoder
    # ----------------------------------------

    print("Building AOI...")
    bbox = dam_name_to_bbox(dam_name)
    expanded_bbox = expand_bbox_meters(bbox, EXPANSION_METERS)
    print("✓ AOI expanded")

    # ----------------------------------------
    # Sentinel Requests
    # ----------------------------------------

    print("Requesting Sentinel NDWI bands...")
    print("BBox in meters:", expanded_bbox)
    """from sentinelhub import CRS
    center_lon = (expanded_bbox.min_x + expanded_bbox.max_x) / 2
    center_lat = (expanded_bbox.min_y + expanded_bbox.max_y) / 2
    utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
    expanded_bbox = expanded_bbox.transform(utm_crs)"""
    from sentinelhub import CRS

    if expanded_bbox.crs == CRS.WGS84:
        center_lon = (expanded_bbox.min_x + expanded_bbox.max_x) / 2
        center_lat = (expanded_bbox.min_y + expanded_bbox.max_y) / 2
        utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
        bbox_utm = expanded_bbox.transform(utm_crs)
    else:
        bbox_utm = expanded_bbox

    width_m = bbox_utm.max_x - bbox_utm.min_x
    height_m = bbox_utm.max_y - bbox_utm.min_y

    print("Width (m):", width_m)
    print("Height (m):", height_m)
    max_dimension_m = max(width_m, height_m)
    max_pixels = 2500 
    if max_dimension_m / resolution > max_pixels:
        resolution = int(np.ceil(max_dimension_m / max_pixels))
    print("Adjusted resolution to:", resolution)

    """water_area_m2, water_area_km2 = stream_water_area(
        bbox=expanded_bbox,
        time_interval=TIME_INTERVAL,
        resolution=resolution,
        tile_size_m=2000,
        threshold=0.2,
    )

    print(f"✓ Water Area: {water_area_m2:.2f} m²")
    print(f"✓ Water Area: {water_area_km2:.6f} km²")"""

    print("Requesting RGB image...")
    rgb = request_rgb_data(
        aoi=expanded_bbox,
        time_interval=TIME_INTERVAL,
        resolution=resolution,
    )
    print(f"✓ RGB received | Shape: {np.array(rgb).shape}")

    # ----------------------------------------
    # NDWI computation
    # ----------------------------------------

    ndwi_bands = request_sentinel_data(
        aoi = expanded_bbox,
        time_interval = TIME_INTERVAL,
        resolution = resolution
    )

    print("Computing NDWI...")
    ndwi = compute_ndwi(ndwi_bands)
    ndwi_arr = np.array(ndwi)

    print(f"✓ NDWI range: {np.nanmin(ndwi_arr):.3f} to {np.nanmax(ndwi_arr):.3f}")

    # ----------------------------------------
    # Water thresholding
    # ----------------------------------------

    threshold = 0.2
    print("Applying water threshold...")
    mask = water_mask(ndwi, threshold)
    mask_arr = np.array(mask)

    water_pixels = np.sum(mask_arr)
    print(f"✓ Water pixels: {water_pixels}")

    # ----------------------------------------
    # Area calculation
    # ----------------------------------------

    pixel_area = resolution * resolution
    water_area_m2 = water_pixels * pixel_area
    water_area_km2 = water_area_m2 / 1_000_000

    print(f"✓ Water Area: {water_area_m2:.2f} m²")
    print(f"✓ Water Area: {water_area_km2:.6f} km²")

    # ----------------------------------------
    # Visual Debug
    # ----------------------------------------

    print("Rendering visual debug...")
    visual_debug(rgb, ndwi_arr, mask_arr, threshold)
    visual_showcase(rgb, ndwi_arr, mask_arr, threshold)

    print("\nPipeline complete.\n")


if __name__ == "__main__":
    main()
