"""
defines whether a tile lies inside, outside or on a polygon
"""

from enum import Enum
from geometry.polygon import Polygon
from tiling.tile import Tile
import math

class TileClass(Enum):
    INSIDE = 1
    OUTSIDE = 2
    BOUNDARY = 3
    pass