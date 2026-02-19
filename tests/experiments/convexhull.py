from geometry.polygon import Polygon
from geometry.point import Point
from geometry.outdated.experimental import convex_hull
import time
import math
import random


# ---------- LARGE POLYGON GENERATOR ----------

def generate_large_polygon(n: int, radius: float = 100.0) -> Polygon:
    """
    Generates n points roughly on a circle.
    This intentionally increases hull size h.
    """
    points = []

    for i in range(n):
        theta = 2 * math.pi * i / n
        r = radius * (0.95 + 0.05 * random.random())
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append(Point((x, y)))

    return Polygon(points)


# ---------- CONVEX HULL TIMING ----------

def time_convex_hull(polygon: Polygon, label: str):
    print(f"\n--- Convex Hull Timing Test ({label}) ---")
    print("Number of vertices:", len(polygon.vertices))

    start = time.time()
    hull = convex_hull(polygon)
    end = time.time()

    print("Hull size (h):", len(hull))
    print("Time taken (seconds):", end - start)

    return hull


# ---------- HARD TESTS ----------

def test_100k_vertices():
    print("\n==============================")
    print("TEST: 100,000 VERTICES")
    print("==============================")

    polygon = generate_large_polygon(100_000)
    time_convex_hull(polygon, "100k vertices")


def test_1m_vertices():
    print("\n==============================")
    print("TEST: 1,000,000 VERTICES")
    print("==============================")

    polygon = generate_large_polygon(1_000_000)
    time_convex_hull(polygon, "1M vertices")


# ---------- MAIN DRIVER ----------

def test_polygon_scaling():
    print("Convex Hull Scaling Test (O(nh))")
    print("Algorithm: Jarvis March / Gift Wrapping")

    x = input("\n⚠️ WARNING: This may take a long time.\nEnter 'c' to continue: ")

    if x.lower() != 'c':
        print("Aborted.")
        return

    test_100k_vertices()

    cont = input("\nProceed to 1,000,000 vertices? (y/n): ")
    if cont.lower() == 'y':
        test_1m_vertices()
    else:
        print("Stopped before 1M test.")


test_polygon_scaling()
