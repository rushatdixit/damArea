"""
defines what a polygon is
how we compute area, perimeter
a polygon is 
    -represented by a set of vertices
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Generator
from geometry.segment import Segment
from geometry.point import Point
import math

@dataclass(frozen=True)
class Polygon:
    """
    represents a 2D polygon
    vertices must be provided in CW or CCW order
    The following methods are contained within this class:
            - area()
            - perimeter()
            - centroid()
            - edges()
            - point_in_polygon(point)
    """
    vertices : List[Tuple[float,float]]

    def __post_init__(self):
        if len(self.vertices) < 3:
            raise ValueError("A polygon must have more than 2 vertices")

    def __repr__(self):
        return """
        This class represents a polygon with {len(self.vertices)} vertices.
        Vertices are provided in CW or CCW order.
        The following methods are contained within this class:
            - area()
            - perimeter()
            - centroid()
            - edges()
            - point_in_polygon(point)
        """
    
    @property
    def leftmost_vertice(self):
        return min(self.vertices, key=lambda v: v[0])
    
    @property
    def topmost_vertice(self):
        return max(self.vertices, key=lambda v: v[1])
    
    @property 
    def bottommost_vertice(self):
        return min(self.vertices, key=lambda v: v[1])
    
    @property
    def rightmost_vertice(self):
        return max(self.vertices, key=lambda v: v[0])
    
    def rushats_convex_hull(self) -> Polygon:
        """
        returns the convex hull of the polygon
        the unoptimized, rushatian way.
        """
        #setting up vertices as vectors
        vertices = [Point(v) for v in self.vertices]
        #creating the hull list
        h0 = self.leftmost_vertice
        hull = [Point(self.leftmost_vertice)]
        hull_indices = set()
        start_index = vertices.index(hull[0])
        hull_indices.add(start_index)
        i = 0
        while True:
            others = [vertices[j] for j in range(len(vertices)) if j not in hull_indices]
            if others == []:
                raise RuntimeError("No points left in others. \
                Dont panic, check the code.")
            if i == 0:
                direction = Point((h0[0] - 1, h0[1]))
            else:
                direction = hull[i] - hull[i-1]
            max_dot = -2
            true_hull = None
            max_length = -1
            collinear_hull = []
            cross_hull = []
            #checking whether any cross > 0 exist
            for other in others:
                possibility = other - hull[i]
                if direction.distance_from_origin == 0 or possibility.distance_from_origin == 0:
                    continue
                if direction.cross(possibility) > 0:
                    cross_hull.append(other)
                elif direction.cross(possibility) == 0:
                    collinear_hull.append(other)
            if len(cross_hull) == 0 and len(collinear_hull) == 0:
                raise ValueError("No points in cross_hull or collinear_hull. \n Dont panic, check the code.")
            else:
                if len(cross_hull) > 0:
                    for other in cross_hull:
                        possibility = other - hull[i]
                        #checking ccw'ness
                        dot = (direction.dot(possibility)/((direction.distance_from_origin)*(possibility.distance_from_origin)))
                        if dot > max_dot:
                                max_dot = dot
                                true_hull = other
                else:
                    for other in collinear_hull:
                        #compare via length
                        #max length wins
                        length = hull[i].distance(other)
                        if length > max_length:
                            max_length = length
                            true_hull = other
                        else:
                            continue
            if true_hull == None:
                raise RuntimeError(
                    "true_hull is None. Dont panic, check the code."
                    )
            if true_hull == hull[0] and i > 1:
                break
            hull.append(true_hull)
            hull_indices.add(vertices.index(true_hull))
            i += 1
        return Polygon(hull)
   
    def optimized_convex_hull(self) -> Polygon:
        """
        returns the convex hull of the polygon
        using indexes, not points.
        """
        #setting up vertices as vectors
        vertices = [Point(v) for v in self.vertices]
        #creating hull list
        h0 = self.leftmost_vertice
        hull = [h0]
        hull_indices = set() #stores indices
        starting_index = vertices.index(h0)
        hull_indices.add(starting_index)
        i = 0
        while True:
            #other indices
            others = [vertices[j] for j in range(len(vertices)) if j not in hull_indices]
            #if others is empty, something wrong has happened since our break statement is at the bottom
            if others == []:
                raise RuntimeError("No points left in others. Dont panic, check the code.")
            #direction vector
            if i == 0:
                direction = Point((h0[0] - 1, h0[1]))
            else:
                direction = hull[i] - hull[i-1]
            
            #this is going to be our next hull point
            true_hull = None
            #if the next hull point is collinear with direction, 
            #then we need to find the point with maximum distance from direction
            #for this we need max_length
            max_length = -1
            #if the next hull point is not collinear with direction, 
            #then we need to find the point with maximum dot product with direction
            max_dot = -2
            #collinear hull -- will store indices instead of points
            collinear_hull = []
            #cross hull -- will store indices instead of points
            cross_hull = []
            #now to check whether cross > 0 exist
            for j in others:
                possibility = others[j] - hull[i] #v = q - h
                if possibility.distance_from_origin == 0 or direction.distance_from_origin == 0:
                    continue #since mod of vector shouldn't be zero -- otherwise all cross and dot will be zero
                if direction.cross(possibility) > 0:
                    cross_hull.append(j)
                elif direction.cross(possibility) == 0:
                    collinear_hull.append(j)
            if not cross_hull and not collinear_hull:
                raise ValueError("No points in cross_hull or collinear_hull. \n Dont panic, check the code.")
            else:
                if cross_hull: #choose the one with the least ccw turn
                    for j in cross_hull:
                        possibility = others[j] - hull[i]
                        dot = direction.dot(possibility)/((direction.distance_from_origin)*(possibility.distance_from_origin))
                        if dot > max_dot:
                            max_dot = dot
                            true_hull = j
                else: #choose the one with max distance
                    for j in collinear_hull:
                        length = others[j].distance(hull[i])
                        if length > max_length:
                            max_length = length
                            true_hull = j
            #true_hull can't be None, is that is so - something has gone wrong
            if true_hull == None:
                raise RuntimeError("true_hull is None. Dont panic, check the code.")
            #terminate only when h_i = h_0 and i > 1
            if true_hull == starting_index and i > 1:
                break
            #add to hull
            hull.append(others[true_hull])
            hull_indices.add(vertices.index(others[true_hull]))
            i += 1
            #lessgo. this took a lot of time, finally done
        return Polygon(hull)
   
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """
        returns the bounding box
        it is the smallest area rectangle which completely encloses the polygon
        """
        pass
    
    def area(self) -> float:
        """
        computes area using shoelace formula
        """
        area = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i+1) % n
            area += self.vertices[j][1]*self.vertices[i][0] - self.vertices[j][0]*self.vertices[i][1]
        return abs(area/2.0)
    
    def perimeter(self) -> float:
        """
        computes perimeter using distance formula
        """
        perimeter = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i+1) % n
            perimeter += math.sqrt(
                (self.vertices[j][1]-self.vertices[i][1])**2 + (self.vertices[j][0]-self.vertices[i][0])**2
            )
        return perimeter

    def centroid(self) -> Point:
        """
        computes centroid of the polygon
        """
        x_c, y_c = 0, 0
        for vertice in self.vertices:
            x_c += vertice[0]
            y_c += vertice[1]
        x_c /= len(self.vertices)
        y_c /= len(self.vertices)
        return (x_c, y_c)
    
    def edges(self) -> Generator[Line, None, None]:
        """
        returns a generator of lines representing the edges of the polygon
        """
        n = len(self.vertices)
        for i in range(n):
            next = (i+1) % n
            line = Line(self.vertices[i], self.vertices[next])
            yield line

    def point_in_polygon(self, point : Point) -> bool:
        """
        checks if a point is inside the polygon
        """
        x, y = point
        vertices = self.vertices
        inside = False
        for i in range(len(vertices)):
            j = (i+1) % len(vertices)
            x1, y1 = vertices[i]
            x2, y2 = vertices[j]
            #checking whether the edge intersects the horizontal ray through y
            if (y1 - y)*(y2  - y) < 0:
                #checking whether the intersection point is to the right of the point
                if x1 + (y - y1)*(x2 - x1)/(y2 - y1) > x:
                    inside = not inside
        return inside

@dataclass(frozen=True)
class Square:
    """
    represents a tile
    initialised using minimum and maximum coordinates on the diagonal
    it contains the following methods:
        - area()
        - corners_CCW()
        - corners_CW()
        - center()
    """
    x_min : float
    y_min : float
    x_max : float
    y_max : float

    def __post_init__(self):
        if self.x_min > self.x_max or self.y_min > self.y_max:
            raise ValueError("Invalid tile dimensions, x_min or y_min is < x_max or y_max")
    
    def area(self):
        return (self.x_max - self.x_min) * (self.y_max - self.y_min)
    
    def corners_CCW(self):
        return [
            (self.x_min, self.y_min),
            (self.x_min, self.y_max),
            (self.x_max, self.y_max),
            (self.x_max, self.y_min)
        ]

    def corners_CW(self):
        corners = self.corners_CCW()
        change = corners[1:3]
        change = change[::-1]
        corners[1:3] = change
        return corners
    
    def center(self):
        return (
            (self.x_min+self.x_max)/2,
            (self.y_min+self.y_max)/2
        )
    pass
