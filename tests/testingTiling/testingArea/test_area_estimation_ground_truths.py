"""
GROUND TRUTH TESTS FOR TILE-BASED AREA ESTIMATION

This file validates the tile subdivision area estimation algorithm
against polygons with known or easily computable true area.

For each test case:
1. True area is computed using the shoelace formula
2. Area is estimated using tile subdivision
3. Epsilon is decreased progressively
4. We observe monotonic convergence
5. Tiles are visualised with classification:
      - INSIDE    (green)
      - OUTSIDE   (white)
      - BOUNDARY  (orange)
6. Recursive subdivision near boundaries is highlighted
"""

import matplotlib.pyplot as plt
import math
import time

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.tile_grid import TileGrid
from tiling.area_estimation import area_estimation, subdivide
from tiling.tile_classifier import tile_in_polygon
from tiling.classify_tile import TileClass


# ------------------------------------------------------------
# POLYGON DEFINITIONS (GROUND TRUTH)
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


def concave_polygon():
    return Polygon([
        Point((0, 0)),
        Point((3, 1)),
        Point((0, 2)),
        Point((1, 1))
    ])


def small_polygon_inside_tile():
    return Polygon([
        Point((0.2, 0.2)),
        Point((0.4, 0.2)),
        Point((0.4, 0.4)),
        Point((0.2, 0.4))
    ])


def polygon_crossing_many_tiles():
    return Polygon([
        Point((0, 0)),
        Point((5, 1)),
        Point((4, 4)),
        Point((1, 5))
    ])


# ------------------------------------------------------------
# VISUALISATION
# ------------------------------------------------------------

def plot_tiles_and_polygon(polygon, grid, epsilon):
    fig, ax = plt.subplots()

    # polygon
    px = [p.coordinates[0] for p in polygon.vertices] + [polygon.vertices[0].coordinates[0]]
    py = [p.coordinates[1] for p in polygon.vertices] + [polygon.vertices[0].coordinates[1]]
    ax.plot(px, py, color="black", linewidth=2, label="Polygon")

    # tiles
    for tile in grid:
        cls = tile_in_polygon(tile, polygon)
        x1, y1, x2, y2 = tile.bounds

        if cls == TileClass.INSIDE:
            color = "green"
            alpha = 0.4
        elif cls == TileClass.OUTSIDE:
            color = "lightgray"
            alpha = 0.2
        else:
            color = "orange"
            alpha = 0.6

        ax.fill(
            [x1, x2, x2, x1],
            [y1, y1, y2, y2],
            color=color,
            alpha=alpha
        )

    ax.set_aspect("equal")
    ax.set_title(f"Tile Classification (epsilon={epsilon})")
    ax.legend()
    ax.grid(True)
    plt.show()


# ------------------------------------------------------------
# TEST HARNESS
# ------------------------------------------------------------

def run_test(name, polygon, tile_size=1.0, overlap=0.0, epsilons=(0.5, 0.25, 0.125)):
    print(f"\n=== TEST CASE: {name} ===")

    true_area = polygon.area()
    print(f"True area (shoelace): {true_area}")

    bounds = polygon.axis_aligned_bounds() # ← CALL IT
    grid = TileGrid(
        bounds=bounds,
        tile_size=tile_size,
        overlap=overlap
    )


    last_error = None

    for eps in epsilons:
        start = time.time()
        est_area = area_estimation(polygon, grid, epsilon=eps)
        elapsed = time.time() - start

        error = abs(est_area - true_area)

        print(
            f"epsilon={eps:<8} "
            f"estimate={est_area:<12.6f} "
            f"error={error:<10.6f} "
            f"time={elapsed:.2f}s"
        )

        if last_error is not None and error > last_error:
            print("⚠️  Non-monotonic error (investigate boundary handling)")

        last_error = error

        plot_tiles_and_polygon(polygon, grid, eps)


# ------------------------------------------------------------
# MAIN DRIVER
# ------------------------------------------------------------

def test_area_estimation_ground_truth():
    tests = [
        ("Square (axis-aligned)", square()),
        ("Rectangle", rectangle()),
        ("Triangle", triangle()),
        ("Concave polygon", concave_polygon()),
        ("Polygon inside one tile", small_polygon_inside_tile()),
        ("Polygon crossing many tiles", polygon_crossing_many_tiles())
    ]

    for name, poly in tests:
        run_test(name, poly)

test_area_estimation_ground_truth()
