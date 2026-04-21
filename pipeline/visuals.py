"""
Dam Area Measure — Visualization Module

This module:
- Does NOT compute NDWI
- Does NOT compute area
- Does NOT modify masks

It only visualizes results produced by the pipeline.

Designed for research-quality figures.
"""

import numpy as np
import matplotlib.pyplot as plt

def normalize_rgb(rgb: np.ndarray) -> np.ndarray:
    """
    Robust RGB normalization using percentile stretch.
    Prevents dark/black images.
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
    Displays the full pipeline progression:

    RGB → NDWI → Mask → Selected → Contour + Area
    """

    rgb = normalize_rgb(rgb)
    contour_pixels = np.array(contour_pixels)
    plt.figure(figsize=(16, 10))

    # RGB
    plt.subplot(2, 3, 1)
    plt.title("RGB")
    plt.imshow(rgb)
    plt.axis("off")

    # NDWI
    plt.subplot(2, 3, 2)
    plt.title("NDWI")
    im = plt.imshow(ndwi, cmap="RdBu")
    plt.colorbar(im, fraction=0.046)
    plt.axis("off")

    # Full mask
    plt.subplot(2, 3, 3)
    plt.title("All Water")
    plt.imshow(full_mask, cmap="Blues")
    plt.axis("off")

    # Selected mask
    plt.subplot(2, 3, 4)
    plt.title("Selected Reservoir")
    plt.imshow(selected_mask, cmap="Blues")
    plt.axis("off")

    # 50km x 50km Context
    plt.subplot(2, 3, 5)
    plt.title("50km x 50km Context")
    plt.imshow(coarse_mask, cmap="Blues", alpha=0.5)
    
    # Overlay selected reservoir in distinct color (e.g., Red) to mark it
    import matplotlib.colors as mcolors
    cmap_red = mcolors.ListedColormap(['none', 'red'])
    plt.imshow(coarse_selected_mask, cmap=cmap_red)
    plt.axis("off")

    # Final overlay
    plt.subplot(2, 3, 6)
    plt.title(f"Final Area\nArea: {area_km2:.4f} ± {uncertainty_km2:.4f} km²")
    plt.imshow(rgb)
    plt.plot(contour_pixels[:, 1], contour_pixels[:, 0], linewidth=2)
    plt.axis("off")

    plt.tight_layout()
    import os
    os.makedirs('your_outputs', exist_ok=True)
    plt.savefig('your_outputs/Pipeline_Overview.png', bbox_inches='tight')
    plt.show()

def show_individual_figures(
    rgb: np.ndarray,
    ndwi: np.ndarray,
    full_mask: np.ndarray,
    selected_mask: np.ndarray,
)-> None:
    """
    Displays each stage separately for detailed inspection.
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