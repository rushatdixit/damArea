"""
test for the dataclass line
"""
from geometry.line import Line
from geometry.point import Point
import matplotlib.pyplot as plt
import math

def test_line():
    print("This is the test for the class Line")
    print(Line.__doc__)
    x = input("Read, and then enter 'c' to continue: ")
    while x.lower() == 'c':
        if x.lower() == 'c':
            d = input("Do you want to see the documentation? (y/n): ")
            if d.lower() == 'y':
                print(Line.__doc__)
            graph = input("Do you want to graph the line? (y/n): ")
            do_graph = False
            if graph.lower() == 'y':
                do_graph = True
            print("NOTE: Some methods are only tested for 2D lines.")
            method = input("Enter the method you want to test: ")
            if method.lower() == "slope":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print(f"Slope: {line.slope}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text((x[1]+x[0])/2, (y[1]+y[0])/2, f"Slope: {line.slope}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "intercept":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print(f"Intercept: {line.intercept}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text(0, line.intercept, f"Intercept: {line.intercept}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "side":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                print(f"Side: {line.side(point)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.scatter(point.coordinates[0], point.coordinates[1])
                    ax.text(point.coordinates[0], point.coordinates[1], f"Side: {line.side(point)}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "point_on_line":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                point = Point((x, y))
                print(f"Point on line: {line.point_on_line(point)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text(point.coordinates[0], point.coordinates[1], f"Point on line: {line.point_on_line(point)}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "intersection":
                print("Initialize the first line: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line1 = Line(point1, point2)
                print("Initialize the second line: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point3 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point4 = Point((x, y))
                line2 = Line(point3, point4)
                print(f"Intersection: {line1.intersection(line2)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x1 = [point1.coordinates[0], point2.coordinates[0]]
                    y1 = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x1, y1, label = "Line 1")
                    x2 = [point3.coordinates[0], point4.coordinates[0]]
                    y2 = [point3.coordinates[1], point4.coordinates[1]]
                    ax.plot(x2, y2, label = "Line 2")
                    ax.text(line1.intersection(line2).coordinates[0], line1.intersection(line2).coordinates[1], f"Intersection: {line1.intersection(line2)}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x1[1]*y1[1]), abs(x1[1]*y1[1]))
                    ax.set_ylim(-abs(x1[1]*y1[1]), abs(x1[1]*y1[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "length":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print(f"Length: {line.length()}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text((point1.coordinates[0] + point2.coordinates[0]) / 2, (point1.coordinates[1] + point2.coordinates[1]) / 2, f"Length: {line.length()}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            elif method.lower() == "is_vertical":
                print("Initialize the line you want to test: ")
                x = float(input("Enter the x coordinate of the first point: "))
                y = float(input("Enter the y coordinate of the first point: "))
                point1 = Point((x, y))
                x = float(input("Enter the x coordinate of the second point: "))
                y = float(input("Enter the y coordinate of the second point: "))
                point2 = Point((x, y))
                line = Line(point1, point2)
                print(f"Is vertical: {line.is_vertical}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = [point1.coordinates[0], point2.coordinates[0]]
                    y = [point1.coordinates[1], point2.coordinates[1]]
                    ax.plot(x, y)
                    ax.text((point1.coordinates[0] + point2.coordinates[0]) / 2, (point1.coordinates[1] + point2.coordinates[1]) / 2, f"Is vertical: {line.is_vertical}")
                    ax.set_aspect("equal")
                    ax.set_xlim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.set_ylim(-abs(x[1]*y[1]), abs(x[1]*y[1]))
                    ax.grid()
                    plt.show()
            
            x = input("If you want to continue testing, enter 'c': ")

test_line()