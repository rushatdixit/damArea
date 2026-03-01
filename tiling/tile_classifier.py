"""
classifies whether a tile lies inside a polygon
"""

from geometry.polygon import Polygon
from tiling.tile import Tile
from tiling.classify_tile import TileClass

def tile_in_polygon(tile : Tile, polygon : Polygon) -> TileClass:
    """
    inputs a tile and polygon
    outputs tells you whether the tile lies inside or outside the polygon
    checks by comparing max and min points
    """
    for tile_edge in tile.tile_edges():
        for polygon_edge in polygon.edges():
            if tile_edge.does_intersect(polygon_edge):
                return TileClass.BOUNDARY
    count = 0
    for corner in tile.corners_ccw():
        if polygon.point_in_polygon(corner):
            count += 1
    if count == 4:
        return TileClass.INSIDE
    else:
        count = 0
        for vertex in polygon.vertices:
            if tile.point_in_tile(vertex):
                count += 1
        if count > 0:
            return TileClass.BOUNDARY
        return TileClass.OUTSIDE