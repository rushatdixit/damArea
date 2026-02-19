"""
Convergence Analysis for Adaptive Tile-Based Area Estimation
------------------------------------------------------------

This module evaluates the convergence and uncertainty behavior of
the adaptive tile-based area estimator.

It answers the following critical questions:

1. Does estimated area converge to the true shoelace area?
2. Does uncertainty decrease as epsilon decreases?
3. Is the true area always inside the reported uncertainty interval?
4. How does subdivision depth scale with epsilon?
5. How does boundary tile count scale with epsilon?

This module DOES NOT modify the estimator.
It only evaluates and validates its behavior.

This is the bridge from algorithm correctness → scientific validation.
"""

import matplotlib.pyplot as plt
import math
import random

from geometry.point import Point
from geometry.polygon import Polygon
from tiling.area_estimation import estimate_area


# ------------------------------------------------------------
# Utility: Random Polygon Generator
# ------------------------------------------------------------

def random_polygon(n: int, radius: float = 1.0) -> Polygon:
    """
    Generates a random simple polygon (non-regular).
    """
    angles = sorted(random.uniform(0, 2 * math.pi) for _ in range(n))
    points = []

    for theta in angles:
        r = radius * (0.5 + random.random())
        points.append(Point((r * math.cos(theta), r * math.sin(theta))))

    return Polygon(points)


# ------------------------------------------------------------
# Core Experiment Runner
# ------------------------------------------------------------

def run_convergence_experiment(
    polygon: Polygon,
    tile_size: float,
    overlap: float,
    epsilons: list
):
    """
    Runs estimate_area for decreasing epsilon values
    and records convergence metrics.
    """

    print("\n====================================================")
    print("Adaptive Tile-Based Area Estimator Convergence Test")
    print("====================================================\n")

    print("Polygon true area (shoelace):", polygon.area())
    print("Tile size:", tile_size)
    print("Overlap:", overlap)
    print("Epsilon sequence:", epsilons)
    print("\nRunning experiments...\n")

    results = []

    true_area = polygon.area()

    for eps in epsilons:

        area, uncertainty, depth, boundary_count, interval, _ = estimate_area(
            polygon,
            tile_size,
            overlap,
            eps
        )

        abs_error = abs(area - true_area)
        rel_error = abs_error / true_area if true_area > 0 else 0
        error_ratio = abs_error / uncertainty if uncertainty > 0 else 0

        inside_interval = interval[0] <= true_area <= interval[1]

        results.append({
            "epsilon": eps,
            "area_est": area,
            "uncertainty": uncertainty,
            "abs_error": abs_error,
            "rel_error": rel_error,
            "error_ratio": error_ratio,
            "depth": depth,
            "boundary_count": boundary_count,
            "interval_contains_truth": inside_interval
        })

        print(f"ε = {eps}")
        print(f"  Estimated Area        : {area}")
        print(f"  Absolute Error        : {abs_error}")
        print(f"  Relative Error        : {rel_error:.6f}")
        print(f"  Uncertainty (ΔA)      : {uncertainty}")
        print(f"  |Error| / ΔA          : {error_ratio:.4f}")
        print(f"  Depth                 : {depth}")
        print(f"  Boundary Tiles        : {boundary_count}")
        print(f"  Truth in Interval?    : {inside_interval}")
        print("----------------------------------------------------")


    print("\nExperiment Complete.\n")
    print("Now evaluating convergence behavior...\n")

    evaluate_monotonicity(results)

    evaluate_convergence_rate(results)

    visualize_results(results)

    return results


# ------------------------------------------------------------
# Monotonicity Checks
# ------------------------------------------------------------

def evaluate_monotonicity(results):

    print("Monotonicity Verification:")
    print("--------------------------")

    for i in range(1, len(results)):
        prev = results[i - 1]
        curr = results[i]

        print(f"\nComparing ε={prev['epsilon']} → ε={curr['epsilon']}")

        print("Uncertainty decreasing:",
              curr["uncertainty"] <= prev["uncertainty"])

        print("Absolute error decreasing:",
              curr["abs_error"] <= prev["abs_error"])

        print("Depth non-decreasing:",
              curr["depth"] >= prev["depth"])

        print("Boundary count non-decreasing:",
              curr["boundary_count"] >= prev["boundary_count"])

def evaluate_convergence_rate(results):
    """
    Estimates empirical convergence order using:
        log(uncertainty) vs log(epsilon)

    If slope ≈ 1 → first-order convergence (ΔA ∝ ε)
    """

    print("\nConvergence Rate Estimation")
    print("---------------------------")

    log_eps = []
    log_unc = []

    for r in results:
        if r["uncertainty"] > 0:
            log_eps.append(math.log(r["epsilon"]))
            log_unc.append(math.log(r["uncertainty"]))

    if len(log_eps) < 2:
        print("Not enough data to estimate convergence rate.")
        return

    # Simple linear regression slope
    n = len(log_eps)
    mean_x = sum(log_eps) / n
    mean_y = sum(log_unc) / n

    numerator = sum((log_eps[i] - mean_x) * (log_unc[i] - mean_y) for i in range(n))
    denominator = sum((log_eps[i] - mean_x) ** 2 for i in range(n))

    slope = numerator / denominator if denominator != 0 else 0

    print(f"Estimated slope (order of convergence): {slope:.4f}")

    if 0.8 <= slope <= 1.2:
        print("→ First-order convergence confirmed (ΔA ∝ ε)")
    elif slope > 1.2:
        print("→ Higher-order convergence observed")
    else:
        print("→ Slower than first-order convergence")

# ------------------------------------------------------------
# Visualization
# ------------------------------------------------------------

def visualize_results(results):

    eps = [r["epsilon"] for r in results]
    unc = [r["uncertainty"] for r in results]
    err = [r["abs_error"] for r in results]
    depth = [r["depth"] for r in results]
    boundary = [r["boundary_count"] for r in results]

    fig, axs = plt.subplots(2, 3, figsize=(15, 10))

    error_ratio = [r["error_ratio"] for r in results]

    # Existing plots...
    axs[0, 0].plot(eps, unc)
    axs[0, 0].set_title("Uncertainty vs Epsilon")

    axs[0, 1].plot(eps, err)
    axs[0, 1].set_title("Absolute Error vs Epsilon")

    axs[0, 2].plot(eps, error_ratio)
    axs[0, 2].set_title("|Error| / ΔA")

    axs[1, 0].plot(eps, depth)
    axs[1, 0].set_title("Max Depth vs Epsilon")

    axs[1, 1].plot(eps, boundary)
    axs[1, 1].set_title("Boundary Tile Count vs Epsilon")

    # NEW: Log-Log Convergence Plot
    log_eps = [math.log(e) for e in eps if e > 0]
    log_unc = [math.log(u) for u in unc if u > 0]

    axs[1, 2].plot(log_eps, log_unc)
    axs[1, 2].set_title("log(ΔA) vs log(ε)")

    plt.tight_layout()
    plt.show()

# ------------------------------------------------------------
# Interactive Entry Point
# ------------------------------------------------------------

def main():

    print("\nConvergence Analysis Module")
    print("============================")
    print("You are validating the adaptive tile-based area estimator.")
    print("This measures convergence, uncertainty behavior, and subdivision scaling.\n")

    print("Choose polygon:")
    print("1: Triangle")
    print("2: Random n-gon")

    choice = input("Selection: ")

    if choice == "1":
        polygon = Polygon([
            Point((0, 0)),
            Point((2, 0)),
            Point((1, 2))
        ])
    else:
        n = int(input("Enter number of vertices (n): "))
        polygon = random_polygon(n)

    tile_size = float(input("Enter tile size: "))
    overlap = float(input("Enter overlap: "))

    epsilons = [
        tile_size / 2,
        tile_size / 4,
        tile_size / 8,
        tile_size / 16,
        tile_size / 32
    ]

    run_convergence_experiment(
        polygon,
        tile_size,
        overlap,
        epsilons
    )


if __name__ == "__main__":
    main()
