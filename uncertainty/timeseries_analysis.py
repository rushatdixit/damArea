from objects import TimeSeries
from objects import Dam
from pipeline.raw_data import acquire_satellite_data
from pipeline.processing import choose_reservoir
from typing import Any
from sentinelhub import BBox
import datetime

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

    current_date = start_date
    times = []
    areas_km2 = []

    from pipeline.utilities import ensure_utm
    aoi = dam_bbox
    aoi = ensure_utm(aoi)

    if interval_days <= 0:
        interval_days = 30

    while current_date < end_date:
        next_date = current_date + datetime.timedelta(days=interval_days)
        if next_date > end_date:
            next_date = end_date
            
        sub_interval = (current_date.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d"))

        try:
            data = acquire_satellite_data(
                expanded_dam_bbox=aoi,
                time_interval=sub_interval,
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
            
            times.append(current_date)
            areas_km2.append(water.area_km2)
        except Exception as e:
            # Skip this interval if satellite data is fully corrupted or not found
            pass
            
        if next_date == end_date:
            break
        current_date = next_date

    return TimeSeries(times=times, areas_km2=areas_km2)
