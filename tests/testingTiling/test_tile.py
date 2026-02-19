from tiling.tile import Tile
from geometry.point import Point
from geometry.segment import Segment
import matplotlib.pyplot as plt


# ---------- VISUALISATION HELPERS ----------

def graph_tile(tile: Tile, title: str = "Tile Visualisation"):
    corners = tile.corners_ccw()
    xs = [p.coordinates[0] for p in corners] + [corners[0].coordinates[0]]
    ys = [p.coordinates[1] for p in corners] + [corners[0].coordinates[1]]

    fig, ax = plt.subplots()

    ax.plot(xs, ys, marker='o', linewidth=2, label="Tile boundary")

    for i, p in enumerate(corners):
        ax.text(
            p.coordinates[0],
            p.coordinates[1],
            f"C{i}{p.coordinates}",
            fontsize=9
        )

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    plt.show()


def graph_point_on_tile(tile: Tile, point: Point):
    corners = tile.corners_ccw()
    xs = [p.coordinates[0] for p in corners] + [corners[0].coordinates[0]]
    ys = [p.coordinates[1] for p in corners] + [corners[0].coordinates[1]]

    fig, ax = plt.subplots()

    ax.plot(xs, ys, linewidth=2, label="Tile")
    ax.scatter(
        point.coordinates[0],
        point.coordinates[1],
        color="red",
        label="Test Point"
    )

    ax.text(
        point.coordinates[0],
        point.coordinates[1],
        f"{point.coordinates}",
        fontsize=9
    )

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Point in Tile Test")
    ax.legend()
    ax.grid(True)

    plt.show()


# ---------- TEST SECTIONS ----------

def test_methods(tile: Tile):
    print("\n--- Testing Methods ---")
    print("Corners (CW):")
    for c in tile.corners_cw():
        print(c)

    print("\nCorners (CCW):")
    for c in tile.corners_ccw():
        print(c)


def test_properties(tile: Tile):
    print("\n--- Testing Properties ---")
    print("Row:", tile.row)
    print("Column:", tile.col)
    print("Bounds:", tile.bounds)


def test_methods_self_only(tile: Tile):
    print("\n--- Testing Methods Requiring Only Self ---")
    print("Tile representation:", tile)

    print("\nTile edges:")
    for edge in tile.tile_edges():
        print(edge)


def test_methods_self_and_other(tile: Tile, do_graph: bool):
    print("\n--- Testing Methods Requiring Self & Other ---")
    x = float(input("Enter x of test point: "))
    y = float(input("Enter y of test point: "))
    p = Point((x, y))

    inside = tile.point_in_tile(p)
    print("Point inside tile:", inside)

    if do_graph:
        graph_point_on_tile(tile, p)


def test_experimental_methods(tile: Tile):
    print("\n--- Experimental / Boundary Tests ---")
    print("Testing points on tile corners:")

    for corner in tile.corners_ccw():
        print(
            f"Point {corner.coordinates} inside tile:",
            tile.point_in_tile(corner)
        )


# ---------- MAIN DRIVER ----------

def test_tile():
    print("Testing the class 'Tile'")
    print(Tile.__doc__)

    x = input("\nRead the documentation and enter 'c' to continue: ")

    while x.lower() == 'c':

        reuse = input("Do you want to use the same tile everywhere? (y/n): ")
        tile = None

        if reuse.lower() == 'y':
            row = int(input("Row index: "))
            col = int(input("Column index: "))
            x1 = float(input("x_min: "))
            y1 = float(input("y_min: "))
            x2 = float(input("x_max: "))
            y2 = float(input("y_max: "))
            tile = Tile(row, col, (x1, y1, x2, y2))

        graph = input("Do you want to graph the tile? (y/n): ")
        do_graph = graph.lower() == 'y'

        if tile is None:
            row = int(input("Row index: "))
            col = int(input("Column index: "))
            x1 = float(input("x_min: "))
            y1 = float(input("y_min: "))
            x2 = float(input("x_max: "))
            y2 = float(input("y_max: "))
            tile = Tile(row, col, (x1, y1, x2, y2))

        print("\nTile under test:")
        print(tile)

        if do_graph:
            graph_tile(tile)

        # 1. Methods
        test_methods(tile)

        # 2. Properties
        test_properties(tile)

        # 3. Methods requiring only self
        test_methods_self_only(tile)

        # 4. Methods requiring self & other
        test_methods_self_and_other(tile, do_graph)

        # 5. Experimental methods
        test_experimental_methods(tile)

        x = input("\nEnter 'c' to continue testing: ")


test_tile()
