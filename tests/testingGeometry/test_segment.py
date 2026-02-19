from geometry.segment import Segment
from geometry.point import Point
import matplotlib.pyplot as plt


# ---------- VISUALISATION HELPERS ----------

def graph_segment(segment: Segment, title: str = "Segment Visualisation"):
    A = segment.A
    B = segment.B

    fig, ax = plt.subplots()

    x = [A.coordinates[0], B.coordinates[0]]
    y = [A.coordinates[1], B.coordinates[1]]

    ax.plot(x, y, marker='o', label="Segment AB")
    ax.scatter(x, y)

    ax.text(A.coordinates[0], A.coordinates[1],
            f"A{A.coordinates}", fontsize=9)
    ax.text(B.coordinates[0], B.coordinates[1],
            f"B{B.coordinates}", fontsize=9)

    mid = segment.midpoint
    ax.scatter(mid.coordinates[0], mid.coordinates[1], color="red", label="Midpoint")
    ax.text(mid.coordinates[0], mid.coordinates[1],
            f"Mid{mid.coordinates}", fontsize=9)

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title(title)
    ax.legend()
    ax.grid(True)

    plt.show()


def graph_intersection(seg1: Segment, seg2: Segment):
    fig, ax = plt.subplots()

    for seg, label in zip([seg1, seg2], ["Segment 1", "Segment 2"]):
        x = [seg.A.coordinates[0], seg.B.coordinates[0]]
        y = [seg.A.coordinates[1], seg.B.coordinates[1]]
        ax.plot(x, y, marker='o', label=label)

    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_title("Segment Intersection Test")
    ax.legend()
    ax.grid(True)

    plt.show()


# ---------- TEST SECTIONS ----------

def test_methods(segment: Segment):
    print("\n--- Testing Methods ---")
    print("Length of segment:", segment.length)
    print("Midpoint of segment:", segment.midpoint)


def test_properties(segment: Segment):
    print("\n--- Testing Properties ---")
    print("Endpoint A:", segment.A)
    print("Endpoint B:", segment.B)


def test_methods_self_only(segment: Segment):
    print("\n--- Testing Methods Requiring Only Self ---")
    bbox = segment.bounding_box()
    print("Bounding box:")
    print("Lower-left:", bbox[0])
    print("Upper-right:", bbox[1])


def test_methods_self_and_other(segment: Segment, do_graph: bool):
    print("\n--- Testing Methods Requiring Self & Other ---")

    print("Enter another segment:")
    cx = float(input("C.x: "))
    cy = float(input("C.y: "))
    dx = float(input("D.x: "))
    dy = float(input("D.y: "))

    other = Segment(Point((cx, cy)), Point((dx, dy)))

    print("Other segment created.")
    print("Does intersect:", segment.does_intersect(other))

    if do_graph:
        graph_intersection(segment, other)


def test_experimental_methods(segment: Segment):
    print("\n--- Testing Experimental / Internal Methods ---")

    print("Enter three points to test orientation:")
    px = float(input("P.x: "))
    py = float(input("P.y: "))
    qx = float(input("Q.x: "))
    qy = float(input("Q.y: "))
    rx = float(input("R.x: "))
    ry = float(input("R.y: "))

    P = Point((px, py))
    Q = Point((qx, qy))
    R = Point((rx, ry))

    orientation = Segment._orientation(P, Q, R)

    if orientation == 0:
        print("Orientation: Collinear")
    elif orientation == 1:
        print("Orientation: Clockwise")
    else:
        print("Orientation: Counterclockwise")


# ---------- MAIN DRIVER ----------

def test_segment():
    print("Testing the class 'Segment'")
    print(Segment.__doc__)

    x = input("\nRead the documentation and enter 'c' to continue: ")

    while x.lower() == 'c':

        reuse = input("Do you want to use the same segment everywhere? (y/n): ")
        segment = None

        if reuse.lower() == 'y':
            ax = float(input("A.x: "))
            ay = float(input("A.y: "))
            bx = float(input("B.x: "))
            by = float(input("B.y: "))
            segment = Segment(Point((ax, ay)), Point((bx, by)))

        graph = input("Do you want to graph the segment? (y/n): ")
        do_graph = graph.lower() == 'y'

        if segment is None:
            ax = float(input("A.x: "))
            ay = float(input("A.y: "))
            bx = float(input("B.x: "))
            by = float(input("B.y: "))
            segment = Segment(Point((ax, ay)), Point((bx, by)))

        print("\nSegment under test:")
        print("A:", segment.A)
        print("B:", segment.B)

        if do_graph:
            graph_segment(segment, title="Initial Segment")

        # 1. Methods
        test_methods(segment)

        # 2. Properties
        test_properties(segment)

        # 3. Methods requiring only self
        test_methods_self_only(segment)

        # 4. Methods requiring self & other
        test_methods_self_and_other(segment, do_graph)

        # 5. Experimental methods
        test_experimental_methods(segment)

        x = input("\nEnter 'c' to continue testing: ")


test_segment()
