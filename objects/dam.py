"""
Creating the class dam, and the reservoir class
"""

from functools import cached_property
from dataclasses import dataclass
from sentinelhub import BBox
from fetch_dam.get_dam import dam_name_to_coords
from objects.results import FetchedDamData

@dataclass
class Dam:
    name : str

    def aoi(self) -> BBox:
        """
        The area of interest (aoi). It is that patch of land you get when you set expansion = 2000m
        """
        from pipeline.acquisition import acquire_aoi
        aoi = acquire_aoi(self, expansion=2000)
        return aoi

    @cached_property
    def fetched_dam_data(self) -> FetchedDamData:
        coords = dam_name_to_coords(self.name)
        return coords
    
    def latitude(self) -> float:
        return self.fetched_dam_data.latitude
    
    def longitude(self) -> float:
        return self.fetched_dam_data.longitude
    