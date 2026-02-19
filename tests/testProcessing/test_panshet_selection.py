"""
=========================================================
Dam Area Measure — Panshet Reservoir Selection Test
=========================================================

This test validates:

1) Old logic: largest connected water component
2) New logic: reservoir physically connected to dam

We compare areas and visually inspect results.

Run:
    python -m tests.testProcessing.test_panshet_selection
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import label
from sentinelhub import CRS

from fetch_dam.get_dam import dam_name_to_coords, dam_name_to_bbox
from sentinel.aoi import expand_bbox_meters
from sentinel.request2 import request_sentinel_data, request_rgb_data
from sentinel.ndwi import compute_ndwi, water_mask
from processing.select_reservoir import select_reservoir_connected_to_dam


# ----------------------------------------
# CONFIG
# ----------------------------------------

DAM_NAME = input("Enter the name of the dam: ")
TIME_INTERVAL = ("2023-01-01", "2023-12-31")
RESOLUTION = 50
EXPANSION_METERS = 25000


# ----------------------------------------
# FETCH DAM + DATA
# ----------------------------------------

print("\nFetching dam info...")
dam_info = dam_name_to_coords(DAM_NAME)

dam_lat = dam_info["latitude"]
dam_lon = dam_info["longitude"]

bbox = dam_name_to_bbox(DAM_NAME)
bbox = expand_bbox_meters(bbox, EXPANSION_METERS)

# Convert bbox to UTM
center_lon = (bbox.min_x + bbox.max_x) / 2
center_lat = (bbox.min_y + bbox.max_y) / 2
utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
bbox_utm = bbox.transform(utm_crs)

print("Downloading Sentinel NDWI bands...")
bands = request_sentinel_data(bbox, TIME_INTERVAL, RESOLUTION)

print("Downloading RGB image...")
rgb = request_rgb_data(bbox, TIME_INTERVAL, RESOLUTION)

print("Computing NDWI...")
ndwi = compute_ndwi(bands)

print("Generating water mask...")
mask = water_mask(ndwi, threshold=0.2)
mask = np.asarray(mask).astype(bool)

pixel_area = RESOLUTION * RESOLUTION


# ----------------------------------------
# OLD LOGIC — Largest Component
# ----------------------------------------

print("\nRunning OLD logic (largest component)...")

labeled, num_features = label(mask)

largest_pixels = 0
largest_id = None

for i in range(1, num_features + 1):
    pixels = np.sum(labeled == i)
    if pixels > largest_pixels:
        largest_pixels = pixels
        largest_id = i

largest_component = (labeled == largest_id)

largest_area_km2 = (largest_pixels * pixel_area) / 1_000_000
print(f"Largest Component Area: {largest_area_km2:.4f} km²")


# ----------------------------------------
# NEW LOGIC — Dam-connected Component
# ----------------------------------------

print("\nRunning NEW logic (dam-connected selection)...")

selected_mask, selected_area_km2 = select_reservoir_connected_to_dam(
    mask=mask,
    dam_lat=dam_lat,
    dam_lon=dam_lon,
    bbox_utm=bbox_utm,
    resolution=RESOLUTION,
)

print(f"Selected Component Area: {selected_area_km2:.4f} km²")


# ----------------------------------------
# VISUALIZATION (Combined)
# ----------------------------------------

rgb_arr = np.asarray(rgb).astype(float)

# Safe normalization
p2, p98 = np.percentile(rgb_arr, (2, 98))
rgb_arr = np.clip((rgb_arr - p2) / (p98 - p2), 0, 1)

plt.figure(figsize=(14, 10))

plt.subplot(2, 2, 1)
plt.title("Original RGB")
plt.imshow(rgb_arr)
plt.axis("off")

plt.subplot(2, 2, 2)
plt.title("All Water Mask")
plt.imshow(mask, cmap="Blues")
plt.axis("off")

plt.subplot(2, 2, 3)
plt.title("Largest Component (OLD LOGIC)")
plt.imshow(largest_component, cmap="Blues")
plt.axis("off")

plt.subplot(2, 2, 4)
plt.title("Closest-to-Dam (NEW LOGIC)")
plt.imshow(selected_mask, cmap="Blues")
plt.axis("off")

plt.tight_layout()
plt.show()


# ----------------------------------------
# INDIVIDUAL FIGURES
# ----------------------------------------

print("\nDisplaying individual figures...")

plt.figure()
plt.title("Largest Component")
plt.imshow(largest_component, cmap="Blues")
plt.axis("off")
plt.show()

plt.figure()
plt.title("Dam-Connected Component")
plt.imshow(selected_mask, cmap="Blues")
plt.axis("off")
plt.show()

print("\nTest complete.")
print("If NEW logic selects Panshet and not Varasgaon,")
print("the semantic reservoir selection works correctly.\n")
