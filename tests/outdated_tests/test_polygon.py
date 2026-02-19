"""
the test for the dataclass - Polygon
"""
from geometry.polygon import Polygon
from geometry.point import Point
from geometry.line import Line
import matplotlib.pyplot as plt
import math

def test_polygon():
    print("This is the test for the class Polygon")
    print(Polygon.__doc__)
    x = input("Read, and then enter 'c' to continue: ")
    while x.lower() == 'c':
        if x.lower() == 'c':
            d = input("Do you want to see the documentation? (y/n): ")
            if d.lower() == 'y':
                print(Polygon.__doc__)
            graph = input("Do you want to graph the polygon? (y/n): ")
            do_graph = False
            if graph.lower() == 'y':
                do_graph = True
            method = input("Enter the method you want to test: ")
            if method.lower() == "area":
                print("Initialize the polygon you want to test: ")
                n = int(input("Enter the number of vertices: "))
                vertices = []
                for i in range(n):
                    x = float(input(f"Enter the x coordinate of vertex {i+1}: "))
                    y = float(input(f"Enter the y coordinate of vertex {i+1}: "))
                    vertices.append((x, y))
                polygon = Polygon(vertices)
                print(f"Area: {polygon.area()}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = []
                    y = []
                    for i in range(n):
                        x.append(vertices[i][0])
                        y.append(vertices[i][1])
                        ax.text(vertices[i][0], vertices[i][1], f"Vertex {i+1}")
                    x.append(vertices[0][0])
                    y.append(vertices[0][1])
                    ax.plot(x, y)
                    ax.set_aspect("equal")
                    ax.grid()
                    plt.show()
            elif method.lower() == "perimeter":
                print("Initialize the polygon you want to test: ")
                n = int(input("Enter the number of vertices: "))
                vertices = []
                for i in range(n):
                    x = float(input(f"Enter the x coordinate of vertex {i+1}: "))
                    y = float(input(f"Enter the y coordinate of vertex {i+1}: "))
                    vertices.append((x, y))
                polygon = Polygon(vertices)
                print(f"Perimeter: {polygon.perimeter()}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = []
                    y = []
                    for i in range(n):
                        x.append(vertices[i][0])
                        y.append(vertices[i][1])
                        ax.text(vertices[i][0], vertices[i][1], f"Vertex {i+1}")
                    x.append(vertices[0][0])
                    y.append(vertices[0][1])
                    ax.plot(x, y)
                    ax.set_aspect("equal")
                    ax.grid()
                    plt.show()
            elif method.lower() == "optimized_convex_hull":
                print("Initialize the polygon you want to test: ")
                n = int(input("Enter the number of vertices: "))
                vertices = []
                for i in range(n):
                    x = float(input(f"Enter the x coordinate of vertex {i+1}: "))
                    y = float(input(f"Enter the y coordinate of vertex {i+1}: "))
                    vertices.append((x, y))
                polygon = Polygon(vertices)
                print(f"Optimized Convex Hull: {polygon.optimized_convex_hull()}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = []
                    y = []
                    for i in range(n):
                        x.append(vertices[i][0])
                        y.append(vertices[i][1])
                        ax.text(vertices[i][0], vertices[i][1], f"Vertex {i+1}")
                    x.append(vertices[0][0])
                    y.append(vertices[0][1])
                    ax.plot(x, y)
                    hull = polygon.optimized_convex_hull()
                    for i in range(len(hull.vertices)):
                        ax.plot(hull.vertices[i][0], hull.vertices[i][1], 'bo', c = "Red")
                        ax.text(hull.vertices[i][0], hull.vertices[i][1], f"Hull Vertex {i+1}")
                    ax.set_aspect("equal")
                    ax.grid()
                    plt.show()
            elif method.lower() == "point_in_polygon":
                print("Initialize the polygon you want to test: ")
                n = int(input("Enter the number of vertices: "))
                vertices = []
                for i in range(n):
                    x = float(input(f"Enter the x coordinate of vertex {i+1}: "))
                    y = float(input(f"Enter the y coordinate of vertex {i+1}: "))
                    vertices.append((x, y))
                polygon = Polygon(vertices)
                print("Initialize the point you want to test: ")
                x = float(input("Enter the x coordinate of the point: "))
                y = float(input("Enter the y coordinate of the point: "))
                point = Point((x, y))
                print(f"Point in Polygon: {polygon.point_in_polygon(point)}")
                if do_graph:
                    fig, ax = plt.subplots()
                    x = []
                    y = []
                    for i in range(n):
                        x.append(vertices[i][0])
                        y.append(vertices[i][1])
                        ax.text(vertices[i][0], vertices[i][1], f"Vertex {i+1}")
                    x.append(vertices[0][0])
                    y.append(vertices[0][1])
                    ax.plot(x, y)
                    ax.scatter(point.coordinates[0], point.coordinates[1], 'bo', c = "Red")
                    ax.text(point.coordinates[0], point.coordinates[1], f"Point")
                    ax.set_aspect("equal")
                    ax.grid()
                    plt.show()
        x = input("To continue testing, enter 'c': ")

test_polygon()