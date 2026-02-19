"""
Full Sentinel Pipeline Test
Tests:
    - Config loading
    - AOI creation
    - NDWI band request
    - RGB request
    - NDWI computation
    - Water mask
    - Area estimation
    - Visual debug (RGB + NDWI + Histogram + Mask)
"""

import numpy as np
import matplotlib.pyplot as plt

from sentinel.aoi import geometry_from_geojson
from sentinel.request import request_sentinel_data, request_rgb_data
from sentinel.ndwi import compute_ndwi, water_mask
from sentinel.config import get_sh_config


# ==============================
# CONFIG
# ==============================

TIME_INTERVAL = ("2023-01-01", "2023-12-31")
RESOLUTION = 10  # meters
NDWI_THRESHOLD = 0.2


# ==============================
# TESTS
# ==============================

def test_config():
    print("Running: Config Test")
    config = get_sh_config()
    assert config.sh_client_id is not None
    assert config.sh_client_secret is not None
    print("✓ Config loaded\n")


def test_geometry():
    print("Running: Geometry Test")

    # Replace with your real polygon if needed
    geojson = {
        "type": "Polygon",
        "coordinates": [[
            [77.0, 28.0],
            [77.01, 28.0],
            [77.01, 28.01],
            [77.0, 28.01],
            [77.0, 28.0]
        ]]
    }

    geometry = geometry_from_geojson(geojson)
    print("✓ Geometry created\n")
    return geometry


def test_ndwi_request(geometry):
    print("Running: NDWI Band Request Test")

    data = request_sentinel_data(
        aoi=geometry,
        time_interval=TIME_INTERVAL,
        resolution=RESOLUTION
    )

    arr = np.array(data)
    print(f"✓ NDWI bands received | Shape: {arr.shape}\n")

    assert arr.shape[2] == 3  # Green + NIR
    return data


def test_rgb_request(geometry):
    print("Running: RGB Request Test")

    data = request_rgb_data(
        aoi=geometry,
        time_interval=TIME_INTERVAL,
        resolution=RESOLUTION
    )

    arr = np.array(data)
    print(f"✓ RGB data received | Shape: {arr.shape}\n")

    assert arr.shape[2] == 3  # R, G, B
    return data


def test_ndwi_computation(data):
    print("Running: NDWI Computation Test")

    ndwi = compute_ndwi(data)
    arr = np.array(ndwi)

    print(f"✓ NDWI computed | Range: {arr.min():.3f} to {arr.max():.3f}\n")
    return ndwi


def test_water_mask(ndwi):
    print("Running: Water Mask Test")

    mask = water_mask(ndwi, threshold=NDWI_THRESHOLD)
    mask_arr = np.array(mask)

    water_pixels = np.sum(mask_arr)
    print(f"✓ Water pixels: {water_pixels}\n")

    return mask


def test_area(mask):
    print("Running: Area Calculation Test")

    mask_arr = np.array(mask)
    water_pixels = np.sum(mask_arr)

    pixel_area = RESOLUTION * RESOLUTION  # m²
    total_area_m2 = water_pixels * pixel_area
    total_area_km2 = total_area_m2 / 1e6

    print(f"✓ Water Area: {total_area_m2:.2f} m²")
    print(f"✓ Water Area: {total_area_km2:.6f} km²\n")


# ==============================
# VISUAL DEBUG
# ==============================

def visual_debug(rgb_data, ndwi, mask):
    print("Running: Visual Debug")

    rgb = np.array(rgb_data).astype(float)

    # Normalize RGB for display
    rgb = rgb / np.max(rgb)

    ndwi_arr = np.array(ndwi)
    mask_arr = np.array(mask)

    plt.figure(figsize=(18, 5))

    # RGB
    plt.subplot(1, 4, 1)
    plt.title("True Color (RGB)")
    plt.imshow(rgb)
    plt.axis("off")

    # NDWI
    plt.subplot(1, 4, 2)
    plt.title("NDWI")
    plt.imshow(ndwi_arr, cmap="RdBu")
    plt.colorbar()

    # Histogram
    plt.subplot(1, 4, 3)
    plt.title("NDWI Histogram")
    plt.hist(ndwi_arr.flatten(), bins=100)
    plt.axvline(0.2, color="red", linestyle="--")
    plt.xlabel("NDWI")
    plt.ylabel("Pixel Count")

    # Water mask
    plt.subplot(1, 4, 4)
    plt.title("Water Mask")
    plt.imshow(mask_arr, cmap="Blues")
    plt.axis("off")

    plt.tight_layout()
    plt.show()

    print("✓ Visual inspection complete\n")


# ==============================
# MAIN RUNNER
# ==============================

def run_all_tests():
    print("\n==============================")
    print(" SENTINEL PIPELINE TEST RUN ")
    print("==============================\n")

    test_config()
    geometry = test_geometry()

    ndwi_bands = test_ndwi_request(geometry)
    rgb_data = test_rgb_request(geometry)

    ndwi = test_ndwi_computation(ndwi_bands)
    mask = test_water_mask(ndwi)

    test_area(mask)
    visual_debug(rgb_data, ndwi, mask)

    print("===================================")
    print(" ALL TESTS PASSED SUCCESSFULLY ")
    print("===================================\n")


if __name__ == "__main__":
    run_all_tests()
