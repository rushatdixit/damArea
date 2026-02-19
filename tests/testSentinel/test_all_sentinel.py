"""
Sentinel Hub Full Pipeline Test Runner
---------------------------------------

This file:

1. Loads config
2. Builds AOI
3. Requests Sentinel-2 data
4. Computes NDWI
5. Computes water mask
6. Computes water area
7. Displays visual diagnostics

Run directly:

    python test_sentinel_pipeline.py

No pytest required.
"""

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------

import sys
import traceback
import numpy as np

from sentinel.config import get_sh_config
from sentinel.aoi import geometry_from_geojson
from sentinel.request import request_sentinel_data
from sentinel.ndwi import compute_ndwi, water_mask

import matplotlib.pyplot as plt


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

TEST_GEOJSON = {
    "type": "Polygon",
    "coordinates": [[
        [72.8, 19.0],
        [72.81, 19.0],
        [72.81, 19.01],
        [72.8, 19.01],
        [72.8, 19.0]
    ]]
}

TIME_INTERVAL = ("2024-01-01", "2024-01-31")
RESOLUTION = 10
THRESHOLD = 0.2
PIXEL_AREA = 10 * 10  # m²


# ------------------------------------------------------------
# Structured Test Functions
# ------------------------------------------------------------

def test_config():
    print("Running: Config Test")
    config = get_sh_config()
    assert config.sh_client_id is not None
    assert config.sh_client_secret is not None
    print("✓ Config loaded\n")


def test_geometry():
    print("Running: Geometry Test")
    geometry = geometry_from_geojson(TEST_GEOJSON)
    assert geometry is not None
    print("✓ Geometry created\n")
    return geometry


def test_request(geometry):
    print("Running: Sentinel Request Test")
    data = request_sentinel_data(
        aoi=geometry,
        time_interval=TIME_INTERVAL,
        resolution=RESOLUTION
    )

    assert data is not None
    assert len(data) > 0
    assert len(data[0]) > 0
    assert len(data[0][0]) >= 3

    print(f"✓ Data received | Shape: {len(data)} x {len(data[0])} x 2\n")
    return data


def test_ndwi(data):
    print("Running: NDWI Computation Test")

    ndwi = compute_ndwi(data)

    assert len(ndwi) == len(data)
    assert len(ndwi[0]) == len(data[0])

    # Check value range
    for row in ndwi:
        for val in row:
            assert -1.1 <= val <= 1.1

    print("✓ NDWI computed | Values within expected range\n")
    return ndwi


def test_mask(ndwi):
    print("Running: Water Mask Test")

    mask = water_mask(ndwi, threshold=THRESHOLD)

    assert len(mask) == len(ndwi)
    assert len(mask[0]) == len(ndwi[0])

    water_pixels = sum(
        1 for row in mask for val in row if val
    )

    print(f"✓ Water mask created | Water pixels: {water_pixels}\n")
    return mask, water_pixels


def test_area(water_pixels):
    print("Running: Area Calculation Test")

    area_m2 = water_pixels * PIXEL_AREA
    area_km2 = area_m2 / 1_000_000

    print(f"✓ Water Area: {area_m2:.2f} m²")
    print(f"✓ Water Area: {area_km2:.6f} km²\n")


def visual_debug(data, threshold=0.2):
    print("Running: Visual Debug")

    import numpy as np
    import matplotlib.pyplot as plt

    data = np.array(data)

    # Split bands
    rgb = data[:, :, :3]
    ndwi = data[:, :, 3]

    # Normalize RGB for display (Sentinel reflectance scaling)
    rgb = rgb / 10000.0
    rgb = np.clip(rgb, 0, 1)

    # Water mask
    water_mask = ndwi > threshold

    # --- RGB Image ---
    plt.figure()
    plt.title("True Color (RGB)")
    plt.imshow(rgb)
    plt.axis("off")
    plt.show()

    # --- NDWI ---
    plt.figure()
    plt.title("NDWI")
    plt.imshow(ndwi, cmap="RdBu")
    plt.colorbar()
    plt.show()

    # --- NDWI Histogram ---
    plt.figure()
    plt.hist(ndwi.flatten(), bins=100)
    plt.axvline(x=threshold, color='red', linestyle='--')
    plt.title("NDWI Histogram")
    plt.xlabel("NDWI Value")
    plt.ylabel("Pixel Count")
    plt.show()

    # --- Water Mask ---
    plt.figure()
    plt.title("Water Mask")
    plt.imshow(water_mask, cmap="Blues")
    plt.axis("off")
    plt.show()

    print("✓ Visual inspection complete\n")



# ------------------------------------------------------------
# Master Runner
# ------------------------------------------------------------

def run_all_tests():

    try:
        print("\n==============================")
        print(" SENTINEL PIPELINE TEST RUN ")
        print("==============================\n")

        test_config()
        geometry = test_geometry()
        data = test_request(geometry)
        ndwi = test_ndwi(data)
        mask, water_pixels = test_mask(ndwi)
        test_area(water_pixels)

        visual_debug(data)

        print("===================================")
        print(" ALL TESTS PASSED SUCCESSFULLY ")
        print("===================================\n")

    except Exception as e:
        print("\n===================================")
        print(" TEST FAILED ")
        print("===================================\n")

        traceback.print_exc()
        sys.exit(1)


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    run_all_tests()
