from geometry.polygon import Polygon
from tiling.tile import Tile
from geometry.line import Line

def main():
    print("This is the file for testing all the classes or functions in geometry.")
    return
#test for polygon
def test_polygon():
    print(Polygon.__doc__)
    x = input("Enter 'c' to continue: ")
    if x.lower() == 'c':
        n = int(input("Enter the number of vertices: "))
        vertices = []
        for i in range(n):
            x = float(input("Enter the x coordinate: "))
            y = float(input("Enter the y coordinate: "))
            vertices.append((x, y))
        polygon = Polygon(vertices)
        print("Your polygon has been created. Enter 'c' to continue.")
        x = input(" ")
        if x.lower() == 'c':
            print(f"Area: {polygon.area()}")
            print(f"Perimeter: {polygon.perimeter()}")
            print(f"Centroid: {polygon.centroid()}")
            #to test edges, since its a generator
            for edge in polygon.edges():
                print(edge)
            print("To use point_in_polygon -- provide the point you want to test, press c: ")
            x = input("")
            if x.lower() == 'c':
                x = float(input("Enter the x coordinate: "))
                y = float(input("Enter the y coordinate: "))
                print(f"Point in polygon: {polygon.point_in_polygon((x, y))}")
    else:
        print("Invalid choice, function is returning.")
    return

#test for convex hull
def test_convex_hull():
    vertices = []
    n = int(input("How many vertices do you want: "))
    for i in range(n):
        x = float(input("Enter the x coordinate: "))
        y = float(input("Enter the y coordinate: "))
        vertices.append((x, y))
    polygon = Polygon(vertices)
    print(polygon.convex_hull())
#test for tile
def test_tile():
    print(Tile.__doc__)
    x = input("Enter 'c' to continue: ")
    if x == 'c':
        x_min = float(input("Enter the x_min coordinate: "))
        y_min = float(input("Enter the y_min coordinate: "))
        x_max = float(input("Enter the x_max coordinate: "))
        y_max = float(input("Enter the y_max coordinate: "))
        tile = Tile(x_min, y_min, x_max, y_max)
        print("Your tile has been created, press 'c' to continue: ")
        x = input("")
        if x == 'c':
            print(f"Area: {tile.area()}")
            print(f"Corners in clockwise rotation: {tile.corners_CW()}")
            print(f"Corners in counter-clockwise rotation: {tile.corners_CCW()}")
            print(f"Center: {tile.center()}")
    else:
        print("Invalid choice, function returning now.")
    return

#test for line
def test_line():
    print(Line.__doc__)
    x = input("Enter 'c' to continue: ")
    if x == 'c':
        x1 = float(input("Enter the x coordinate of point 1: "))
        y1 = float(input("Enter the y coordinate of point 1: "))
        x2 = float(input("Enter the x coordinate of point 2: "))
        y2 = float(input("Enter the y coordinate of point 2: "))
        line = Line((x1, y1), (x2, y2))
        print("Your line has been created, press 'c' to continue: ")
        x = input("")
        if x == 'c':
            print(f"Slope: {line.slope}")
            print(f"Intercept: {line.intercept}")
            print("Testing all further function with respect to (0,0) and intersection with respect to (0,0) and (1,1)")
            print(f"Side of point: {line.side((0, 0))}")
            print(f"Point on line: {line.point_on_line((0, 0))}")
            print(f"Intersection: {line.intersection(Line((0, 0), (1, 1)))}")
            print(f"Length: {line.length()}")
    else:
        print("Invalid choice, function returning now.")
    return
#choose what to test
def test():
    choice = input("Enter what you want to test: ")
    choice = choice.lower()
    if choice == "polygon":
        test_polygon()
    elif choice == "tile":
        test_tile()
    elif choice == "line":
        test_line()
    elif choice == "convex hull":
        test_convex_hull()
    else:
        print("Invalid choice")
    return

main()
test()