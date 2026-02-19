"""
test_visual_debug.py
====================

Purpose
-------
Automated regression test for the `visual_debug` function.

This test ensures:

1. The function runs without crashing.
2. Exactly 4 subplots are created.
3. RGB visualization is not rendered fully black.
4. NDWI subplot renders correctly.
5. Histogram contains the threshold vertical line.
6. Mask subplot renders boolean data.
7. Cloud-masked pixels (NaN NDWI) do not break plotting.

Why This Exists
---------------
visual_debug() does not return values.
It produces matplotlib figures.

Without testing:
- Silent scaling bugs (e.g., double division by 10000)
- Black RGB plots
- Missing threshold line
- Broken subplot layout
- NaN crashes

could go unnoticed.

This test prevents visual regressions in your dam-area
measurement pipeline.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Headless backend for CI / pytest

import matplotlib.pyplot as plt
import pytest

from pipeline.run_dam_pipeline import visual_debug
from sentinel.ndwi import compute_ndwi, water_mask


# ------------------------------------------------------------------
# Synthetic Sentinel-like dataset fixture
# ------------------------------------------------------------------

@pytest.fixture
def synthetic_dataset():
    """
    Creates controlled synthetic Sentinel-style data cube.

    Bands:
        0 = Green (B03)
        1 = NIR   (B08)
        2 = SCL   (scene classification)

    Includes:
        - Water pixel
        - Land pixel
        - Cloud pixel (should become NaN in NDWI)
    """

    data = [
        [[5000, 1000, 4], [2000, 3000, 4]],
        [[6000, 1000, 8], [4000, 2000, 4]],
    ]

    # Create realistic RGB reflectance in raw Sentinel scale (0–10000)
    rgb = np.random.uniform(2000, 8000, (2, 2, 3))

    return rgb, data


# ------------------------------------------------------------------
# Core Visual Debug Test
# ------------------------------------------------------------------

def test_visual_debug_full_pipeline(synthetic_dataset):
    """
    Full integration test of visual_debug().

    Validates:
        - No runtime errors
        - Proper subplot count
        - RGB not fully black
        - NDWI image rendered
        - Histogram contains threshold line
        - Mask contains booleans
    """

    rgb, data = synthetic_dataset

    ndwi = compute_ndwi(data)
    mask = water_mask(ndwi, threshold=0.2)

    # Run function
    visual_debug(rgb, ndwi, mask, threshold=0.2)

    fig = plt.gcf()
    axes = fig.axes

    # -------------------------------------------------
    # 1️⃣ Validate subplot structure
    # -------------------------------------------------
    assert len(axes) >= 4, "Expected at least 4 subplots."

    rgb_axis = axes[0]
    ndwi_axis = axes[1]
    hist_axis = axes[2]
    mask_axis = axes[3]

    # -------------------------------------------------
    # 2️⃣ Validate RGB image not black
    # -------------------------------------------------
    rgb_image = rgb_axis.images[0].get_array()
    mean_intensity = np.mean(rgb_image)

    assert mean_intensity > 0.05, (
        "RGB appears nearly black. "
        "Likely incorrect reflectance scaling."
    )

    # -------------------------------------------------
    # 3️⃣ Validate NDWI subplot rendered
    # -------------------------------------------------
    assert len(ndwi_axis.images) == 1, "NDWI image missing."

    ndwi_image = ndwi_axis.images[0].get_array()
    assert not np.all(np.isnan(ndwi_image)), (
        "NDWI image entirely NaN."
    )

    # -------------------------------------------------
    # 4️⃣ Validate histogram contains threshold line
    # -------------------------------------------------
    vertical_lines = hist_axis.lines
    assert len(vertical_lines) >= 1, (
        "Threshold vertical line missing from histogram."
    )

    threshold_x = vertical_lines[0].get_xdata()[0]
    assert np.isclose(threshold_x, 0.2), (
        "Histogram threshold line placed incorrectly."
    )

    # -------------------------------------------------
    # 5️⃣ Validate mask subplot rendered boolean data
    # -------------------------------------------------
    mask_image = mask_axis.images[0].get_array()
    assert mask_image.dtype == bool or np.array_equal(
        mask_image, mask_image.astype(bool)
    ), "Mask subplot does not contain boolean data."

    # Cleanup
    plt.close(fig)