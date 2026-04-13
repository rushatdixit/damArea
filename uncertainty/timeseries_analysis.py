from objects import TimeSeries
from objects import Dam
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from typing import Any
from sentinelhub import BBox
import datetime
from concurrent.futures import ThreadPoolExecutor

def compute_timeseries(
        dam : Dam,
        resolution : float,
        dam_bbox : BBox,
        time_interval : Any,
        threshold : float = 0.2,
        interval_days: int = 30
    ) -> TimeSeries:
    """
    Computes area vs time across the given time_interval by stepping through it.
    """
    start_date_str, end_date_str = time_interval
    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")

    from pipeline.utilities import ensure_utm
    aoi = dam_bbox
    aoi = ensure_utm(aoi)

    if interval_days <= 0:
        interval_days = 30

    sub_intervals = []
    current_date = start_date
    while current_date < end_date:
        next_date = current_date + datetime.timedelta(days=interval_days)
        if next_date > end_date:
            next_date = end_date
        sub_intervals.append((current_date, next_date))
        if next_date == end_date:
            break
        current_date = next_date

    def process_interval(interval_tuple):
        c_date, n_date = interval_tuple
        sub_int_str = (c_date.strftime("%Y-%m-%d"), n_date.strftime("%Y-%m-%d"))
        try:
            data = acquire_satellite_data(
                expanded_dam_bbox=aoi,
                time_interval=sub_int_str,
                resolution=resolution,
                threshold=threshold,
                wants_rgb=False,
                wants_ndwi=False,
                wants_mask=True,
                wants_area=False,
                wants_debugs=False
            )
            water = choose_reservoir(
                dam_mask=data.mask,
                expanded_dam_bbox=aoi,
                dam=dam,
                resolution=resolution,
                min_area_km2=0.01,
                wants_debugs=False
            )
            return (c_date, water.area_km2)
        except Exception as e:
            print(f"Skipping interval {sub_int_str} due to Error: {e}")
            return None

    times = []
    areas_km2 = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(process_interval, sub_intervals)
        
    for res in results:
        if res is not None:
            times.append(res[0])
            areas_km2.append(res[1])

    return TimeSeries(times=times, areas_km2=areas_km2)
