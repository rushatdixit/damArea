"""
Inspection CLI tools for visualizing intermediate arrays and masks.
"""

import os
import joblib
import numpy as np
from pathlib import Path
from sentinelhub import CRS, transform_point, BBox
from fetch_dam.get_dam import dam_name_to_coords
from sentinel.ndwi import water_mask
from sentinel.sar import sar_water_mask
from pipeline.visuals import normalize_rgb
from utils.logger import get_logger

logger = get_logger(__name__)


def load_array(path_str: str) -> np.ndarray:
    """
    Loads a numpy array from a .npy file or a joblib output.pkl file.
    """
    path = Path(path_str)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix == '.npy':
        return np.load(path)
    elif path.name == 'output.pkl' or path.suffix == '.pkl':
        data = joblib.load(path)
        if isinstance(data, np.ndarray):
            return data
        else:
            raise ValueError(f"Joblib pickle does not contain a numpy array. Found: type {type(data)}")
    elif path.is_dir() and (path / 'output.pkl').exists():
        data = joblib.load(path / 'output.pkl')
        if isinstance(data, np.ndarray):
            return data
        else:
            raise ValueError(f"Joblib pickle does not contain a numpy array. Found: type {type(data)}")
    else:
        raise ValueError(f"Unsupported file type. Please provide a .npy or .pkl file (or a joblib hash directory): {path}")


def inspect_bbox(dam_name: str, resolution: float = 10) -> None:
    """
    Inspect the coarse and refined bounding boxes for a dam.
    """
    logger.info(f"Inspecting bounding boxes for {dam_name}")
    try:
        coords = dam_name_to_coords(dam_name)
    except Exception as e:
        logger.error(f"Failed to fetch coords for {dam_name}: {e}")
        return

    utm_crs = CRS.get_utm_from_wgs84(coords.longitude, coords.latitude)
    dam_x, dam_y = transform_point((coords.longitude, coords.latitude), CRS.WGS84, utm_crs)

    coarse_bbox = BBox([dam_x - 25000, dam_y - 25000, dam_x + 25000, dam_y + 25000], crs=utm_crs)
    refined_bbox_width = 10000
    refined_bbox = BBox([dam_x - refined_bbox_width/2, dam_y - refined_bbox_width/2, dam_x + refined_bbox_width/2, dam_y + refined_bbox_width/2], crs=utm_crs)

    print("\n--- Bounding Box Inspection ---")
    print(f"Dam: {dam_name}")
    print(f"Coordinates: {coords.latitude:.6f}, {coords.longitude:.6f}")
    print(f"UTM Projection: {utm_crs}")
    print(f"Center UTM: X={dam_x:.2f}, Y={dam_y:.2f}")
    print("\nCoarse BBox (50km x 50km):")
    print(f"  Min: X={coarse_bbox.min_x:.2f}, Y={coarse_bbox.min_y:.2f}")
    print(f"  Max: X={coarse_bbox.max_x:.2f}, Y={coarse_bbox.max_y:.2f}")
    print("\nExpected Refined BBox (10km x 10km):")
    print(f"  Min: X={refined_bbox.min_x:.2f}, Y={refined_bbox.min_y:.2f}")
    print(f"  Max: X={refined_bbox.max_x:.2f}, Y={refined_bbox.max_y:.2f}")


def inspect_mask(path: str) -> None:
    """
    Inspect a binary mask.
    """
    try:
        arr = load_array(path)
    except Exception as e:
        logger.error(e)
        return

    if arr.ndim != 2:
        logger.error(f"Expected 2D array, got {arr.ndim}D array")
        return

    water_pixels = np.sum(arr > 0)
    total_pixels = arr.size
    percent_water = (water_pixels / total_pixels) * 100

    print("\n--- Mask Inspection ---")
    print(f"Shape: {arr.shape}")
    print(f"Water Pixels: {water_pixels}")
    print(f"Total Pixels: {total_pixels}")
    print(f"Percentage: {percent_water:.2f}%")


def inspect_ndwi(path: str, threshold: float = 0.2) -> None:
    """
    Inspect an NDWI array and apply a threshold.
    """
    try:
        arr = load_array(path)
    except Exception as e:
        logger.error(e)
        return

    if arr.ndim > 2:
        logger.info(f"Array is {arr.ndim}D. Assuming it is a multi-band optical image; please provide an NDWI array directly.")
        return

    mask = water_mask(arr.tolist(), threshold)
    mask = np.array(mask)
    water_pixels = np.sum(mask)

    print("\n--- NDWI Inspection ---")
    print(f"Shape: {arr.shape}")
    print(f"Min NDWI: {np.nanmin(arr):.4f}")
    print(f"Max NDWI: {np.nanmax(arr):.4f}")
    print(f"Mean NDWI: {np.nanmean(arr):.4f}")
    print(f"Threshold Applied: {threshold}")
    print(f"Water Pixels Found: {water_pixels}")


def inspect_sar(path: str, threshold: float = 0.09) -> None:
    """
    Inspect a SAR backscatter array and apply a threshold.
    """
    try:
        arr = load_array(path)
    except Exception as e:
        logger.error(e)
        return

    mask = sar_water_mask(arr, threshold)
    water_pixels = np.sum(mask)

    print("\n--- SAR Inspection ---")
    print(f"Shape: {arr.shape}")
    print(f"Min Backscatter: {np.nanmin(arr):.4f}")
    print(f"Max Backscatter: {np.nanmax(arr):.4f}")
    print(f"Mean Backscatter: {np.nanmean(arr):.4f}")
    print(f"Threshold Applied: {threshold}")
    print(f"Water Pixels Found: {water_pixels}")


def inspect_compare(opt_path: str, sar_path: str) -> None:
    """
    Compare an optical mask and a SAR mask.
    """
    try:
        opt_arr = load_array(opt_path)
        sar_arr = load_array(sar_path)
    except Exception as e:
        logger.error(e)
        return

    if opt_arr.shape != sar_arr.shape:
        logger.error(f"Shape mismatch: Optical {opt_arr.shape} vs SAR {sar_arr.shape}")
        return

    opt_mask = opt_arr > 0
    sar_mask = sar_arr > 0

    intersection = np.logical_and(opt_mask, sar_mask)
    union = np.logical_or(opt_mask, sar_mask)
    
    iou = np.sum(intersection) / np.sum(union) if np.sum(union) > 0 else 0
    dice = 2 * np.sum(intersection) / (np.sum(opt_mask) + np.sum(sar_mask)) if (np.sum(opt_mask) + np.sum(sar_mask)) > 0 else 0

    print("\n--- Optical vs SAR Comparison ---")
    print(f"Optical Water Pixels: {np.sum(opt_mask)}")
    print(f"SAR Water Pixels: {np.sum(sar_mask)}")
    print(f"Intersection Pixels: {np.sum(intersection)}")
    print(f"Union Pixels: {np.sum(union)}")
    print(f"IoU (Intersection over Union): {iou:.4f}")
    print(f"Dice Coefficient: {dice:.4f}")
