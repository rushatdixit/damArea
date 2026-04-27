"""
Output validation tool.
"""

import os
import pandas as pd
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)


def validate_outputs(dam_name: str, outputs_dir: str = "./your_outputs", strict: bool = False) -> None:
    """
    Validates pipeline outputs (such as timeseries data) for physical plausibility
    and cache staleness anomalies.
    """
    logger.info(f"Validating outputs for {dam_name} in {outputs_dir}...")
    
    out_path = Path(outputs_dir)
    if not out_path.exists():
        logger.warning(f"Outputs directory {outputs_dir} does not exist. (Pipeline might not have saved outputs yet).")
        return

    # Check for timeseries CSV
    safe_dam_name = dam_name.replace(" ", "_").lower()
    ts_file = out_path / f"{safe_dam_name}_timeseries.csv"
    
    issues_found = 0

    if ts_file.exists():
        logger.info(f"Found timeseries data: {ts_file.name}")
        try:
            df = pd.read_csv(ts_file)
            if 'area_km2' not in df.columns:
                logger.error("Missing 'area_km2' column in timeseries data.")
                issues_found += 1
            else:
                areas = df['area_km2'].values
                
                # Check 1: Area Plausibility (0.01 km^2 to 10,000 km^2)
                out_of_bounds = df[(df['area_km2'] < 0.01) | (df['area_km2'] > 10000)]
                if not out_of_bounds.empty:
                    logger.warning(f"Found {len(out_of_bounds)} physically implausible area estimates (<0.01 or >10000 km²).")
                    issues_found += 1
                    
                # Check 2: Exact Duplicates (suggests stale cache or identical SAR fallback)
                diffs = df['area_km2'].diff()
                duplicates = diffs[diffs == 0]
                if not duplicates.empty:
                    logger.warning(f"Found {len(duplicates)} exactly identical consecutive area measurements (possible stale cache).")
                    issues_found += 1
                    
                # Check 3: Huge swings (>50% single-step change, likely cloud contamination)
                if len(areas) > 1:
                    pct_changes = df['area_km2'].pct_change().abs()
                    huge_swings = pct_changes[pct_changes > 0.5]
                    if not huge_swings.empty:
                        logger.warning(f"Found {len(huge_swings)} extreme intervals with >50% area change (possible cloud masking failure).")
                        issues_found += 1
                        
        except Exception as e:
            logger.error(f"Failed to validate timeseries data: {e}")
            issues_found += 1
    else:
        logger.info(f"No timeseries CSV found for {dam_name}. Skipping timeseries checks.")

    print("\n--- Validation Summary ---")
    if issues_found == 0:
        logger.info("✅ All validation checks passed. Data looks healthy.")
    else:
        msg = f"⚠️ Found {issues_found} potential issues with the output data."
        if strict:
            logger.error(msg)
            import sys
            sys.exit(1)
        else:
            logger.warning(msg)
