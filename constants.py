"""
Configuration constants for the damArea pipeline.
Centralizes hyperparameters and operational thresholds.
"""

# Default resolution (meters per pixel) for fetching satellite data if not specified
DEFAULT_RESOLUTION: int = 10

# NDWI threshold for classifying pixels as water
WATER_MASK_THRESHOLD: float = 0.2

# SAR VV backscatter threshold (linear scale) for classifying pixels as water
SAR_THRESHOLD: float = 0.09

# Median filter kernel size for suppressing SAR speckle noise
SAR_SPECKLE_KERNEL: int = 5

# The minimum area (in km²) a water body must be to be considered during processing
MIN_AREA_KM2_PROCESSING: float = 0.01

# The minimum area (in km²) a water body must be to be considered a valid reservoir candidate
MIN_AREA_KM2_SELECTION: float = 0.5

# Initial expansion (in meters) around the dam coordinates for the first Area of Interest check
INITIAL_EXPANSION: int = 20000

# The maximum expansion (in meters) to attempt before breaking the expansion loop
BREAKING_EXPANSION: int = 20000

# The minimum number of water pixels touching the bounding box border
# to consider the expansion "insufficient" and trigger a larger expansion
BOUNDARY_PIXELS_THRESHOLD: int = 10
