"""
Configuration settings for the damArea pipeline.
Centralizes hyperparameters and operational constants.
"""

# Default resolution (meters per pixel) for fetching satellite data if not specified
DEFAULT_RESOLUTION = 10

# NDWI threshold for classifying pixels as water
WATER_MASK_THRESHOLD = 0.2

# The minimum area (in km^2) a water body must be to be considered during processing.
# Used to eliminate noise.
MIN_AREA_KM2_PROCESSING = 0.01

# The minimum area (in km^2) a water body must be to be considered a valid reservoir candidate.
# Slightly larger than processing to ensure we only look at significant water bodies.
MIN_AREA_KM2_SELECTION = 0.5

# Initial expansion (in meters) around the dam coordinates for the first Area of Interest check
INITIAL_EXPANSION = 2000

# The maximum expansion (in meters) to attempt before breaking the expansion loop
BREAKING_EXPANSION = 20000

# The minimum number of water pixels touching the bounding box border
# to consider the expansion "insufficient" and trigger a larger expansion.
BOUNDARY_PIXELS_THRESHOLD = 10
