"""
the algorithm for subdivision of tiles
what it does:
    1. takes a tile and a polygon
    2. if the tile is on the boundary, splits it into four
    3. repeats the process for each of the four tiles
    4. after this has been done, adds up all the areas of the inside tiles
    5. returns half the area of boundary tiles (those with tilesize = epsilon)
"""

from dataclasses import dataclass
from typing import Tuple
from tiling.tile import Tile
from tiling.tile_classifier import tile_in_polygon
from tiling.classify_tile import TileClass
from tiling.tile_grid import TileGrid
from geometry.polygon import Polygon

def subdivide(tile : Tile, polygon : Polygon, epsilon = 1e-6) -> float:
    classification = tile_in_polygon(tile, polygon)
    if tile.bounds[2] - tile.bounds[0] < epsilon and tile.bounds[3] - tile.bounds[1] < epsilon and classification == TileClass.INSIDE:
        return (tile.bounds[2] - tile.bounds[0])*(tile.bounds[3] - tile.bounds[1])
    elif tile.bounds[2] - tile.bounds[0] < epsilon and tile.bounds[3] - tile.bounds[1] < epsilon and classification == TileClass.BOUNDARY:
        return (tile.bounds[2] - tile.bounds[0])*(tile.bounds[3] - tile.bounds[1]) / 2
    elif classification == TileClass.INSIDE:
        return (tile.bounds[2] - tile.bounds[0])*(tile.bounds[3] - tile.bounds[1])
    elif classification == TileClass.OUTSIDE:
        return 0
    if classification == TileClass.BOUNDARY:
        c_x = (tile.bounds[0] + tile.bounds[2]) / 2
        c_y = (tile.bounds[1] + tile.bounds[3]) / 2
        tile1 = Tile(None, None, (tile.bounds[0], tile.bounds[1], c_x, c_y)) #bottom left
        tile2 = Tile(None, None, (c_x, tile.bounds[1], tile.bounds[2], c_y)) #bottom right
        tile3 = Tile(None, None, (tile.bounds[0], c_y, c_x, tile.bounds[3])) #top left
        tile4 = Tile(None, None, (c_x, c_y, tile.bounds[2], tile.bounds[3])) #top right
        return subdivide(tile1, polygon, epsilon) + subdivide(tile2, polygon, epsilon) + subdivide(tile3, polygon, epsilon) + subdivide(tile4, polygon, epsilon)

def area_characteristics(tile : Tile, polygon : Polygon, epsilon) -> Tuple[float, float, int]:
    """
    given a tilegrid:
        1. firstly checks whether the grid contains the entire polygon
        2. if not, returs None
        3. if yes, then for each tile in the grid:
            1. if the tile is inside the polygon, add its area to the total
            2. if the tile is on the boundary, subdivides it
            3. if the tile is outside the polygon, do nothing
    """
    
    classification = tile_in_polygon(tile, polygon)
    tile_area = (tile.bounds[2] - tile.bounds[0])*(tile.bounds[3] - tile.bounds[1])
    is_small = (tile.bounds[2] - tile.bounds[0] < epsilon) and (tile.bounds[3] - tile.bounds[1] < epsilon)
    if classification == TileClass.INSIDE:
        return (tile_area, 0,0,0)
    elif classification == TileClass.OUTSIDE:
        return (0,0,0,0)
    else:
        if is_small:
            return (tile_area/2, tile_area/2, 0, 1)
        else:
            c_x = (tile.bounds[0] + tile.bounds[2]) / 2
            c_y = (tile.bounds[1] + tile.bounds[3]) / 2
            subtiles = [
                Tile(None, None, (tile.bounds[0], tile.bounds[1], c_x, c_y)), #bottom left
                Tile(None, None, (c_x, tile.bounds[1], tile.bounds[2], c_y)), #bottom right
                Tile(None, None, (tile.bounds[0], c_y, c_x, tile.bounds[3])), #top left
                Tile(None, None, (c_x, c_y, tile.bounds[2], tile.bounds[3])) #top right
            ]
            area = 0
            uncertainty = 0
            max_depth = 0
            boundary_count = 0
            for subtile in subtiles:
                a, u, d, b = area_characteristics(subtile, polygon, epsilon)
                area += a
                uncertainty += u
                boundary_count += b
                max_depth = max(max_depth, d)
            return (area, uncertainty, max_depth+1, boundary_count)

def estimate_area(polygon : Polygon, tile_size : float, overlap : float, epsilon) -> Tuple[float, float, int, int, Tuple[float,float]]:
    grid = TileGrid(polygon.axis_aligned_bounds(), tile_size, overlap)
    area = 0
    uncertainty = 0
    max_depth = 0
    boundary_count = 0
    for tile in grid:
        classification = tile_in_polygon(tile, polygon)
        a, u, d, b = area_characteristics(tile, polygon, epsilon)
        area += a
        uncertainty += u
        max_depth = max(d, max_depth)
        boundary_count += b
    range = (area - uncertainty, area + uncertainty)
    return (area, uncertainty, max_depth, boundary_count, range, epsilon)
