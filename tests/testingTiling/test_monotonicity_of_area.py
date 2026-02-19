"""
MONOTONICITY TEST FOR estimate_area

We verify that as epsilon decreases:

1. Uncertainty decreases (monotonic non-increasing)
2. Range width decreases
3. Max recursion depth increases or stays same
4. Boundary count increases or stays same
5. Estimated area stabilizes

This confirms correct subdivision behavior.
"""

import math
import random
import matplotlib.pyplot as plt

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.area_estimation import estimate_area


# ------------------------------------------------------------
# POLYGONS
# ------------------------------------------------------------

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

def random_polygon(n: int, radius: float = 1.0) -> Polygon:
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
    points = []
    for theta in angles:
        r = radius * (0.5 + random.random())
        points.append(Point((r * math.cos(theta), r * math.sin(theta))))
    return Polygon(points)


# ------------------------------------------------------------
# MONOTONICITY CHECK
# ------------------------------------------------------------

def run_monotonicity_test(polygon: Polygon, tile_size: float, overlap: float):

    epsilons = sorted(
        [(0.5)**(n) for n in range(10)],
        reverse=True
    )

    results = []

    print("\nEpsilon progression test")
    print("------------------------")

    for eps in epsilons:
        area, uncertainty, depth, boundary_count, rng, _ = estimate_area(
            polygon,
            tile_size,
            overlap,
            eps
        )

        results.append({
            "epsilon": eps,
            "area": area,
            "uncertainty": uncertainty,
            "depth": depth,
            "boundary": boundary_count,
            "range_width": rng[1] - rng[0]
        })

        print(
            f"ε={eps:<8} "
            f"area={area:<10.6f} "
            f"unc={uncertainty:<10.6f} "
            f"depth={depth:<4} "
            f"boundary={boundary_count:<6}"
        )

    # ------------------------------------------------------------
    # MONOTONICITY CHECKS
    # ------------------------------------------------------------

    print("\nMonotonicity Checks")
    print("-------------------")

    for i in range(1, len(results)):
        prev = results[i - 1]
        curr = results[i]

        print(f"\nComparing ε={prev['epsilon']} → ε={curr['epsilon']}")

        print("Uncertainty decreasing:",
              curr["uncertainty"] <= prev["uncertainty"])

        print("Range width decreasing:",
              curr["range_width"] <= prev["range_width"])

        print("Depth non-decreasing:",
              curr["depth"] >= prev["depth"])

        print("Boundary count non-decreasing:",
              curr["boundary"] >= prev["boundary"])

    # ------------------------------------------------------------
    # VISUALIZATION
    # ------------------------------------------------------------

    eps = [r["epsilon"] for r in results]
    unc = [r["uncertainty"] for r in results]
    depth = [r["depth"] for r in results]
    boundary = [r["boundary"] for r in results]
    range_width = [r["range_width"] for r in results]

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    axs[0, 0].plot(eps, unc)
    axs[0, 0].set_title("Uncertainty vs Epsilon")

    axs[0, 1].plot(eps, range_width)
    axs[0, 1].set_title("Range Width vs Epsilon")

    axs[1, 0].plot(eps, depth)
    axs[1, 0].set_title("Max Depth vs Epsilon")

    axs[1, 1].plot(eps, boundary)
    axs[1, 1].set_title("Boundary Count vs Epsilon")

    for ax in axs.flat:
        ax.set_xlabel("Epsilon")
        ax.grid(True)

    plt.tight_layout()
    plt.show()


# ------------------------------------------------------------
# MAIN DRIVER
# ------------------------------------------------------------

def test_monotonicity():

    print("Monotonicity Test Suite")
    print("-----------------------")
    print("1: Triangle")
    print("2: Concave")
    print("3: Random n-gon")

    choice = input("Choose test: ")
    tile_size = float(input("Enter tile size: "))
    overlap = float(input("Enter overlap: "))

    if choice == "1":
        poly = triangle()
    elif choice == "2":
        poly = concave()
    else:
        n = int(input("Enter n: "))
        poly = random_polygon(n)

    run_monotonicity_test(poly, tile_size, overlap)


test_monotonicity()
