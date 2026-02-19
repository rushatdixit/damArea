from geometry.polygon import Polygon
from geometry.point import Point
from geometry.outdated.experimental import convex_hull
import time
import math
import random
import matplotlib.pyplot as plt


# ---------- LARGE POLYGON GENERATOR ----------

def generate_large_polygon(n: int, radius: float = 100.0) -> Polygon:
    """
    Generates points roughly on a circle to force large hull size (h ≈ n).
    """
    points = []
    for i in range(n):
        theta = 2 * math.pi * i / n
        r = radius * (0.95 + 0.05 * random.random())
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        points.append(Point((x, y)))
    return Polygon(points)


# ---------- VISUALISATION ----------

def plot_polygon_and_hull(polygon: Polygon, hull, title: str, max_points=5000):
    fig, ax = plt.subplots()

    # Subsample interior points if needed
    if len(polygon.vertices) > max_points:
        step = len(polygon.vertices) // max_points
        sampled = polygon.vertices[::step]
    else:
        sampled = polygon.vertices

    # Plot polygon points
    x = [p.coordinates[0] for p in sampled]
    y = [p.coordinates[1] for p in sampled]
    ax.scatter(x, y, s=1, alpha=0.4, label="Polygon points (sampled)")

    # Plot convex hull
    hx = [p.coordinates[0] for p in hull] + [hull[0].coordinates[0]]
    hy = [p.coordinates[1] for p in hull] + [hull[0].coordinates[1]]
    ax.plot(hx, hy, color="red", linewidth=2, label="Convex Hull")

    ax.set_title(title)
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.legend()
    ax.grid(True)

    plt.show()


# ---------- TIMING ----------

def time_convex_hull(polygon: Polygon, label: str, do_plot: bool):
    print(f"\n--- Convex Hull Timing ({label}) ---")
    print("Vertices (n):", len(polygon.vertices))

    start = time.time()
    hull = convex_hull(polygon)
    end = time.time()

    print("Hull size (h):", len(hull))
    print("Time taken (seconds):", end - start)

    if do_plot:
        plot_polygon_and_hull(
            polygon,
            hull,
            title=f"Convex Hull | n = {len(polygon.vertices)}, h = {len(hull)}"
        )

    return hull


# ---------- STRESS TESTS ----------

def test_100k_vertices(do_plot: bool):
    print("\n==============================")
    print("TEST: 100,000 VERTICES")
    print("==============================")

    polygon = generate_large_polygon(100_000)
    time_convex_hull(polygon, "100k vertices", do_plot)


def test_1m_vertices(do_plot: bool):
    print("\n==============================")
    print("TEST: 1,000,000 VERTICES")
    print("==============================")

    polygon = generate_large_polygon(1_000_000)

    # Force plot to hull only (safe)
    start = time.time()
    hull = convex_hull(polygon)
    end = time.time()

    print("Hull size (h):", len(hull))
    print("Time taken (seconds):", end - start)

    if do_plot:
        plot_polygon_and_hull(
            Polygon(hull),  # only hull vertices
            hull,
            title="Convex Hull | 1,000,000 vertices (hull only)"
        )


# ---------- MAIN DRIVER ----------

def test_polygon_scaling_visual():
    print("Convex Hull Scaling Experiment")
    print("Algorithm: Jarvis March (O(nh))")

    x = input(
        "\n⚠️ WARNING:\n"
        "- 100k will be slow\n"
        "- 1M may take minutes\n"
        "Enter 'c' to continue: "
    )

    if x.lower() != 'c':
        print("Aborted.")
        return

    graph = input("Do you want to visualise the convex hulls? (y/n): ")
    do_plot = graph.lower() == 'y'

    test_100k_vertices(do_plot)

    cont = input("\nProceed to 1,000,000 vertices? (y/n): ")
    if cont.lower() == 'y':
        test_1m_vertices(do_plot)
    else:
        print("Stopped before 1M test.")


test_polygon_scaling_visual()
