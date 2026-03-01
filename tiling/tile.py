"""
defines the basic unit of area
a tile is essentially dxdy
"""
from dataclasses import dataclass
from typing import List, Tuple, Generator
from geometry.point import Point
from geometry.segment import Segment

@dataclass(frozen=True)
class Tile:
    """
    represents a tile
    row, col = None is allowed
    """
    row : int
    col : int
    bounds : Tuple[float, float, float, float]

    def __post_init__(self):
        if self.bounds[0] > self.bounds[2] or self.bounds[1] > self.bounds[3]:
            raise ValueError("Invalid tile dimensions, x_min or y_min is < x_max or y_max")
    
    def corners_cw(self) -> List[Point]:
        """
        returns corners in clockwise sense starting from bottomleft
        """
        bottom_left = Point((self.bounds[0], self.bounds[1]))
        top_right = Point((self.bounds[2], self.bounds[3]))
        top_left = Point((self.bounds[0], self.bounds[3]))
        bottom_right = Point((self.bounds[2], self.bounds[1]))
        return [
            bottom_left,
            bottom_right,
            top_right,
            top_left
        ]
    
    def corners_ccw(self) -> List[Point]:
        """
        returns corners in counter clockwise sense starting from bottom left
        """
        bl, br, tr, tl = self.corners_cw()
        return [bl, tl, tr, br]

    def point_in_tile(self, point : Point) -> bool:
        x1, y1, x2, y2 = self.bounds
        x = point.coordinates[0]
        y = point.coordinates[1]
        return x1 <= x <= x2 and y1 <= y <= y2 
    
    def tile_edges(self) -> Generator[Segment, None, None]:
        for i in range(len(self.corners_ccw())):
            j = (i + 1) % len(self.corners_ccw())
            yield Segment(self.corners_ccw()[i], self.corners_ccw()[j])

    def __repr__(self):
        return f"Tile(row={self.row}, col={self.col}, bounds={self.bounds})"