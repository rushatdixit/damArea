"""
Manual test runner for visual_debug()

Run with:
    python test_visual_debug_manual.py

This script:
1. Generates synthetic Sentinel-like data
2. Computes NDWI + mask
3. Runs visual_debug()
4. Programmatically validates:
   - 4 subplots exist
   - RGB not black
   - Histogram contains threshold line
   - Mask contains boolean values
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")  # Prevent GUI popups

import matplotlib.pyplot as plt

from pipeline.run_dam_pipeline import visual_debug
from sentinel.ndwi import compute_ndwi, water_mask


def run_test():
    # ----------------------------
    # Synthetic data
    # ----------------------------
    data = [
        [[5000, 1000, 4], [2000, 3000, 4]],
        [[6000, 1000, 8], [4000, 2000, 4]],
    ]

    rgb = np.random.uniform(2000, 8000, (2, 2, 3))

    ndwi = compute_ndwi(data)
    mask = water_mask(ndwi, threshold=0.2)

    # ----------------------------
    # Run visualization
    # ----------------------------
    visual_debug(rgb, ndwi, mask, threshold=0.2)

    fig = plt.gcf()
    axes = fig.axes

    # 1️⃣ Check subplot count
    assert len(axes) >= 4, "Expected at least 4 subplots."

    # 2️⃣ Check RGB not black
    rgb_image = axes[0].images[0].get_array()
    assert np.mean(rgb_image) > 0.05, "RGB appears black."

    # 3️⃣ Check histogram threshold line
    hist_axis = axes[2]
    assert len(hist_axis.lines) >= 1, "Threshold line missing."

    # 4️⃣ Check mask boolean
    mask_image = axes[3].images[0].get_array()
    assert mask_image.dtype == bool or np.array_equal(
        mask_image, mask_image.astype(bool)
    ), "Mask is not boolean."

    plt.close(fig)

    print("✅ visual_debug test passed successfully.")


if __name__ == "__main__":
    run_test()
