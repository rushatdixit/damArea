"""
Manual Geometry Pipeline Test
==============================

This file tests the core geometric components of the Dam Area Measure system.

We test in THREE layers:

1) Pure mathematical sanity test
   - Green's theorem on a known square.
   - If this fails, area computation is broken.

2) Pixel → Metric conversion test
   - Ensures coordinate transformation is correct.
   - Verifies axis flip and resolution scaling.

3) Full synthetic raster pipeline test
   - Simulates a binary water mask.
   - Extracts contour using marching squares.
   - Converts contour to metric coordinates.
   - Computes area using Green’s theorem.

This file is self-contained and does NOT require pytest.

Run:

    python3 test_geometry_pipeline_manual.py

If all tests pass, your geometric foundation is correct.
"""

import numpy as np

# Import your project functions
from geometry.greens_theorem import greens_area
from processing.pixel_to_metric import contour_pixels_to_metric
from processing.contour_extraction import extract_contours


# ============================================================
# TEST 1: PURE MATHEMATICAL SANITY CHECK
# ============================================================

def test_known_square():
    print("\n==============================")
    print("TEST 1: Known Square Area Test")
    print("==============================")
    print("We construct a square of side length 10 meters.")
    print("Expected area = 100 m².")

    square = np.array([
        [0, 0],
        [10, 0],
        [10, 10],
        [0, 10]
    ])

    area = greens_area(square)

    print("Computed area:", area)

    if abs(area - 100) < 1e-6:
        print("PASS ✅ Green's theorem works correctly.")
    else:
        print("FAIL ❌ Area computation incorrect.")


# ============================================================
# TEST 2: PIXEL → METRIC TRANSFORMATION
# ============================================================

def test_pixel_to_metric():
    print("\n====================================")
    print("TEST 2: Pixel → Metric Conversion")
    print("====================================")
    print("We simulate a 10×10 pixel square.")
    print("Resolution = 10 meters per pixel.")
    print("Expected area = (100m × 100m) = 10,000 m².")

    resolution = 10  # meters per pixel

    # Pixel contour
    contour_pixels = np.array([
        [0, 0],
        [0, 10],
        [10, 10],
        [10, 0]
    ])

    # Fake UTM bounding box
    class FakeBBox:
        min_x = 1000
        max_y = 2000

    bbox = FakeBBox()

    metric_polygon = contour_pixels_to_metric(
        contour_pixels,
        bbox,
        resolution
    )

    area = greens_area(metric_polygon)

    expected_area = (10 * resolution) ** 2

    print("Computed area:", area)
    print("Expected area:", expected_area)

    if abs(area - expected_area) < 1e-6:
        print("PASS ✅ Pixel-to-metric transformation correct.")
    else:
        print("FAIL ❌ Coordinate transformation incorrect.")


# ============================================================
# TEST 3: FULL SYNTHETIC RASTER PIPELINE
# ============================================================

def test_synthetic_mask_pipeline():
    print("\n========================================")
    print("TEST 3: Full Raster → Geometry Pipeline")
    print("========================================")
    print("We simulate a binary mask containing a square water region.")
    print("Then we extract contour, convert to metric, compute area.")

    resolution = 5  # meters per pixel

    # Create 100x100 mask
    mask = np.zeros((100, 100), dtype=bool)

    # Create a 20x20 water square
    mask[30:50, 40:60] = True

    print("Synthetic square size: 20 pixels × 20 pixels")
    print("Resolution:", resolution, "meters per pixel")

    # Extract contours
    contours = extract_contours(mask)

    if not contours:
        print("FAIL ❌ No contours detected.")
        return

    # Select largest contour
    largest = max(contours, key=lambda x: len(x))

    # Fake UTM bounding box
    class FakeBBox:
        min_x = 0
        max_y = 500

    bbox = FakeBBox()

    metric_polygon = contour_pixels_to_metric(
        largest,
        bbox,
        resolution
    )

    area = greens_area(metric_polygon)

    expected_area = (20 * resolution) ** 2

    print("Computed area:", area)
    print("Expected area (approx):", expected_area)

    print("\nNOTE:")
    print("Marching squares smooths pixel edges.")
    print("So computed area may differ slightly from pixel area.")

    difference = abs(area - expected_area)
    print("Difference:", difference)

    if difference < expected_area * 0.05:
        print("PASS ✅ Full pipeline behaves correctly.")
    else:
        print("WARNING ⚠️ Large discrepancy detected.")


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("\n==============================================")
    print("Dam Area Measure — Geometry Validation Suite")
    print("==============================================")

    test_known_square()
    test_pixel_to_metric()
    test_synthetic_mask_pipeline()

    print("\nAll tests completed.")
    print("If all sections show PASS, your geometry engine is sound.\n")
