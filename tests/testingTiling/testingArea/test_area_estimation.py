"""
TEST FOR AREA ESTIMATION VIA TILE SUBDIVISION (RANDOM POLYGON)

This is NOT a unit test.
It is a guided numerical experiment.

Goal
----
To understand and verify the tile-subdivision-based area estimation
algorithm for arbitrary polygons.

What the algorithm does (high level):
-------------------------------------
1. Covers space with tiles (TileGrid)
2. Classifies tiles relative to a polygon:
       INSIDE / OUTSIDE / BOUNDARY
3. Recursively subdivides boundary tiles until resolution epsilon
4. Sums:
       - full area for INSIDE tiles
       - half area for BOUNDARY tiles at epsilon resolution

This test lets you:
-------------------
- choose polygon complexity (n vertices)
- see how estimation behaves for irregular shapes
- compare estimated area vs true polygon area
- visualize polygon + grid to build intuition
"""

import time
import math
import random
import matplotlib.pyplot as plt

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.tile_grid import TileGrid
from tiling.area_estimation import subdivide, area_estimation
from tiling.classify_tile import TileClass
from tiling.tile_classifier import tile_in_polygon

# ------------------------------------------------------------
# POLYGON GENERATION
# ------------------------------------------------------------

def random_simple_polygon(n: int, radius: float = 1.0) -> Polygon:
    """
    Generates a random *simple* polygon.

    Method:
    -------
    1. Sample random angles in [0, 2π)
    2. Sample random radii (with small noise)
    3. Convert to Cartesian points
    4. Sort by angle to avoid self-intersections

    This produces an irregular but valid polygon.
    """
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
    vertices = []

    for theta in angles:
        r = radius * (0.5 + random.random())
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        vertices.append(Point((x, y)))

    return Polygon(vertices)


def axis_aligned_bounds(polygon: Polygon):
    """
    Computes axis-aligned bounding box for the polygon.
    """
    xs = [p.coordinates[0] for p in polygon.vertices]
    ys = [p.coordinates[1] for p in polygon.vertices]
    return (min(xs), min(ys), max(xs), max(ys))


# ------------------------------------------------------------
# VISUAL DIAGNOSTICS
# ------------------------------------------------------------

def plot_polygon_and_grid(polygon: Polygon, grid: TileGrid, max_tiles=400):
    """
    Visual sanity check:
    - Polygon outline
    - Tile grid overlay (subsampled)

    This is NOT meant to show every tile.
    It is meant to give geometric intuition.
    """
    fig, ax = plt.subplots()

    # --- polygon ---
    px = [p.coordinates[0] for p in polygon.vertices] + [polygon.vertices[0].coordinates[0]]
    py = [p.coordinates[1] for p in polygon.vertices] + [polygon.vertices[0].coordinates[1]]
    ax.plot(px, py, linewidth=2, color="black", label="Polygon")

    # --- grid ---
    count = 0
    for tile in grid:
        if count >= max_tiles:
            break
        x1, y1, x2, y2 = tile.bounds
        ax.plot(
            [x1, x2, x2, x1, x1],
            [y1, y1, y2, y2, y1],
            linewidth=0.5,
            color="blue",
            alpha=0.4
        )
        count += 1

    ax.set_aspect("equal")
    ax.set_title("Random Polygon with TileGrid Overlay")
    ax.legend()
    ax.grid(True)
    plt.show()


# ------------------------------------------------------------
# MAIN TEST DRIVER
# ------------------------------------------------------------

def test_area_estimation():
    print("TEST: Area Estimation via Tile Subdivision")
    print("------------------------------------------")

    n = int(input("Enter number of polygon vertices (n): "))
    tile_size = float(input("Enter tile size: "))
    overlap = float(input("Enter tile overlap: "))
    epsilon = float(input("Enter epsilon (subdivision threshold): "))

    # ---- generate polygon ----
    polygon = random_simple_polygon(n)

    # ---- bounding box ----
    bounds = axis_aligned_bounds(polygon)

    # ---- tile grid ----
    grid = TileGrid(
        bounds=bounds,
        tile_size=tile_size,
        overlap=overlap
    )

    # ---- optional visualization ----
    graph = input("Do you want to visualise polygon and grid? (y/n): ")
    if graph.lower() == "y":
        plot_polygon_and_grid(polygon, grid)

    # ---- area computation with progress ----
    true_area = polygon.area()
    print("\nStarting area estimation...")
    print("This may take time for small epsilon.")
    print("Progress will be printed periodically.\n")

    start_time = time.time()
    area = 0.0

    total_tiles = len(grid)
    processed = 0
    last_report = start_time

    for tile in grid:
        processed += 1

        classification = tile_in_polygon(tile, polygon)

        if classification == TileClass.INSIDE:
            area += (tile.bounds[2] - tile.bounds[0]) * (tile.bounds[3] - tile.bounds[1])

        elif classification == TileClass.BOUNDARY:
            area += subdivide(tile, polygon, epsilon)

        # ---- progress report every 1 second ----
        now = time.time()
        if now - last_report >= 1.0:
            elapsed = now - start_time
            rate = processed / elapsed if elapsed > 0 else 0
            print(
                f"Processed {processed}/{total_tiles} tiles "
                f"({processed/total_tiles:.1%}) | "
                f"{rate:.2f} tiles/sec | "
                f"elapsed {elapsed:.1f}s"
            )
            last_report = now

    estimated_area = area

    # ---- diagnostics ----
    end_time = time.time()
    true_area = polygon.area()

    abs_error = abs(estimated_area - true_area)
    rel_error = abs_error / true_area if true_area != 0 else 0

    print("\nRESULTS")
    print("-------")
    print(f"True polygon area      : {true_area}")
    print(f"Estimated area         : {estimated_area}")
    print(f"Absolute error         : {abs_error}")
    print(f"Relative error         : {rel_error:.6f}")
    print(f"Total time             : {end_time - start_time:.2f} seconds")

test_area_estimation()