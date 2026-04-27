"""
Cache inspection and purging utilities.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)


def get_cache_dir() -> Path:
    """
    Returns the path to the joblib cache directory.
    
    :return: Path object pointing to the cache directory.
    :rtype: Path
    """
    return Path(__file__).parent.parent / ".cache"


def display_cache_size() -> None:
    """
    Calculates and displays the size of the joblib cache directory.
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        logger.info("Cache directory does not exist.")
        return

    total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    logger.info(f"Total cache size: {size_mb:.2f} MB")


def purge_cache(dry_run: bool = False) -> None:
    """
    Purges the entire joblib cache directory.

    :param dry_run: If True, only simulate the deletion.
    :type dry_run: bool
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        logger.info("Cache directory does not exist. Nothing to purge.")
        return

    if dry_run:
        total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        logger.info(f"[Dry Run] Would delete {cache_dir} ({size_mb:.2f} MB)")
        return

    try:
        shutil.rmtree(cache_dir)
        logger.info(f"Successfully purged cache directory: {cache_dir}")
    except Exception as e:
        logger.error(f"Failed to purge cache directory: {e}")


def list_cache_entries() -> None:
    """
    Lists entries in the joblib cache, extracting metadata where possible.
    """
    cache_dir = get_cache_dir()
    if not cache_dir.exists():
        logger.info("Cache directory does not exist.")
        return

    joblib_dir = cache_dir / "joblib"
    if not joblib_dir.exists():
        logger.info("No joblib cache found.")
        return

    entries = []
    # joblib structure: .cache/joblib/module/function/hash/
    for module_dir in joblib_dir.iterdir():
        if not module_dir.is_dir():
            continue
        for func_dir in module_dir.iterdir():
            if not func_dir.is_dir():
                continue
            for hash_dir in func_dir.iterdir():
                if not hash_dir.is_dir():
                    continue
                
                # Check for metadata
                # Note: joblib does not always write metadata.json
                metadata = {}
                # In many joblib setups, output is stored in output.pkl
                output_file = hash_dir / "output.pkl"
                if output_file.exists():
                    size = output_file.stat().st_size
                    mtime = datetime.fromtimestamp(output_file.stat().st_mtime)
                    entries.append({
                        "function": f"{module_dir.name}.{func_dir.name}",
                        "hash": hash_dir.name,
                        "size_mb": size / (1024 * 1024),
                        "modified": mtime.strftime("%Y-%m-%d %H:%M:%S")
                    })

    if not entries:
        logger.info("No cache entries found.")
        return

    # Sort by modification time (newest first)
    entries.sort(key=lambda x: x["modified"], reverse=True)

    print("\nCache Entries:")
    print("-" * 80)
    print(f"{'Function':<40} | {'Modified':<20} | {'Size (MB)':<10}")
    print("-" * 80)
    for entry in entries:
        print(f"{entry['function']:<40} | {entry['modified']:<20} | {entry['size_mb']:.2f}")
    print("-" * 80)
