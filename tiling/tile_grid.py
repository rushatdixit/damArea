"""
converts a polygon into a grid of tiles
kind of like integrating a space in R2 using dxdy
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from geometry.polygon import Polygon
from tiling.tile import Tile
from geometry.segment import Segment
from geometry.point import Point
import math

@dataclass(frozen=True)
class TileGrid:
    """
    represents a grid of tiles
    takes input as a bounding box
    returns none
    stores grid parameters
    no tile clipping is done, tiles may overflow
    to future rushat, please code remembering the above.
    """
    bounds : Tuple[float, float, float, float]
    tile_size : float
    overlap : float

    def __post_init__(self):
        if self.bounds[0] > self.bounds[2] or self.bounds[1] > self.bounds[3]:
            raise ValueError("Incorrect Bounding Box. x_min > x_max or y_min > y_max")
        if self.overlap > self.tile_size:
            raise ValueError("Overlap cannot be greater than tile size")
        elif self.overlap < 0:
            self.overlap = self.tile_size % abs(self.overlap)
    
    @property
    def stride(self) -> float:
        return self.tile_size - self.overlap
    
    @property
    def grid_origin(self) -> Tuple[float, float]:
        return (
            self.bounds[0],
            self.bounds[1]
        )
    
    @property
    def n_cols(self) -> int:
        """
        the number of columns
        """
        width = self.bounds[2] - self.bounds[0]
        return math.ceil(width/self.stride)

    @property
    def n_rows(self) -> int:
        """
        the number of rows
        """
        height = self.bounds[3] - self.bounds[1]
        return math.ceil(height/self.stride)
    
    def tile_bounds(self, row : int, col : int) -> Tuple[float, float, float, float]:
        """
        returns the bounds of a tile at row,col
        remember a tile starts at
        x = x_min + col*stride
        y = y_min + row*stride
        """
        x, y = self.bounds[0], self.bounds[1]
        tile_x_min = x + col*self.stride
        tile_y_min = y + row*self.stride
        tile_x_max = tile_x_min + self.tile_size
        tile_y_max = tile_y_min + self.tile_size
        return (
            tile_x_min,
            tile_y_min,
            tile_x_max,
            tile_y_max
        )
    
    def __iter__(self):
        """
        an iterator which iterates tiles
        with this you can write:
            for tile in TileGrid:
                ...
        """
        for row in range(self.n_rows):
            for col in range(self.n_cols):
                bounds = self.tile_bounds(row, col)
                tile = Tile(row, col, bounds)
                yield tile
    
    def __len__(self) -> int:
        """
        outputs how many tiles there are
        """
        return self.n_rows*self.n_cols