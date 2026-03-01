from sentinelhub import BBox
from fetch_dam.get_dam import dam_name_to_bbox
from sentinel.aoi import expand_bbox_meters

def acquire_aoi(dam_name : str, expansion : int) -> BBox:
    """
    Given a name and an expansion, gives you the dam bbox expanded by "expansion" meters on all sides.
    
    :param dam_name: Name of the dam/reservoir
    :type dam_name: str
    :param expansion: Expansion in metres
    :type expansion: int
    :return: Expanded dam bbox
    :rtype: BBox
    """
    dam_bbox = dam_name_to_bbox(dam_name)
    expanded_dam_bbox = expand_bbox_meters(dam_bbox, expansion)
    return expanded_dam_bbox