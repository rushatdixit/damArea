"""
Full Visual Geometry Pipeline Demonstration
===========================================

This script visually demonstrates the full transformation chain:

RGB image
→ NDWI computation
→ Water mask
→ Largest connected component
→ Contour extraction
→ Green’s theorem area computation

It first displays ALL stages together in one overview figure.
Then it displays each stage individually, full screen.

Run:

    python3 test_full_contour_visual.py

This is a visual diagnostic and validation tool.
"""

import numpy as np
import matplotlib.pyplot as plt

from sentinelhub import CRS
from fetch_dam.get_dam import dam_name_to_bbox
from sentinel.aoi import expand_bbox_meters
from sentinel.request2 import request_sentinel_data, request_rgb_data
from sentinel.ndwi import compute_ndwi, water_mask

from processing.mask_processing import largest_connected_component
from processing.contour_extraction import extract_contours

from processing.pixel_to_metric import contour_pixels_to_metric
from geometry.greens_theorem import greens_area


# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------

DAM_NAME = "Panshet Dam"
TIME_INTERVAL = ("2023-01-01", "2023-12-31")
RESOLUTION = 10
EXPANSION_METERS = 10000
THRESHOLD = 0.2


# -----------------------------------------------------------
# DATA FETCHING
# -----------------------------------------------------------

print("\n==========================================")
print("Full Contour Processing Visual Test")
print("==========================================\n")

print("Fetching bounding box...")
bbox = dam_name_to_bbox(DAM_NAME)
bbox = expand_bbox_meters(bbox, EXPANSION_METERS)

print("Requesting RGB image...")
rgb = request_rgb_data(
    aoi=bbox,
    time_interval=TIME_INTERVAL,
    resolution=RESOLUTION
)

print("Requesting NDWI bands...")
ndwi_bands = request_sentinel_data(
    aoi=bbox,
    time_interval=TIME_INTERVAL,
    resolution=RESOLUTION
)

# -----------------------------------------------------------
# PROCESSING PIPELINE
# -----------------------------------------------------------

print("Computing NDWI...")
ndwi = compute_ndwi(ndwi_bands)
ndwi_arr = np.array(ndwi)

print("Applying threshold...")
mask = water_mask(ndwi, THRESHOLD)
mask_arr = np.array(mask)

print("Selecting largest connected component...")
main_mask = largest_connected_component(mask_arr)

print("Extracting contour...")
contours = extract_contours(main_mask)
largest_contour = max(contours, key=lambda x: len(x))

# -----------------------------------------------------------
# METRIC CONVERSION + AREA
# -----------------------------------------------------------

print("Converting contour to metric space...")

if bbox.crs == CRS.WGS84:
    center_lon = (bbox.min_x + bbox.max_x) / 2
    center_lat = (bbox.min_y + bbox.max_y) / 2
    utm_crs = CRS.get_utm_from_wgs84(center_lon, center_lat)
    bbox_utm = bbox.transform(utm_crs)
else:
    bbox_utm = bbox

metric_polygon = contour_pixels_to_metric(
    largest_contour,
    bbox_utm,
    RESOLUTION
)

area_m2 = greens_area(metric_polygon)
area_km2 = area_m2 / 1_000_000

print("\nGreen's Theorem Area:")
print(f"{area_m2:.2f} m²")
print(f"{area_km2:.6f} km²\n")


# ===========================================================
# PART 1: DISPLAY EVERYTHING TOGETHER
# ===========================================================

print("Displaying full pipeline overview...")

plt.figure(figsize=(18, 10))

rgb_arr = np.array(rgb, dtype=float)
max_val = rgb_arr.max()
if max_val > 1000:
    # Sentinel reflectance scale (0–10000)
    rgb_arr = rgb_arr / 10000.0
elif max_val > 1:
    # 8-bit image (0–255)
    rgb_arr = rgb_arr / 255.0
# else: already 0–1
p2, p98 = np.percentile(rgb_arr, (2, 98))
rgb_arr = (rgb_arr - p2) / (p98 - p2)
rgb_arr = np.clip(rgb_arr, 0, 1)


# RGB
plt.subplot(2, 3, 1)
plt.title("RGB")
plt.imshow(rgb_arr)
plt.axis("off")

# NDWI
plt.subplot(2, 3, 2)
plt.title("NDWI")
plt.imshow(ndwi_arr, cmap="RdBu")
plt.colorbar()
plt.axis("off")

# Mask
plt.subplot(2, 3, 3)
plt.title("Water Mask")
plt.imshow(mask_arr, cmap="Blues")
plt.axis("off")

# Largest component
plt.subplot(2, 3, 4)
plt.title("Largest Connected Component")
plt.imshow(main_mask, cmap="Blues")
plt.axis("off")

# Contour
plt.subplot(2, 3, 5)
plt.title("Extracted Contour")
plt.imshow(main_mask, cmap="gray")
plt.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=2)
plt.axis("off")

# Final overlay
plt.subplot(2, 3, 6)
plt.title("Final Boundary + Area")
plt.imshow(rgb_arr)
plt.plot(largest_contour[:, 1], largest_contour[:, 0], linewidth=2)
plt.text(
    10, 20,
    f"Area: {area_km2:.4f} km²",
    color="yellow",
    fontsize=12,
    bbox=dict(facecolor="black", alpha=0.6)
)
plt.axis("off")

plt.tight_layout()
plt.show()


# ===========================================================
# PART 2: DISPLAY EACH STAGE INDIVIDUALLY
# ===========================================================

print("Displaying individual stages...\n")

def show_fullscreen(title, image, cmap=None, contour=None):
    plt.figure(figsize=(8, 8))
    plt.title(title)
    plt.imshow(image, cmap=cmap)
    if contour is not None:
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)
    plt.axis("off")
    plt.show()


# 1 RGB
show_fullscreen("RGB Image", rgb_arr)

# 2 NDWI
show_fullscreen("NDWI Heatmap", ndwi_arr, cmap="RdBu")

# 3 Binary Mask
show_fullscreen("Binary Water Mask", mask_arr, cmap="Blues")

# 4 Largest Component
show_fullscreen("Largest Connected Component", main_mask, cmap="Blues")

# 5 Contour Only
show_fullscreen("Extracted Contour", main_mask, cmap="gray", contour=largest_contour)

# 6 Final Overlay
show_fullscreen("Final Reservoir Boundary + Area", rgb_arr, contour=largest_contour)

print("Visualization complete.\n")
