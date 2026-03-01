"""
defines whether a tile lies inside, outside or on a polygon
"""

from enum import Enum
from geometry.polygon import Polygon

class TileClass(Enum):
    INSIDE = 1
    OUTSIDE = 2
    BOUNDARY = 3
    pass