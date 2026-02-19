from geometry.point import Point
import matplotlib.pyplot as plt
import math


# ---------- VISUALISATION HELPERS ----------

def graph_point(point: Point, title: str = "Point Visualisation"):
    if point.dimension != 2:
        print("Graphing only supported for 2D points.")
        return

    fig, ax = plt.subplots()

    x = [0, point.coordinates[0]]
    y = [0, point.coordinates[1]]

    ax.plot(x, y, marker='o', label="Vector from Origin")
    ax.scatter(point.coordinates[0], point.coordinates[1], color='red', label="Point")

    ax.text(0, 0, "Origin (0,0)", fontsize=9)
    ax.text(point.coordinates[0], point.coordinates[1],
            f"({point.coordinates[0]}, {point.coordinates[1]})",
            fontsize=9)

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    plt.show()


# ---------- TEST SECTIONS ----------

def test_methods(set_point: Point):
    print("\n--- Testing Methods ---")
    print("Angle with x-axis (rad):", set_point.angle())
    print("Polar coordinates (r, θ):", set_point.polar_coordinates())


def test_properties(set_point: Point):
    print("\n--- Testing Properties ---")
    print("Dimension:", set_point.dimension)
    print("Distance from origin:", set_point.distance_from_origin)


def test_methods_self_only(set_point: Point):
    print("\n--- Testing Methods Requiring Only Self ---")
    phi = float(input("Enter angle (in radians) to rotate the point: "))
    rotated = set_point.rotate(phi)
    print("Rotated point:", rotated)


def test_methods_self_and_other(set_point: Point):
    print("\n--- Testing Methods Requiring Self & Other ---")
    x = float(input("Enter x coordinate of other point: "))
    y = float(input("Enter y coordinate of other point: "))
    other = Point((x, y))

    print("Other point:", other)
    print("Distance between points:", set_point.distance(other))
    print("Dot product:", set_point.dot(other))
    print("Cross product:", set_point.cross(other))
    print("Addition:", set_point + other)
    print("Subtraction:", set_point - other)


def test_experimental_methods(set_point: Point):
    print("\n--- Testing Experimental Methods ---")
    scalar = float(input("Enter scalar value: "))
    print("Scalar multiplication:", set_point * scalar)
    print("Scalar division:", set_point / scalar)


# ---------- MAIN DRIVER ----------

def test_point():
    print("Testing the class 'Point'")
    print(Point.__doc__)

    x = input("\nRead the documentation and enter 'c' to continue: ")

    while x.lower() == 'c':

        set_point = None

        reuse = input("Do you want to use the same point everywhere? (y/n): ")
        if reuse.lower() == 'y':
            px = float(input("Enter x coordinate: "))
            py = float(input("Enter y coordinate: "))
            set_point = Point((px, py))

        graph = input("Do you want to graph the point? (y/n): ")
        do_graph = graph.lower() == 'y'

        if set_point is None:
            px = float(input("Enter x coordinate: "))
            py = float(input("Enter y coordinate: "))
            set_point = Point((px, py))

        print("\nPoint under test:")
        print(set_point)

        if do_graph:
            graph_point(set_point, title="Initial Point")

        # 1. Methods
        test_methods(set_point)

        # 2. Properties
        test_properties(set_point)

        # 3. Methods requiring only self
        test_methods_self_only(set_point)

        if do_graph:
            graph_point(set_point.rotate(math.pi / 4),
                        title="Point after Rotation")

        # 4. Methods requiring self & other
        test_methods_self_and_other(set_point)

        # 5. Experimental methods
        test_experimental_methods(set_point)

        x = input("\nEnter 'c' to continue testing: ")


test_point()
