"""
defines a polygon
a polygon is a set of points
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Generator
from geometry.point import Point
from geometry.segment import Segment

@dataclass(frozen=True)
class Polygon:
    vertices : List[Point]

    def __post_init__(self):
        if len(self.vertices) < 3:
            raise ValueError("A polygon cannot have less than three vertices.")
    
    @property
    def leftmost_vertex(self) -> Point:
        leftmost = self.vertices[0]
        for vertice in self.vertices:
            if vertice.coordinates[0] < leftmost.coordinates[0]:
                leftmost = vertice
        return leftmost
    
    @property
    def rightmost_vertex(self) -> Point:
        rightmost = self.vertices[0]
        for vertice in self.vertices:
            if vertice.coordinates[0] > rightmost.coordinates[0]:
                rightmost = vertice
        return rightmost
    
    @property
    def topmost_vertex(self) -> Point:
        topmost = self.vertices[0]
        for vertice in self.vertices:
            if vertice.coordinates[1] > topmost.coordinates[1]:
                topmost = vertice
        return topmost

    @property
    def bottommost_vertex(self) -> Point:
        bottommost = self.vertices[0]
        for vertice in self.vertices:
            if vertice.coordinates[1] < bottommost.coordinates[1]:
                bottommost = vertice
        return bottommost
    
    def area(self) -> float:
        area = 0
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            area += self.vertices[i].coordinates[0] * self.vertices[j].coordinates[1]
            area -= self.vertices[j].coordinates[0] * self.vertices[i].coordinates[1]
        return abs(area) / 2.0
    
    def perimeter(self) -> float:
        perimeter = 0
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            perimeter += self.vertices[i].distance(self.vertices[j])
        return perimeter
    
    def edges(self) -> Generator[Segment, None, None]:
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            yield Segment(self.vertices[i], self.vertices[j])
    
    def point_in_polygon(self, point: Point) -> bool:
        x, y = point.coordinates
        inside = False
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            x1, y1 = self.vertices[i].coordinates
            x2, y2 = self.vertices[j].coordinates
            if ((y1 > y) != (y2 > y)) and \
                    (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
                inside = not inside
        return inside
    
    def axis_aligned_bounds(self) -> Tuple[float, float, float, float]:
        return (
            self.leftmost_vertex.coordinates[0],
            self.bottommost_vertex.coordinates[1],
            self.rightmost_vertex.coordinates[0],
            self.topmost_vertex.coordinates[1]
        )