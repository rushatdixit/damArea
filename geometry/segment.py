"""
defines a line segment between two points A and B
This class exists to support:
    -polygon edges
    -tile edges
    -robust intersection testing
    -boundary classification
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from geometry.point import Point

@dataclass(frozen=True)
class Segment:
    A : Point
    B : Point
    def __post_init__(self):
        if self.A == self.B:
            raise ValueError("Points must be different")
    
    @property
    def length(self) -> float:
        return self.A.distance(self.B)
    
    @property
    def midpoint(self) -> Point:
        return (self.A + self.B) / 2
    
    @staticmethod
    def _orientation(P : Point, Q : Point, R : Point) -> int:
        """
        Returns:
        0 : collinear
        1 : clockwise
        -1 : counterclockwise
        """
        val = (Q - P).cross(R - P)
        if abs(val) < 1e-12:
            return 0
        else:
            return 1 if val > 0 else -1
    
    @staticmethod
    def _on_segment(P : Point, Q : Point, R : Point) -> bool:
        """
        Returns True if point Q lies on line segment PR assuming, PQR are collinear
        """
        px, py = P.coordinates
        qx, qy = Q.coordinates
        rx, ry = R.coordinates

        return (
            min(px, rx) <= qx <= max(px, rx) and
            min(py, ry) <= qy <= max(py, ry) and
            Segment._orientation(P, Q, R) == 0
        )
    def bounding_box(self) -> Tuple[Point, Point]:
        min_x = min(self.A.coordinates[0], self.B.coordinates[0])
        max_x = max(self.A.coordinates[0], self.B.coordinates[0])
        min_y = min(self.A.coordinates[1], self.B.coordinates[1])
        max_y = max(self.A.coordinates[1], self.B.coordinates[1])
        return (Point((min_x, min_y)), Point((max_x, max_y)))
    
    def does_intersect(self, other : Segment) -> bool:
        A = self.A
        B = self.B
        C = other.A
        D = other.B
        o1 = self._orientation(A, B, C)
        o2 = self._orientation(A, B, D)
        o3 = self._orientation(C, D, A)
        o4 = self._orientation(C, D, B)
        
        if o1 != o2 and o3 != o4:
            return True
        if o1 == 0 and self._on_segment(A, C, B):
            return True
        if o2 == 0 and self._on_segment(A, D, B):
            return True
        if o3 == 0 and self._on_segment(C, A, D):
            return True
        if o4 == 0 and self._on_segment(C, B, D):
            return True
        return False
