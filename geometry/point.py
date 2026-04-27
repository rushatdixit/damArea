"""
Defines an immutable Point in n-dimensional space with vector operations.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Sequence
from objects import PolarCoordinates
import math

@dataclass(frozen=True)
class Point:
    """
    Immutable n-dimensional point supporting vector arithmetic.

    :param coordinates: Sequence of coordinate values (minimum 2).
    :type coordinates: Sequence[float]
    """
        
    coordinates : Sequence[float]
    
    def __post_init__(self):
        if len(self.coordinates) < 2:
            raise ValueError("Point must have at least 2 coordinates")
    
    def __repr__(self) -> str:
        return f"""Point({self.coordinates})
        dimension : {self.dimension}
        distance from origin : {self.distance_from_origin}"""
    
    def __add__(self, other : Point) -> Point:
        if self.dimension != other.dimension:
            raise ValueError("Points must have the same dimension")
        return Point(
            tuple(
                self.coordinates[i] + other.coordinates[i]
                for i in range(self.dimension)  
            )
        )
    
    def __sub__(self, other : Point) -> Point:
        if self.dimension != other.dimension:
            raise ValueError("Points must have the same dimension")
        return Point(
            tuple(
                self.coordinates[i] - other.coordinates[i]
                for i in range(self.dimension)
            )
        )
    
    def __mul__(self, scalar : float) -> Point:
        return Point(
            tuple(
                coord*scalar
                for coord in self.coordinates
            )
        )
    
    def __rmul__(self, scalar : float) -> Point:
        return self*scalar
    
    def __truediv__(self, scalar : float) -> Point:
        return Point(
            tuple(
                self.coordinates[i] / scalar
                for i in range(self.dimension)
            )
        )
    
    def __eq__(self, point : Point) -> bool:
        if self.coordinates == point.coordinates:
            return True
        return False
    
    @property
    def dimension(self) -> int:
        return len(self.coordinates)
    
    @property 
    def distance_from_origin(self) -> float:
        return math.sqrt(sum(x**2 for x in self.coordinates))

    def distance(self, point : Point) -> float:
        """returns the euclidean distance between the point and another point"""
        if self.dimension != point.dimension:
            raise ValueError("Points must have the same dimension")
        return math.sqrt(
            sum(
                (self.coordinates[i] - point.coordinates[i])**2
                for i in range(self.dimension)
            )
        )
    
    def angle(self) -> float:
        """returns the angle of the point with respect to the x-axis"""
        if self.dimension == 2:
            return math.atan2(self.coordinates[1], self.coordinates[0])
        else:
            raise ValueError("Point must have exactly 2 coordinates")
    
    def polar_coordinates(self) -> PolarCoordinates:
        """
        Returns polar coordinates of this 2D point.

        :return: Polar representation with radius and angle.
        :rtype: PolarCoordinates
        :raises ValueError: If the point is not 2D.
        """
        if self.dimension == 2:
            return PolarCoordinates(radius=self.distance_from_origin, angle=self.angle())
        else:
            raise ValueError("Point must have exactly 2 coordinates")
    
    def rotate(self, phi : float) -> Point:
        """returns the point after counter-clockwise rotation by angle"""
        if self.dimension == 2:
            x, y = self.coordinates
            r = self.distance_from_origin
            theta = self.angle()
            new_x = r * math.cos(theta + phi)
            new_y = r * math.sin(theta + phi)
            return Point((new_x, new_y))
        else:
            raise ValueError("Point must have exactly 2 coordinates")
    
    def cross(self, other : Point) -> float:
        if self.dimension != other.dimension:
            raise ValueError("Points must have the same dimension")
        elif self.dimension > 2:
            raise NotImplementedError("We are not ready for vectors of more than 2 dimensions.")
        else:
            return (self.coordinates[0]*other.coordinates[1] - self.coordinates[1]*other.coordinates[0])

    def dot(self, other : Point) -> float:
        return self.coordinates[0]*other.coordinates[0] + self.coordinates[1]*other.coordinates[1]