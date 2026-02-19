from tiling.tile_grid import TileGrid
from tiling.tile import Tile
from geometry.point import Point
import matplotlib.pyplot as plt


# ---------- VISUALISATION HELPERS ----------

def graph_tile_grid(grid: TileGrid, max_tiles: int = 500):
    """
    Visualises the tile grid.
    Limits number of tiles drawn to avoid overload.
    """
    fig, ax = plt.subplots()

    count = 0
    for tile in grid:
        if count >= max_tiles:
            break

        x1, y1, x2, y2 = tile.bounds
        xs = [x1, x2, x2, x1, x1]
        ys = [y1, y1, y2, y2, y1]

        ax.plot(xs, ys, linewidth=1, color="blue", alpha=0.6)
        count += 1

    ax.set_title("TileGrid Visualisation")
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.grid(True)

    plt.show()


# ---------- TEST SECTIONS ----------

def test_methods(grid: TileGrid):
    print("\n--- Testing Methods / Derived Quantities ---")
    print("Stride:", grid.stride)
    print("Grid origin:", grid.grid_origin)
    print("Number of rows:", grid.n_rows)
    print("Number of columns:", grid.n_cols)


def test_properties(grid: TileGrid):
    print("\n--- Testing Properties ---")
    print("Bounds:", grid.bounds)
    print("Tile size:", grid.tile_size)
    print("Overlap:", grid.overlap)


def test_methods_self_only(grid: TileGrid):
    print("\n--- Testing Methods Requiring Only Self ---")
    print("Total tiles (len):", len(grid))

    print("\nSample tile bounds:")
    print("Tile (0,0):", grid.tile_bounds(0, 0))
    if grid.n_rows > 1 and grid.n_cols > 1:
        print("Tile (1,1):", grid.tile_bounds(1, 1))


def test_methods_self_and_other(grid: TileGrid):
    print("\n--- Testing Methods Requiring Self & Other ---")
    print("Iterating over first few tiles:")

    for i, tile in enumerate(grid):
        if i >= 5:
            break
        print(tile)


def test_experimental_methods(grid: TileGrid):
    print("\n--- Experimental / Sanity Tests ---")
    print("Checking grid coverage of origin:")

    origin = Point(grid.grid_origin)
    found = False

    for tile in grid:
        if tile.point_in_tile(origin):
            print("Origin lies in tile:", tile)
            found = True
            break

    if not found:
        print("Origin does not lie in any tile (this may be expected).")


# ---------- MAIN DRIVER ----------

def test_tile_grid():
    print("Testing the class 'TileGrid'")
    print(TileGrid.__doc__)

    x = input("\nRead the documentation and enter 'c' to continue: ")

    while x.lower() == 'c':

        # ---- Grid creation ----
        x1 = float(input("Enter x_min: "))
        y1 = float(input("Enter y_min: "))
        x2 = float(input("Enter x_max: "))
        y2 = float(input("Enter y_max: "))
        tile_size = float(input("Enter tile size: "))
        overlap = float(input("Enter overlap: "))

        grid = TileGrid(
            bounds=(x1, y1, x2, y2),
            tile_size=tile_size,
            overlap=overlap
        )

        graph = input("Do you want to visualise the tile grid? (y/n): ")
        do_graph = graph.lower() == 'y'

        print("\nTileGrid under test:")
        print(grid)

        if do_graph:
            graph_tile_grid(grid)

        # 1. Methods
        test_methods(grid)

        # 2. Properties
        test_properties(grid)

        # 3. Methods requiring only self
        test_methods_self_only(grid)

        # 4. Methods requiring self & other
        test_methods_self_and_other(grid)

        # 5. Experimental methods
        test_experimental_methods(grid)

        x = input("\nEnter 'c' to continue testing: ")


test_tile_grid()
