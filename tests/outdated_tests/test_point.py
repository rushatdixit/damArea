"""
test for the module point.py
"""
from geometry.point import Point
import matplotlib.pyplot as plt

def test_point():
    """
    tests for the Point class
    """
    print("This is the test for the class Point. It is very similar to a vector.")
    print(Point.__doc__)
    x = input("Read, and then enter 'c' to continue: ")
    while x.lower() == 'c':
        if x.lower() == 'c':
            graph = input("Do you want to graph the point? (y/n): ")
            do_graph = False
            if graph.lower() == 'y':
                do_graph = True
            print("NOTE: Some methods are only tested for 2D points.")
            method = input("Enter the method you want to test: ")
            if method.lower() == "polar_coordinates":
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                print(f"Polar coordinates: {point.polar_coordinates()}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [0, point.coordinates[0]]
                    y = [0, point.coordinates[1]]
                    ax.plot(x, y)
                    ax.annotate(f"({x[1]}, {y[1]})", (x[1], y[1]))
                    ax.set_aspect("equal")
                    ax.set_xlim(0, x[1]*y[1])
                    ax.set_ylim(0, x[1]*y[1])
                    ax.grid()
                    plt.show()
            elif method.lower() == "distance_from_origin":
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                print(f"Distance from origin: {point.distance_from_origin}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [0, point.coordinates[0]]
                    y = [0, point.coordinates[1]]
                    ax.plot(x, y)
                    ax.text(x[1], y[1], f"Length: {point.distance_from_origin}")
                    ax.set_aspect("equal")
                    ax.set_xlim(0, x[1]*y[1])
                    ax.set_ylim(0, x[1]*y[1])
                    ax.grid()
                    plt.show()
            elif method.lower() == "distance":
                print("Initialize the first point: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                print("Initialize the second point: ")
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                print(f"Distance: {point1.distance(point2)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text((x[1]+x[0])/2, (y[1]+y[0])/2, f"Length: {point1.distance(point2)}")
                    ax.set_aspect("equal")
                    ax.set_xlim(0, x[1]*y[1])
                    ax.set_ylim(0, x[1]*y[1])
                    ax.grid()
                    plt.show()
            elif method.lower() == "angle":
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                print(f"Angle: {point.angle}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [0, point.coordinates[0]]
                    y = [0, point.coordinates[1]]
                    ax.plot(x, y)
                    ax.text(x[1], y[1], f"Angle: {point.angle}")
                    ax.set_aspect("equal")
                    ax.set_xlim(0, x[1]*y[1])
                    ax.set_ylim(0, x[1]*y[1])
                    ax.grid()
                    plt.show()
            elif method.lower() == "dimension":
                print("Initialize the point you want to test: ")
                i = 0
                coords = []
                while True:
                    try:
                        coordinates = float(input(f"Enter the {i+1}th coordinate: "))
                        coords.append(coordinates)
                        if i > 2:
                            print("Reminder: To stop entering coordinates, enter a non-numeric value.")
                        i += 1
                    except ValueError:
                        break
                point = Point(coords)
                print(f"Dimension: {point.dimension}")
                if do_graph:
                    print("You cannot graph a point with more than 2 dimensions.")
            elif method.lower() == "rotate":
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                phi = float(input("Enter the angle of rotation: "))
                print(f"Rotated point: {point.rotate(phi)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [0, point.coordinates[0]]
                    y = [0, point.coordinates[1]]
                    ax.plot(x, y)
                    newpoint = point.rotate(phi)
                    x = [0, newpoint.coordinates[0]]
                    y = [0, newpoint.coordinates[1]]
                    ax.plot(x, y)
                    ax.text(x[1], y[1], f"Rotated point: {newpoint}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-x[1]*y[1], x[1]*y[1])
                    ax.set_ylim(-x[1]*y[1], x[1]*y[1])
                    ax.grid()
                    plt.show()
            elif method.lower() == "cross":
                print("Initialize the first point: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                print("Initialize the second point: ")
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                print(f"Cross product: {point1.cross(point2)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x1 = [0, point1.coordinates[0]]
                    y1 = [0, point1.coordinates[1]]
                    x2 = [0, point2.coordinates[0]]
                    y2 = [0, point2.coordinates[1]]
                    a_plus_b_x = [x1[1], x2[1] + x1[1]]
                    a_plus_b_y = [y1[1], y2[1] + y1[1]]
                    a_minus_b_x = [x2[1], x2[1] + x1[1]]
                    a_minus_b_y = [y2[1], y2[1] + y1[1]]
                    ax.plot(x1, y1, label = "Point 1: Vector")
                    ax.plot(x2, y2, label = "Point 2: Vector")
                    ax.plot(a_plus_b_x, a_plus_b_y, label = "Point 1 + Point 2 : Vector")
                    ax.plot(a_minus_b_x, a_minus_b_y, label = "Point 2 - Point 1 : Vector")
                    ax.set_aspect("equal")
                    if (x2[1] > x1[1]):
                        ax.set_xlim(-x2[1]*y2[1], x2[1]*y2[1])
                    else:
                        ax.set_xlim(-x1[1]*y1[1], x1[1]*y1[1])
                    if (y2[1] > y1[1]):
                        ax.set_ylim(-y2[1]*x2[1], y2[1]*x2[1])
                    else:
                        ax.set_ylim(-y1[1]*x1[1], y1[1]*x1[1])
                    ax.grid()
                    ax.legend()
                    ax.set_title("Cross product")
                    plt.show()
            elif method.lower() == "dot":
                print("Initialize the first point: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                print("Initialize the second point: ")
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                print(f"Dot product: {point1.dot(point2)}")
                if do_graph:
                    print("You cannot graph a dot product.")
            x = input("Do you want to continue testing? ('c' to continue): ")
    return

test_point()
