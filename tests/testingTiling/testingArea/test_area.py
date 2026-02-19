"""
TESTS FOR area_characteristics

This test suite is EXPLORATORY, not assert-based.

What we are testing:
--------------------
Given a tile and a polygon, area_characteristics returns:
    (estimated_area, uncertainty, max_depth)

- INSIDE tiles contribute full area
- OUTSIDE tiles contribute zero
- BOUNDARY tiles:
    - subdivide recursively
    - small tiles split area into (area/2, uncertainty=area/2)
    - track maximum subdivision depth

This file contains:
-------------------
1. 10 hardcoded geometric test cases
2. A random n-gon stress test
3. Matplotlib visualisation for every test
4. Option to run one test or all tests
"""

import math
import random
import matplotlib.pyplot as plt

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.tile import Tile
from tiling.tile_classifier import tile_in_polygon
from tiling.classify_tile import TileClass
from tiling.area_estimation import area_characteristics


# ------------------------------------------------------------
# VISUALISATION HELPERS
# ------------------------------------------------------------

def plot_tile_and_polygon(tile: Tile, polygon: Polygon, title: str):
    fig, ax = plt.subplots()

    # --- tile ---
    x1, y1, x2, y2 = tile.bounds
    ax.plot(
        [x1, x2, x2, x1, x1],
        [y1, y1, y2, y2, y1],
        linewidth=2,
        color="blue",
        label="Tile"
    )

    # --- polygon ---
    px = [p.coordinates[0] for p in polygon.vertices] + [polygon.vertices[0].coordinates[0]]
    py = [p.coordinates[1] for p in polygon.vertices] + [polygon.vertices[0].coordinates[1]]
    ax.plot(px, py, linewidth=2, color="black", label="Polygon")

    ax.set_aspect("equal")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)
    plt.show()


# ------------------------------------------------------------
# HARD-CODED POLYGONS
# ------------------------------------------------------------

def square():
    return Polygon([
        Point((0, 0)),
        Point((1, 0)),
        Point((1, 1)),
        Point((0, 1))
    ])

def rectangle():
    return Polygon([
        Point((0, 0)),
        Point((2, 0)),
        Point((2, 1)),
        Point((0, 1))
    ])

def triangle():
    return Polygon([
        Point((0, 0)),
        Point((2, 0)),
        Point((1, 2))
    ])

def concave():
    return Polygon([
        Point((0, 0)),
        Point((2, 1)),
        Point((0, 2)),
        Point((1, 1))
    ])

def diamond():
    return Polygon([
        Point((1, 0)),
        Point((2, 1)),
        Point((1, 2)),
        Point((0, 1))
    ])

def thin_sliver():
    return Polygon([
        Point((0, 0)),
        Point((3, 0)),
        Point((3, 0.1)),
        Point((0, 0.1))
    ])

def l_shape():
    return Polygon([
        Point((0, 0)),
        Point((2, 0)),
        Point((2, 1)),
        Point((1, 1)),
        Point((1, 2)),
        Point((0, 2))
    ])

def rotated_square():
    return Polygon([
        Point((0, 1)),
        Point((1, 2)),
        Point((2, 1)),
        Point((1, 0))
    ])

def small_inside():
    return Polygon([
        Point((0.2, 0.2)),
        Point((0.4, 0.2)),
        Point((0.4, 0.4)),
        Point((0.2, 0.4))
    ])

def crosses_tile():
    return Polygon([
        Point((-1, 0)),
        Point((1, 0)),
        Point((1, 1)),
        Point((-1, 1))
    ])


HARD_CODED_TESTS = [
    ("Square", square),
    ("Rectangle", rectangle),
    ("Triangle", triangle),
    ("Concave", concave),
    ("Diamond", diamond),
    ("Thin sliver", thin_sliver),
    ("L-shape", l_shape),
    ("Rotated square", rotated_square),
    ("Small inside tile", small_inside),
    ("Crosses tile", crosses_tile),
]


# ------------------------------------------------------------
# RANDOM POLYGON
# ------------------------------------------------------------

def random_polygon(n: int, radius: float = 1.0) -> Polygon:
    """
    Generates a random SIMPLE polygon by:
    - sampling random angles
    - sampling random radii
    - sorting by angle
    """
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
    points = []

    for theta in angles:
        r = radius * (0.5 + random.random())
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append(Point((x, y)))

    return Polygon(points)


# ------------------------------------------------------------
# SINGLE TEST RUNNER
# ------------------------------------------------------------

def run_test(name: str, polygon: Polygon, epsilon: float):
    print(f"\n=== TEST: {name} ===")

    bounds = polygon.axis_aligned_bounds()
    pad = max(bounds[2] - bounds[0], bounds[3] - bounds[1]) * 0.2

    tile = Tile(
        None,
        None,
        (
            bounds[0] - pad,
            bounds[1] - pad,
            bounds[2] + pad,
            bounds[3] + pad,
        )
    )

    plot_tile_and_polygon(tile, polygon, f"{name} (epsilon={epsilon})")

    area, uncertainty, depth = area_characteristics(tile, polygon, epsilon)

    print("Estimated area   :", area)
    print("Uncertainty      :", uncertainty)
    print("Max recursion depth:", depth)
    print("True area (shoelace):", polygon.area())


# ------------------------------------------------------------
# MAIN DRIVER
# ------------------------------------------------------------

def test_area_characteristics():
    print("Area Characteristics Test Suite")
    print("--------------------------------")

    print("\nHardcoded tests:")
    for i, (name, _) in enumerate(HARD_CODED_TESTS):
        print(f"{i}: {name}")

    print("a: Run ALL hardcoded tests")
    print("r: Random n-gon test")

    choice = input("\nChoose test: ")

    epsilon = float(input("Enter epsilon: "))

    if choice == "a":
        for name, fn in HARD_CODED_TESTS:
            run_test(name, fn(), epsilon)

    elif choice == "r":
        n = int(input("Enter number of vertices (n): "))
        poly = random_polygon(n)
        run_test(f"Random {n}-gon", poly, epsilon)

    else:
        idx = int(choice)
        name, fn = HARD_CODED_TESTS[idx]
        run_test(name, fn(), epsilon)


test_area_characteristics()
