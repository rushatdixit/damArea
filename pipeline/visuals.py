"""
Pipeline visualization module.

Renders the full pipeline progression and individual diagnostic figures.
Does not compute or modify data — visualization only.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Optional


def normalize_rgb(rgb: np.ndarray) -> np.ndarray:
    """
    Robust RGB normalization using percentile stretch.

    :param rgb: Raw RGB array.
    :type rgb: np.ndarray
    :return: Normalized RGB array clipped to [0, 1].
    :rtype: np.ndarray
    """
    rgb = np.asarray(rgb).astype(float)

    p2, p98 = np.percentile(rgb, (2, 98))
    if p98 - p2 == 0:
        return np.clip(rgb, 0, 1)

    rgb = np.clip((rgb - p2) / (p98 - p2), 0, 1)

    return rgb


def show_pipeline_overview(
    rgb: np.ndarray,
    ndwi: np.ndarray,
    full_mask: np.ndarray,
    selected_mask: np.ndarray,
    contour_pixels: np.ndarray,
    area_km2: float,
    uncertainty_km2: float,
    coarse_mask: np.ndarray,
    coarse_selected_mask: np.ndarray,
) -> None:
    """
    Displays the full pipeline progression as a 2×3 grid:
    RGB → NDWI → Mask → Selected → 50km Context → Final Area.

    Saves the figure to ``your_outputs/Pipeline_Overview.png``.

    :param rgb: RGB composite array.
    :type rgb: np.ndarray
    :param ndwi: NDWI array.
    :type ndwi: np.ndarray
    :param full_mask: Full binary water mask.
    :type full_mask: np.ndarray
    :param selected_mask: Binary mask of the selected reservoir.
    :type selected_mask: np.ndarray
    :param contour_pixels: Contour coordinates in (row, col) format.
    :type contour_pixels: np.ndarray
    :param area_km2: Estimated reservoir area in km².
    :type area_km2: float
    :param uncertainty_km2: Uncertainty bound in km².
    :type uncertainty_km2: float
    :param coarse_mask: Coarse-scale water mask for context.
    :type coarse_mask: np.ndarray
    :param coarse_selected_mask: Coarse-scale selected reservoir mask.
    :type coarse_selected_mask: np.ndarray
    """
    rgb = normalize_rgb(rgb)
    contour_pixels = np.array(contour_pixels)
    plt.figure(figsize=(16, 10))

    plt.subplot(2, 3, 1)
    plt.title("RGB")
    plt.imshow(rgb)
    plt.axis("off")

    plt.subplot(2, 3, 2)
    plt.title("NDWI")
    im = plt.imshow(ndwi, cmap="RdBu")
    plt.colorbar(im, fraction=0.046)
    plt.axis("off")

    plt.subplot(2, 3, 3)
    plt.title("All Water")
    plt.imshow(full_mask, cmap="Blues")
    plt.axis("off")

    plt.subplot(2, 3, 4)
    plt.title("Selected Reservoir")
    plt.imshow(selected_mask, cmap="Blues")
    plt.axis("off")

    plt.subplot(2, 3, 5)
    plt.title("50km x 50km Context")
    plt.imshow(coarse_mask, cmap="Blues", alpha=0.5)
    cmap_red = mcolors.ListedColormap(['none', 'red'])
    plt.imshow(coarse_selected_mask, cmap=cmap_red)
    plt.axis("off")

    plt.subplot(2, 3, 6)
    plt.title(f"Final Area\nArea: {area_km2:.4f} ± {uncertainty_km2:.4f} km²")
    plt.imshow(rgb)
    plt.plot(contour_pixels[:, 1], contour_pixels[:, 0], linewidth=2)
    plt.axis("off")

    plt.tight_layout()
    os.makedirs('your_outputs', exist_ok=True)
    plt.savefig('your_outputs/Pipeline_Overview.png', bbox_inches='tight')
    plt.show()


def show_individual_figures(
    rgb: np.ndarray,
    ndwi: np.ndarray,
    full_mask: np.ndarray,
    selected_mask: np.ndarray,
) -> None:
    """
    Displays each pipeline stage as a separate figure for detailed inspection.

    :param rgb: RGB composite array.
    :type rgb: np.ndarray
    :param ndwi: NDWI array.
    :type ndwi: np.ndarray
    :param full_mask: Full binary water mask.
    :type full_mask: np.ndarray
    :param selected_mask: Selected reservoir mask.
    :type selected_mask: np.ndarray
    """
    rgb = normalize_rgb(rgb)
    plt.figure()
    plt.title("RGB")
    plt.imshow(rgb)
    plt.axis("off")
    plt.show()

    plt.figure()
    plt.title("NDWI")
    plt.imshow(ndwi, cmap="RdBu")
    plt.colorbar()
    plt.axis("off")
    plt.show()

    plt.figure()
    plt.title("All Water Mask")
    plt.imshow(full_mask, cmap="Blues")
    plt.axis("off")
    plt.show()

    plt.figure()
    plt.title("Selected Reservoir Mask")
    plt.imshow(selected_mask, cmap="Blues")
    plt.axis("off")
    plt.show()