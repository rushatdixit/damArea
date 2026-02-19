"""
just to play around with geometry
"""
from geometry.point import Point
from geometry.polygon import Polygon
from typing import List

def convex_hull(polygon: Polygon) -> List[Point]:
    """
    Computes the convex hull of a polygon's vertices
    using Jarvis March (Gift Wrapping).

    Returns hull points in counter-clockwise order.
    """

    points = polygon.vertices
    if len(points) < 3:
        raise ValueError("Convex hull requires at least 3 points")

    # Step 1: find leftmost point
    start = min(points, key=lambda p: p.coordinates[0])
    hull = []

    current = start
    while True:
        hull.append(current)

        # Start with an arbitrary candidate different from current
        candidate = points[0] if points[0] != current else points[1]

        for p in points:
            if p == current:
                continue

            # orientation test
            direction = (candidate - current).cross(p - current)

            if direction < 0:
                candidate = p
            elif direction == 0:
                # collinear: take the farther point
                if current.distance(p) > current.distance(candidate):
                    candidate = p

        current = candidate
        if current == start:
            break

    return hull

