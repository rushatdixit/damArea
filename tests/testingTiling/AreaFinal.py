"""
VISUAL TEST FOR estimate_area

This test focuses ONLY on estimate_area(polygon, tile_size, overlap, epsilon).

What this test shows:
---------------------
1. Tile classification:
      - INSIDE   → green
      - BOUNDARY → orange
      - OUTSIDE  → light gray
2. Estimated area vs true (shoelace) area
3. Uncertainty reported as a percentage
4. Maximum subdivision depth reached

This is an exploratory, visual test — not assert-based.
"""

import math
import random
import matplotlib.pyplot as plt

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.tile_grid import TileGrid
from tiling.tile_classifier import tile_in_polygon
from tiling.classify_tile import TileClass
from tiling.area_estimation import estimate_area


# ------------------------------------------------------------
# VISUALISATION
# ------------------------------------------------------------

def plot_classified_grid(polygon: Polygon, grid: TileGrid, title: str):
    fig, ax = plt.subplots()

    # --- polygon outline ---
    px = [p.coordinates[0] for p in polygon.vertices] + [polygon.vertices[0].coordinates[0]]
    py = [p.coordinates[1] for p in polygon.vertices] + [polygon.vertices[0].coordinates[1]]
    ax.plot(px, py, linewidth=2.5, color="black", label="Polygon")

    # --- tiles ---
    for tile in grid:
        cls = tile_in_polygon(tile, polygon)
        x1, y1, x2, y2 = tile.bounds

        if cls == TileClass.INSIDE:
            color, alpha = "green", 0.45
        elif cls == TileClass.BOUNDARY:
            color, alpha = "orange", 0.6
        else:
            color, alpha = "cornflowerblue", 0.25

        ax.fill(
            [x1, x2, x2, x1],
            [y1, y1, y2, y2],
            color=color,
            alpha=alpha
        )

    ax.set_aspect("equal")
    ax.set_title(title)
    ax.grid(True)
    plt.show()


# ------------------------------------------------------------
# HARD-CODED POLYGONS (10)
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
        Point((3, 0)),
        Point((3, 1)),
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

def crosses_bounds():
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
    ("Small inside", small_inside),
    ("Crosses bounds", crosses_bounds),
]


# ------------------------------------------------------------
# RANDOM POLYGON
# ------------------------------------------------------------

def random_polygon(n: int, radius: float = 1.0) -> Polygon:
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
    points = []
    for theta in angles:
        r = radius * (0.5 + random.random())
        points.append(Point((r * math.cos(theta), r * math.sin(theta))))
    return Polygon(points)


# ------------------------------------------------------------
# SINGLE TEST RUN
# ------------------------------------------------------------

def run_estimate_area_test(name: str, polygon: Polygon,
                           tile_size: float, overlap: float, epsilon: float):

    # pad bounds so OUTSIDE tiles are visible
    x1, y1, x2, y2 = polygon.axis_aligned_bounds()
    pad = tile_size

    bounds = (x1 - pad, y1 - pad, x2 + pad, y2 + pad)
    grid = TileGrid(bounds, tile_size, overlap)

    area, uncertainty, depth = estimate_area(
        polygon,
        tile_size=tile_size,
        overlap=overlap,
        epsilon=epsilon
    )

    true_area = polygon.area()
    uncertainty_pct = (uncertainty / true_area * 100) if true_area > 0 else 0

    print(f"\n=== {name} ===")
    print(f"Estimated area        : {area}")
    print(f"True area (shoelace)  : {true_area}")
    print(f"Uncertainty           : {uncertainty} ({uncertainty_pct:.2f}%)")
    print(f"Max subdivision depth : {depth}")

    plot_classified_grid(
        polygon,
        grid,
        f"{name} | ε={epsilon}, uncertainty={uncertainty_pct:.2f}%"
    )


# ------------------------------------------------------------
# MAIN DRIVER
# ------------------------------------------------------------

def test_estimate_area():
    print("estimate_area Visual Test Suite")
    print("--------------------------------\n")

    print("Hardcoded tests:")
    for i, (name, _) in enumerate(HARD_CODED_TESTS):
        print(f"{i}: {name}")
    print("a: Run ALL hardcoded tests")
    print("r: Random n-gon test")

    choice = input("\nChoose test: ")
    tile_size = float(input("Enter tile size: "))
    overlap = float(input("Enter overlap: "))
    epsilon = float(input("Enter epsilon: "))

    if choice == "a":
        for name, fn in HARD_CODED_TESTS:
            run_estimate_area_test(name, fn(), tile_size, overlap, epsilon)

    elif choice == "r":
        n = int(input("Enter number of vertices (n): "))
        poly = random_polygon(n)
        run_estimate_area_test(f"Random {n}-gon", poly, tile_size, overlap, epsilon)

    else:
        idx = int(choice)
        name, fn = HARD_CODED_TESTS[idx]
        run_estimate_area_test(name, fn(), tile_size, overlap, epsilon)


test_estimate_area()
