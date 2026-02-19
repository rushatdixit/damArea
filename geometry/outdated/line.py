"""
Defines a geometric line segment between two points.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
from geometry.point import Point
import math


@dataclass(frozen=True)
class Segment:
    """
    Defines a geometric line segment between two points.
    To initialize, use the following syntax:
        - Segment(point1, point2)
        - where point1 and point2 are instances of the Point class.
    It contains the following properties:
        - is_vertical: True if the line is vertical
        - slope: The slope of the line
        - intercept: The intercept of the line
    It contains the following methods:
        - side(point): Returns -1 if point is below / left, 0 if on the line, 1 if above / right
        - point_on_line(point): Returns True if point is on the line
        - intersection(other): Returns intersection point of two infinite lines, or None if parallel
        - length(): Returns the length of the line
    """
    point1 : Point
    point2 : Point

    def __post_init__(self):
        if self.point1 == self.point2:
            raise ValueError("Points must be different")
        
    def __repr__(self) -> str:
        return f"Line({self.point1} → {self.point2})"
    
    @property
    def midpoint(self) -> Point:
        return (self.point1 + self.point2) / 2

    @property
    def slope(self) -> float:
        if self.is_vertical:
            return math.inf
        x1, y1 = self.point1.coordinates
        x2, y2 = self.point2.coordinates
        return (y2 - y1) / (x2 - x1)

    @property
    def intercept(self) -> float | None:
        """
        y-intercept if non-vertical, x-intercept if vertical
        """
        if self.is_vertical:
            return self.point1.coordinates[0]  # x = c
        x1, y1 = self.point1.coordinates
        return y1 - self.slope * x1
    
    @property
    def length(self) -> float:
        dx = self.point2.coordinates[0] - self.point1.coordinates[0]
        dy = self.point2.coordinates[1] - self.point1.coordinates[1]
        return math.hypot(dx, dy)
    
    def function(self, point : Point) -> float:
        """
        Returns the value of the function at the given point
        """
        x = point.coordinates[0]
        y = point.coordinates[1]
        return y - (self.slope * x + self.intercept)

    def side(self, point: Point) -> int:
        """
        Returns:
        -1 if point is below / left
         0 if on the line
         1 if above / right
        """
        x = point.coordinates[0]
        y = point.coordinates[1]
        if self.is_vertical:
            val = x - self.intercept
        else:
            val = y - (self.slope * x + self.intercept)

        if abs(val) < 1e-12:
            return 0
        return 1 if val > 0 else -1

    def point_on_line(self, point: Point) -> bool:
        return self.side(point) == 0

    def is_vertical(self) -> bool:
        return self.point1.coordinates[0] == self.point2.coordinates[0]
    
    def does_intersect(self, other : Segment) -> bool:
        """
        to check if they intersect or not
        uses circles to check
        rotate segment around its midpoint
        """
        #radius = (p1 - p2) /2
        radius1 = ((self.point1 - self.point2)/2).distance_from_origin
        radius2 = ((other.point1 - other.point2)/2).distance_from_origin
        #never intersect if r1 + r2 > c1c2 :
        if radius1 + radius2 > self.midpoint.distance(other.midpoint):
            return False
        elif radius1 + radius2 == self.midpoint.distance(other.midpoint):
            #special case, intersects only if one of the end points are the same
            if self.point1 == other.point1 or self.point1 == other.point2 or self.point2 == other.point1 or self.point2 == other.point2:
                return True
        else:
            #now we can check the intersection point
            #and see if it lies inside both the circles c1 and c2
            x = (self.intercept - other.intercept) / (other.slope - self.slope)
            y = self.slope * x + self.intercept
            intersection = Point((x, y))
            if intersection.distance(self.midpoint) <= radius1 and intersection.distance(other.midpoint) <= radius2:
                return True
        return False


    def intersection(self, other: Segment) -> Point | None:
        """
        Returns intersection point of two segments
        """
        # Parallel
        if self.slope == other.slope:
            return None

        #To check whether the point lies inside both segments
        #We will use r = kp+q / k+1 wherein p, q are vectors and r is the vector whose ratio between p and q is 1:k
        #If r lies between p and q, k lies between 0 and 1
        A = self.point1
        B = self.point2
        C = other.point1
        D = other.point2
        #To increase readibility, please draw ABCD on a piece of paper
        #where AB is the first segment and CD is the second segment
        x = (self.intercept - other.intercept) / (other.slope - self.slope)
        y = self.slope * x + self.intercept
        I = Point((x, y))
        #I is the intersection point of the two segments
        #(k+1)I = kp + q
        #k = (I - p) / (q - p)
        new1 = I - A
        new2 = B - A
        k = new1.coordinates[0] / new2.coordinates[0]
        if 0 <= k <= 1:
            return I
        return None