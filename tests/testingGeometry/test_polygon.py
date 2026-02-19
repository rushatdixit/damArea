from geometry.polygon import Polygon
from geometry.point import Point
from geometry.outdated.experimental import convex_hull
import matplotlib.pyplot as plt
import math
import random


# ---------- HELPERS ----------

def generate_random_polygon(n: int, radius: float = 10.0) -> Polygon:
    """
    Generates a simple polygon by sampling points on a noisy circle
    and ordering them by angle.
    """
    points = []
    for _ in range(n):
        r = radius * (0.7 + 0.3 * random.random())
        theta = random.uniform(0, 2 * math.pi)
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append(Point((x, y)))

    # sort by angle to avoid self-intersections
    center_x = sum(p.coordinates[0] for p in points) / n
    center_y = sum(p.coordinates[1] for p in points) / n

    points.sort(
        key=lambda p: math.atan2(
            p.coordinates[1] - center_y,
            p.coordinates[0] - center_x
        )
    )

    return Polygon(points)


def plot_polygon(polygon: Polygon, title: str, color="blue"):
    x = [p.coordinates[0] for p in polygon.vertices] + [polygon.vertices[0].coordinates[0]]
    y = [p.coordinates[1] for p in polygon.vertices] + [polygon.vertices[0].coordinates[1]]

    plt.plot(x, y, marker='o', linewidth=1, color=color, label=title)


def plot_convex_hull(polygon: Polygon, hull_points, title: str):
    fig, ax = plt.subplots()

    # original polygon
    plot_polygon(polygon, "Original Polygon", color="gray")

    # convex hull
    hull_x = [p.coordinates[0] for p in hull_points] + [hull_points[0].coordinates[0]]
    hull_y = [p.coordinates[1] for p in hull_points] + [hull_points[0].coordinates[1]]

    ax.plot(hull_x, hull_y, marker='o', linewidth=2, color="red", label="Convex Hull")

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    plt.show()


# ---------- TEST SECTIONS ----------

def test_basic_properties(polygon: Polygon):
    print("\n--- Testing Polygon Properties ---")
    print("Number of vertices:", len(polygon.vertices))
    print("Area:", polygon.area())
    print("Perimeter:", polygon.perimeter())
    print("Leftmost vertex:", polygon.leftmost_vertex)
    print("Rightmost vertex:", polygon.rightmost_vertex)
    print("Topmost vertex:", polygon.topmost_vertex)
    print("Bottommost vertex:", polygon.bottommost_vertex)


def test_point_query(polygon: Polygon):
    print("\n--- Testing Point-In-Polygon ---")
    x = float(input("Enter x of test point: "))
    y = float(input("Enter y of test point: "))
    p = Point((x, y))
    print("Point inside polygon:", polygon.point_in_polygon(p))


def test_convex_hull(polygon: Polygon, label: str):
    print(f"\n--- Testing Convex Hull ({label}) ---")
    hull = convex_hull(polygon)
    print("Convex hull vertex count:", len(hull))
    return hull


# ---------- HARD-CODED STRESS TESTS ----------

def test_polygon_100_vertices():
    print("\n=== Polygon Test: 100 Vertices ===")
    polygon = generate_random_polygon(100)
    test_basic_properties(polygon)
    return polygon


def test_polygon_1000_vertices():
    print("\n=== Polygon Test: 1000 Vertices ===")
    polygon = generate_random_polygon(1000)
    test_basic_properties(polygon)
    return polygon


# ---------- MAIN DRIVER ----------

def test_polygon():
    print("Testing the class 'Polygon'")
    print(Polygon.__doc__)

    x = input("\nRead the documentation and enter 'c' to continue: ")

    while x.lower() == 'c':

        graph = input("Do you want to visualise the polygons and convex hulls? (y/n): ")
        do_graph = graph.lower() == 'y'

        # ---- 100 vertices ----
        poly_100 = test_polygon_100_vertices()
        hull_100 = test_convex_hull(poly_100, "100 vertices")

        if do_graph:
            plot_convex_hull(
                poly_100,
                hull_100,
                title="Convex Hull of Polygon (100 Vertices)"
            )

        # ---- 1000 vertices ----
        poly_1000 = test_polygon_1000_vertices()
        hull_1000 = test_convex_hull(poly_1000, "1000 vertices")

        if do_graph:
            plot_convex_hull(
                poly_1000,
                hull_1000,
                title="Convex Hull of Polygon (1000 Vertices)"
            )

        x = input("\nEnter 'c' to continue testing: ")


test_polygon()
