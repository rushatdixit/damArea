"""
Dam Area Measure — Panshet Component Selection Test
====================================================

This script tests whether our new function:

    select_component_closest_to_dam()

correctly selects Panshet reservoir instead of Varasgaon,
even though Varasgaon may be larger.

What this script does:

1️⃣ Fetch Panshet bounding box
2️⃣ Download Sentinel imagery
3️⃣ Compute NDWI
4️⃣ Create water mask
5️⃣ Label all connected components
6️⃣ Compare:
        - Largest component
        - Closest-to-dam component
7️⃣ Visualize everything

Run:

    python3 test_panshet_component_selection.py
"""

import numpy as np
import matplotlib.pyplot as plt

from sentinelhub import CRS, transform_point
from skimage.measure import label, regionprops

from fetch_dam.get_dam import dam_name_to_bbox, dam_name_to_coords
from sentinel.aoi import expand_bbox_meters
from sentinel.request import request_sentinel_data, request_rgb_data
from sentinel.ndwi import compute_ndwi, water_mask

from processing.mask_processing import select_closest_component


# ---------------------------------------------
# CONFIG
# ---------------------------------------------

DAM_NAME = "Panshet Dam"
TIME_INTERVAL = ("2023-01-01", "2023-12-31")
RESOLUTION = 10
EXPANSION_METERS = 10000


# ---------------------------------------------
# STEP 1 — GET DATA
# ---------------------------------------------

print("\nFetching dam info...")
bbox = dam_name_to_bbox(DAM_NAME)
dam_info = dam_name_to_coords(DAM_NAME)
dam_lat = dam_info["latitude"]
dam_lon = dam_info["longitude"]

bbox = expand_bbox_meters(bbox, EXPANSION_METERS)

print("Downloading Sentinel NDWI bands...")
bands = request_sentinel_data(
    aoi=bbox,
    time_interval=TIME_INTERVAL,
    resolution=RESOLUTION
)

print("Downloading RGB image...")
rgb = request_rgb_data(
    aoi=bbox,
    time_interval=TIME_INTERVAL,
    resolution=RESOLUTION
)

print("Computing NDWI...")
ndwi = np.array(compute_ndwi(bands))

print("Generating water mask...")
mask = np.array(water_mask(ndwi, threshold=0.2))


# ---------------------------------------------
# STEP 2 — LABEL COMPONENTS
# ---------------------------------------------

print("Labelling connected components...")
labeled = label(mask)
regions = regionprops(labeled)

print(f"Found {len(regions)} water components.")


# ---------------------------------------------
# STEP 3 — SELECT COMPONENTS
# ---------------------------------------------

# Largest component (old logic)
largest_region = max(regions, key=lambda r: r.area)
largest_mask = labeled == largest_region.label

# New logic — closest to dam
print("Selecting component closest to dam...")
selected_mask = select_closest_component(
    mask=mask,
    dam_coords_wgs84=(dam_lat, dam_lon),
    bbox_utm=bbox.transform(CRS.get_utm_from_wgs84(dam_lon, dam_lat)),
    resolution=RESOLUTION
)


# ---------------------------------------------
# STEP 4 — AREA COMPUTATION
# ---------------------------------------------

pixel_area = RESOLUTION * RESOLUTION

largest_area_km2 = np.sum(largest_mask) * pixel_area / 1_000_000
selected_area_km2 = np.sum(selected_mask) * pixel_area / 1_000_000

print(f"\nLargest Component Area:  {largest_area_km2:.4f} km²")
print(f"Selected Component Area: {selected_area_km2:.4f} km²")


# ---------------------------------------------
# STEP 5 — VISUALIZATION (COMBINED)
# ---------------------------------------------

rgb_arr = np.array(rgb, dtype=float)

# Normalize RGB properly
if rgb_arr.max() <= 255:
    rgb_arr /= 255.0
else:
    rgb_arr /= 10000.0

p2, p98 = np.percentile(rgb_arr, (2, 98))
rgb_arr = (rgb_arr - p2) / (p98 - p2)

rgb_arr = np.clip(rgb_arr, 0, 1)

plt.figure(figsize=(16, 10))

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
plt.imshow(largest_mask, cmap="Blues")
plt.axis("off")

plt.subplot(2, 2, 4)
plt.title("Closest-to-Dam Component (NEW LOGIC)")
plt.imshow(selected_mask, cmap="Blues")
plt.axis("off")

plt.tight_layout()
plt.show()


# ---------------------------------------------
# STEP 6 — INDIVIDUAL FIGURES
# ---------------------------------------------

print("\nDisplaying individual figures...\n")

plt.figure()
plt.title("Largest Component")
plt.imshow(largest_mask, cmap="Blues")
plt.axis("off")
plt.show()

plt.figure()
plt.title("Selected Component (Closest to Dam)")
plt.imshow(selected_mask, cmap="Blues")
plt.axis("off")
plt.show()


print("\nTest complete.")
print("If selected component corresponds to Panshet and not Varasgaon,")
print("the semantic selection works correctly.\n")