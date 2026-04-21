"""
Timeseries computation: reservoir area over time with SAR cloud failover.
"""

import os
import datetime
from typing import Tuple, Optional, List

import numpy as np
import pandas as pd
from sentinelhub import BBox
from concurrent.futures import ThreadPoolExecutor

from objects import TimeSeries, Dam
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from sentinel.request import NoImageryFoundError


def compute_timeseries(
    dam: Dam,
    resolution: float,
    dam_bbox: BBox,
    time_interval: Tuple[str, str],
    threshold: float = 0.2,
    interval_days: int = 30,
    allow_sar: bool = True,
    expected_area_km2: Optional[float] = None,
) -> TimeSeries:
    """
    Computes reservoir area at regular intervals over a time span.

    Steps through the time range in ``interval_days`` increments, attempts
    optical acquisition for each sub-interval, and falls back to SAR
    if cloud cover is detected or the computed area is suspiciously low.

    :param dam: Dam object with coordinates.
    :type dam: Dam
    :param resolution: Pixel resolution in meters.
    :type resolution: float
    :param dam_bbox: UTM bounding box of the reservoir.
    :type dam_bbox: BBox
    :param time_interval: Start and end dates as (YYYY-MM-DD, YYYY-MM-DD).
    :type time_interval: Tuple[str, str]
    :param threshold: NDWI threshold for water classification.
    :type threshold: float
    :param interval_days: Step size in days between measurements.
    :type interval_days: int
    :param allow_sar: Whether to allow SAR failover on cloudy intervals.
    :type allow_sar: bool
    :param expected_area_km2: Expected area for cloud-detection heuristic.
    :type expected_area_km2: Optional[float]
    :return: Timeseries of area measurements with min/max date metadata.
    :rtype: TimeSeries
    """
    start_date_str, end_date_str = time_interval
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

    from pipeline.utilities import ensure_utm
    aoi = ensure_utm(dam_bbox)

    if interval_days <= 0:
        interval_days = 30

    sub_intervals: List[Tuple[datetime.datetime, datetime.datetime]] = []
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + datetime.timedelta(days=interval_days)
        if next_date > end_date:
            next_date = end_date
        sub_intervals.append((current_date, next_date))
        if next_date == end_date:
            break
        current_date = next_date

    def process_interval(
        interval_tuple: Tuple[datetime.datetime, datetime.datetime],
    ) -> Optional[Tuple[datetime.datetime, float]]:
        """
        Processes a single time interval to compute reservoir area.

        :param interval_tuple: Start and end datetime for this sub-interval.
        :type interval_tuple: Tuple[datetime.datetime, datetime.datetime]
        :return: Tuple of (date, area_km2) or None if both optical and SAR fail.
        :rtype: Optional[Tuple[datetime.datetime, float]]
        """
        c_date, n_date = interval_tuple
        sub_int_str = (c_date.strftime("%Y-%m-%d"), n_date.strftime("%Y-%m-%d"))

        def attempt_sar() -> Optional[Tuple[datetime.datetime, float]]:
            """
            Attempts SAR-based area estimation as a fallback.

            :return: Tuple of (date, area_km2) or None if SAR also fails.
            :rtype: Optional[Tuple[datetime.datetime, float]]
            """
            print(f"Falling back to Sentinel-1 SAR for interval {sub_int_str}...")
            try:
                sar_data = acquire_satellite_data(
                    expanded_dam_bbox=aoi, time_interval=sub_int_str, resolution=resolution,
                    threshold=threshold, wants_rgb=False, wants_ndwi=False,
                    wants_mask=True, wants_area=False, wants_debugs=False, use_sar=True,
                )
                sar_water = choose_reservoir(
                    dam_mask=sar_data.mask, expanded_dam_bbox=aoi, dam=dam,
                    resolution=resolution, min_area_km2=0.01, wants_debugs=False,
                )
                return (c_date, sar_water.area_km2)
            except (NoImageryFoundError, ValueError) as e:
                print(f"SAR also failed for interval {sub_int_str}: {e}")
                return None

        try:
            data = acquire_satellite_data(
                expanded_dam_bbox=aoi, time_interval=sub_int_str, resolution=resolution,
                threshold=threshold, wants_rgb=False, wants_ndwi=False, wants_mask=True,
                wants_area=False, wants_debugs=False, use_sar=False,
            )
            water = choose_reservoir(
                dam_mask=data.mask, expanded_dam_bbox=aoi, dam=dam,
                resolution=resolution, min_area_km2=0.01, wants_debugs=False,
            )
            computed_area = water.area_km2

            if expected_area_km2 is not None and computed_area < (expected_area_km2 / 2):
                if allow_sar:
                    print(f"Optical area {computed_area:.2f} < threshold ({expected_area_km2/2:.2f}) for {sub_int_str}. Clouds likely obscured reservoir.")
                    return attempt_sar()
                else:
                    return (c_date, computed_area)

            return (c_date, computed_area)

        except NoImageryFoundError:
            if not allow_sar:
                print(f"Skipping interval {sub_int_str}: no imagery (SAR disabled)")
                return None
            print(f"Clouds detected for interval {sub_int_str}.")
            return attempt_sar()

        except ValueError as e:
            if not allow_sar:
                print(f"Skipping interval {sub_int_str}: {e}")
                return None
            print(f"Optical extraction failed for {sub_int_str}: {e}")
            return attempt_sar()

    times: List[datetime.datetime] = []
    areas_km2: List[float] = []

    is_debug = os.environ.get("DAM_DEBUG_DIR") or os.environ.get("DAM_VERBOSE_DIR")
    workers = 1 if is_debug else 5

    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = executor.map(process_interval, sub_intervals)

    for res in results:
        if res is not None:
            times.append(res[0])
            areas_km2.append(res[1])

    df = pd.DataFrame({'date': times, 'area_km2': areas_km2})
    if not df.empty:
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
    else:
        df = pd.DataFrame(columns=['area_km2'])
        df.index.name = 'date'

    min_date_str: Optional[str] = None
    max_date_str: Optional[str] = None

    if not df.empty:
        min_date = df['area_km2'].idxmin()
        max_date = df['area_km2'].idxmax()

        for c_date, n_date in sub_intervals:
            if pd.Timestamp(c_date) == pd.Timestamp(min_date):
                min_date_str = c_date.strftime("%Y-%m-%d") + "," + n_date.strftime("%Y-%m-%d")
                break
        for c_date, n_date in sub_intervals:
            if pd.Timestamp(c_date) == pd.Timestamp(max_date):
                max_date_str = c_date.strftime("%Y-%m-%d") + "," + n_date.strftime("%Y-%m-%d")
                break

    return TimeSeries(
        df=df,
        min_date_str=min_date_str,
        max_date_str=max_date_str,
    )
